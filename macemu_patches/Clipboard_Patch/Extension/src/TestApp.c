/*
 *  ClipboardTest.c
 *  Test Host <-> Guest Clipboard Image Transfer
 *  debug version
 *
 *  Created by DINKIssTyle on 2026.
 *  Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
 */

#include <Dialogs.h>
#include <Events.h>
#include <Fonts.h>
#include <Memory.h>
#include <Menus.h>
#include <QDOffscreen.h>
#include <QuickDraw.h>
#include <Scrap.h>
#include <SegLoad.h>
#include <Sound.h>
#include <TextEdit.h>
#include <ToolUtils.h>
#include <Types.h>
#include <Windows.h>
#include <stdio.h>
#include <string.h>

/* Opcodes - MUST match emul_op.h */
#define OP_CLIP_GET_IMG_SIZE 0x7131
#define OP_CLIP_GET_IMG_DATA 0x7132
#define OP_CLIP_PUT_IMG 0x7133

/* Global Variables */
WindowPtr gWindow;
Boolean gDone;

/* Forward Declarations */
void CtoPStr(char *cStr, Str255 pStr);
void DrawStatus(Str255 msg);
void DrawStatusNum(char *msg, long num);

/*
 * Opcode Wrappers (C Calling Convention)
 * Caller cleans up stack. Args pushed right-to-left.
 */
void GetHostImageSize(long *outSize) = { 0x7131 };
long ClipboardGetImageData(void *buffer, long size) = { 0x7132 };
void ClipboardPutImage(long type, void *buffer, long size) = { 0x7133 };

/* Initialize Toolbox */
void InitToolbox(void) {
  InitGraf(&qd.thePort);
  InitFonts();
  InitWindows();
  InitMenus();
  TEInit();
  InitDialogs(NULL);
  InitCursor();
}

void DrawStatus(Str255 msg) {
  Rect r = gWindow->portRect;
  SetPort(gWindow);
  TextFont(systemFont);
  TextSize(12);
  ForeColor(blackColor);
  BackColor(whiteColor);
  EraseRect(&r);
  MoveTo(20, 30);
  DrawString(msg);
}

/* Helper to convert C string to Pascal string */
void CtoPStr(char *cStr, Str255 pStr) {
  long len = strlen(cStr);
  if (len > 255)
    len = 255;
  pStr[0] = (unsigned char)len;
  BlockMove(cStr, pStr + 1, len);
}

void DrawStatusNum(char *msg, long num) {
  Str255 pStr;
  char cStr[256];

  sprintf(cStr, "%s: %ld", msg, num);
  CtoPStr(cStr, pStr);
  DrawStatus(pStr);
}

/**
 * SyncImageToHost
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

  DrawStatus("\pChecking Mac Clipboard...");

  /* 1. Get PICT from Scrap */
  hScrap = NewHandle(0);
  len = GetScrap(hScrap, 'PICT', &offset);
  if (len <= 0) {
    DrawStatus("\pError: No PICT in Clipboard");
    DisposeHandle(hScrap);
    SysBeep(1);
    return;
  }

  DrawStatusNum("Found PICT, Size", len);

  /* 2. Load Picture */
  pict = (PicHandle)hScrap;

  /* Get PICT Bounds */
  bounds = (**pict).picFrame;
  width = bounds.right - bounds.left;
  height = bounds.bottom - bounds.top;

  DrawStatusNum("PICT Width:", width);

  /* 3. Create GWorld */
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DrawStatusNum("Error: NewGWorld Failed", (long)err);
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

  DrawStatus("\pPICT Drawn to GWorld.");

  /* 5. Prepare Buffer for Host */
  pixMap = GetGWorldPixMap(gWorld);
  if (LockPixels(pixMap)) {
    Ptr baseAddr = GetPixBaseAddr(pixMap);
    long gWorldRowBytes = (*pixMap)->rowBytes & 0x3FFF;

    /* Calculate Size: Header(16) + Data */
    totalSize = 16 + (height * width * 4);

    data = NewPtr(totalSize);
    if (!data) {
      DrawStatus("\pError: Out of Memory for Send");
      DisposeGWorld(gWorld);
      DisposeHandle(hScrap);
      return;
    }

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

    DrawStatusNum("Sending Size:", totalSize);

    /* 6. Send to Host */
    ClipboardPutImage('IMG ', data, totalSize);

    DisposePtr(data);
    DrawStatus("\pSent to Host!");
    SysBeep(1);

  } else {
    DrawStatus("\pError: LockPixels Failed");
  }

  DisposeGWorld(gWorld);
  DisposeHandle(hScrap);
}

