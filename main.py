#!/usr/bin/env python3
# Created by DINKIssTyle on 2025. Copyright (C) 2025 DINKI'ssTyle. All rights reserved.

"""
Sheepshaver & Basilisk II Preferences Editor
A QtPy-based GUI for editing emulator configuration files.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from qtpy.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QComboBox, QListWidget, QListWidgetItem, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QToolBar, QSplitter, QFrame, QDoubleSpinBox,
    QSizePolicy
)
from qtpy.QtCore import Qt, QSettings
from qtpy.QtGui import QAction, QIcon, QPixmap


# ============================================================================
# Configuration Parser
# ============================================================================

class ConfigParser:
    """Parse and save Basilisk II / Sheepshaver configuration files."""
    
    @staticmethod
    def parse(filepath: str) -> dict:
        """Parse a configuration file into a dictionary."""
        config = {}
        disks = []
        
        if not os.path.exists(filepath):
            return config
            
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(' ', 1)
                key = parts[0]
                value = parts[1] if len(parts) > 1 else ''
                
                # Handle multiple disk entries
                if key == 'disk':
                    disks.append(value)
                else:
                    # Convert boolean strings
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    config[key] = value
        
        config['disks'] = disks
        return config
    
    @staticmethod
    def save(filepath: str, config: dict):
        """Save configuration dictionary to file."""
        with open(filepath, 'w') as f:
            # Write disks first
            for disk in config.get('disks', []):
                f.write(f"disk {disk}\n")
            
            # Write other settings
            for key, value in config.items():
                if key == 'disks':
                    continue
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                f.write(f"{key} {value}\n")


# ============================================================================
# Sub-Tab Widgets
# ============================================================================

class DrivesTab(QWidget):
    """Disk and storage configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Disk Images Group
        disk_group = QGroupBox("Disk Images")
        disk_layout = QVBoxLayout(disk_group)
        
        self.disk_list = QListWidget()
        self.disk_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        disk_layout.addWidget(self.disk_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_remove = QPushButton("Remove")
        self.btn_up = QPushButton("▲ Up")
        self.btn_down = QPushButton("▼ Down")
        
        self.btn_add.clicked.connect(self.add_disk)
        self.btn_remove.clicked.connect(self.remove_disk)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addStretch()
        disk_layout.addLayout(btn_layout)
        
        layout.addWidget(disk_group)
        
        # Other Storage Options
        storage_group = QGroupBox("Storage Options")
        storage_layout = QFormLayout(storage_group)
        
        # ExtFS
        extfs_layout = QHBoxLayout()
        self.extfs_edit = QLineEdit()
        extfs_btn = QPushButton("Browse")
        extfs_btn.clicked.connect(lambda: self.browse_dir(self.extfs_edit))
        extfs_layout.addWidget(self.extfs_edit)
        extfs_layout.addWidget(extfs_btn)
        storage_layout.addRow("ExtFS Path:", extfs_layout)
        
        # ROM
        rom_layout = QHBoxLayout()
        self.rom_edit = QLineEdit()
        rom_btn = QPushButton("Browse")
        rom_btn.clicked.connect(lambda: self.browse_file(self.rom_edit, "ROM Files (*.rom);;All Files (*)"))
        rom_layout.addWidget(self.rom_edit)
        rom_layout.addWidget(rom_btn)
        storage_layout.addRow("ROM File:", rom_layout)
        
        # Boot options
        self.boot_drive = QSpinBox()
        self.boot_drive.setRange(0, 255)
        storage_layout.addRow("Boot Drive:", self.boot_drive)
        
        self.boot_driver = QSpinBox()
        self.boot_driver.setRange(0, 255)
        storage_layout.addRow("Boot Driver:", self.boot_driver)
        
        self.no_cdrom = QCheckBox("Disable CD-ROM")
        storage_layout.addRow("", self.no_cdrom)
        
        layout.addWidget(storage_group)
        layout.addStretch()
    
    def add_disk(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Disk Image",
            "", "Disk Images (*.img *.dmg *.iso *.hfv);;All Files (*)"
        )
        if path:
            self.disk_list.addItem(path)
    
    def remove_disk(self):
        row = self.disk_list.currentRow()
        if row >= 0:
            self.disk_list.takeItem(row)
    
    def move_up(self):
        row = self.disk_list.currentRow()
        if row > 0:
            item = self.disk_list.takeItem(row)
            self.disk_list.insertItem(row - 1, item)
            self.disk_list.setCurrentRow(row - 1)
    
    def move_down(self):
        row = self.disk_list.currentRow()
        if row < self.disk_list.count() - 1:
            item = self.disk_list.takeItem(row)
            self.disk_list.insertItem(row + 1, item)
            self.disk_list.setCurrentRow(row + 1)
    
    def browse_file(self, line_edit, filter_str):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter_str)
        if path:
            line_edit.setText(path)
    
    def browse_dir(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            line_edit.setText(path)
    
    def load_config(self, config: dict):
        self.disk_list.clear()
        for disk in config.get('disks', []):
            self.disk_list.addItem(disk)
        self.extfs_edit.setText(str(config.get('extfs', '')))
        self.rom_edit.setText(str(config.get('rom', '')))
        self.boot_drive.setValue(config.get('bootdrive', 0))
        self.boot_driver.setValue(config.get('bootdriver', 0))
        self.no_cdrom.setChecked(config.get('nocdrom', False))
    
    def save_config(self, config: dict):
        config['disks'] = [self.disk_list.item(i).text() for i in range(self.disk_list.count())]
        config['extfs'] = self.extfs_edit.text()
        config['rom'] = self.rom_edit.text()
        config['bootdrive'] = self.boot_drive.value()
        config['bootdriver'] = self.boot_driver.value()
        config['nocdrom'] = self.no_cdrom.isChecked()


class GraphicsTab(QWidget):
    """Graphics and display configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Display Group
        display_group = QGroupBox("Display")
        display_layout = QFormLayout(display_group)
        
        # Screen mode
        self.screen_mode = QComboBox()
        self.screen_mode.addItems(["win", "dga", "full"])
        display_layout.addRow("Screen Mode:", self.screen_mode)
        
        self.screen_width = QSpinBox()
        self.screen_width.setRange(320, 3840)
        self.screen_width.setValue(800)
        display_layout.addRow("Width:", self.screen_width)
        
        self.screen_height = QSpinBox()
        self.screen_height.setRange(240, 2160)
        self.screen_height.setValue(600)
        display_layout.addRow("Height:", self.screen_height)
        
        self.color_depth = QComboBox()
        self.color_depth.addItems(["0 (Default)", "8", "16", "24", "32"])
        display_layout.addRow("Color Depth:", self.color_depth)
        
        layout.addWidget(display_group)
        
        # Performance Group
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.frameskip = QSpinBox()
        self.frameskip.setRange(0, 60)
        perf_layout.addRow("Frame Skip:", self.frameskip)
        
        self.gfx_accel = QCheckBox("Enable")
        if self.emulator_type == 'sheepshaver':
            perf_layout.addRow("GFX Acceleration:", self.gfx_accel)
        
        layout.addWidget(perf_group)
        
        # Scaling Group
        scale_group = QGroupBox("Scaling")
        scale_layout = QFormLayout(scale_group)
        
        self.scale_nearest = QCheckBox("Nearest Neighbor")
        scale_layout.addRow("", self.scale_nearest)
        
        self.scale_integer = QCheckBox("Integer Scaling")
        scale_layout.addRow("", self.scale_integer)
        
        self.mag_rate = QDoubleSpinBox()
        self.mag_rate.setRange(0.0, 4.0)
        self.mag_rate.setSingleStep(0.1)
        self.mag_rate.setValue(1.0)
        scale_layout.addRow("Magnification:", self.mag_rate)
        
        layout.addWidget(scale_group)
        
        # Render Group
        render_group = QGroupBox("Renderer")
        render_layout = QFormLayout(render_group)
        
        self.sdl_render = QComboBox()
        self.sdl_render.addItems(["software", "opengl", "opengles", "opengles2", "metal"])
        render_layout.addRow("SDL Render:", self.sdl_render)
        
        layout.addWidget(render_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        screen = str(config.get('screen', 'win/800/600'))
        parts = screen.split('/')
        if len(parts) >= 3:
            self.screen_mode.setCurrentText(parts[0])
            self.screen_width.setValue(int(parts[1]))
            self.screen_height.setValue(int(parts[2]))
        
        depth = config.get('displaycolordepth', 0)
        if depth == 0:
            self.color_depth.setCurrentIndex(0)
        else:
            self.color_depth.setCurrentText(str(depth))
        
        self.frameskip.setValue(config.get('frameskip', 0))
        self.gfx_accel.setChecked(config.get('gfxaccel', False))
        
        # Handle typo in config file ('ture' instead of 'true')
        scale_nearest = config.get('scale_nearest', False)
        if isinstance(scale_nearest, str):
            scale_nearest = scale_nearest.lower() in ['true', 'ture']
        self.scale_nearest.setChecked(scale_nearest)
        
        scale_integer = config.get('scale_integer', False)
        if isinstance(scale_integer, str):
            scale_integer = scale_integer.lower() in ['true', 'ture']
        self.scale_integer.setChecked(scale_integer)
        
        self.mag_rate.setValue(float(config.get('mag_rate', 1.0)))
        self.sdl_render.setCurrentText(config.get('sdlrender', 'software'))
    
    def save_config(self, config: dict):
        config['screen'] = f"{self.screen_mode.currentText()}/{self.screen_width.value()}/{self.screen_height.value()}"
        
        depth_text = self.color_depth.currentText()
        config['displaycolordepth'] = 0 if '0' in depth_text else int(depth_text)
        
        config['frameskip'] = self.frameskip.value()
        if self.emulator_type == 'sheepshaver':
            config['gfxaccel'] = self.gfx_accel.isChecked()
        config['scale_nearest'] = self.scale_nearest.isChecked()
        config['scale_integer'] = self.scale_integer.isChecked()
        config['mag_rate'] = self.mag_rate.value()
        config['sdlrender'] = self.sdl_render.currentText()


class SoundTab(QWidget):
    """Sound configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QFormLayout(sound_group)
        
        self.no_sound = QCheckBox("Disable Sound")
        sound_layout.addRow("", self.no_sound)
        
        self.sound_buffer = QSpinBox()
        self.sound_buffer.setRange(0, 65536)
        sound_layout.addRow("Buffer Size:", self.sound_buffer)
        
        self.dsp_edit = QLineEdit()
        self.dsp_edit.setPlaceholderText("/dev/dsp")
        sound_layout.addRow("DSP Device:", self.dsp_edit)
        
        self.mixer_edit = QLineEdit()
        self.mixer_edit.setPlaceholderText("/dev/mixer")
        sound_layout.addRow("Mixer Device:", self.mixer_edit)
        
        layout.addWidget(sound_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        self.no_sound.setChecked(config.get('nosound', False))
        self.sound_buffer.setValue(config.get('sound_buffer', 0))
        self.dsp_edit.setText(str(config.get('dsp', '/dev/dsp')))
        self.mixer_edit.setText(str(config.get('mixer', '/dev/mixer')))
    
    def save_config(self, config: dict):
        config['nosound'] = self.no_sound.isChecked()
        config['sound_buffer'] = self.sound_buffer.value()
        config['dsp'] = self.dsp_edit.text()
        config['mixer'] = self.mixer_edit.text()


class NetworkTab(QWidget):
    """Network configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        net_group = QGroupBox("Network Settings")
        net_layout = QFormLayout(net_group)
        
        self.ether_mode = QComboBox()
        self.ether_mode.addItems(["slirp", "none", "tap", "sheep_net"])
        self.ether_mode.setEditable(True)
        net_layout.addRow("Ethernet:", self.ether_mode)
        
        if self.emulator_type == 'basilisk':
            self.udp_tunnel = QCheckBox("Enable")
            net_layout.addRow("UDP Tunnel:", self.udp_tunnel)
            
            self.udp_port = QSpinBox()
            self.udp_port.setRange(1, 65535)
            self.udp_port.setValue(6066)
            net_layout.addRow("UDP Port:", self.udp_port)
        
        if self.emulator_type == 'sheepshaver':
            self.no_net = QCheckBox("Disable Network")
            net_layout.addRow("", self.no_net)
        
        layout.addWidget(net_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        self.ether_mode.setCurrentText(str(config.get('ether', 'slirp')))
        if self.emulator_type == 'basilisk':
            self.udp_tunnel.setChecked(config.get('udptunnel', False))
            self.udp_port.setValue(config.get('udpport', 6066))
        if self.emulator_type == 'sheepshaver':
            self.no_net.setChecked(config.get('nonet', False))
    
    def save_config(self, config: dict):
        config['ether'] = self.ether_mode.currentText()
        if self.emulator_type == 'basilisk':
            config['udptunnel'] = self.udp_tunnel.isChecked()
            config['udpport'] = self.udp_port.value()
        if self.emulator_type == 'sheepshaver':
            config['nonet'] = self.no_net.isChecked()


class CpuMemoryTab(QWidget):
    """CPU and Memory configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Memory Group
        mem_group = QGroupBox("Memory")
        mem_layout = QFormLayout(mem_group)
        
        self.ram_size = QComboBox()
        ram_sizes = [
            ("8 MB", 8*1024*1024),
            ("16 MB", 16*1024*1024),
            ("32 MB", 32*1024*1024),
            ("64 MB", 64*1024*1024),
            ("128 MB", 128*1024*1024),
            ("256 MB", 256*1024*1024),
            ("512 MB", 512*1024*1024),
            ("1 GB", 1024*1024*1024),
        ]
        for name, size in ram_sizes:
            self.ram_size.addItem(name, size)
        mem_layout.addRow("RAM Size:", self.ram_size)
        
        layout.addWidget(mem_group)
        
        # CPU Group (Basilisk specific)
        if self.emulator_type == 'basilisk':
            cpu_group = QGroupBox("CPU")
            cpu_layout = QFormLayout(cpu_group)
            
            self.cpu_type = QComboBox()
            self.cpu_type.addItems(["68020", "68030", "68040"])
            cpu_layout.addRow("CPU Type:", self.cpu_type)
            
            self.model_id = QSpinBox()
            self.model_id.setRange(0, 255)
            cpu_layout.addRow("Model ID:", self.model_id)
            
            self.fpu_enabled = QCheckBox("Enable FPU")
            cpu_layout.addRow("", self.fpu_enabled)
            
            layout.addWidget(cpu_group)
        
        # Sheepshaver CPU options
        if self.emulator_type == 'sheepshaver':
            cpu_group = QGroupBox("CPU")
            cpu_layout = QFormLayout(cpu_group)
            
            self.cpu_clock = QSpinBox()
            self.cpu_clock.setRange(0, 10000)
            cpu_layout.addRow("CPU Clock (0=auto):", self.cpu_clock)
            
            layout.addWidget(cpu_group)
        
        # JIT Group
        jit_group = QGroupBox("JIT Compiler")
        jit_layout = QFormLayout(jit_group)
        
        self.jit_enabled = QCheckBox("Enable JIT")
        jit_layout.addRow("", self.jit_enabled)
        
        if self.emulator_type == 'basilisk':
            self.jit_fpu = QCheckBox("JIT FPU")
            jit_layout.addRow("", self.jit_fpu)
            
            self.jit_cache_size = QSpinBox()
            self.jit_cache_size.setRange(0, 65536)
            self.jit_cache_size.setValue(8192)
            jit_layout.addRow("Cache Size (KB):", self.jit_cache_size)
            
            self.jit_lazy_flush = QCheckBox("Lazy Flush")
            jit_layout.addRow("", self.jit_lazy_flush)
            
            self.jit_inline = QCheckBox("Inline")
            jit_layout.addRow("", self.jit_inline)
            
            self.jit_debug = QCheckBox("Debug")
            jit_layout.addRow("", self.jit_debug)
        
        if self.emulator_type == 'sheepshaver':
            self.jit_68k = QCheckBox("JIT 68K")
            jit_layout.addRow("", self.jit_68k)
        
        layout.addWidget(jit_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        ram = config.get('ramsize', 128*1024*1024)
        for i in range(self.ram_size.count()):
            if self.ram_size.itemData(i) == ram:
                self.ram_size.setCurrentIndex(i)
                break
        
        if self.emulator_type == 'basilisk':
            cpu = config.get('cpu', 3)
            cpu_map = {2: 0, 3: 1, 4: 2}
            self.cpu_type.setCurrentIndex(cpu_map.get(cpu, 1))
            self.model_id.setValue(config.get('modelid', 5))
            self.fpu_enabled.setChecked(config.get('fpu', True))
            self.jit_fpu.setChecked(config.get('jitfpu', True))
            self.jit_cache_size.setValue(config.get('jitcachesize', 8192))
            self.jit_lazy_flush.setChecked(config.get('jitlazyflush', True))
            self.jit_inline.setChecked(config.get('jitinline', True))
            self.jit_debug.setChecked(config.get('jitdebug', False))
        
        if self.emulator_type == 'sheepshaver':
            self.cpu_clock.setValue(config.get('cpuclock', 0))
            self.jit_68k.setChecked(config.get('jit68k', False))
        
        self.jit_enabled.setChecked(config.get('jit', True))
    
    def save_config(self, config: dict):
        config['ramsize'] = self.ram_size.currentData()
        
        if self.emulator_type == 'basilisk':
            cpu_map = {0: 2, 1: 3, 2: 4}
            config['cpu'] = cpu_map.get(self.cpu_type.currentIndex(), 3)
            config['modelid'] = self.model_id.value()
            config['fpu'] = self.fpu_enabled.isChecked()
            config['jitfpu'] = self.jit_fpu.isChecked()
            config['jitcachesize'] = self.jit_cache_size.value()
            config['jitlazyflush'] = self.jit_lazy_flush.isChecked()
            config['jitinline'] = self.jit_inline.isChecked()
            config['jitdebug'] = self.jit_debug.isChecked()
        
        if self.emulator_type == 'sheepshaver':
            config['cpuclock'] = self.cpu_clock.value()
            config['jit68k'] = self.jit_68k.isChecked()
        
        config['jit'] = self.jit_enabled.isChecked()


class InputTab(QWidget):
    """Keyboard and mouse configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Keyboard Group
        kb_group = QGroupBox("Keyboard")
        kb_layout = QFormLayout(kb_group)
        
        self.kb_type = QSpinBox()
        self.kb_type.setRange(0, 255)
        kb_layout.addRow("Keyboard Type:", self.kb_type)
        
        self.keycodes = QCheckBox("Use Keycodes")
        kb_layout.addRow("", self.keycodes)
        
        keycode_layout = QHBoxLayout()
        self.keycode_file = QLineEdit()
        keycode_btn = QPushButton("Browse")
        keycode_btn.clicked.connect(self.browse_keycode_file)
        keycode_layout.addWidget(self.keycode_file)
        keycode_layout.addWidget(keycode_btn)
        kb_layout.addRow("Keycode File:", keycode_layout)
        
        self.hotkey = QSpinBox()
        self.hotkey.setRange(0, 255)
        kb_layout.addRow("Hotkey:", self.hotkey)
        
        self.swap_opt_cmd = QCheckBox("Swap Option/Command")
        kb_layout.addRow("", self.swap_opt_cmd)
        
        layout.addWidget(kb_group)
        
        # Mouse Group
        mouse_group = QGroupBox("Mouse")
        mouse_layout = QFormLayout(mouse_group)
        
        self.mouse_wheel_mode = QSpinBox()
        self.mouse_wheel_mode.setRange(0, 3)
        mouse_layout.addRow("Wheel Mode:", self.mouse_wheel_mode)
        
        self.mouse_wheel_lines = QSpinBox()
        self.mouse_wheel_lines.setRange(1, 20)
        mouse_layout.addRow("Wheel Lines:", self.mouse_wheel_lines)
        
        self.init_grab = QCheckBox("Initial Grab")
        mouse_layout.addRow("", self.init_grab)
        
        if self.emulator_type == 'sheepshaver':
            self.hard_cursor = QCheckBox("Hardware Cursor")
            mouse_layout.addRow("", self.hard_cursor)
        
        layout.addWidget(mouse_group)
        layout.addStretch()
    
    def browse_keycode_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Keycode File", "", "All Files (*)")
        if path:
            self.keycode_file.setText(path)
    
    def load_config(self, config: dict):
        self.kb_type.setValue(config.get('keyboardtype', 5))
        self.keycodes.setChecked(config.get('keycodes', True))
        self.keycode_file.setText(str(config.get('keycodefile', '')))
        self.hotkey.setValue(config.get('hotkey', 0))
        self.swap_opt_cmd.setChecked(config.get('swap_opt_cmd', True))
        self.mouse_wheel_mode.setValue(config.get('mousewheelmode', 1))
        self.mouse_wheel_lines.setValue(config.get('mousewheellines', 3))
        self.init_grab.setChecked(config.get('init_grab', False))
        if self.emulator_type == 'sheepshaver':
            self.hard_cursor.setChecked(config.get('hardcursor', False))
    
    def save_config(self, config: dict):
        config['keyboardtype'] = self.kb_type.value()
        config['keycodes'] = self.keycodes.isChecked()
        config['keycodefile'] = self.keycode_file.text()
        config['hotkey'] = self.hotkey.value()
        config['swap_opt_cmd'] = self.swap_opt_cmd.isChecked()
        config['mousewheelmode'] = self.mouse_wheel_mode.value()
        config['mousewheellines'] = self.mouse_wheel_lines.value()
        config['init_grab'] = self.init_grab.isChecked()
        if self.emulator_type == 'sheepshaver':
            config['hardcursor'] = self.hard_cursor.isChecked()


class SerialTab(QWidget):
    """Serial port configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        serial_group = QGroupBox("Serial Ports")
        serial_layout = QFormLayout(serial_group)
        
        self.serial_a = QLineEdit()
        self.serial_a.setPlaceholderText("/dev/ttyS0")
        serial_layout.addRow("Serial A:", self.serial_a)
        
        self.serial_b = QLineEdit()
        self.serial_b.setPlaceholderText("/dev/ttyS1")
        serial_layout.addRow("Serial B:", self.serial_b)
        
        layout.addWidget(serial_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        self.serial_a.setText(str(config.get('seriala', '/dev/ttyS0')))
        self.serial_b.setText(str(config.get('serialb', '/dev/ttyS1')))
    
    def save_config(self, config: dict):
        config['seriala'] = self.serial_a.text()
        config['serialb'] = self.serial_b.text()


class MiscTab(QWidget):
    """Miscellaneous configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        misc_group = QGroupBox("Miscellaneous")
        misc_layout = QFormLayout(misc_group)
        
        self.no_gui = QCheckBox("No GUI")
        misc_layout.addRow("", self.no_gui)
        
        self.no_clip_conversion = QCheckBox("No Clipboard Conversion")
        misc_layout.addRow("", self.no_clip_conversion)
        
        self.ignore_segv = QCheckBox("Ignore SEGV")
        misc_layout.addRow("", self.ignore_segv)
        
        if self.emulator_type == 'sheepshaver':
            self.ignore_illegal = QCheckBox("Ignore Illegal Instructions")
            misc_layout.addRow("", self.ignore_illegal)
        
        self.idle_wait = QCheckBox("Idle Wait")
        misc_layout.addRow("", self.idle_wait)
        
        layout.addWidget(misc_group)
        
        # Time offset
        time_group = QGroupBox("Time Offset")
        time_layout = QFormLayout(time_group)
        
        self.year_offset = QSpinBox()
        self.year_offset.setRange(-100, 100)
        time_layout.addRow("Year Offset:", self.year_offset)
        
        self.day_offset = QSpinBox()
        self.day_offset.setRange(-365, 365)
        time_layout.addRow("Day Offset:", self.day_offset)
        
        layout.addWidget(time_group)
        
        # Encoding
        enc_group = QGroupBox("Encoding")
        enc_layout = QFormLayout(enc_group)
        
        self.name_encoding = QSpinBox()
        self.name_encoding.setRange(0, 10)
        enc_layout.addRow("Name Encoding:", self.name_encoding)
        
        layout.addWidget(enc_group)
        
        if self.emulator_type == 'basilisk':
            delay_group = QGroupBox("Performance")
            delay_layout = QFormLayout(delay_group)
            
            self.delay = QSpinBox()
            self.delay.setRange(0, 1000)
            delay_layout.addRow("Delay:", self.delay)
            
            layout.addWidget(delay_group)
        
        layout.addStretch()
    
    def load_config(self, config: dict):
        self.no_gui.setChecked(config.get('nogui', True))
        self.no_clip_conversion.setChecked(config.get('noclipconversion', False))
        self.ignore_segv.setChecked(config.get('ignoresegv', False))
        if self.emulator_type == 'sheepshaver':
            self.ignore_illegal.setChecked(config.get('ignoreillegal', False))
        self.idle_wait.setChecked(config.get('idlewait', True))
        self.year_offset.setValue(config.get('yearofs', 0))
        self.day_offset.setValue(config.get('dayofs', 0))
        self.name_encoding.setValue(config.get('name_encoding', 3))
        if self.emulator_type == 'basilisk':
            self.delay.setValue(config.get('delay', 0))
    
    def save_config(self, config: dict):
        config['nogui'] = self.no_gui.isChecked()
        config['noclipconversion'] = self.no_clip_conversion.isChecked()
        config['ignoresegv'] = self.ignore_segv.isChecked()
        if self.emulator_type == 'sheepshaver':
            config['ignoreillegal'] = self.ignore_illegal.isChecked()
        config['idlewait'] = self.idle_wait.isChecked()
        config['yearofs'] = self.year_offset.value()
        config['dayofs'] = self.day_offset.value()
        config['name_encoding'] = self.name_encoding.value()
        if self.emulator_type == 'basilisk':
            config['delay'] = self.delay.value()


# ============================================================================
# Emulator Tab (contains sub-tabs)
# ============================================================================

class EmulatorTab(QWidget):
    """Container for emulator-specific sub-tabs."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.config = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.sub_tabs = QTabWidget()
        
        self.drives_tab = DrivesTab(self.emulator_type)
        self.graphics_tab = GraphicsTab(self.emulator_type)
        self.sound_tab = SoundTab(self.emulator_type)
        self.network_tab = NetworkTab(self.emulator_type)
        self.cpu_memory_tab = CpuMemoryTab(self.emulator_type)
        self.input_tab = InputTab(self.emulator_type)
        self.serial_tab = SerialTab(self.emulator_type)
        self.misc_tab = MiscTab(self.emulator_type)
        
        self.sub_tabs.addTab(self.drives_tab, "💾 Drives")
        self.sub_tabs.addTab(self.graphics_tab, "🖥️ Graphics")
        self.sub_tabs.addTab(self.sound_tab, "🔊 Sound")
        self.sub_tabs.addTab(self.network_tab, "🌐 Network")
        self.sub_tabs.addTab(self.cpu_memory_tab, "⚡ CPU/Memory")
        self.sub_tabs.addTab(self.input_tab, "⌨️ Input")
        self.sub_tabs.addTab(self.serial_tab, "📡 Serial")
        self.sub_tabs.addTab(self.misc_tab, "⚙️ Misc")
        
        layout.addWidget(self.sub_tabs)
    
    def load_config(self, config: dict):
        self.config = config
        self.drives_tab.load_config(config)
        self.graphics_tab.load_config(config)
        self.sound_tab.load_config(config)
        self.network_tab.load_config(config)
        self.cpu_memory_tab.load_config(config)
        self.input_tab.load_config(config)
        self.serial_tab.load_config(config)
        self.misc_tab.load_config(config)
    
    def save_config(self) -> dict:
        config = {}
        self.drives_tab.save_config(config)
        self.graphics_tab.save_config(config)
        self.sound_tab.save_config(config)
        self.network_tab.save_config(config)
        self.cpu_memory_tab.save_config(config)
        self.input_tab.save_config(config)
        self.serial_tab.save_config(config)
        self.misc_tab.save_config(config)
        return config


# ============================================================================
# Settings Tab
# ============================================================================

class SettingsTab(QWidget):
    """Application settings - executable and config paths."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('DINKIssTyle', 'EmulatorPrefs')
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Basilisk II Settings
        basilisk_group = QGroupBox("Basilisk II")
        basilisk_layout = QFormLayout(basilisk_group)
        
        basilisk_exe_layout = QHBoxLayout()
        self.basilisk_exe = QLineEdit()
        basilisk_exe_btn = QPushButton("Browse")
        basilisk_exe_btn.clicked.connect(lambda: self.browse_exe(self.basilisk_exe))
        basilisk_exe_layout.addWidget(self.basilisk_exe)
        basilisk_exe_layout.addWidget(basilisk_exe_btn)
        basilisk_layout.addRow("Executable:", basilisk_exe_layout)
        
        basilisk_cfg_layout = QHBoxLayout()
        self.basilisk_cfg = QLineEdit()
        basilisk_cfg_btn = QPushButton("Browse")
        basilisk_cfg_btn.clicked.connect(lambda: self.browse_file(self.basilisk_cfg))
        basilisk_cfg_layout.addWidget(self.basilisk_cfg)
        basilisk_cfg_layout.addWidget(basilisk_cfg_btn)
        basilisk_layout.addRow("Config File:", basilisk_cfg_layout)
        
        layout.addWidget(basilisk_group)
        
        # Sheepshaver Settings
        sheepshaver_group = QGroupBox("Sheepshaver")
        sheepshaver_layout = QFormLayout(sheepshaver_group)
        
        sheepshaver_exe_layout = QHBoxLayout()
        self.sheepshaver_exe = QLineEdit()
        sheepshaver_exe_btn = QPushButton("Browse")
        sheepshaver_exe_btn.clicked.connect(lambda: self.browse_exe(self.sheepshaver_exe))
        sheepshaver_exe_layout.addWidget(self.sheepshaver_exe)
        sheepshaver_exe_layout.addWidget(sheepshaver_exe_btn)
        sheepshaver_layout.addRow("Executable:", sheepshaver_exe_layout)
        
        sheepshaver_cfg_layout = QHBoxLayout()
        self.sheepshaver_cfg = QLineEdit()
        sheepshaver_cfg_btn = QPushButton("Browse")
        sheepshaver_cfg_btn.clicked.connect(lambda: self.browse_file(self.sheepshaver_cfg))
        sheepshaver_cfg_layout.addWidget(self.sheepshaver_cfg)
        sheepshaver_cfg_layout.addWidget(sheepshaver_cfg_btn)
        sheepshaver_layout.addRow("Config File:", sheepshaver_cfg_layout)
        
        layout.addWidget(sheepshaver_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
    
    def browse_exe(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "Select Executable", "", "All Files (*)")
        if path:
            line_edit.setText(path)
    
    def browse_file(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "All Files (*)")
        if path:
            line_edit.setText(path)
    
    def load_settings(self):
        self.basilisk_exe.setText(self.settings.value('basilisk/exe', ''))
        self.basilisk_cfg.setText(self.settings.value('basilisk/cfg', ''))
        self.sheepshaver_exe.setText(self.settings.value('sheepshaver/exe', ''))
        self.sheepshaver_cfg.setText(self.settings.value('sheepshaver/cfg', ''))
    
    def save_settings(self):
        self.settings.setValue('basilisk/exe', self.basilisk_exe.text())
        self.settings.setValue('basilisk/cfg', self.basilisk_cfg.text())
        self.settings.setValue('sheepshaver/exe', self.sheepshaver_exe.text())
        self.settings.setValue('sheepshaver/cfg', self.sheepshaver_cfg.text())
        QMessageBox.information(self, "Settings", "Settings saved successfully!")


# ============================================================================
# Main Window
# ============================================================================

class PrefsEditor(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('DINKIssTyle', 'EmulatorPrefs')
        self.init_ui()
        self.load_configs()
    
    def init_ui(self):
        self.setWindowTitle("Sheepshaver & Basilisk II Preferences Editor")
        self.setMinimumSize(800, 600)
        
        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        save_action = QAction("💾 Save All", self)
        save_action.triggered.connect(self.save_all_configs)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        reload_action = QAction("🔄 Reload", self)
        reload_action.triggered.connect(self.load_configs)
        toolbar.addAction(reload_action)
        
        toolbar.addSeparator()
        
        launch_basilisk = QAction("▶️ Launch Basilisk", self)
        launch_basilisk.triggered.connect(lambda: self.launch_emulator('basilisk'))
        toolbar.addAction(launch_basilisk)
        
        launch_sheepshaver = QAction("▶️ Launch Sheepshaver", self)
        launch_sheepshaver.triggered.connect(lambda: self.launch_emulator('sheepshaver'))
        toolbar.addAction(launch_sheepshaver)
        
        # Spacer to push About to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
        
        # Main tabs
        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)
        
        self.basilisk_tab = EmulatorTab('basilisk')
        self.sheepshaver_tab = EmulatorTab('sheepshaver')
        self.settings_tab = SettingsTab()
        
        self.main_tabs.addTab(self.basilisk_tab, "Basilisk II")
        self.main_tabs.addTab(self.sheepshaver_tab, "Sheepshaver")
        self.main_tabs.addTab(self.settings_tab, "⚙️ Settings")
    
    def load_configs(self):
        """Load configuration files."""
        basilisk_cfg = self.settings.value('basilisk/cfg', '')
        if basilisk_cfg and os.path.exists(basilisk_cfg):
            config = ConfigParser.parse(basilisk_cfg)
            self.basilisk_tab.load_config(config)
        
        sheepshaver_cfg = self.settings.value('sheepshaver/cfg', '')
        if sheepshaver_cfg and os.path.exists(sheepshaver_cfg):
            config = ConfigParser.parse(sheepshaver_cfg)
            self.sheepshaver_tab.load_config(config)
    
    def save_all_configs(self):
        """Save all configuration files."""
        try:
            basilisk_cfg = self.settings.value('basilisk/cfg', '')
            if basilisk_cfg:
                config = self.basilisk_tab.save_config()
                ConfigParser.save(basilisk_cfg, config)
            
            sheepshaver_cfg = self.settings.value('sheepshaver/cfg', '')
            if sheepshaver_cfg:
                config = self.sheepshaver_tab.save_config()
                ConfigParser.save(sheepshaver_cfg, config)
            
            QMessageBox.information(self, "Save", "Configurations saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configurations:\n{e}")
    
    def launch_emulator(self, emulator_type: str):
        """Launch the specified emulator."""
        if emulator_type == 'basilisk':
            exe = self.settings.value('basilisk/exe', '')
            cfg = self.settings.value('basilisk/cfg', '')
        else:
            exe = self.settings.value('sheepshaver/exe', '')
            cfg = self.settings.value('sheepshaver/cfg', '')
        
        if not exe:
            QMessageBox.warning(self, "Launch", f"Please set {emulator_type} executable path in Settings.")
            return
        
        if not os.path.exists(exe):
            QMessageBox.warning(self, "Launch", f"Executable not found: {exe}")
            return
        
        try:
            # Save config before launching
            if emulator_type == 'basilisk':
                config = self.basilisk_tab.save_config()
            else:
                config = self.sheepshaver_tab.save_config()
            
            if cfg:
                ConfigParser.save(cfg, config)
            
            # Launch emulator
            args = [exe]
            if cfg:
                args.extend(['--config', cfg])
            
            subprocess.Popen(args, start_new_session=True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch emulator:\n{e}")
    
    def show_about(self):
        """Show About dialog."""
        from qtpy.QtWidgets import QDialog, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignCenter)
        
        # App icon
        icon_path = os.path.join(os.path.dirname(__file__), 'Appicon.png')
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel("Sheepshaver & Basilisk II\nPreferences Editor")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Version
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Copyright
        copyright_label = QLabel("© 2025 DINKI'ssTyle")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = PrefsEditor()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
