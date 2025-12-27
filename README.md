# Sheepshaver & Basilisk II Preferences Editor

A cross-platform GUI application for editing Sheepshaver and Basilisk II emulator configuration files.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Qt](https://img.shields.io/badge/Qt-QtPy-green)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red)

## Features

- **Tabbed Interface**: Separate tabs for Basilisk II and Sheepshaver configurations
- **Comprehensive Settings**: 8 sub-tabs covering all emulator options
  - 💾 Drives: Disk images (add/remove/reorder), ExtFS, ROM, boot options
  - 🖥️ Graphics: Screen mode, resolution, scaling, renderer
  - 🔊 Sound: Enable/disable, buffer, devices
  - 🌐 Network: Ethernet mode, UDP tunnel
  - ⚡ CPU/Memory: RAM size, CPU type, JIT options
  - ⌨️ Input: Keyboard, mouse, keycodes
  - 📡 Serial: Serial port configuration
  - ⚙️ Misc: GUI, clipboard, time offset
- **Emulator Launch**: Run emulators directly from the app
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Screenshots

*(Coming soon)*

## Requirements

- Python 3.8+
- QtPy
- PyQt6 (or PyQt5/PySide6)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/YourUsername/DINKIssTyle-Sheepshaver-Basilisk-Prefs.git
cd DINKIssTyle-Sheepshaver-Basilisk-Prefs

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Using uv (Recommended)

```bash
uv run --with qtpy --with PyQt6 python main.py
```

## Building Executables

### Linux
```bash
chmod +x build_linux.sh
./build_linux.sh
# Output: dist/EmulatorPrefs
```

### macOS
```bash
chmod +x build_macos.sh
./build_macos.sh
# Output: dist/EmulatorPrefs.app
```

### Windows
```cmd
build_windows.bat
REM Output: dist\EmulatorPrefs.exe
```

## First-Time Setup

1. Launch the application
2. Go to the **Settings** tab
3. Configure paths:
   - Basilisk II executable and config file paths
   - Sheepshaver executable and config file paths
4. Click **Save Settings**
5. Click **Reload** to load your configurations

## Configuration File Locations

| OS | Basilisk II | Sheepshaver |
|----|-------------|-------------|
| Linux | `~/.basilisk_ii_prefs` | `~/.sheepshaver_prefs` |
| macOS | `~/.basilisk_ii_prefs` | `~/.sheepshaver_prefs` |
| Windows | `%USERPROFILE%\.basilisk_ii_prefs` | `%USERPROFILE%\.sheepshaver_prefs` |

## License

Copyright (C) 2025 DINKI'ssTyle. All rights reserved.

## Author

Created by **DINKIssTyle**
