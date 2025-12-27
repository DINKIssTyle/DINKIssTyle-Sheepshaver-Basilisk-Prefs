@echo off
REM Created by DINKIssTyle on 2025. Copyright (C) 2025 DINKI'ssTyle. All rights reserved.
REM Build script for Windows

echo === Building Sheepshaver ^& Basilisk II Preferences Editor for Windows ===

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install qtpy PyQt6 pyinstaller

REM Build with PyInstaller (no console, with icon)
echo Building executable...
pyinstaller --noconfirm --onefile --windowed ^
    --name "EmulatorPrefs" ^
    --add-data "Appicon.png;." ^
    main.py

echo.
echo === Build Complete ===
echo Executable: dist\EmulatorPrefs.exe
echo.

pause
