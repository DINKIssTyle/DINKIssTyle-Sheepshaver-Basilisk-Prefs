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
    QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QGridLayout
)
from qtpy.QtCore import Qt, QSettings, QSize
from qtpy.QtGui import QAction, QIcon, QPixmap


# ============================================================================
# Left Panel Layout Configuration
# ============================================================================

LEFT_PANEL_CONFIG = {
    # Overall panel settings
    'panel_width': 230,
    'panel_margin_top': 10,
    'panel_margin_bottom': 10,
    'panel_margin_left': 10,
    'panel_margin_right': 10,
    
    # Row 1: Icon (fixed height)
    'row1_height': 200,  # px, 0 = auto
    'row1_align': 'center',  # top, center, bottom
    'icon_size': 190,
    
    # Row 2: Title (fixed height)
    'row2_height': 60,  # px, 0 = auto
    'row2_align': 'top',
    'title_font_size': 16,
    'title_max_width': 190,
    
    # Row 3: Power Button (fixed height)
    'row3_height': 190,  # px, 0 = auto
    'row3_align': 'center',
    'power_btn_width': 190,
    'power_btn_height': 190,
    
    # Row 4: Action Buttons (stretch to fill remaining, align bottom)
    'row4_height': 0,  # 0 = stretch
    'row4_align': 'bottom',
    'row4_padding_bottom': 10,
    'action_btn_spacing': 10,
    
    # Colors
    'panel_background_color': '#FFFFFF',
    'content_background_color': '#FFFFFF',
}


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
                    disks.append((value, False))
                elif key == '#disk':
                    disks.append((value, True))
                # Handle #model comment for model selection
                elif key == '#model':
                    config['model'] = value
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
            for disk, disabled in config.get('disks', []):
                if disabled:
                    f.write(f"#disk {disk}\n")
                else:
                    f.write(f"disk {disk}\n")
            
            # Write other settings
            for key, value in config.items():
                if key == 'disks':
                    continue
                # Save model as comment
                if key == 'model':
                    f.write(f"#model {value}\n")
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
        
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(2)
        self.disk_table.setHorizontalHeaderLabels(["Disk Image", "Disabled"])
        self.disk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.disk_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.disk_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.disk_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.disk_table.verticalHeader().setFixedWidth(25)  # Make numbering column wider
        # self.disk_table.setDragDropMode(QAbstractItemView.InternalMove) # Drag drop rows in TableWidget is complex, relying on buttons
        disk_layout.addWidget(self.disk_table)

        # self.disk_table.setMaximumHeight(100)
        
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
        
        # Other Storage Options - Grid Layout
        storage_group = QGroupBox("Storage Options")
        storage_layout = QGridLayout(storage_group)
        
        # Row 0: ExtFS
        storage_layout.addWidget(QLabel("ExtFS Path:"), 0, 0)
        extfs_layout = QHBoxLayout()
        self.extfs_edit = QLineEdit()
        extfs_btn = QPushButton("Browse")
        extfs_btn.clicked.connect(lambda: self.browse_dir(self.extfs_edit))
        extfs_layout.addWidget(self.extfs_edit)
        extfs_layout.addWidget(extfs_btn)
        storage_layout.addLayout(extfs_layout, 0, 1, 1, 5)
        
        # Row 1: ROM
        storage_layout.addWidget(QLabel("ROM File:"), 1, 0)
        rom_layout = QHBoxLayout()
        self.rom_edit = QLineEdit()
        rom_btn = QPushButton("Browse")
        rom_btn.clicked.connect(lambda: self.browse_file(self.rom_edit, "ROM Files (*.rom);;All Files (*)"))
        rom_layout.addWidget(self.rom_edit)
        rom_layout.addWidget(rom_btn)
        storage_layout.addLayout(rom_layout, 1, 1, 1, 5)
        
        # Row 2: Boot Drive | Boot Driver | Disable CD-ROM
        storage_layout.addWidget(QLabel("Boot Drive:"), 2, 0)
        self.boot_drive = QSpinBox()
        self.boot_drive.setRange(0, 255)
        storage_layout.addWidget(self.boot_drive, 2, 1)
        
        storage_layout.addWidget(QLabel("Boot Driver:"), 2, 2)
        self.boot_driver = QSpinBox()
        self.boot_driver.setRange(0, 255)
        storage_layout.addWidget(self.boot_driver, 2, 3)
        
        self.no_cdrom = QCheckBox("Disable CD-ROM")
        storage_layout.addWidget(self.no_cdrom, 2, 4, 1, 2)
        
        # Set column stretch
        storage_layout.setColumnStretch(1, 1)
        storage_layout.setColumnStretch(3, 1)
        
        layout.addWidget(storage_group)
        layout.addStretch()
    
    def add_disk(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Disk Image",
            "", "Disk Images (*.img *.dmg *.iso *.hfv);;All Files (*)"
        )
        if path:
            self._add_disk_row(path, False)
            
    def _add_disk_row(self, path, disabled):
        row = self.disk_table.rowCount()
        self.disk_table.insertRow(row)
        
        # Path item
        path_item = QTableWidgetItem(path)
        path_item.setFlags(path_item.flags() ^ Qt.ItemIsEditable) # Make read-only
        self.disk_table.setItem(row, 0, path_item)
        
        # Checkbox item
        # We use a cell widget or a checkstate. Using cell widget for better centering if needed, but checkstate is standard.
        # Let's use QTableWidgetItem with checkstate for simplicity, but it's text+check. 
        # Ideally we want a specialized column. 
        # Let's use a widget for the disabled column to be explicit.
        
        chk = QCheckBox()
        chk.setChecked(disabled)
        # Center the checkbox
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(chk)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.disk_table.setCellWidget(row, 1, cell_widget)
    
    def remove_disk(self):
        row = self.disk_table.currentRow()
        if row >= 0:
            self.disk_table.removeRow(row)
    
    def move_up(self):
        row = self.disk_table.currentRow()
        if row > 0:
            self._swap_rows(row, row - 1)
            self.disk_table.setCurrentCell(row - 1, 0)
    
    def move_down(self):
        row = self.disk_table.currentRow()
        if row < self.disk_table.rowCount() - 1 and row >= 0:
            self._swap_rows(row, row + 1)
            self.disk_table.setCurrentCell(row + 1, 0)
            
    def _swap_rows(self, row1, row2):
        # Swap content
        path1 = self.disk_table.item(row1, 0).text()
        chk1 = self.disk_table.cellWidget(row1, 1).findChild(QCheckBox).isChecked()
        
        path2 = self.disk_table.item(row2, 0).text()
        chk2 = self.disk_table.cellWidget(row2, 1).findChild(QCheckBox).isChecked()
        
        self.disk_table.item(row1, 0).setText(path2)
        self.disk_table.cellWidget(row1, 1).findChild(QCheckBox).setChecked(chk2)
        
        self.disk_table.item(row2, 0).setText(path1)
        self.disk_table.cellWidget(row2, 1).findChild(QCheckBox).setChecked(chk1)
    
    def browse_file(self, line_edit, filter_str):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filter_str)
        if path:
            line_edit.setText(path)
    
    def browse_dir(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            line_edit.setText(path)
    
    def load_config(self, config: dict):
        self.disk_table.setRowCount(0)
        for disk_entry in config.get('disks', []):
            if isinstance(disk_entry, tuple):
                path, disabled = disk_entry
            else:
                path, disabled = disk_entry, False
            self._add_disk_row(path, disabled)
        self.extfs_edit.setText(str(config.get('extfs', '')))
        self.rom_edit.setText(str(config.get('rom', '')))
        self.boot_drive.setValue(config.get('bootdrive', 0))
        self.boot_driver.setValue(config.get('bootdriver', 0))
        self.no_cdrom.setChecked(config.get('nocdrom', False))
    
    def save_config(self, config: dict):
        disks = []
        for i in range(self.disk_table.rowCount()):
            path = self.disk_table.item(i, 0).text()
            disabled = self.disk_table.cellWidget(i, 1).findChild(QCheckBox).isChecked()
            disks.append((path, disabled))
        config['disks'] = disks
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
        
        # Display Group - Grid layout
        display_group = QGroupBox("Display")
        display_layout = QGridLayout(display_group)
        
        # Row 0: Screen Mode
        display_layout.addWidget(QLabel("Screen Mode:"), 0, 0)
        self.screen_mode = QComboBox()
        self.screen_mode.addItems(["win", "dga", "full"])
        display_layout.addWidget(self.screen_mode, 0, 1, 1, 5)
        
        # Row 1: Width | Height | Color Depth
        display_layout.addWidget(QLabel("Width:"), 1, 0)
        self.screen_width = QSpinBox()
        self.screen_width.setRange(320, 3840)
        self.screen_width.setValue(800)
        display_layout.addWidget(self.screen_width, 1, 1)
        
        display_layout.addWidget(QLabel("Height:"), 1, 2)
        self.screen_height = QSpinBox()
        self.screen_height.setRange(240, 2160)
        self.screen_height.setValue(600)
        display_layout.addWidget(self.screen_height, 1, 3)
        
        display_layout.addWidget(QLabel("Color Depth:"), 1, 4)
        self.color_depth = QComboBox()
        self.color_depth.addItems(["0 (Default)", "8", "16", "24", "32"])
        display_layout.addWidget(self.color_depth, 1, 5)
        
        # Row 2: Frame Skip | SDL Render (moved from Performance and Renderer)
        display_layout.addWidget(QLabel("Frame Skip:"), 2, 0)
        self.frameskip = QSpinBox()
        self.frameskip.setRange(0, 60)
        display_layout.addWidget(self.frameskip, 2, 1)
        
        display_layout.addWidget(QLabel("SDL Render:"), 2, 2)
        self.sdl_render = QComboBox()
        self.sdl_render.addItems(["software", "opengl", "opengles", "opengles2", "metal"])
        display_layout.addWidget(self.sdl_render, 2, 3, 1, 3)
        
        # GFX Acceleration (Sheepshaver only)
        self.gfx_accel = QCheckBox("GFX Acceleration")
        if self.emulator_type == 'sheepshaver':
            display_layout.addWidget(self.gfx_accel, 3, 0, 1, 2)
        
        # Set column stretch
        display_layout.setColumnStretch(1, 1)
        display_layout.setColumnStretch(3, 1)
        display_layout.setColumnStretch(5, 1)
        
        layout.addWidget(display_group)
        
        # Scaling Group - Grid layout
        scale_group = QGroupBox("Scaling")
        scale_layout = QGridLayout(scale_group)
        
        # Row 0: Nearest Neighbor | Integer Scaling
        self.scale_nearest = QCheckBox("Nearest Neighbor")
        scale_layout.addWidget(self.scale_nearest, 0, 0)
        
        self.scale_integer = QCheckBox("Integer Scaling")
        scale_layout.addWidget(self.scale_integer, 0, 1)
        
        # Row 1: Magnification
        scale_layout.addWidget(QLabel("Magnification:"), 1, 0)
        self.mag_rate = QDoubleSpinBox()
        self.mag_rate.setRange(0.0, 4.0)
        self.mag_rate.setSingleStep(0.1)
        self.mag_rate.setValue(1.0)
        scale_layout.addWidget(self.mag_rate, 1, 1)
        
        layout.addWidget(scale_group)
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


class GraphicsSoundTab(QWidget):
    """Combined Graphics and Sound configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.graphics_tab = GraphicsTab(emulator_type)
        self.sound_tab = SoundTab(emulator_type)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Add Graphics settings
        layout.addWidget(self.graphics_tab)
        
        # Add Sound settings
        layout.addWidget(self.sound_tab)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def load_config(self, config: dict):
        self.graphics_tab.load_config(config)
        self.sound_tab.load_config(config)
    
    def save_config(self, config: dict):
        self.graphics_tab.save_config(config)
        self.sound_tab.save_config(config)


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
            
            self.model_id = QComboBox()
            models = [
                ("Mac IIci (Default)", 5),
                ("Mac IIfx", 6),
                ("Quadra 700", 12),
                ("Quadra 800", 23),
                ("Quadra 650", 24),
                ("Quadra 900", 14),
                ("Quadra 950", 16)
            ]
            for name, mid in models:
                self.model_id.addItem(name, mid)
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
        
        # JIT Group - 2 column layout
        jit_group = QGroupBox("JIT Compiler")
        jit_layout = QGridLayout(jit_group)
        
        self.jit_enabled = QCheckBox("Enable JIT")
        
        if self.emulator_type == 'basilisk':
            self.jit_fpu = QCheckBox("JIT FPU")
            self.jit_lazy_flush = QCheckBox("Lazy Flush")
            self.jit_inline = QCheckBox("Inline")
            self.jit_debug = QCheckBox("Debug")
            
            self.jit_cache_size = QSpinBox()
            self.jit_cache_size.setRange(0, 65536)
            self.jit_cache_size.setValue(8192)
            
            # Row 0: Enable JIT | JIT FPU
            jit_layout.addWidget(self.jit_enabled, 0, 0)
            jit_layout.addWidget(self.jit_fpu, 0, 1)
            # Row 1: Cache Size label | Cache Size spinbox | Lazy Flush
            jit_layout.addWidget(QLabel("Cache Size (KB):"), 1, 0)
            jit_layout.addWidget(self.jit_cache_size, 1, 1)
            # Row 2: Lazy Flush | Inline
            jit_layout.addWidget(self.jit_lazy_flush, 2, 0)
            jit_layout.addWidget(self.jit_inline, 2, 1)
            # Row 3: Debug
            jit_layout.addWidget(self.jit_debug, 3, 0)
        
        if self.emulator_type == 'sheepshaver':
            self.jit_68k = QCheckBox("JIT 68K")
            # Row 0: Enable JIT | JIT 68K
            jit_layout.addWidget(self.jit_enabled, 0, 0)
            jit_layout.addWidget(self.jit_68k, 0, 1)
        
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
            
            model_val = config.get('modelid', 5)
            index = self.model_id.findData(model_val)
            if index >= 0:
                self.model_id.setCurrentIndex(index)
            else:
                self.model_id.setCurrentIndex(0) # Default to first item (IIci)
                
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
            config['modelid'] = self.model_id.currentData()
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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Keyboard Group
        km_group = QGroupBox("Keyboard")
        kb_layout = QFormLayout(km_group)
        
        self.kb_type = QComboBox()
        kb_types = [
            ("Apple Extended Keyboard II (5) - Default", 5),
            ("Macintosh Plus (11)", 11),
            ("PowerBook (13)", 13),
            ("Mac Standard (2)", 2),
            ("Unknown (0)", 0)
        ]
        for name, val in kb_types:
            self.kb_type.addItem(name, val)
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
        
        self.hotkey = QComboBox()
        hotkeys = [
            ("Control (Default)", 1),
            ("Option", 2),
            ("Control+Option", 3),
            ("Command", 4),
            ("Control+Command", 5),
            ("Option+Command", 6),
            ("Control+Option+Command", 7)
        ]
        for name, val in hotkeys:
            self.hotkey.addItem(name, val)
        kb_layout.addRow("Hotkey:", self.hotkey)
        
        self.swap_opt_cmd = QCheckBox("Swap Option/Command")
        kb_layout.addRow("", self.swap_opt_cmd)
        
        layout.addWidget(km_group)
        
        # Mouse Group - 2 column layout
        mouse_group = QGroupBox("Mouse")
        mouse_layout = QGridLayout(mouse_group)
        
        # Row 0: Wheel Mode | Wheel Lines
        mouse_layout.addWidget(QLabel("Wheel Mode:"), 0, 0)
        self.mouse_wheel_mode = QComboBox()
        self.mouse_wheel_mode.addItem("Page Up/Down", 0)
        self.mouse_wheel_mode.addItem("Cursor Up/Down", 1)
        mouse_layout.addWidget(self.mouse_wheel_mode, 0, 1)
        
        mouse_layout.addWidget(QLabel("Wheel Lines:"), 0, 2)
        self.mouse_wheel_lines = QSpinBox()
        self.mouse_wheel_lines.setRange(1, 20)
        mouse_layout.addWidget(self.mouse_wheel_lines, 0, 3)
        
        # Row 1: Checkboxes
        self.init_grab = QCheckBox("Initial Grab")
        mouse_layout.addWidget(self.init_grab, 1, 0, 1, 2)
        
        if self.emulator_type == 'sheepshaver':
            self.hard_cursor = QCheckBox("Hardware Cursor")
            mouse_layout.addWidget(self.hard_cursor, 1, 2, 1, 2)
        
        # Set column stretch
        mouse_layout.setColumnStretch(1, 1)
        mouse_layout.setColumnStretch(3, 1)
        
        layout.addWidget(mouse_group)
        layout.addStretch()
    
    def browse_keycode_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Keycode File", "", "All Files (*)")
        if path:
            self.keycode_file.setText(path)
    
    def load_config(self, config: dict):
        kb_val = config.get('keyboardtype', 5)
        index = self.kb_type.findData(kb_val)
        if index >= 0:
            self.kb_type.setCurrentIndex(index)
        else:
            # Add custom value dynamically
            self.kb_type.addItem(f"Custom ({kb_val})", kb_val)
            self.kb_type.setCurrentIndex(self.kb_type.count() - 1)
            
        self.keycodes.setChecked(config.get('keycodes', True))
        self.keycode_file.setText(str(config.get('keycodefile', '')))
        
        hotkey_val = config.get('hotkey', 1)
        # Handle 0 as default (1) or just fallback
        if hotkey_val == 0: hotkey_val = 1
            
        index = self.hotkey.findData(hotkey_val)
        if index >= 0:
            self.hotkey.setCurrentIndex(index)
        else:
            self.hotkey.setCurrentIndex(0) # Default to Control (1)
            
        self.swap_opt_cmd.setChecked(config.get('swap_opt_cmd', True))
        wheel_mode = config.get('mousewheelmode', 1)
        index = self.mouse_wheel_mode.findData(wheel_mode)
        if index >= 0:
            self.mouse_wheel_mode.setCurrentIndex(index)
        else:
            self.mouse_wheel_mode.setCurrentIndex(1)  # Default to Cursor Up/Down
        self.mouse_wheel_lines.setValue(config.get('mousewheellines', 3))
        self.init_grab.setChecked(config.get('init_grab', False))
        if self.emulator_type == 'sheepshaver':
            self.hard_cursor.setChecked(config.get('hardcursor', False))
    
    def save_config(self, config: dict):
        config['keyboardtype'] = self.kb_type.currentData()
        config['keycodes'] = self.keycodes.isChecked()
        config['keycodefile'] = self.keycode_file.text()
        config['hotkey'] = self.hotkey.currentData()
        config['swap_opt_cmd'] = self.swap_opt_cmd.isChecked()
        config['mousewheelmode'] = self.mouse_wheel_mode.currentData()
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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Serial Ports - 2 column layout
        serial_group = QGroupBox("Serial Ports")
        serial_layout = QGridLayout(serial_group)
        
        serial_layout.addWidget(QLabel("Serial A:"), 0, 0)
        self.serial_a = QLineEdit()
        self.serial_a.setPlaceholderText("/dev/ttyS0")
        serial_layout.addWidget(self.serial_a, 0, 1)
        
        serial_layout.addWidget(QLabel("Serial B:"), 0, 2)
        self.serial_b = QLineEdit()
        self.serial_b.setPlaceholderText("/dev/ttyS1")
        serial_layout.addWidget(self.serial_b, 0, 3)
        
        # Set column stretch
        serial_layout.setColumnStretch(1, 1)
        serial_layout.setColumnStretch(3, 1)
        
        layout.addWidget(serial_group)
        layout.addStretch()
    
    def load_config(self, config: dict):
        self.serial_a.setText(str(config.get('seriala', '/dev/ttyS0')))
        self.serial_b.setText(str(config.get('serialb', '/dev/ttyS1')))
    
    def save_config(self, config: dict):
        config['seriala'] = self.serial_a.text()
        config['serialb'] = self.serial_b.text()


class InputSerialTab(QWidget):
    """Combined Input and Serial configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.input_tab = InputTab(emulator_type)
        self.serial_tab = SerialTab(emulator_type)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        
        # Add Input settings
        layout.addWidget(self.input_tab)
        
        # Add Serial settings
        layout.addWidget(self.serial_tab)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def load_config(self, config: dict):
        self.input_tab.load_config(config)
        self.serial_tab.load_config(config)
    
    def save_config(self, config: dict):
        self.input_tab.save_config(config)
        self.serial_tab.save_config(config)


class MiscTab(QWidget):
    """Miscellaneous configuration."""
    from qtpy.QtCore import Signal
    model_changed = Signal(str)  # Signal to notify icon change
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.model_list = self._load_model_list()
        self.init_ui()
    
    def _load_model_list(self):
        """Load model list from res/modelList folder."""
        models = [("None", "default")]  # Default option
        
        prefix = "68k_" if self.emulator_type == 'basilisk' else "ppc_"
        model_path = os.path.join(os.path.dirname(__file__), 'res', 'modelList')
        
        if os.path.exists(model_path):
            for filename in sorted(os.listdir(model_path)):
                if filename.lower().endswith('.png') and filename.lower().startswith(prefix.lower()):
                    # Remove prefix and .png extension
                    model_name = filename[len(prefix):-4]
                    if model_name.lower() != 'default':
                        # Replace underscores with spaces for display
                        display_name = model_name.replace('_', ' ')
                        models.append((display_name, model_name))
        
        return models
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title Group - 2 column layout
        title_group = QGroupBox("Machine Info")
        title_layout = QGridLayout(title_group)
        
        # Title
        title_layout.addWidget(QLabel("Title:"), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("My Macintosh")
        title_layout.addWidget(self.title_edit, 0, 1)
        
        # Model dropdown
        title_layout.addWidget(QLabel("Model:"), 0, 2)
        self.model_combo = QComboBox()
        for display_name, value in self.model_list:
            self.model_combo.addItem(display_name, value)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        title_layout.addWidget(self.model_combo, 0, 3)
        
        # Set column stretch
        title_layout.setColumnStretch(1, 2)
        title_layout.setColumnStretch(3, 1)
        
        layout.addWidget(title_group)
        
        # Miscellaneous Group - 2 column layout
        misc_group = QGroupBox("Miscellaneous")
        misc_layout = QGridLayout(misc_group)
        
        self.no_gui = QCheckBox("No GUI")
        self.no_clip_conversion = QCheckBox("No Clipboard Conversion")
        self.ignore_segv = QCheckBox("Ignore SEGV")
        self.idle_wait = QCheckBox("Idle Wait")
        
        if self.emulator_type == 'sheepshaver':
            self.ignore_illegal = QCheckBox("Ignore Illegal Instructions")
            # Sheepshaver: 3 + 2 layout
            misc_layout.addWidget(self.no_gui, 0, 0)
            misc_layout.addWidget(self.no_clip_conversion, 0, 1)
            misc_layout.addWidget(self.ignore_segv, 1, 0)
            misc_layout.addWidget(self.ignore_illegal, 1, 1)
            misc_layout.addWidget(self.idle_wait, 2, 0)
        else:
            # Basilisk: 2 + 2 layout
            misc_layout.addWidget(self.no_gui, 0, 0)
            misc_layout.addWidget(self.no_clip_conversion, 0, 1)
            misc_layout.addWidget(self.ignore_segv, 1, 0)
            misc_layout.addWidget(self.idle_wait, 1, 1)
        
        layout.addWidget(misc_group)
        
        # Time offset - 2 column layout
        time_group = QGroupBox("Time Offset")
        time_layout = QGridLayout(time_group)
        
        time_layout.addWidget(QLabel("Year Offset:"), 0, 0)
        self.year_offset = QSpinBox()
        self.year_offset.setRange(-100, 100)
        time_layout.addWidget(self.year_offset, 0, 1)
        
        time_layout.addWidget(QLabel("Day Offset:"), 0, 2)
        self.day_offset = QSpinBox()
        self.day_offset.setRange(-365, 365)
        time_layout.addWidget(self.day_offset, 0, 3)
        
        # Set column stretch for even distribution
        time_layout.setColumnStretch(1, 1)
        time_layout.setColumnStretch(3, 1)
        
        layout.addWidget(time_group)
        
        # Encoding
        enc_group = QGroupBox("Encoding")
        enc_layout = QFormLayout(enc_group)
        
        self.name_encoding = QComboBox()
        encodings = [
            ("Auto/MacRoman (Default)", 0),
            ("Japanese", 1),
            ("Chinese Traditional", 2),
            ("Korean", 3),
            ("Arabic", 4),
            ("Hebrew", 5),
            ("Greek", 6),
            ("Cyrillic", 7),
            ("Chinese Simplified", 25)
        ]
        for name, value in encodings:
            self.name_encoding.addItem(name, value)
            
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
    
    def _on_model_changed(self, index):
        """Handle model selection change."""
        model_value = self.model_combo.currentData()
        prefix = "68k_" if self.emulator_type == 'basilisk' else "ppc_"
        image_name = f"{prefix}{model_value}.png"
        self.model_changed.emit(image_name)
    
    def get_current_model_image(self):
        """Get the current model image filename."""
        model_value = self.model_combo.currentData()
        prefix = "68k_" if self.emulator_type == 'basilisk' else "ppc_"
        return f"{prefix}{model_value}.png"
    
    def load_config(self, config: dict):
        self.title_edit.setText(str(config.get('title', '')))
        
        # Load model from config (stored as #model value)
        model_value = config.get('model', 'default')
        index = self.model_combo.findData(model_value)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.setCurrentIndex(0)  # Default to None
        
        self.no_gui.setChecked(config.get('nogui', True))
        self.no_clip_conversion.setChecked(config.get('noclipconversion', False))
        self.ignore_segv.setChecked(config.get('ignoresegv', False))
        if self.emulator_type == 'sheepshaver':
            self.ignore_illegal.setChecked(config.get('ignoreillegal', False))
        self.idle_wait.setChecked(config.get('idlewait', True))
        self.year_offset.setValue(config.get('yearofs', 0))
        self.day_offset.setValue(config.get('dayofs', 0))
        
        encoding_val = config.get('name_encoding', 0)
        index = self.name_encoding.findData(encoding_val)
        if index >= 0:
            self.name_encoding.setCurrentIndex(index)
        else:
            self.name_encoding.setCurrentIndex(0) # Default to first item if not found
        if self.emulator_type == 'basilisk':
            self.delay.setValue(config.get('delay', 0))
    
    def save_config(self, config: dict):
        title = self.title_edit.text().strip()
        if title:
            config['title'] = title
        
        # Save model (will be stored as comment #model value)
        model_value = self.model_combo.currentData()
        if model_value and model_value != 'default':
            config['model'] = model_value
        
        config['nogui'] = self.no_gui.isChecked()
        config['noclipconversion'] = self.no_clip_conversion.isChecked()
        config['ignoresegv'] = self.ignore_segv.isChecked()
        if self.emulator_type == 'sheepshaver':
            config['ignoreillegal'] = self.ignore_illegal.isChecked()
        config['idlewait'] = self.idle_wait.isChecked()
        config['yearofs'] = self.year_offset.value()
        config['dayofs'] = self.day_offset.value()
        config['name_encoding'] = self.name_encoding.currentData()
        if self.emulator_type == 'basilisk':
            config['delay'] = self.delay.value()


# ============================================================================
# Clickable Label for Power Button
# ============================================================================

class ClickableLabel(QLabel):
    """A QLabel that emits a clicked signal when pressed."""
    
    from qtpy.QtCore import Signal
    clicked = Signal()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ============================================================================
# Left Panel (Icon, Title, Power Button)
# ============================================================================

class LeftPanel(QWidget):
    """Left panel containing icon, title label, and power button."""
    
    from qtpy.QtCore import Signal
    power_clicked = Signal()
    save_clicked = Signal()
    reload_clicked = Signal()
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        cfg = LEFT_PANEL_CONFIG
        
        # Set panel background color
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {cfg['panel_background_color']};")
        
        # Main layout - no spacing between rows
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(
            cfg['panel_margin_left'],
            cfg['panel_margin_top'],
            cfg['panel_margin_right'],
            cfg['panel_margin_bottom']
        )
        
        # ==================== Row 1: Icon ====================
        row1 = QWidget()
        row1_layout = QVBoxLayout(row1)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(0)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(cfg['icon_size'], cfg['icon_size'])
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: none; background: transparent;")
        
        # Alignment for row 1
        align = Qt.AlignHCenter
        if cfg['row1_align'] == 'top':
            align |= Qt.AlignTop
        elif cfg['row1_align'] == 'bottom':
            align |= Qt.AlignBottom
        else:
            align |= Qt.AlignVCenter
            
        row1_layout.addWidget(self.icon_label, alignment=align)
        
        if cfg['row1_height'] > 0:
            row1.setFixedHeight(cfg['row1_height'])
            layout.addWidget(row1)
        else:
            layout.addWidget(row1, 1)

        # ==================== Row 2: Title ====================
        row2 = QWidget()
        row2_layout = QVBoxLayout(row2)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(0)
        
        self.title_label = QLabel(self._get_default_title())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: {cfg['title_font_size']}px;
                font-weight: bold;
                color: #333;
            }}
        """)
        self.title_label.setWordWrap(False)
        self.title_label.setMaximumWidth(cfg['title_max_width'])
        
        # Alignment for row 2
        align = Qt.AlignHCenter
        if cfg['row2_align'] == 'top':
            align |= Qt.AlignTop
        elif cfg['row2_align'] == 'bottom':
            align |= Qt.AlignBottom
        else:
            align |= Qt.AlignVCenter
            
        row2_layout.addWidget(self.title_label, alignment=align)
        
        if cfg['row2_height'] > 0:
            row2.setFixedHeight(cfg['row2_height'])
            layout.addWidget(row2)
        else:
            layout.addWidget(row2, 1)
        
        # ==================== Row 3: Power Button ====================
        row3 = QWidget()
        row3_layout = QVBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(0)
        
        self.power_btn = ClickableLabel()
        self.power_btn.setFixedSize(cfg['power_btn_width'], cfg['power_btn_height'])
        self.power_btn.setAlignment(Qt.AlignCenter)
        self.power_btn.setCursor(Qt.PointingHandCursor)
        self.power_btn.setToolTip("Click to launch emulator")
        
        # Load power switch image
        power_img_name = "68k_pwrsw.png" if self.emulator_type == 'basilisk' else "ppc_pwrsw.png"
        power_img_path = os.path.join(os.path.dirname(__file__), 'res', power_img_name)
        
        if os.path.exists(power_img_path):
            pixmap = QPixmap(power_img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(cfg['power_btn_width'], cfg['power_btn_height'], Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.power_btn.setPixmap(pixmap)
        else:
            self.power_btn.setText("⏻ Start")
            self.power_btn.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    background-color: #444;
                    color: white;
                    border-radius: 10px;
                }
                QLabel:hover {
                    background-color: #555;
                }
            """)
        
        self.power_btn.clicked.connect(self.power_clicked.emit)
        
        # Alignment for row 3
        align = Qt.AlignHCenter
        if cfg['row3_align'] == 'top':
            align |= Qt.AlignTop
        elif cfg['row3_align'] == 'bottom':
            align |= Qt.AlignBottom
        else:
            align |= Qt.AlignVCenter
            
        row3_layout.addWidget(self.power_btn, alignment=align)
        
        if cfg['row3_height'] > 0:
            row3.setFixedHeight(cfg['row3_height'])
            layout.addWidget(row3)
        else:
            layout.addWidget(row3, 1)
        
        # ==================== Row 4: Action Buttons (stretch) ====================
        row4 = QWidget()
        row4_layout = QVBoxLayout(row4)
        row4_layout.setContentsMargins(0, 0, 0, cfg['row4_padding_bottom'])
        row4_layout.setSpacing(0)
        
        # ==================== Row 4: Spacer (stretch) ====================
        row4 = QWidget()
        # Row 4 stretches to fill remaining space
        if cfg['row4_height'] > 0:
            row4.setFixedHeight(cfg['row4_height'])
            layout.addWidget(row4)
        else:
            layout.addWidget(row4, 1)
        
        # Set fixed width for left panel
        self.setFixedWidth(cfg['panel_width'])
    
    def _get_default_title(self):
        if self.emulator_type == 'basilisk':
            return "68k Macintosh"
        else:
            return "PPC Macintosh"
    
    def set_title(self, title: str):
        """Set the title label text."""
        if title.strip():
            self.title_label.setText(title)
        else:
            self.title_label.setText(self._get_default_title())
    
    def set_icon(self, icon_path: str):
        """Set the icon image from path."""
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                size = LEFT_PANEL_CONFIG['icon_size']
                pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(pixmap)
    
    def set_model_icon(self, image_name: str):
        """Set the icon from model image in res/modelList folder."""
        model_path = os.path.join(os.path.dirname(__file__), 'res', 'modelList', image_name)
        
        if os.path.exists(model_path):
            pixmap = QPixmap(model_path)
            if not pixmap.isNull():
                size = LEFT_PANEL_CONFIG['icon_size']
                pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_label.setPixmap(pixmap)
        else:
            # Clear the icon if not found
            self.icon_label.clear()


