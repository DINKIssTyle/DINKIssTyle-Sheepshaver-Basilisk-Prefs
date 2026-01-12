#!/bin/bash
# ============================================================================
# Created by DINKIssTyle on 2026.
# Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
# ============================================================================
# macemu Clipboard Patch Script
# Applies bidirectional clipboard support to BasiliskII and SheepShaver
# Usage: ./apply_clipboard_patch.sh [macemu_path]
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES_DIR="${SCRIPT_DIR}/patches"
MACEMU_DIR="${1:-${SCRIPT_DIR}/../../macemu}"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "=========================================="
echo "  macemu Clipboard Patch Script"
echo "  Bidirectional Clipboard Support"
echo "=========================================="
echo ""

# Check macemu folder
if [ ! -d "$MACEMU_DIR" ]; then
    print_error "macemu folder not found: $MACEMU_DIR"
    echo ""
    print_info "Please clone macemu first:"
    echo "  git clone https://github.com/kanjitalk755/macemu.git"
    exit 1
fi

# Get absolute path and base name
MACEMU_DIR=$(cd "$MACEMU_DIR" && pwd)
MACEMU_BASE=$(basename "$MACEMU_DIR")
WORK_DIR=$(dirname "$MACEMU_DIR")

print_info "Working directory: $WORK_DIR"
print_info "macemu folder: $MACEMU_BASE"
print_info "Patches folder: $PATCHES_DIR"
echo ""

cd "$WORK_DIR"

# Apply patch function
apply_patch() {
    local patch_file="$1"
    local patch_name=$(basename "$patch_file")
    
    if [ ! -f "$patch_file" ]; then
        print_warning "Patch file not found: $patch_name"
        return 1
    fi
    
    # Replace $MACEMU_BASE with actual directory name
    local temp_patch="/tmp/${patch_name}.tmp"
    sed "s|\\\$MACEMU_BASE|${MACEMU_BASE}|g" "$patch_file" > "$temp_patch"
    
    print_info "  Applying: $patch_name"
    if patch -p0 --dry-run < "$temp_patch" > /dev/null 2>&1; then
        patch -p0 < "$temp_patch"
    else
        print_warning "  Already applied or conflict: $patch_name"
    fi
    rm -f "$temp_patch"
}

# Apply BasiliskII patches
apply_basilisk_patches() {
    print_info "Applying BasiliskII patches..."
    
    if [ ! -d "${MACEMU_DIR}/BasiliskII" ]; then
        print_warning "BasiliskII folder not found. Skipping."
        return 1
    fi
    
    # Apply clip.h patch
    apply_patch "${PATCHES_DIR}/basilisk_clip_h.patch"
    
    # Apply emul_op.h and emul_op.cpp patches for BasiliskII
    apply_patch "${PATCHES_DIR}/basilisk_emul_op_h.patch"
    apply_patch "${PATCHES_DIR}/basilisk_emul_op_cpp.patch"
    
    # Manual check for clip.h (in case patch failed due to fuzz)
    local CLIP_H="${MACEMU_DIR}/BasiliskII/src/include/clip.h"
    if [ -f "$CLIP_H" ]; then
        if ! grep -q "ClipboardGetImageSize" "$CLIP_H"; then
             print_warning "  Patching clip.h manually for Image support..."
             sed -i '/extern void ClipboardPutData/a extern int32 ClipboardGetImageSize(void);\nextern int32 ClipboardGetImageData(void *buffer, int32 size);' "$CLIP_H"
        fi
    fi
     
    
    # Copy new file: clip_sdl.cpp
    if [ -f "${PATCHES_DIR}/clip_sdl.cpp" ]; then
        mkdir -p "${MACEMU_DIR}/BasiliskII/src/SDL"
        cp "${PATCHES_DIR}/clip_sdl.cpp" "${MACEMU_DIR}/BasiliskII/src/SDL/clip_sdl.cpp"
        print_success "  Copied clip_sdl.cpp to BasiliskII"
    fi
    
    # Patch BasiliskII Makefile to use clip_sdl.cpp instead of clip_dummy.cpp
    local B2_MAKEFILE="${MACEMU_DIR}/BasiliskII/src/Unix/Makefile"
    if [ -f "$B2_MAKEFILE" ]; then
        print_info "  Patching BasiliskII Makefile..."
        if grep -q "clip_dummy" "$B2_MAKEFILE"; then
            sed -i 's|../dummy/clip_dummy.cpp|../SDL/clip_sdl.cpp|g' "$B2_MAKEFILE"
            sed -i 's|clip_dummy.cpp|../SDL/clip_sdl.cpp|g' "$B2_MAKEFILE"
            sed -i 's|clip_dummy.o|clip_sdl.o|g' "$B2_MAKEFILE"
            print_success "  Patched Makefile to use clip_sdl.cpp"
        elif grep -q "clip_sdl" "$B2_MAKEFILE"; then
            print_info "  Makefile already uses clip_sdl"
        fi
    else
        print_warning "  BasiliskII Makefile not found. Run ./configure first."
    fi

    # Patch LIBS to include X11 and png
    if [ -f "$B2_MAKEFILE" ]; then
        if ! grep -q "\-lpng" "$B2_MAKEFILE"; then
            sed -i 's|^LIBS =.*|& -lX11 -lpng|' "$B2_MAKEFILE"
            print_success "  Added -lX11 -lpng to LIBS"
        fi
    fi
    
    print_success "BasiliskII patches complete!"
}

