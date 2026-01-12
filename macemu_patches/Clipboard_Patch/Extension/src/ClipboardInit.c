/*
 * ClipboardInit.c
 * System Extension (INIT) for Background Clipboard Sync
 *
 * Patches GetNextEvent to sync clipboard during idle time.
 */

#include <Gestalt.h>
#include <Memory.h>
#include <OSUtils.h>
#include <QDOffscreen.h>
#include <QuickDraw.h>
#include <Resources.h>
#include <Scrap.h>
#include <ToolUtils.h>
#include <Traps.h>
#include <Types.h>
#include <Video.h>

/* Opcodes */
#define OP_CLIP_GET_IMG_SIZE 0x7131
#define OP_CLIP_GET_IMG_DATA 0x7132
#define OP_CLIP_PUT_IMG 0x7133

/* Gestalt Selector */
#define kGestaltClipboard 'clp+'

/* Global Storage Structure */
typedef struct {
  UniversalProcPtr oldGetNextEvent;
  long lastScrapCount;
  long lastHostSize;
  Boolean inSync; /* Re-entrancy protection */
} ClipGlobals, *ClipGlobalsPtr;

/* Forward Declarations */
void SyncImageToHost(ClipGlobalsPtr g);
void SyncImageFromHost(ClipGlobalsPtr g);
pascal OSErr ClipboardGestalt(OSType selector, long *response);
pascal Boolean MyGetNextEvent(unsigned short eventMask, EventRecord *theEvent);

/* Typedef for GetNextEvent function pointer */
typedef pascal Boolean (*GetNextEventProc)(unsigned short eventMask,
                                           EventRecord *theEvent);

/* Typedef for Gestalt function pointer (if missing) */
#ifndef SelectorFunctionUPP
typedef pascal OSErr (*SelectorFunctionUPP)(OSType selector, long *response);
#endif

/* Opcode Wrappers */
void GetHostImageSize(long *outSize) = { 0x7131 };
long ClipboardGetImageData(void *buffer, long size) = { 0x7132 };
void ClipboardPutImage(long type, void *buffer, long size) = { 0x7133 };

/*
 * GetTrapAddress (0xA146) - Machine Code Glue
 * Glue required because this is a register-based OS Trap not in standard libs
 * sometimes. Pascal convention: Arg on stack, Result on stack (or D0 for C).
 * Input: trapNum (2 bytes) on stack.
 * Output: Address in D0 (for C return).
 * Cleanup: Pop 2 bytes.
 */
pascal UniversalProcPtr GetTrapAddress(short trapNum) = {
  0x302F,
  0x0004, /* move.w 4(sp), d0   ; Get trapNum */
  0xA146, /* _GetTrapAddress    ; Call Trap */
  0x2008, /* move.l a0, d0      ; Move result to D0 */
  0x205F, /* move.l (sp)+, a0   ; Pop return address */
  0x544F, /* addq.l #2, sp      ; Pop arguments */
  0x4ED0  /* jmp (a0)           ; Return */
};

/*
 * SetTrapAddress (0xA047) - Machine Code Glue
 * Pascal convention: SetTrapAddress(trapAddr, trapNum)
 * Stack: [Ret] [trapNum:2] [trapAddr:4]
 */
pascal void SetTrapAddress(UniversalProcPtr trapAddr, short trapNum) = {
  0x302F,
  0x0004, /* move.w 4(sp), d0   ; Get trapNum */
  0x206F,
  0x0006, /* move.l 6(sp), a0   ; Get trapAddr */
  0xA047, /* _SetTrapAddress    ; Call Trap */
  0x205F, /* move.l (sp)+, a0   ; Pop return addr */
  0x5C4F, /* addq.l #6, sp      ; Pop args (4+2) */
  0x4ED0  /* jmp (a0)           ; Return */
};

/*
 * ClipboardGestalt has been replaced by dynamic code generation in main()
 * to avoid static data access issues in INIT resource.
 */

/*
 * Patch: GetNextEvent
 */
pascal Boolean MyGetNextEvent(unsigned short eventMask, EventRecord *theEvent) {
  long response;
  ClipGlobalsPtr g = NULL;
  Boolean result;

  /* 1. Retrieve Globals via Gestalt */
  /* This is safe because Gestalt table is global */
  if (Gestalt(kGestaltClipboard, &response) == noErr) {
    g = (ClipGlobalsPtr)response;
  }

  /* CRITICAL: check if g was actually patched. If still DEADBEEF, we crash if
   * used. */
  if ((unsigned long)g == 0xDEADBEEF || (unsigned long)g == 0) {
    /* Not patched yet or invalid. Do nothing but call original if possible?
       We can't call original if we don't have g->oldGetNextEvent!
       But wait, if g is bad, we can't find oldGetNextEvent.
       This is a catastrophic failure state. We should just return false
       (swallow event) or try to crash gracefully. Returning false is safest.
    */
    return false;
  }

  /* 2. Call Original Trap */
  if (g && g->oldGetNextEvent) {
    GetNextEventProc oldProc = (GetNextEventProc)g->oldGetNextEvent;
    result = oldProc(eventMask, theEvent);
  } else {
    return false;
  }

  /* 3. Do Sync Logic on Null Event (Idle) */
  if (g && !g->inSync && theEvent->what == nullEvent) {
    g->inSync = true;

    /*
       Safeguard: Ensure we have a valid GDevice/Port
       Sometimes GetNextEvent is called early.
    */
    if (GetMainDevice()) {
      SyncImageFromHost(g);
      SyncImageToHost(g);
    }

    g->inSync = false;
  }

  return result;
}

