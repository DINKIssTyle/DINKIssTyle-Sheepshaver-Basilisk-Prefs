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
pip install qtpy PyQt6 pyinstaller pillow

REM Convert PNG to ICO if needed
if exist "res\Appicon.png" (
    if not exist "res\Appicon.ico" (
        echo Converting icon to ICO format...
        python -c "from PIL import Image; img = Image.open('res/Appicon.png'); img.save('res/Appicon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])"
    )
)

REM Build with PyInstaller (no console, with icon)
echo Building executable...
if exist "res\Appicon.ico" (
    pyinstaller --noconfirm --onefile --windowed ^
        --name "EmulatorPrefs" ^
        --icon "res\Appicon.ico" ^
        --add-data "res;res" ^
        main.py
) else (
    pyinstaller --noconfirm --onefile --windowed ^
        --name "EmulatorPrefs" ^
        --add-data "res;res" ^
        main.py
)

echo.
echo === Build Complete ===
echo Executable: dist\EmulatorPrefs.exe
echo.

pause
