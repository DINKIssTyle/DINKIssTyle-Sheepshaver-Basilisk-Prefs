# macemu 쉐이더 패치

Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.

macemu(Basilisk II, SheepShaver) 에뮬레이터에 GLSL 쉐이더 지원을 추가하는 패치입니다.

---

## 📋 패치 내용

### 추가된 기능 
- **GLSL 쉐이더 렌더링** - CRT, 스캔라인 등 다양한 효과 적용 가능
- **쉐이더 파라미터 조절** - 밝기, 대비, 감마 등 실시간 조정
- **핫키 리로드** - 설정 변경 후 즉시 적용 (기본: F6)

### 추가되는 설정 항목
| 설정 | 타입 | 설명 |
|-----|-----|-----|
| `shader` | STRING | GLSL 쉐이더 파일 경로 |
| `shader_params` | STRING | 쉐이더 파라미터 (key=value,...) |
| `key_shader_toggle` | STRING | 쉐이더 리로드 핫키 (예: F6) |

---

## 📁 폴더 구조

```
macemu-patch/
├── apply_shader_patch.sh    # 패치 적용 스크립트
├── README.md                # 이 파일
├── macemu/                  # 오리지널 macemu (패치 대상)
│   ├── BasiliskII/
│   │   └── build.sh         # BasiliskII 빌드 스크립트
│   └── SheepShaver/
│       └── build.sh         # SheepShaver 빌드 스크립트
└── patches/                 # 패치 파일들
    ├── basilisk_*.patch     # BasiliskII용 패치
    └── sheepshaver_*.patch  # SheepShaver용 패치
```

---

## 🚀 사용 방법

### 1. 패치 적용

```bash
cd /home/dinki/Desktop/macemu-patch
./apply_shader_patch.sh
```

다른 경로의 macemu를 패치하려면:
```bash
./apply_shader_patch.sh /path/to/your/macemu
```

패치 스크립트는 다음을 자동으로 수행합니다:
- 쉐이더 관련 소스 파일 패치 적용
- `prefs.cpp` 버퍼 크기 수정 (256 → 4096, 긴 shader_params 지원)
- `BasiliskII/build.sh`, `SheepShaver/build.sh` 빌드 스크립트 생성

**BasiliskII:**
```bash
./macemu/BasiliskII/build.sh
```

**SheepShaver:**
```bash
./macemu/SheepShaver/build.sh
```

### 3. 쉐이더 설정

`~/.basilisk_ii_prefs` 또는 `~/.sheepshaver_prefs` 파일에 추가:

```
shader /path/to/shader.glsl
shader_params brightness=1.2,contrast=1.1
key_shader_toggle F6
```

---

## 📦 패치 파일 목록

### BasiliskII
| 파일 | 설명 |
|-----|-----|
| `basilisk_prefs_items.patch` | 쉐이더 설정 항목 추가 |
| `basilisk_configure.patch` | 빌드 설정 (video_shader.cpp, -lGL) |
| `basilisk_video_sdl2.patch` | 쉐이더 렌더링 통합 |
| `basilisk_video_shader_cpp.patch` | 쉐이더 시스템 구현 (신규) |
| `basilisk_video_shader_h.patch` | 쉐이더 헤더 (신규) |
| `basilisk_prefs_buffer.patch` | prefs.cpp 버퍼 크기 증가 (256→4096) |

### SheepShaver
| 파일 | 설명 |
|-----|-----|
| `sheepshaver_prefs_items.patch` | 쉐이더 설정 항목 추가 |
| `sheepshaver_configure.patch` | 빌드 설정 (video_shader.cpp, -lGL) |
| `sheepshaver_video_sdl2.patch` | 쉐이더 렌더링 통합 |
| `sheepshaver_video_shader_cpp.patch` | 쉐이더 시스템 구현 (신규) |
| `sheepshaver_video_shader_h.patch` | 쉐이더 헤더 (신규) |

---

## ⚠️ 주의사항

- **OpenGL 필수**: 쉐이더 기능은 OpenGL을 필요로 합니다.
- **SDL2 필수**: SDL2 비디오 드라이버가 필요합니다.
- **빌드 의존성**: `libgl1-mesa-dev`, `libsdl2-dev`, `libgtk-3-dev` 등 필요

### 의존성 설치 (Ubuntu/Debian)
```bash
sudo apt install build-essential autoconf automake \
  libsdl2-dev libgtk-3-dev libgl1-mesa-dev
```

---

## 📝 변경 이력

- **2026-01-10**: 초기 패치 시스템 구축
  - 쉐이더 렌더링 지원 추가
  - prefs.cpp 버퍼 크기 4096으로 증가 (긴 shader_params 지원)
