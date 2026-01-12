/*
 *  ClipboardTest.c
 *  Test Host <-> Guest Clipboard Image Transfer
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

/* Opcodes - MUST match emul_op.h */
#define OP_CLIP_GET_IMG_SIZE 0x7131
#define OP_CLIP_GET_IMG_DATA 0x7132

/* Global Variables */
WindowPtr gWindow;
Boolean gDone;

/*
 * Opcode Wrappers
 * Using standard 68k glue for opcodes
 */

pascal long ClipboardGetImageSize(void) = { 0x7131 };
pascal long ClipboardGetImageData(void *buffer, long size) = { 0x7132 };

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

/**
 * SyncImageFromHost
 * Checks if host has image, retrieves it, creates PICT, puts on clipboard
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
  char str[256];

  /* 1. Check Image Size */
  size = ClipboardGetImageSize();
  if (size <= 0) {
    SysBeep(1);
    return; /* No image or error */
  }

  /* 2. Allocate Memory */
  /* Use TempNewHandle for temporary large storage? Or NewPtr */
  data = NewPtr(size);
  if (!data) {
    SysBeep(30); /* OOM */
    return;
  }

  /* 3. Retrieve Data */
  if (ClipboardGetImageData(data, size) != size) {
    DisposePtr(data);
    SysBeep(30);
    return;
  }

  /* 4. Parse Header (matches FetchHostImage)
     [Width(4)][Height(4)][RowBytes(4)][Depth(4)]...Pixels
  */
  width = *(long *)data;
  height = *(long *)(data + 4);
  rowBytes = *(long *)(data + 8);
  /* depth ignored, assumed 32 */

  /* 5. Create GWorld */
  SetRect(&bounds, 0, 0, width, height);
  err = NewGWorld(&gWorld, 32, &bounds, NULL, NULL, 0);
  if (err != noErr) {
    DisposePtr(data);
    SysBeep(20);
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

    /* Copy row by row since rowBytes might differ */
    for (y = 0; y < height; y++) {
      BlockMove(src, dst, width * 4); /* 32-bit = 4 bytes */
      src += rowBytes;
      dst += gWorldRowBytes;
    }

    UnlockPixels(pixMap);
  }

  DisposePtr(data); /* Raw data no longer needed */

  /* 7. Create Picture from GWorld */
  pict = OpenPicture(&bounds);
  if (pict) {
    /* CopyBits from GWorld to Picture (current port) */
    CopyBits((BitMap *)*pixMap, &qd.thePort->portBits, &bounds, &bounds,
             srcCopy, NULL);
    ClosePicture();

    /* 8. Put on Clipboard */
    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    SysBeep(10); /* Success! */
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
          /* Click in window triggers sync */
          SyncImageFromHost();
        }
        break;
      case keyDown:
      case autoKey:
        if ((event.message & charCodeMask) == 'q') {
          gDone = true;
        }
        break;
      }
    }
  }
}

void main(void) {
  Rect bounds;

  InitToolbox();

  SetRect(&bounds, 50, 50, 400, 300);
  gWindow = NewWindow(NULL, &bounds, "\pClick to Sync Image", true,
                      documentProc, (WindowPtr)-1, true, 0);

  gDone = false;

  ShowWindow(gWindow);
  MainLoop();
}
