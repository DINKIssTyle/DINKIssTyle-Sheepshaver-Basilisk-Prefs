/*
 * Clipboard Image Control Panel (cdev)
 * Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights
 * reserved.
 *
 * Simple control panel to test PICT creation and clipboard operations.
 * When opened, creates a red square PICT and puts it on clipboard.
 */

#include <Controls.h>
#include <Dialogs.h>
#include <Memory.h>
#include <QDOffscreen.h>
#include <QuickDraw.h>
#include <Scrap.h>
#include <Sound.h>
#include <ToolUtils.h>
#include <Types.h>
#include <stdio.h>
#include <string.h>

/* Opcodes - MUST match emul_op.h */
#define OP_CLIP_GET_IMG_SIZE 0x7131
#define OP_CLIP_GET_IMG_DATA 0x7132
#define OP_CLIP_PUT_IMG 0x7133

/* Control Panel message constants */
#define initDev 0
#define hitDev 1
#define closeDev 2
#define nulDev 3
#define updateDev 4
#define activDev 5
#define deactivDev 6
#define keyEvtDev 7
#define macDev 8
#define undoDev 9
#define cutDev 10
#define copyDev 11
#define pasteDev 12
#define clearDev 13

/* Dialog item IDs */
#define kTestButton 1
#define kStatusText 2

/* Global Variables for Polling */
static long gLastScrapCount = -1;
static long gLastHostSize = -1;

/* Forward declarations */
void SyncImageToHost(void);
void SyncImageFromHost(void);
void DrawStatus(Str255 msg);
void DrawStatusNum(char *msg, long num);

/*
 * Opcode Wrappers (C Calling Convention)
 */
void GetHostImageSize(long *outSize) = { 0x7131 };
long ClipboardGetImageData(void *buffer, long size) = { 0x7132 };
void ClipboardPutImage(long type, void *buffer, long size) = { 0x7133 };

/* Status Helper (Dummy for now, or draw to dialog) */
void DrawStatus(Str255 msg) {
  /* TODO: Draw to kStatusText item if possible, or just ignore */
}
void DrawStatusNum(char *msg, long num) {
  /* Silent for cdev automatic mode, or use logic to display if needed */
}

/*
 * Main cdev entry point
 * Called by the Control Panel with various messages
 */
pascal long main(short message, short item, short numItems, short CPanelID,
                 EventRecord *theEvent, long cdevValue, DialogPtr CPDialog) {
  long result = cdevValue;

  switch (message) {
  case initDev:
    /* Initialization - return non-zero to indicate success */
    result = 1;
    /* Initialize monitoring globals */
    {
      long offset;
      Handle hScrap = NewHandle(0);
      gLastScrapCount = GetScrap(hScrap, 'PICT', &offset);
      DisposeHandle(hScrap);

      GetHostImageSize(&gLastHostSize);
    }
    break;

  case hitDev:
    /* User clicked an item */
    if (item - numItems == kTestButton) {
      /* Test button clicked - Manual Sync to Host */
      SyncImageToHost();
    }
    break;

  case closeDev:
    /* Control panel closing */
    break;

  case nulDev:
    /* Idle time - called periodically */
    SyncImageFromHost();
    SyncImageToHost();
    break;

  case updateDev:
    /* Need to update display */
    break;

  case activDev:
    /* Control panel activated */
    break;

  case deactivDev:
    /* Control panel deactivated */
    break;

  case macDev:
    /* Machine check */
    result = 1; /* We work on all machines */
    break;

  default:
    break;
  }

  return result;
}

/*
 * Create a test PICT and put it on the clipboard
 */
/*
 * Sync Mac -> Host
 * Checks if Scrap size changed or just runs on demand.
 * For automatic, we should check GetScrap counter if possible, or just size.
 */