# Apply SheepShaver patches
apply_sheepshaver_patches() {
    print_info "Applying SheepShaver patches..."
    
    if [ ! -d "${MACEMU_DIR}/SheepShaver" ]; then
        print_warning "SheepShaver folder not found. Skipping."
        return 1
    fi
    
    # Apply emul_op.h and emul_op.cpp patches
    apply_patch "${PATCHES_DIR}/sheepshaver_emul_op_h.patch"
    apply_patch "${PATCHES_DIR}/sheepshaver_emul_op_cpp.patch"
    
    # Copy clip_sdl.cpp to SheepShaver SDL folder (uses same file as BasiliskII)
    if [ -f "${PATCHES_DIR}/clip_sdl.cpp" ]; then
        mkdir -p "${MACEMU_DIR}/SheepShaver/src/SDL"
        cp "${PATCHES_DIR}/clip_sdl.cpp" "${MACEMU_DIR}/SheepShaver/src/SDL/clip_sdl.cpp"
        print_success "  Copied clip_sdl.cpp to SheepShaver"
    fi
    
    # Patch SheepShaver Makefile to use clip_sdl.cpp instead of clip_dummy.cpp
    local SS_MAKEFILE="${MACEMU_DIR}/SheepShaver/src/Unix/Makefile"
    if [ -f "$SS_MAKEFILE" ]; then
        print_info "  Patching SheepShaver Makefile..."
        if grep -q "clip_dummy" "$SS_MAKEFILE"; then
            sed -i 's|../dummy/clip_dummy.cpp|../SDL/clip_sdl.cpp|g' "$SS_MAKEFILE"
            sed -i 's|clip_dummy.cpp|../SDL/clip_sdl.cpp|g' "$SS_MAKEFILE"
            sed -i 's|clip_dummy.o|clip_sdl.o|g' "$SS_MAKEFILE"
            print_success "  Patched Makefile to use clip_sdl.cpp"
        elif grep -q "clip_sdl" "$SS_MAKEFILE"; then
            print_info "  Makefile already uses clip_sdl"
        fi
    else
        print_warning "  SheepShaver Makefile not found. Run ./configure first."
    fi

    # Patch LIBS to include X11 and png
    if [ -f "$SS_MAKEFILE" ]; then
        if ! grep -q "\-lpng" "$SS_MAKEFILE"; then
            sed -i 's|^LIBS =.*|& -lX11 -lpng|' "$SS_MAKEFILE"
            print_success "  Added -lX11 -lpng to LIBS"
        fi
    fi
    
    print_success "SheepShaver patches complete!"
}

# Main execution
apply_basilisk_patches
echo ""
apply_sheepshaver_patches

echo ""
echo "=========================================="
print_success "Clipboard patches applied successfully!"
echo "=========================================="
echo ""
echo -e "${GREEN}Supported Features:${NC}"
echo "  - Mac -> Host: ✅ Supported (text only)"
echo "  - Host -> Mac: ✅ Supported (text only)"
echo ""
echo "To build:"
echo "  BasiliskII:  cd ${MACEMU_DIR}/BasiliskII/src/Unix && make"
echo "  SheepShaver: cd ${MACEMU_DIR}/SheepShaver/src/Unix && make"
echo ""