# ============================================================================
# Emulator Tab (contains sub-tabs)
# ============================================================================

class EmulatorTab(QWidget):
    """Container for emulator-specific sub-tabs."""
    
    from qtpy.QtCore import Signal
    launch_requested = Signal()
    save_requested = Signal()
    reload_requested = Signal()
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.config = {}
        self.init_ui()
    
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Left Panel
        self.left_panel = LeftPanel(self.emulator_type)
        self.left_panel.power_clicked.connect(self.launch_requested.emit)
        main_layout.addWidget(self.left_panel)
        
        # Right Panel (sub-tabs)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {LEFT_PANEL_CONFIG['content_background_color']};
                border: 1px solid #C0C0C0;
            }}
            QTabBar::tab {{
                background-color: #E0E0E0;
                border: 1px solid #A0A0A0;
                padding: 6px;
                min-width: 30px;
                min-height: 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                qproperty-iconSize: 24px 24px;
            }}
            QTabBar::tab:selected {{
                background-color: {LEFT_PANEL_CONFIG['content_background_color']};
                border-bottom-color: {LEFT_PANEL_CONFIG['content_background_color']};
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
        """)
        
        # Create tabs
        self.drives_tab = DrivesTab(self.emulator_type)
        self.graphics_tab = GraphicsTab(self.emulator_type)
        self.sound_tab = SoundTab(self.emulator_type)
        self.network_tab = NetworkTab(self.emulator_type)
        self.cpu_memory_tab = CpuMemoryTab(self.emulator_type)
        self.input_serial_tab = InputSerialTab(self.emulator_type)
        self.misc_tab = MiscTab(self.emulator_type)
        
        # Connect model changed signal to update left panel icon
        self.misc_tab.model_changed.connect(self.left_panel.set_model_icon)
        
        # Load tab icons from res folder
        res_path = os.path.join(os.path.dirname(__file__), 'res')
        
        def get_icon(icon_name):
            icon_path = os.path.join(res_path, icon_name)
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            return QIcon()
        
        # Add tabs with icons (text can be added later)
        self.sub_tabs.addTab(self.drives_tab, get_icon("drives.png"), "")
        self.sub_tabs.addTab(self.graphics_tab, get_icon("monitor.png"), "")
        self.sub_tabs.addTab(self.sound_tab, get_icon("sound.png"), "")
        self.sub_tabs.addTab(self.network_tab, get_icon("network.png"), "")
        self.sub_tabs.addTab(self.cpu_memory_tab, get_icon("cpu_memory.png"), "")
        self.sub_tabs.addTab(self.input_serial_tab, get_icon("keyboard.png"), "")
        self.sub_tabs.addTab(self.misc_tab, get_icon("misc.png"), "")
        
        # Set icon size for better visibility
        self.sub_tabs.setIconSize(QSize(24, 24))
        
        right_layout.addWidget(self.sub_tabs)
        main_layout.addWidget(right_widget, 1)  # Stretch factor 1 for right panel
    
    def load_config(self, config: dict):
        self.config = config
        self.drives_tab.load_config(config)
        self.graphics_tab.load_config(config)
        self.sound_tab.load_config(config)
        self.network_tab.load_config(config)
        self.cpu_memory_tab.load_config(config)
        self.input_serial_tab.load_config(config)
        self.misc_tab.load_config(config)
        
        # Update left panel title from config
        title = str(config.get('title', ''))
        self.left_panel.set_title(title)
        
        # Update left panel model icon
        model_image = self.misc_tab.get_current_model_image()
        self.left_panel.set_model_icon(model_image)
    
    def save_config(self) -> dict:
        config = {}
        self.drives_tab.save_config(config)
        self.graphics_tab.save_config(config)
        self.sound_tab.save_config(config)
        self.network_tab.save_config(config)
        self.cpu_memory_tab.save_config(config)
        self.input_serial_tab.save_config(config)
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
        
        zap_basilisk_btn = QPushButton("Zap PRAM")
        zap_basilisk_btn.clicked.connect(lambda: self.zap_pram('basilisk'))
        basilisk_layout.addRow("", zap_basilisk_btn)
        
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
        
        zap_sheepshaver_btn = QPushButton("Zap PRAM")
        zap_sheepshaver_btn.clicked.connect(lambda: self.zap_pram('sheepshaver'))
        sheepshaver_layout.addRow("", zap_sheepshaver_btn)
        
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
    
    def zap_pram(self, emulator_type: str):
        """Delete PRAM/NVRAM file for the specified emulator."""
        if emulator_type == 'basilisk':
            cfg_path = self.basilisk_cfg.text()
            pram_filename = '.basilisk_ii_xpram'
        else:
            cfg_path = self.sheepshaver_cfg.text()
            pram_filename = '.sheepshaver_nvram'
        
        if not cfg_path:
            QMessageBox.warning(self, "Zap PRAM", f"Please set {emulator_type} config file path first.")
            return
        
        cfg_dir = os.path.dirname(cfg_path)
        pram_path = os.path.join(cfg_dir, pram_filename)
        
        if not os.path.exists(pram_path):
            QMessageBox.information(self, "Zap PRAM", f"PRAM file not found:\n{pram_path}")
            return
        
        try:
            os.remove(pram_path)
            QMessageBox.information(self, "Zap PRAM", f"PRAM file deleted successfully:\n{pram_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete PRAM file:\n{e}")


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
        self.setMinimumSize(800, 550)
        self.resize(800, 550)  # 초기 창 크기
        
        # Helper function to get icon
        res_path = os.path.join(os.path.dirname(__file__), 'res')
        def get_icon(icon_name):
            icon_path = os.path.join(res_path, icon_name)
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            return QIcon()
        
        # Main tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setIconSize(QSize(24, 24))  # Increase icon size to ensure tab height ensures button fit while keeping native style
        self.setCentralWidget(self.main_tabs)
        
        self.basilisk_tab = EmulatorTab('basilisk')
        self.sheepshaver_tab = EmulatorTab('sheepshaver')
        self.settings_tab = SettingsTab()
        
        # Connect power button signals
        self.basilisk_tab.launch_requested.connect(lambda: self.launch_emulator('basilisk'))
        self.sheepshaver_tab.launch_requested.connect(lambda: self.launch_emulator('sheepshaver'))
        
        # Connect save and reload signals
        self.basilisk_tab.save_requested.connect(self.save_all_configs)
        self.basilisk_tab.reload_requested.connect(self.load_configs)
        self.sheepshaver_tab.save_requested.connect(self.save_all_configs)
        self.sheepshaver_tab.reload_requested.connect(self.load_configs)
        
        self.main_tabs.addTab(self.basilisk_tab, get_icon("68k.png"), "Basilisk II")
        self.main_tabs.addTab(self.sheepshaver_tab, get_icon("ppc.png"), "Sheepshaver")
        self.main_tabs.addTab(self.settings_tab, get_icon("settings.png"), "Settings")
        
        # About button in top-right corner of tab bar
        # Top-right corner buttons: Save All, Reload, About
        top_right_widget = QWidget()
        top_right_layout = QHBoxLayout(top_right_widget)
        top_right_layout.setAlignment(Qt.AlignVCenter)
        top_right_layout.setContentsMargins(0, 2, 2, 2)
        top_right_layout.setSpacing(2)
        
        btn_height = 26
        
        # Save All Button
        save_btn = QPushButton("Save All")
        save_btn.setIcon(get_icon("save.png"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(btn_height)
        save_btn.clicked.connect(self.save_all_configs)
        top_right_layout.addWidget(save_btn)
        
        # Reload Button
        reload_btn = QPushButton("Reload")
        reload_btn.setIcon(get_icon("reload.png"))
        reload_btn.setCursor(Qt.PointingHandCursor)
        reload_btn.setFixedHeight(btn_height)
        reload_btn.clicked.connect(self.load_configs)
        top_right_layout.addWidget(reload_btn)
        
        # About Button
        about_btn = QPushButton("About")
        about_btn.setIcon(get_icon("about.png"))
        about_btn.setCursor(Qt.PointingHandCursor)
        about_btn.setFixedHeight(btn_height)
        about_btn.clicked.connect(self.show_about)
        top_right_layout.addWidget(about_btn)
        
        self.main_tabs.setCornerWidget(top_right_widget, Qt.TopRightCorner)
    
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
            
            # Reload configurations to reflect changes
            self.load_configs()
            
            QMessageBox.information(self, "Save", "Configuration saved and reloaded successfully!")
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
            if sys.platform == 'darwin' and exe.endswith('.app'):
                # Use 'open' command for macOS .app bundles
                args = ['open', '-n', '-a', exe]
                if cfg:
                    args.extend(['--args', '--config', cfg])
            else:
                # Standard binary execution
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
        icon_path = os.path.join(os.path.dirname(__file__), 'res/Appicon.png')
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
        version_label = QLabel("Version 2.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Copyright
        copyright_label = QLabel("© 2026 DINKI'ssTyle")
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
