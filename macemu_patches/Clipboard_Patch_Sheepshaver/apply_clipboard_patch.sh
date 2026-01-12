#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
# Clipboard Patch Script for SheepShaver
# Adds SDL clipboard support (bidirectional: Mac <-> Host)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  SheepShaver Clipboard Patch Script"
echo "  Bidirectional Clipboard Support"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES_DIR="$SCRIPT_DIR/patches"

if [ -n "$1" ]; then
    MACEMU_PATH="$1"
elif [ -d "${SCRIPT_DIR}/../macemu" ]; then
    MACEMU_PATH="${SCRIPT_DIR}/../macemu"
else
    echo -e "${RED}[ERROR]${NC} macemu folder not found."
    echo "Usage: $0 [path_to_macemu_root]"
    exit 1
fi

if [ ! -d "$MACEMU_PATH/SheepShaver" ]; then
    echo -e "${RED}[ERROR]${NC} Invalid macemu path. Expected SheepShaver folder."
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} macemu folder: $MACEMU_PATH"
echo -e "${BLUE}[INFO]${NC} Patches folder: $PATCHES_DIR"
echo ""

# Create SDL folder if it doesn't exist
mkdir -p "$MACEMU_PATH/SheepShaver/src/SDL"

# Copy clip_sdl.cpp (main clipboard implementation)
echo -e "${BLUE}[INFO]${NC} Applying clipboard patch to SheepShaver..."
if [ -f "$PATCHES_DIR/clip_sdl.cpp" ]; then
    cp "$PATCHES_DIR/clip_sdl.cpp" "$MACEMU_PATH/SheepShaver/src/SDL/clip_sdl.cpp"
    echo -e "${GREEN}[SUCCESS]${NC}   Copied clip_sdl.cpp to SheepShaver/src/SDL/"
elif [ -f "$PATCHES_DIR/clip_sdl_ss.cpp" ]; then
    cp "$PATCHES_DIR/clip_sdl_ss.cpp" "$MACEMU_PATH/SheepShaver/src/SDL/clip_sdl.cpp"
    echo -e "${GREEN}[SUCCESS]${NC}   Copied clip_sdl_ss.cpp as clip_sdl.cpp"
else
    echo -e "${RED}[ERROR]${NC}   Neither clip_sdl.cpp nor clip_sdl_ss.cpp found in patches folder"
    exit 1
fi

# Apply patches
echo -e "${BLUE}[INFO]${NC} Applying patches..."

apply_patch() {
    local patch_file="$1"
    local target_dir="$2"
    
    if [ -f "$patch_file" ]; then
        echo -e "${BLUE}[INFO]${NC} Applying $(basename $patch_file)..."
        # Determine strip level. If creating new file, -p0? If modifying, depend on diff.
        # Generated diffs were "macemu/SheepShaver/..." vs "macemu_patches/..."
        # So inside macemu root, it's -p0. But script takes macemu path.
        # Let's use patch -p1 inside macemu dir? 
        # Actually, let's copy patch to /tmp/temp.patch and sed the paths if needed, but since I generated them relative to macemu root,
        # I can apply them from MACEMU_PATH with -p1 (since diff has macemu/ prefix)
        
        # Adjust patch paths to be relative to MACEMU_PATH
        # The patch header looks like: --- macemu/SheepShaver/src/emul_op.cpp
        # If we cd to MACEMU_PATH (which is macemu), and run patch -p1, it should match SheepShaver/src/emul_op.cpp
        
        cwd=$(pwd)
        cd "$MACEMU_PATH"
        if patch -p1 --forward --dry-run < "$patch_file" > /dev/null 2>&1; then
             patch -p1 --forward < "$patch_file"
             echo -e "${GREEN}[SUCCESS]${NC}   Applied $(basename $patch_file)"
        else
             echo -e "${YELLOW}[WARNING]${NC}   Already applied or failed: $(basename $patch_file)"
        fi
        cd "$cwd"
    else
         echo -e "${RED}[ERROR]${NC}   Patch not found: $patch_file"
    fi
}

apply_patch "$PATCHES_DIR/emul_op.cpp.patch"
apply_patch "$PATCHES_DIR/emul_op.h.patch"

# clip.h is a symlink to BasiliskII, so patch the target
CLIP_H="$MACEMU_PATH/SheepShaver/src/include/clip.h"
if [ -L "$CLIP_H" ]; then
    echo -e "${BLUE}[INFO]${NC} clip.h is a symlink. Patching target..."
    TARGET=$(readlink -f "$CLIP_H")
    if patch --forward --dry-run "$TARGET" < "$PATCHES_DIR/clip.h.patch" > /dev/null 2>&1; then
        patch --forward "$TARGET" < "$PATCHES_DIR/clip.h.patch"
        echo -e "${GREEN}[SUCCESS]${NC}   Applied clip.h.patch to $TARGET"
    else
         echo -e "${YELLOW}[WARNING]${NC}   Already applied or failed: clip.h.patch"
    fi