/*
 * Main Entry Point (INIT)
 */
void main(void) {
  long response;
  ClipGlobalsPtr g;
  unsigned short *glueCode;

  /* 1. Check if already installed */
  if (Gestalt(kGestaltClipboard, &response) == noErr) {
    SysBeep(1); /* Already installed beep */
    return;
  }

  /* 2. Allocate Globals in System Heap */
  g = (ClipGlobalsPtr)NewPtrSysClear(sizeof(ClipGlobals));
  if (!g) {
    SysBeep(30);
    return;
  }

  g->lastScrapCount = -1;
  g->lastHostSize = -1;
  g->inSync = false;

  /* 3. Create Gestalt Glue Code dynamically in System Heap */
  /* This avoids accessing any static data (global vars) which crashes without
   * A4 */
  /* Size: ~24 bytes is enough */
  glueCode = (unsigned short *)NewPtrSysClear(32);
  if (!glueCode) {
    SysBeep(30);
    return;
  }

  /* Construct 68k Code:
   * 206F 0004       move.l 4(sp), a0
   * 20BC GGGG GGGG  move.l #g, (a0)
   * 7000            moveq #0, d0
   * 225F            move.l (sp)+, a1
   * 504F            addq.l #8, sp
   * 4E91            jmp (a1)
   */
  glueCode[0] = 0x206F;
  glueCode[1] = 0x0004;
  glueCode[2] = 0x20BC;

  /* Split 32-bit pointer g into two 16-bit words */
  glueCode[3] = (unsigned short)((unsigned long)g >> 16);
  glueCode[4] = (unsigned short)((unsigned long)g & 0xFFFF);

  glueCode[5] = 0x7000;
  glueCode[6] = 0x225F;
  glueCode[7] = 0x504F;
  glueCode[8] = 0x4E91;

  /* Flush I-Cache for the new code */
  BlockMove(glueCode, glueCode, 32);

  /* 3. Install Gestalt Selector using our dynamic code */
  NewGestalt(kGestaltClipboard, (SelectorFunctionUPP)glueCode);

  /* 4. Store Old Trap */
  g->oldGetNextEvent = GetTrapAddress(0xA970);

  /* 5. Patch Trap */
  SetTrapAddress((UniversalProcPtr)MyGetNextEvent, 0xA970);

  /* Beep to signal success */
  SysBeep(1);
  {
    long dummy;
    Delay(30, &dummy);
  }
}

/*
 * Sync Logic (Adapted from TestApp)
 */
void SyncImageToHost(ClipGlobalsPtr g) {
  long offset, len;
  Handle hScrap;
  OSErr err;
  PicHandle pict;
  Rect bounds;
  GWorldPtr gWorld;
  PixMapHandle pixMap;
  Ptr data;
  long totalSize;
  long width, height;

  /* Check Scrap Forcefully (GetScrap) */
  /* Note: InfoScrap() is faster? */
  /* PInfoScrap pInfo = (PInfoScrap)InfoScrap(); */
  /* if (pInfo->scrapCount == g->lastScrapCount) return; */

  /* We use GetScrap to be sure of size */
  hScrap = NewHandle(0);
  len = GetScrap(hScrap, 'PICT', &offset);

  if (len <= 0) {
    DisposeHandle(hScrap);
    return;
  }

  if (len == g->lastScrapCount) {
    DisposeHandle(hScrap);
    return;
  }
  g->lastScrapCount = len;

  pict = (PicHandle)hScrap;
  bounds = (**pict).picFrame;
  width = bounds.right - bounds.left;
  height = bounds.bottom - bounds.top;

  /* Limitation: Don't sync huge images automatically in background to avoid lag
   */
  if (width * height > 1024 * 768) {
    DisposeHandle(hScrap);
    return;
  }

  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposeHandle(hScrap);
    return;
  }

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
      ClipboardPutImage('IMG ', data, totalSize);
      DisposePtr(data);
    }
  }

  DisposeGWorld(gWorld);
  DisposeHandle(hScrap);
}

void SyncImageFromHost(ClipGlobalsPtr g) {
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

  if (size == g->lastHostSize)
    return;
  g->lastHostSize = size;

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

  pict = OpenPicture(&bounds);
  if (pict) {
    /* Need valid port for CopyBits? OpenPicture sets up its own port usually */
    /* But to be safe, we rely on QuickDraw dispatch */
    GrafPtr port;
    GetPort(&port);

    CopyBits((BitMap *)*pixMap, &port->portBits, &bounds, &bounds, srcCopy,
             NULL);
    ClosePicture();

    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    /* Updates local counter to avoid bounce */
    {
      long offset;
      Handle hScrap = NewHandle(0);
      g->lastScrapCount = GetScrap(hScrap, 'PICT', &offset);
      DisposeHandle(hScrap);
    }
  }

  DisposeGWorld(gWorld);
}