void SyncImageToHost(void) {
  long offset, len;
  Handle hScrap;
  OSErr err;
  PicHandle pict;
  Rect bounds;
  GWorldPtr gWorld;
  PixMapHandle pixMap;
  Ptr data;
  long totalSize;
  long width, height, rowBytes;

  /* 1. Get PICT from Scrap */
  hScrap = NewHandle(0);
  len = GetScrap(hScrap, 'PICT', &offset);

  if (len <= 0) {
    DisposeHandle(hScrap);
    return;
  }

  /* Check change by size (rudimentary) */
  if (len == gLastScrapCount) {
    DisposeHandle(hScrap);
    return;
  }
  gLastScrapCount = len;

  /* 2. Load Picture */
  pict = (PicHandle)hScrap;

  /* Get PICT Bounds */
  bounds = (**pict).picFrame;
  width = bounds.right - bounds.left;
  height = bounds.bottom - bounds.top;

  /* 3. Create GWorld */
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposeHandle(hScrap);
    return;
  }

  /* 4. Draw PICT to GWorld */
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

  /* 5. Prepare Buffer for Host */
  pixMap = GetGWorldPixMap(gWorld);
  if (LockPixels(pixMap)) {
    Ptr baseAddr = GetPixBaseAddr(pixMap);
    long gWorldRowBytes = (*pixMap)->rowBytes & 0x3FFF;

    /* Calculate Size: Header(16) + Data */
    totalSize = 16 + (height * width * 4);

    data = NewPtr(totalSize);
    if (data) {
      /* Write Header */
      *(long *)data = width;
      *(long *)(data + 4) = height;
      *(long *)(data + 8) = width * 4; // RowBytes
      *(long *)(data + 12) = 32;       // Depth

      /* Copy Pixels */
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

      /* 6. Send to Host */
      ClipboardPutImage('IMG ', data, totalSize);

      DisposePtr(data);
      SysBeep(1); /* Notify success */
    }
  }

  DisposeGWorld(gWorld);
  DisposeHandle(hScrap);
}

/*
 * Sync Host -> Mac
 */
void SyncImageFromHost(void) {
  long size;
  Ptr data;
  long width, height, rowBytes;
  GWorldPtr gWorld;
  PixMapHandle pixMap;
  Rect bounds;
  PicHandle pict;
  OSErr err;

  /* 1. Check Image Size */
  GetHostImageSize(&size);
  if (size <= 0)
    return;

  /* Check change by size */
  if (size == gLastHostSize)
    return;
  gLastHostSize = size;

  /* 2. Allocate Memory */
  data = NewPtr(size);
  if (!data)
    return;

  /* 3. Retrieve Data */
  if (ClipboardGetImageData(data, size) != size) {
    DisposePtr(data);
    return;
  }

  /* 4. Parse Header */
  width = *(long *)data;
  height = *(long *)(data + 4);
  rowBytes = *(long *)(data + 8);

  /* 5. Create GWorld */
  SetRect(&bounds, 0, 0, width, height);
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposePtr(data);
    return;
  }

  /* 6. Copy Pixels to GWorld */
  pixMap = GetGWorldPixMap(gWorld);
  if (LockPixels(pixMap)) {
    Ptr baseAddr = GetPixBaseAddr(pixMap);
    long gWorldRowBytes = (*pixMap)->rowBytes & 0x3FFF;
    long y;
    Ptr src = data + 16; /* Skip header */
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

  /* 7. Create Picture from GWorld */
  pict = OpenPicture(&bounds);
  if (pict) {
    GrafPtr port;
    GetPort(&port);
    CopyBits((BitMap *)*pixMap, &port->portBits, &bounds, &bounds, srcCopy,
             NULL);
    ClosePicture();

    /* 8. Put on Clipboard */
    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    SysBeep(2); /* Notify success */

    /* Update LastScrapCount to avoid bounce-back loop */
    {
      long offset;
      Handle hScrap = NewHandle(0);
      gLastScrapCount = GetScrap(hScrap, 'PICT', &offset);
      DisposeHandle(hScrap);
    }
  }

  DisposeGWorld(gWorld);
}
