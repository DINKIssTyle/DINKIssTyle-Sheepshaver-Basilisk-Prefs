# BasiliskII Clipboard Patch

SDL 기반 클립보드 공유 패치 (다국어 인코딩 지원)

## 개요

이 패치는 BasiliskII에 SDL 클립보드 API를 사용한 클립보드 공유 기능을 추가합니다.
기존 X11 기반 구현을 대체하며, 다국어 인코딩 변환을 지원합니다.

> **참고**: 이 패치는 BasiliskII 전용입니다. SheepShaver는 PowerPC 에뮬레이션 특성상 호스트→Mac 방향이 구현되지 않아 제외되었습니다.

## 지원 언어/인코딩

| name_encoding 값 | 언어 | 인코딩 |
|------------------|------|--------|
| 0 (기본값) | 영어/서유럽어 | MacRoman |
| 1 | 일본어 | EUC-JP |
| 2 | 중국어 번체 | Big5 |
| **3** | **한국어** | **EUC-KR** |
| 4 | 아랍어 | ISO-8859-6 |
| 5 | 히브리어 | ISO-8859-8 |
| 6 | 그리스어 | ISO-8859-7 |
| 7 | 키릴 문자 | KOI8-R |
| 25 | 중국어 간체 | GB2312 |

## 사용법

### 1. 패치 적용

```bash
./apply_clipboard_patch.sh /path/to/macemu
```

### 2. 설정

프레퍼런스 에디터 또는 설정 파일에서:

1. **Name Encoding**을 사용하는 언어로 설정 (예: Korean = 3)
2. **"No Clipboard Conversion"** 체크 해제 (필수!)

설정 파일 예시 (`~/.basilisk_ii_prefs`):
```
name_encoding 3
noclipconversion false
```

### 3. 빌드

```bash
cd /path/to/macemu/BasiliskII/src/Unix
make
```

## 파일 목록

- `apply_clipboard_patch.sh` - 패치 적용 스크립트
- `patches/clip_sdl.cpp` - SDL 클립보드 구현

## 라이선스

GNU General Public License v2

## 작성자

Copyright (C) 2026 DINKIssTyle. All rights reserved.
