/*
 * ClipboardDaemon.c
 * Faceless Background Application for Clipboard Synchronization
 *
 * Config:
 *  - File Type: APPL
 *  - Creator: ???? (Any unique signature)
 *  - SIZE resource: High Level Events aware, Background Only (optional)
 */

#include <Events.h>
#include <Memory.h>
#include <QDOffscreen.h>
#include <QuickDraw.h>
#include <Resources.h>
#include <Scrap.h>
#include <ToolUtils.h>
#include <Windows.h> /* Fixed: MacWindows.h -> Windows.h */

/* Opcodes */
#define OP_CLIP_GET_IMG_SIZE 0x7131
#define OP_CLIP_GET_IMG_DATA 0x7132
#define OP_CLIP_PUT_IMG 0x7133

/*
 * Trap Wrappers
 * We use 0xA89F as a Gateway.
 * We declare functions with opcode as the FIRST argument.
 * C calling convention (default) pushes arguments Right-to-Left.
 * So 'opcode' will be valid at the Top of Stack (Low Address) when Trap
 * executes.
 */

/* void TrapSize(long opcode, long* outSize) */
void CallSizeTrap(long opcode, long *outSize) = { 0xA89F, 0x4E75 };

/* long TrapRead(long opcode, void* buffer, long size) */
/* Return value extraction might be tricky with void trap.
   But 68k C compiler expects return in D0.
   If our Trap Handler sets D0, it works!
*/
long CallReadTrap(long opcode, void *buffer, long size) = { 0xA89F, 0x4E75 };

/* void TrapWrite(long opcode, long type, void* buffer, long size) */
void CallWriteTrap(long opcode, long type, void *buffer, long size) = {
  0xA89F,
  0x4E75
};

void GetHostImageSize(long *outSize) {
  CallSizeTrap(OP_CLIP_GET_IMG_SIZE, outSize);
}

long ClipboardGetImageData(void *buffer, long size) {
  return CallReadTrap(OP_CLIP_GET_IMG_DATA, buffer, size);
}

void ClipboardPutImage(long type, void *buffer, long size) {
  CallWriteTrap(OP_CLIP_PUT_IMG, type, buffer, size);
}

/* Global Sync State */
static long gLastScrapCount = -1;
static long gLastHostSize = -1;

/* Forward Declarations */
void SyncImageToHost(void);
void SyncImageFromHost(void);

void SyncImageToHost(void) {
  long offset, len;
  Handle hScrap;
  PicHandle pict;
  Rect bounds;
  GWorldPtr gWorld;
  PixMapHandle pixMap;
  Ptr data;
  long totalSize;
  long width, height;
  OSErr err;

  /* 1. Check Mac Scrap Count */
  /* We assume LScrap is maintained by OS. */
  /* InfoScrap is quick check */
  /* But to be safe and simple, we check GetScrap result length or offset
   * change? */
  /* Actually GetScrap with a empty handle returns size. */

  hScrap = NewHandle(0);
  len = GetScrap(hScrap, 'PICT', &offset);

  if (len <= 0) {
    DisposeHandle(hScrap);
    return;
  }

  if (len == gLastScrapCount) {
    DisposeHandle(hScrap);
    return;
  }
  /* Update count immediately to enforce sync-once per change */
  gLastScrapCount = len;

  pict = (PicHandle)hScrap;
  /* QuickDraw expects locked handle usually or copy? GetScrap returns a copy of
   * scrap handle content. */
  /* bounds check */
  if (GetHandleSize((Handle)pict) < 10) { /* Too small header */
    DisposeHandle(hScrap);
    return;
  }

  bounds = (**pict).picFrame;
  width = bounds.right - bounds.left;
  height = bounds.bottom - bounds.top;

  /* Limit size to avoid freezing system on huge copy */
  if (width * height > 2048 * 2048) {
    DisposeHandle(hScrap);
    return;
  }

  /* Create GWorld to render PICT */
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposeHandle(hScrap);
    return;
  }

  /* Draw PICT to GWorld */
  {
    CGrafPtr oldPort;
    GDHandle oldDev;
    GetGWorld(&oldPort, &oldDev);
    SetGWorld(gWorld, NULL);

    LockPixels(GetGWorldPixMap(gWorld));
    EraseRect(&bounds);
    DrawPicture(pict, &bounds);
    UnlockPixels(GetGWorldPixMap(gWorld));

    SetGWorld(oldPort, oldDev);
  }

  /* Extract RGB */
  pixMap = GetGWorldPixMap(gWorld);
  if (LockPixels(pixMap)) {
    Ptr baseAddr = GetPixBaseAddr(pixMap);
    long gWorldRowBytes = (*pixMap)->rowBytes & 0x3FFF;
    totalSize = 16 + (height * width * 4);

    data = NewPtr(totalSize);
    if (data) {
      *(long *)data = width;
      *(long *)(data + 4) = height;
      *(long *)(data + 8) = width * 4;
      *(long *)(data + 12) = 32;

      {
        long y;
        Ptr src = baseAddr;
        Ptr dst = data + 16;
        long rowLen = width * 4;
        for (y = 0; y < height; y++) {
          BlockMove(src, dst, rowLen);
          src += gWorldRowBytes;
          dst += rowLen;
        }
      }

      UnlockPixels(pixMap);

      /* Send to Host */
      ClipboardPutImage('IMG ', data, totalSize);

      DisposePtr(data);
    }
  }

  DisposeGWorld(gWorld);
  DisposeHandle(hScrap);
}