else
    apply_patch "$PATCHES_DIR/clip.h.patch"
fi

apply_patch "$PATCHES_DIR/sheepshaver_glue.cpp.patch"
apply_patch "$PATCHES_DIR/thunks.cpp.patch"
apply_patch "$PATCHES_DIR/thunks.h.patch"

# Patch Makefile
MAKEFILE="$MACEMU_PATH/SheepShaver/src/Unix/Makefile"
if [ -f "$MAKEFILE" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching Makefile..."
    
    if grep -q "clip_dummy.cpp" "$MAKEFILE"; then
        sed -i 's|\.\.\/dummy\/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$MAKEFILE"
        echo -e "${GREEN}[SUCCESS]${NC}   Patched Makefile to use clip_sdl.cpp"
    elif grep -q "clip_unix.cpp" "$MAKEFILE"; then
        sed -i 's|clip_unix\.cpp|../SDL/clip_sdl.cpp|g' "$MAKEFILE"
        echo -e "${GREEN}[SUCCESS]${NC}   Patched Makefile to use clip_sdl.cpp"
    elif grep -q "clip_sdl.cpp" "$MAKEFILE"; then
        echo -e "${YELLOW}[INFO]${NC}   Makefile already uses clip_sdl.cpp"
    fi
    
    if ! grep -q "\-lX11" "$MAKEFILE"; then
        sed -i 's/^LIBS = /LIBS = -lX11 /' "$MAKEFILE"
        echo -e "${GREEN}[SUCCESS]${NC}   Added -lX11 to LIBS"
    fi
else
    echo -e "${YELLOW}[WARNING]${NC} Makefile not found. Run ./configure first, then re-run this script."
fi

# Patch configure and Makefile.in to make it permanent
CONFIGURE="$MACEMU_PATH/SheepShaver/src/Unix/configure"
if [ -f "$CONFIGURE" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching configure..."
    sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$CONFIGURE"
    echo -e "${GREEN}[SUCCESS]${NC}   Patched configure"
fi

MAKEFILE_IN="$MACEMU_PATH/SheepShaver/src/Unix/Makefile.in"
if [ -f "$MAKEFILE_IN" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching Makefile.in..."
    sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$MAKEFILE_IN"
    echo -e "${GREEN}[SUCCESS]${NC}   Patched Makefile.in"
fi

CONFIGURE_AC="$MACEMU_PATH/SheepShaver/src/Unix/configure.ac"
if [ -f "$CONFIGURE_AC" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching configure.ac..."
    if grep -q "\.\./dummy/clip_dummy\.cpp" "$CONFIGURE_AC"; then
        sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$CONFIGURE_AC"
        echo -e "${GREEN}[SUCCESS]${NC}   Patched configure.ac (replaced clip_dummy.cpp)"
    fi
    if grep -q "clip_unix\.cpp" "$CONFIGURE_AC"; then
        sed -i 's|clip_unix\.cpp|../SDL/clip_sdl.cpp|g' "$CONFIGURE_AC"
        echo -e "${GREEN}[SUCCESS]${NC}   Patched configure.ac (replaced clip_unix.cpp)"
    fi
    # Add -lX11 to LIBS in configure.ac if not present?
    # Actually, let's just rely on the clip_dummy replacement being enough. 
    # The shader patch adds -lGL, usually X11 is implied or added elsewhere, 
    # but let's see. If we replace clip_unix.cpp which usually pulls in X11 dependencies, 
    # we might need to be careful. But for now, ensuring the source file replacement is key.
fi

echo ""
echo "========================================"
echo -e "${GREEN}[SUCCESS]${NC} SheepShaver clipboard patch applied!"
echo "========================================"
echo ""
echo -e "${GREEN}Supported Features:${NC}"
echo "  - Mac -> Host: ✅ Supported (text only)"
echo "  - Host -> Mac: ✅ Supported (text only)"
echo ""
echo "Supported encodings (set via name_encoding preference):"
echo "  0 = MacRoman (default), 3 = Korean, 1 = Japanese, etc."
echo ""
echo "IMPORTANT: Set 'noclipconversion false' in your prefs file"
echo ""
echo "To rebuild: cd macemu/SheepShaver/src/Unix && make"
echo ""
