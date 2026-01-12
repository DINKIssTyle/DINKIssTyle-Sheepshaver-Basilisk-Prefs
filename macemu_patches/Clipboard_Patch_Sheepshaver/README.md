# SheepShaver Clipboard Patch

SDL 기반 양방향 클립보드 공유 패치

## 개요

SheepShaver용 클립보드 패치입니다. Mac ↔ Host 양방향 텍스트 클립보드를 지원합니다.

## 지원 상태

| 방향 | 상태 | 비고 |
|-----|------|-----|
| Mac → Host | ✅ 지원 | 텍스트 전용 |
| Host → Mac | ✅ 지원 | 텍스트 전용 |

> **참고**: 이미지 클립보드(PICT)는 현재 지원되지 않습니다.

## 사용법

### 1. 패치 적용

```bash
./apply_clipboard_patch.sh /path/to/macemu
```

### 2. 설정

`~/.sheepshaver_prefs` 파일에서:
```
name_encoding 3
noclipconversion false
```

### 3. 빌드

```bash
cd /path/to/macemu/SheepShaver/src/Unix
make
```

## 지원 인코딩

| 값 | 언어 |
|---|-----|
| 0 | MacRoman (기본) |
| 3 | 한국어 (EUC-KR) |
| 1 | 일본어 |
| 2 | 중국어 번체 |
| 25 | 중국어 간체 |

## 패치 파일

| 파일 | 설명 |
|-----|------|
| `clip_sdl.cpp` | SDL 기반 양방향 클립보드 구현 (메인 파일) |
| `clip.h` | 클립보드 함수 선언 |
| `emul_op.cpp` | EmulOp 핸들러 (NativeOp 클립보드 지원) |
| `emul_op.h` | EmulOp opcode 정의 |

## 기술 세부사항

### Host → Mac 클립보드
- Mac 앱에서 붙여넣기(⌘V)를 실행하면 `GetScrap()` 함수가 호출됨
- SDL 클립보드에서 텍스트를 가져와 68k 트랩을 통해 Mac 클립보드에 주입
- UTF-8 → Mac 인코딩 변환 지원

### Mac → Host 클립보드
- Mac 앱에서 복사(⌘C)를 실행하면 `PutScrap()` 함수가 호출됨
- Mac 클립보드 데이터를 SDL 클립보드로 전송
- Mac 인코딩 → UTF-8 변환 지원

## 라이선스

GNU General Public License v2

## 작성자

Copyright (C) 2026 DINKIssTyle. All rights reserved.