void SyncImageFromHost(void) {
  long size;
  Ptr data;
  long width, height, rowBytes;
  GWorldPtr gWorld;
  PixMapHandle pixMap;
  Rect bounds;
  PicHandle pict;
  OSErr err;

  GetHostImageSize(&size);
  if (size <= 0)
    return;

  if (size == gLastHostSize)
    return;
  gLastHostSize = size;

  data = NewPtr(size);
  if (!data)
    return;

  if (ClipboardGetImageData(data, size) != size) {
    DisposePtr(data);
    return;
  }

  width = *(long *)data;
  height = *(long *)(data + 4);
  rowBytes = *(long *)(data + 8);

  SetRect(&bounds, 0, 0, width, height);
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposePtr(data);
    return;
  }

  pixMap = GetGWorldPixMap(gWorld);
  if (LockPixels(pixMap)) {
    Ptr baseAddr = GetPixBaseAddr(pixMap);
    long gWorldRowBytes = (*pixMap)->rowBytes & 0x3FFF;
    long y;
    Ptr src = data + 16;
    Ptr dst = baseAddr;

    for (y = 0; y < height; y++) {
      BlockMove(src, dst, width * 4);
      src += rowBytes;
      dst += gWorldRowBytes;
    }
    UnlockPixels(pixMap);
  } else {
    DisposeGWorld(gWorld);
    DisposePtr(data);
    return;
  }

  DisposePtr(data);

  /* Convert GWorld to PICT */
  pict = OpenPicture(&bounds);
  if (pict) {
    GrafPtr port;
    GetPort(&port);
    /* Ensure we copy from GWorld to Current Port (which is OpenPicture port) */
    CopyBits((BitMap *)*pixMap, &port->portBits, &bounds, &bounds, srcCopy,
             NULL);
    ClosePicture();

    /* Put on Clipboard */
    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    /* Update local counter to prevent bounce-back loop */
    {
      long offset;
      Handle hScrap = NewHandle(0);
      gLastScrapCount = GetScrap(hScrap, 'PICT', &offset);
      DisposeHandle(hScrap);
    }
  }

  DisposeGWorld(gWorld);
}

void main(void) {
  EventRecord event;
  long finalTicks;

  /* Initialize Toolbox */
  InitGraf(&qd.thePort);
  InitFonts();
  InitWindows();
  InitMenus();
  TEInit();
  InitDialogs(NULL);
  InitCursor();

  /* Main Event Loop */
  while (true) {
    /* Process events (quit etc) */
    WaitNextEvent(everyEvent, &event, 1, NULL);

    /* Clipboard Sync */
    SyncImageFromHost();
    SyncImageToHost();

    /* FORCE sleep for 60 ticks (1 second) */
    Delay(60, &finalTicks);
  }
}
