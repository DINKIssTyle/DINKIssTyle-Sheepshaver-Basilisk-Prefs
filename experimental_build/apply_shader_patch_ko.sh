#!/bin/bash
# ============================================================================
# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
# ============================================================================
# macemu 쉐이더 패치 적용 스크립트
# 사용법: ./apply_shader_patch.sh [macemu_path]
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES_DIR="${SCRIPT_DIR}/patches"
MACEMU_DIR="${1:-${SCRIPT_DIR}/macemu}"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# macemu 폴더 확인
if [ ! -d "$MACEMU_DIR" ]; then
    print_error "macemu 폴더를 찾을 수 없습니다: $MACEMU_DIR"
    echo ""
    print_info "먼저 macemu를 클론하세요:"
    echo "  git clone https://github.com/kanjitalk755/macemu.git"
    exit 1
fi

if [ ! -d "$PATCHES_DIR" ]; then
    print_error "patches 폴더를 찾을 수 없습니다: $PATCHES_DIR"
    exit 1
fi

# macemu 디렉토리명 추출 (상대 경로용)
MACEMU_BASENAME=$(basename "$MACEMU_DIR")
WORK_DIR=$(dirname "$MACEMU_DIR")

print_info "작업 디렉토리: $WORK_DIR"
print_info "macemu 폴더: $MACEMU_BASENAME"
print_info "패치 폴더: $PATCHES_DIR"
echo ""

# BasiliskII 패치 적용
apply_basilisk_patches() {
    print_info "BasiliskII 패치 적용 중..."
    
    local basilisk_dir="${MACEMU_DIR}/BasiliskII"
    
    if [ ! -d "$basilisk_dir" ]; then
        print_warning "BasiliskII 폴더를 찾을 수 없습니다. 건너뜁니다."
        return 1
    fi
    
    cd "$WORK_DIR"
    
    # 개별 패치 적용
    local patches=(
        "basilisk_prefs_items.patch"
        "basilisk_configure.patch"
        "basilisk_video_sdl2.patch"
        "basilisk_video_shader_cpp.patch"
        "basilisk_video_shader_h.patch"
    )
    
    for patch_file in "${patches[@]}"; do
        if [ -f "${PATCHES_DIR}/${patch_file}" ]; then
            # 패치 파일 내 경로를 실제 디렉토리명으로 치환
            local temp_patch="/tmp/${patch_file}.tmp"
            sed "s|macemu/|${MACEMU_BASENAME}/|g; s|macemu_patched/|${MACEMU_BASENAME}/|g" \
                "${PATCHES_DIR}/${patch_file}" > "$temp_patch"
            
            print_info "  적용 중: ${patch_file}"
            if patch -p0 --dry-run < "$temp_patch" > /dev/null 2>&1; then
                patch -p0 < "$temp_patch"
            else
                print_warning "  이미 적용되었거나 충돌: ${patch_file}"
            fi
            rm -f "$temp_patch"
        else
            print_warning "  패치 파일 없음: ${patch_file}"
        fi
    done
    
    print_success "BasiliskII 패치 완료!"
    return 0
}

# SheepShaver 패치 적용
apply_sheepshaver_patches() {
    print_info "SheepShaver 패치 적용 중..."
    
    local sheepshaver_dir="${MACEMU_DIR}/SheepShaver"
    
    if [ ! -d "$sheepshaver_dir" ]; then
        print_warning "SheepShaver 폴더를 찾을 수 없습니다. 건너뜁니다."
        return 1
    fi
    
    cd "$WORK_DIR"
    
    # 개별 패치 적용
    local patches=(
        "sheepshaver_prefs_items.patch"
        "sheepshaver_configure.patch"
        "sheepshaver_video_sdl2.patch"
        "sheepshaver_video_shader_cpp.patch"
        "sheepshaver_video_shader_h.patch"
    )
    
    for patch_file in "${patches[@]}"; do
        if [ -f "${PATCHES_DIR}/${patch_file}" ]; then
            # 패치 파일 내 경로를 실제 디렉토리명으로 치환
            local temp_patch="/tmp/${patch_file}.tmp"
            sed "s|macemu/|${MACEMU_BASENAME}/|g; s|macemu_patched/|${MACEMU_BASENAME}/|g" \
                "${PATCHES_DIR}/${patch_file}" > "$temp_patch"
            
            print_info "  적용 중: ${patch_file}"
            if patch -p0 --dry-run < "$temp_patch" > /dev/null 2>&1; then
                patch -p0 < "$temp_patch"
            else
                print_warning "  이미 적용되었거나 충돌: ${patch_file}"
            fi
            rm -f "$temp_patch"
        else
            print_warning "  패치 파일 없음: ${patch_file}"
        fi
    done
    
    print_success "SheepShaver 패치 완료!"
    return 0
}

