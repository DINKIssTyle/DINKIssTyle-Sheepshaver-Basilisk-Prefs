#!/bin/bash
# Created by DINKIssTyle on 2026. Copyright (C) 2026 DINKI'ssTyle. All rights reserved.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve macemu path: Argument > Sibling > Subdirectory
if [ -n "$1" ]; then
    MACEMU_DIR="$1"
elif [ -d "${SCRIPT_DIR}/../macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/../macemu"
elif [ -d "${SCRIPT_DIR}/macemu" ]; then
    MACEMU_DIR="${SCRIPT_DIR}/macemu"
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
[ -f "SheepShaver" ] && echo "[SUCCESS] Build complete: ${BUILD_DIR}/SheepShaver" || echo "[ERROR] Build failed!"