/**
 * SyncImageFromHost
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
  char msg[256];
  Str255 pMsg;

  DrawStatus("\pChecking Host Clipboard...");

  /* 1. Check Image Size */
  GetHostImageSize(&size);
  if (size <= 0) {
    sprintf(msg, "Error: No Image (Size=%ld)", size);
    CtoPStr(msg, pMsg);
    DrawStatus(pMsg);
    SysBeep(1);
    return;
  }

  DrawStatusNum("Image Size found", size);

  /* 2. Allocate Memory */
  data = NewPtr(size);
  if (!data) {
    sprintf(msg, "Error: Out of Memory (Size=%ld)", size);
    CtoPStr(msg, pMsg);
    DrawStatus(pMsg);
    SysBeep(1);
    return;
  }

  /* 3. Retrieve Data */
  if (ClipboardGetImageData(data, size) != size) {
    DisposePtr(data);
    DrawStatus("\pError: Data Transfer Failed");
    SysBeep(1);
    return;
  }

  /* 4. Parse Header */
  width = *(long *)data;
  height = *(long *)(data + 4);
  rowBytes = *(long *)(data + 8);

  DrawStatusNum("Image Info Read, Width:", width);

  /* 5. Create GWorld */
  SetRect(&bounds, 0, 0, width, height);
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposePtr(data);
    DrawStatusNum("Error: NewGWorld Failed", (long)err);
    SysBeep(1);
    return;
  }
  DrawStatus("\pGWorld Created.");

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
    DrawStatus("\pError: LockPixels Failed");
    DisposeGWorld(gWorld);
    DisposePtr(data);
    return;
  }

  DrawStatus("\pPixels Copied.");
  DisposePtr(data);

  /* 7. Create Picture from GWorld */
  pict = OpenPicture(&bounds);
  if (pict) {
    CopyBits((BitMap *)*pixMap, &qd.thePort->portBits, &bounds, &bounds,
             srcCopy, NULL);
    ClosePicture();

    DrawStatus("\pPicture Created. Putting on Scrap...");

    /* 8. Put on Clipboard */
    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    DrawStatus("\pSuccess! Image Copied.");
    SysBeep(1);
  } else {
    DrawStatus("\pError: OpenPicture Failed");
  }

  DisposeGWorld(gWorld);
}

/* Main Event Loop */
void MainLoop(void) {
  EventRecord event;

  while (!gDone) {
    if (WaitNextEvent(everyEvent, &event, 60, NULL)) {
      switch (event.what) {
      case mouseDown:
        if (FindWindow(event.where, &gWindow) == inContent) {
          SyncImageFromHost();
        }
        break;
      case keyDown:
      case autoKey: {
        char key = event.message & charCodeMask;
        if (key == 'q' || key == 'Q') {
          gDone = true;
        } else if (key == 's' || key == 'S') {
          SyncImageToHost();
        }
      } break;
      case updateEvt:
        BeginUpdate(gWindow);
        DrawStatus("\pClick to Sync(Recv), 'S' to Send");
        EndUpdate(gWindow);
        break;
      }
    }
  }
}

void DrawStatusHex(char *msg, unsigned long num) {
  char buf[256];
  Str255 pBuf;
  sprintf(buf, "%s %08lX", msg, num);
  CtoPStr(buf, pBuf);
  DrawStatus(pBuf);
}

void main(void) {
  Rect bounds;

  InitToolbox();

  SetRect(&bounds, 50, 50, 400, 300);
  gWindow = (WindowPtr)NewCWindow(NULL, &bounds, "\pClipboard Test", true,
                                  documentProc, (WindowPtr)-1, true, 0);

  gDone = false;

  ShowWindow(gWindow);
  MainLoop();
}
