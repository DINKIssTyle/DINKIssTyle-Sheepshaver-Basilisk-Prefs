#!/bin/bash
# ============================================================================
# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
# ============================================================================
# macemu Shader Patch Script
# Usage: ./apply_shader_patch.sh [macemu_path]
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES_DIR="${SCRIPT_DIR}/patches"
MACEMU_DIR="${1:-${SCRIPT_DIR}/../macemu}"

# Color definitions
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

# Check macemu folder
if [ ! -d "$MACEMU_DIR" ]; then
    print_error "macemu folder not found: $MACEMU_DIR"
    echo ""
    print_info "Please clone macemu first:"
    echo "  git clone https://github.com/kanjitalk755/macemu.git"
    exit 1
fi

if [ ! -d "$PATCHES_DIR" ]; then
    print_error "patches folder not found: $PATCHES_DIR"
    exit 1
fi

# Extract macemu directory name (for relative paths)
MACEMU_BASENAME=$(basename "$MACEMU_DIR")
WORK_DIR=$(dirname "$MACEMU_DIR")

print_info "Working directory: $WORK_DIR"
print_info "macemu folder: $MACEMU_BASENAME"
print_info "Patches folder: $PATCHES_DIR"
echo ""

# Apply BasiliskII patches
apply_basilisk_patches() {
    print_info "Applying BasiliskII patches..."
    
    local basilisk_dir="${MACEMU_DIR}/BasiliskII"
    
    if [ ! -d "$basilisk_dir" ]; then
        print_warning "BasiliskII folder not found. Skipping."
        return 1
    fi
    
    cd "$WORK_DIR"
    
    # Apply individual patches
    local patches=(
        "basilisk_prefs_items.patch"
        "basilisk_configure.patch"
        "basilisk_video_sdl2.patch"
        "basilisk_video_shader_cpp.patch"
        "basilisk_video_shader_h.patch"
    )
    
    for patch_file in "${patches[@]}"; do
        if [ -f "${PATCHES_DIR}/${patch_file}" ]; then
            # Replace paths in patch file with actual directory name
            local temp_patch="/tmp/${patch_file}.tmp"
            sed "s|macemu/|${MACEMU_BASENAME}/|g; s|macemu_patched/|${MACEMU_BASENAME}/|g" \
                "${PATCHES_DIR}/${patch_file}" > "$temp_patch"
            
            print_info "  Applying: ${patch_file}"
            if patch -p0 --dry-run < "$temp_patch" > /dev/null 2>&1; then
                patch -p0 < "$temp_patch"
            else
                print_warning "  Already applied or conflict: ${patch_file}"
            fi
            rm -f "$temp_patch"
        else
            print_warning "  Patch file not found: ${patch_file}"
        fi
    done
    
    print_success "BasiliskII patches complete!"
    return 0
}

# Apply SheepShaver patches
apply_sheepshaver_patches() {
    print_info "Applying SheepShaver patches..."
    
    local sheepshaver_dir="${MACEMU_DIR}/SheepShaver"
    
    if [ ! -d "$sheepshaver_dir" ]; then
        print_warning "SheepShaver folder not found. Skipping."
        return 1
    fi
    
    cd "$WORK_DIR"
    
    # Apply individual patches
    local patches=(
        "sheepshaver_prefs_items.patch"
        "sheepshaver_configure.patch"
        "sheepshaver_video_sdl2.patch"
        "sheepshaver_video_shader_cpp.patch"
        "sheepshaver_video_shader_h.patch"
    )
    
    for patch_file in "${patches[@]}"; do
        if [ -f "${PATCHES_DIR}/${patch_file}" ]; then
            # Replace paths in patch file with actual directory name
            local temp_patch="/tmp/${patch_file}.tmp"
            sed "s|macemu/|${MACEMU_BASENAME}/|g; s|macemu_patched/|${MACEMU_BASENAME}/|g" \
                "${PATCHES_DIR}/${patch_file}" > "$temp_patch"
            
            print_info "  Applying: ${patch_file}"
            if patch -p0 --dry-run < "$temp_patch" > /dev/null 2>&1; then
                patch -p0 < "$temp_patch"
            else
                print_warning "  Already applied or conflict: ${patch_file}"
            fi
            rm -f "$temp_patch"
        else
            print_warning "  Patch file not found: ${patch_file}"
        fi
    done
    
    print_success "SheepShaver patches complete!"
    return 0
}

# Main execution
echo "======================================"
echo "  macemu Shader Patch Script"
echo "======================================"
echo ""

apply_basilisk_patches
echo ""
apply_sheepshaver_patches

echo ""

