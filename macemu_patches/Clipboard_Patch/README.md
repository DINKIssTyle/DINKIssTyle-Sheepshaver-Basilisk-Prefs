# Clipboard Patch for macemu

BasiliskII와 SheepShaver용 양방향 클립보드 공유 패치

## 개요

macemu(BasiliskII/SheepShaver)용 통합 클립보드 패치입니다.  
Mac ↔ Host 양방향 텍스트 클립보드를 지원합니다.

## 지원 상태

| 방향 | BasiliskII | SheepShaver |
|------|------------|-------------|
| Mac → Host | ✅ 지원 | ✅ 지원 |
| Host → Mac | ✅ 지원 | ✅ 지원 |

> **참고**: 현재 텍스트(TEXT) 클립보드만 지원됩니다. 이미지(PICT)는 미지원.

## 사용법

### 1. 패치 적용

```bash
./apply_clipboard_patch.sh /path/to/macemu
```

### 2. 빌드

```bash
# BasiliskII
cd /path/to/macemu/BasiliskII/src/Unix
./configure && make

# SheepShaver  
cd /path/to/macemu/SheepShaver/src/Unix
./configure && make
```

### 3. 설정 (선택)

`~/.basilisk_ii_prefs` 또는 `~/.sheepshaver_prefs`:
```
name_encoding 3
noclipconversion false
```

## 지원 인코딩

| 값 | 언어 |
|---|-----|
| 0 | MacRoman (기본) |
| 1 | 일본어 |
| 2 | 중국어 번체 |
| 3 | 한국어 (EUC-KR) |
| 25 | 중국어 간체 |

## 패치 파일

| 파일 | 설명 |
|-----|------|
| `clip_sdl.cpp` | SDL 기반 양방향 클립보드 구현 (새 파일) |
| `basilisk_clip_h.patch` | clip.h 수정 (새 함수 선언) |
| `sheepshaver_emul_op_h.patch` | emul_op.h 수정 (NativeOp 코드 추가) |
| `sheepshaver_emul_op_cpp.patch` | emul_op.cpp 수정 (NativeOp 핸들러 추가) |

## 라이선스

GNU General Public License v2

## 작성자

Copyright (C) 2026 DINKIssTyle. All rights reserved.
