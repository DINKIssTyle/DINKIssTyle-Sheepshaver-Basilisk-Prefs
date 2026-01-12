/*
 * PICT Test with VBL delayed execution
 * Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights
 * reserved.
 *
 * Uses VBL Task to delay execution until after QuickDraw is fully initialized
 */

#include <Memory.h>
#include <QuickDraw.h>
#include <Retrace.h>
#include <Scrap.h>
#include <Sound.h>
#include <Types.h>

/* VBL Task record - must be in global or static memory */
typedef struct {
  VBLTask vbl;
  short count;
} MyVBLRec;

static MyVBLRec gVBL;
static Boolean gDone = false;

/* Forward declaration */
pascal void MyVBLTask(void);

/* Create PICT and put on clipboard */
void CreatePICT(void) {
  GrafPort myPort;
  Rect bounds;
  PicHandle pict;
  long dummy;

  /* 새 GrafPort 생성 */
  OpenPort(&myPort);

  /* 64x64 사각형 정의 */
  SetRect(&bounds, 0, 0, 64, 64);

  /* PICT 생성 시작 */
  pict = OpenPicture(&bounds);
  if (pict != NULL) {
    /* 빨간색으로 채우기 */
    ForeColor(redColor);
    PaintRect(&bounds);

    /* 파란색 테두리 */
    ForeColor(blueColor);
    FrameRect(&bounds);

    /* 기본 색상 복원 */
    ForeColor(blackColor);

    ClosePicture();

    /* 클립보드에 넣기 */
    ZeroScrap();
    HLock((Handle)pict);
    PutScrap(GetHandleSize((Handle)pict), 'PICT', *pict);
    HUnlock((Handle)pict);
    KillPicture(pict);

    /* 성공 - 두 번 비프 */
    SysBeep(10);
    Delay(30, &dummy);
    SysBeep(10);
  } else {
    /* OpenPicture 실패 */
    SysBeep(5);
    Delay(10, &dummy);
    SysBeep(5);
    Delay(10, &dummy);
    SysBeep(5);
    Delay(10, &dummy);
    SysBeep(5);
  }

  /* 포트 정리 */
  ClosePort(&myPort);
}

/* VBL Task - called every 1/60th second */
pascal void MyVBLTask(void) {
  /* Continue counting down */
  gVBL.count--;

  if (gVBL.count <= 0) {
    /* Time's up - do our work */
    gDone = true;
    gVBL.vbl.vblCount = 0; /* Don't reschedule */
  } else {
    /* Keep waiting */
    gVBL.vbl.vblCount = 60; /* Check again in 1 second */
  }
}

/* Extension entry point */
void main(void) {
  long dummy;

  /* 시작 비프 */
  SysBeep(10);

  /* Initialize VBL task - wait 3 seconds for system to settle */
  gVBL.vbl.qType = vType;
  gVBL.vbl.vblAddr = (VBLUPP)MyVBLTask;
  gVBL.vbl.vblCount = 60; /* 1 second intervals */
  gVBL.vbl.vblPhase = 0;
  gVBL.count = 3; /* Wait 3 seconds total */
  gDone = false;

  /* Install VBL task */
  VInstall((QElemPtr)&gVBL.vbl);

  /* Wait for VBL to complete (blocking) */
  while (!gDone) {
    /* Spin wait - not ideal but simple for test */
  }

  /* Remove VBL task */
  VRemove((QElemPtr)&gVBL.vbl);

  /* Now create the PICT */
  CreatePICT();
}
