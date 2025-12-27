#!/bin/bash
# Created by DINKIssTyle on 2025. Copyright (C) 2025 DINKI'ssTyle. All rights reserved.
# Build script for Ubuntu/Linux

set -e

echo "=== Building Sheepshaver & Basilisk II Preferences Editor for Linux ==="

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

# Build with PyInstaller (no console, with icon)
echo "Building executable..."
pyinstaller --noconfirm --onefile --windowed \
    --name "EmulatorPrefs" \
    --add-data "Appicon.png:." \
    main.py

echo ""
echo "=== Build Complete ==="
echo "Executable: dist/EmulatorPrefs"
echo ""