# Modify prefs.cpp buffer size (256 -> 4096)
print_info "Modifying prefs.cpp buffer size..."
for prefs_file in "${MACEMU_DIR}/BasiliskII/src/prefs.cpp" "${MACEMU_DIR}/SheepShaver/src/prefs.cpp"; do
    if [ -f "$prefs_file" ]; then
        if grep -q 'char line\[256\]' "$prefs_file"; then
            sed -i 's/char line\[256\];/char line[4096];  \/\/ Increased for long shader_params/' "$prefs_file"
            print_info "  Modified: $(basename $(dirname $(dirname $prefs_file)))/src/prefs.cpp"
        fi
    fi
done

# Generate build scripts in macemu_patches folder
BUILD_SCRIPTS_DIR="$(dirname "$SCRIPT_DIR")"
print_info "Generating build scripts in $BUILD_SCRIPTS_DIR..."

# BasiliskII build script
cat > "${BUILD_SCRIPTS_DIR}/build_basiliskii.sh" << 'BUILDSCRIPT'
#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve macemu path: Argument > Subdirectory > Sibling
if [ -n "$1" ]; then
    MACEMU_DIR="$1"
elif [ -d "${SCRIPT_DIR}/macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/macemu"
elif [ -d "${SCRIPT_DIR}/../macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/../macemu"
else
    echo "Error: macemu directory not found."
    echo "Usage: $0 [path_to_macemu_root]"
    exit 1
fi

BUILD_DIR="${MACEMU_DIR}/BasiliskII/src/Unix"

if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory not found: $BUILD_DIR"
    exit 1
fi

cd "$BUILD_DIR"
echo "[INFO] Building BasiliskII..."
[ ! -f "../SDL/video_shader.cpp" ] && echo "[ERROR] video_shader.cpp not found. Apply patches first." && exit 1
[ ! -f "configure" ] && NO_CONFIGURE=1 ./autogen.sh
[ ! -f "Makefile" ] && ./configure --enable-sdl-video=yes --enable-sdl-audio=yes --disable-vosf --without-esd --without-mon --with-gtk --enable-jit-compiler
make -j$(nproc)
if [ -f "BasiliskII" ]; then
    echo "[SUCCESS] Build complete: ${BUILD_DIR}/BasiliskII"
    cp "BasiliskII" "${SCRIPT_DIR}/BasiliskII"
    echo "[INFO] Copied executable to: ${SCRIPT_DIR}/BasiliskII"
else
    echo "[ERROR] Build failed!"
    exit 1
fi
BUILDSCRIPT
chmod +x "${BUILD_SCRIPTS_DIR}/build_basiliskii.sh"

# SheepShaver build script
cat > "${BUILD_SCRIPTS_DIR}/build_sheepshaver.sh" << 'BUILDSCRIPT'
#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve macemu path: Argument > Subdirectory > Sibling
if [ -n "$1" ]; then
    MACEMU_DIR="$1"
elif [ -d "${SCRIPT_DIR}/macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/macemu"
elif [ -d "${SCRIPT_DIR}/../macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/../macemu"
else
    echo "Error: macemu directory not found."
    echo "Usage: $0 [path_to_macemu_root]"
    exit 1
fi

BUILD_DIR="${MACEMU_DIR}/SheepShaver/src/Unix"

if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory not found: $BUILD_DIR"
    exit 1
fi

cd "$BUILD_DIR"
echo "[INFO] Building SheepShaver..."
[ ! -f "../SDL/video_shader.cpp" ] && echo "[ERROR] video_shader.cpp not found. Apply patches first." && exit 1
[ ! -f "configure" ] && NO_CONFIGURE=1 ./autogen.sh
[ ! -f "Makefile" ] && ./configure --enable-sdl-video=yes --enable-sdl-audio=yes --disable-vosf --without-esd --without-mon --with-gtk --enable-jit-compiler
make -j$(nproc)
if [ -f "SheepShaver" ]; then
    echo "[SUCCESS] Build complete: ${BUILD_DIR}/SheepShaver"
    cp "SheepShaver" "${SCRIPT_DIR}/SheepShaver"
    echo "[INFO] Copied executable to: ${SCRIPT_DIR}/SheepShaver"
else
    echo "[ERROR] Build failed!"
    exit 1
fi
BUILDSCRIPT
chmod +x "${BUILD_SCRIPTS_DIR}/build_sheepshaver.sh"

print_success "Build scripts generated!"

echo ""
echo "======================================"
print_success "All patches applied successfully!"
echo "======================================"
echo ""
print_info "To build, run the following scripts:"
echo "  - BasiliskII: ${BUILD_SCRIPTS_DIR}/build_basiliskii.sh [macemu_path]"
echo "  - SheepShaver: ${BUILD_SCRIPTS_DIR}/build_sheepshaver.sh [macemu_path]"

