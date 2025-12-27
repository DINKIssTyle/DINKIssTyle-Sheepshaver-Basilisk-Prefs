#!/bin/bash
# Created by DINKIssTyle on 2025. Copyright (C) 2025 DINKI'ssTyle. All rights reserved.
# Build script for macOS

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
if [ -f "Appicon.png" ]; then
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

# Build with PyInstaller (no console, as .app bundle)
echo "Building application bundle..."
ICON_OPT=""
if [ -f "Appicon.icns" ]; then
    ICON_OPT="--icon Appicon.icns"
fi

pyinstaller --noconfirm --onefile --windowed \
    --name "EmulatorPrefs" \
    $ICON_OPT \
    --add-data "Appicon.png:." \
    --osx-bundle-identifier "com.dinkisstyle.emulatorprefs" \
    main.py

echo ""
echo "=== Build Complete ==="
echo "Application: dist/EmulatorPrefs.app"
echo ""
