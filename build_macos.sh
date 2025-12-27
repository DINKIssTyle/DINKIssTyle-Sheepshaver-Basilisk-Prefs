#!/bin/bash
# Created by DINKIssTyle on 2025. Copyright (C) 2025 DINKI'ssTyle. All rights reserved.
# Build script for macOS (Universal Binary)

set -e

echo "=== Building Sheepshaver & Basilisk II Preferences Editor for macOS ==="

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install qtpy PyQt6 pyinstaller

# Convert icon to icns if needed (requires iconutil)
if [ -f "Appicon.png" ] && [ ! -f "Appicon.icns" ]; then
    echo "Converting icon to icns format..."
    mkdir -p Appicon.iconset
    sips -z 16 16 Appicon.png --out Appicon.iconset/icon_16x16.png
    sips -z 32 32 Appicon.png --out Appicon.iconset/icon_16x16@2x.png
    sips -z 32 32 Appicon.png --out Appicon.iconset/icon_32x32.png
    sips -z 64 64 Appicon.png --out Appicon.iconset/icon_32x32@2x.png
    sips -z 128 128 Appicon.png --out Appicon.iconset/icon_128x128.png
    sips -z 256 256 Appicon.png --out Appicon.iconset/icon_128x128@2x.png
    sips -z 256 256 Appicon.png --out Appicon.iconset/icon_256x256.png
    sips -z 512 512 Appicon.png --out Appicon.iconset/icon_256x256@2x.png
    sips -z 512 512 Appicon.png --out Appicon.iconset/icon_512x512.png
    sips -z 1024 1024 Appicon.png --out Appicon.iconset/icon_512x512@2x.png
    iconutil -c icns Appicon.iconset
    rm -rf Appicon.iconset
fi

# Build icon option
ICON_OPT=""
if [ -f "Appicon.icns" ]; then
    ICON_OPT="--icon Appicon.icns"
fi

# Check if we can build universal binary
ARCH=$(uname -m)
echo "Current architecture: $ARCH"

# Build for current architecture (PyInstaller doesn't support cross-compilation)
# For true Universal Binary, you need to:
# 1. Build on Intel Mac (x86_64)
# 2. Build on Apple Silicon Mac (arm64)
# 3. Use 'lipo' to combine them

echo "Building application bundle..."
pyinstaller --noconfirm --windowed \
    --name "EmulatorPrefs" \
    $ICON_OPT \
    --add-data "Appicon.png:." \
    --osx-bundle-identifier "com.dinkisstyle.emulatorprefs" \
    main.py

# Clean up standalone executable, keep only .app bundle
if [ -f "dist/EmulatorPrefs" ]; then
    rm -f "dist/EmulatorPrefs"
fi

echo ""
echo "=== Build Complete ==="
echo "Application: dist/EmulatorPrefs.app"
echo "Architecture: $ARCH"
echo ""
echo "Note: For Universal Binary, build on both Intel and Apple Silicon Macs,"
echo "      then combine using: lipo -create -output EmulatorPrefs EmulatorPrefs_x86 EmulatorPrefs_arm64"
echo ""
