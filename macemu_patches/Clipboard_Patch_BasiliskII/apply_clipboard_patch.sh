#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
# Clipboard Patch Script for BasiliskII
# Adds SDL clipboard support with multi-language encoding conversion

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================"
echo "  BasiliskII Clipboard Patch Script"
echo "======================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCHES_DIR="$SCRIPT_DIR/patches"

# Check for macemu path argument or use default
if [ -n "$1" ]; then
    MACEMU_PATH="$1"
elif [ -d "${SCRIPT_DIR}/../macemu" ]; then
    MACEMU_PATH="${SCRIPT_DIR}/../macemu"
else
    echo -e "${RED}[ERROR]${NC} macemu folder not found."
    echo "Usage: $0 [path_to_macemu_root]"
    exit 1
fi

# Verify macemu structure
if [ ! -d "$MACEMU_PATH/BasiliskII" ]; then
    echo -e "${RED}[ERROR]${NC} Invalid macemu path. Expected BasiliskII folder."
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} macemu folder: $MACEMU_PATH"
echo -e "${BLUE}[INFO]${NC} Patches folder: $PATCHES_DIR"
echo ""

# Create SDL folder if it doesn't exist
mkdir -p "$MACEMU_PATH/BasiliskII/src/SDL"

# Copy clip_sdl.cpp
echo -e "${BLUE}[INFO]${NC} Applying clipboard patch to BasiliskII..."
if [ -f "$PATCHES_DIR/clip_sdl.cpp" ]; then
    cp "$PATCHES_DIR/clip_sdl.cpp" "$MACEMU_PATH/BasiliskII/src/SDL/clip_sdl.cpp"
    echo -e "${GREEN}[SUCCESS]${NC}   Copied clip_sdl.cpp"
else
    echo -e "${RED}[ERROR]${NC}   clip_sdl.cpp not found in patches folder"
    exit 1
fi

# Patch Makefile
MAKEFILE="$MACEMU_PATH/BasiliskII/src/Unix/Makefile"
if [ -f "$MAKEFILE" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching Makefile..."
    
    if grep -q "clip_dummy.cpp" "$MAKEFILE"; then
        sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$MAKEFILE"
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
CONFIGURE="$MACEMU_PATH/BasiliskII/src/Unix/configure"
if [ -f "$CONFIGURE" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching configure..."
    sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$CONFIGURE"
    echo -e "${GREEN}[SUCCESS]${NC}   Patched configure"
fi

MAKEFILE_IN="$MACEMU_PATH/BasiliskII/src/Unix/Makefile.in"
if [ -f "$MAKEFILE_IN" ]; then
    echo -e "${BLUE}[INFO]${NC} Patching Makefile.in..."
    sed -i 's|\.\./dummy/clip_dummy\.cpp|../SDL/clip_sdl.cpp|g' "$MAKEFILE_IN"
    echo -e "${GREEN}[SUCCESS]${NC}   Patched Makefile.in"
fi

CONFIGURE_AC="$MACEMU_PATH/BasiliskII/src/Unix/configure.ac"
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
fi

echo ""
echo "======================================"
echo -e "${GREEN}[SUCCESS]${NC} BasiliskII clipboard patch applied!"
echo "======================================"
echo ""
echo "Supported encodings (set via name_encoding preference):"
echo "  0 = MacRoman (English/Western - default)"
echo "  1 = Japanese"
echo "  2 = Chinese Traditional (Big5)"
echo "  3 = Korean (EUC-KR)"
echo "  4 = Arabic"
echo "  5 = Hebrew"
echo "  6 = Greek"
echo "  7 = Cyrillic"
echo "  25 = Chinese Simplified (GB2312)"
echo ""
echo "IMPORTANT: Set 'noclipconversion false' in your prefs file"
echo "           to enable encoding conversion."
echo ""
echo "To rebuild: cd macemu/BasiliskII/src/Unix && make"
echo ""