# 메인 실행
echo "======================================"
echo "  macemu 쉐이더 패치 스크립트"
echo "======================================"
echo ""

apply_basilisk_patches
echo ""
apply_sheepshaver_patches

echo ""

# prefs.cpp 버퍼 크기 수정 (256 -> 4096)
print_info "prefs.cpp 버퍼 크기 수정 중..."
for prefs_file in "${MACEMU_DIR}/BasiliskII/src/prefs.cpp" "${MACEMU_DIR}/SheepShaver/src/prefs.cpp"; do
    if [ -f "$prefs_file" ]; then
        if grep -q 'char line\[256\]' "$prefs_file"; then
            sed -i 's/char line\[256\];/char line[4096];  \/\/ Increased for long shader_params/' "$prefs_file"
            print_info "  수정됨: $(basename $(dirname $(dirname $prefs_file)))/src/prefs.cpp"
        fi
    fi
done

# 빌드 스크립트 생성
print_info "빌드 스크립트 생성 중..."

# BasiliskII 빌드 스크립트
cat > "${MACEMU_DIR}/BasiliskII/build.sh" << 'BUILDSCRIPT'
#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/src/Unix"
cd "$BUILD_DIR"
echo "[INFO] BasiliskII 빌드 시작..."
[ ! -f "../SDL/video_shader.cpp" ] && echo "[ERROR] video_shader.cpp 없음. 패치 먼저 적용하세요." && exit 1
[ ! -f "configure" ] && NO_CONFIGURE=1 ./autogen.sh
[ ! -f "Makefile" ] && ./configure --enable-sdl-video=yes --enable-sdl-audio=yes --disable-vosf --without-esd --without-mon --with-gtk --enable-jit-compiler
make -j$(nproc)
[ -f "BasiliskII" ] && echo "[SUCCESS] 빌드 완료: ${BUILD_DIR}/BasiliskII" || echo "[ERROR] 빌드 실패!"
BUILDSCRIPT
chmod +x "${MACEMU_DIR}/BasiliskII/build.sh"

# SheepShaver 빌드 스크립트
cat > "${MACEMU_DIR}/SheepShaver/build.sh" << 'BUILDSCRIPT'
#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/src/Unix"
cd "$BUILD_DIR"
echo "[INFO] SheepShaver 빌드 시작..."
[ ! -f "../SDL/video_shader.cpp" ] && echo "[ERROR] video_shader.cpp 없음. 패치 먼저 적용하세요." && exit 1
[ ! -f "configure" ] && NO_CONFIGURE=1 ./autogen.sh
[ ! -f "Makefile" ] && ./configure --enable-sdl-video=yes --enable-sdl-audio=yes --disable-vosf --without-esd --without-mon --with-gtk --enable-jit-compiler
make -j$(nproc)
[ -f "SheepShaver" ] && echo "[SUCCESS] 빌드 완료: ${BUILD_DIR}/SheepShaver" || echo "[ERROR] 빌드 실패!"
BUILDSCRIPT
chmod +x "${MACEMU_DIR}/SheepShaver/build.sh"

print_success "빌드 스크립트 생성 완료!"

echo ""
echo "======================================"
print_success "모든 패치 적용 완료!"
echo "======================================"
echo ""
print_info "빌드하려면 다음 스크립트를 실행하세요:"
echo "  - BasiliskII: ${MACEMU_DIR}/BasiliskII/build.sh"
echo "  - SheepShaver: ${MACEMU_DIR}/SheepShaver/build.sh"
