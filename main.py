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
    QScrollArea, QGridLayout, QDialog, QStyledItemDelegate, QInputDialog,
    QButtonGroup
)
from qtpy.QtCore import Qt, QSettings, QSize, QTimer
from qtpy.QtGui import QAction, QIcon, QPixmap, QColor, QPalette


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
    'row2_height': 40,  # px, 0 = auto
    'row2_align': 'top',
    'title_font_size': 16,
    'title_max_width': 190,
    'title_color': '#333333',  # Title text color
    
    # Row 3: Power Button (fixed height)
    'row3_height': 190,  # px, 0 = auto
    'row3_align': 'center',
    'power_btn_width': 96,
    'power_btn_height': 96,
    
    # Row 4: Action Buttons (stretch to fill remaining, align bottom)
    'row4_height': 0,  # 0 = stretch
    'row4_align': 'bottom',
    'row4_padding_bottom': 10,
    'action_btn_spacing': 10,
    
    # Left panel background color (set to None to use system default)
    'panel_background_color': '#FFFFFF',
}


# ============================================================================
# Translations (i18n)
# ============================================================================

TRANSLATIONS = {
    'en': {  # English (Default)
        'app_title': 'Sheepshaver & Basilisk II Preferences Editor',
        'basilisk_tab': 'Basilisk II',
        'sheepshaver_tab': 'Sheepshaver',
        'settings_tab': 'Settings',
        'save': 'Save',
        'reload': 'Reload',
        'management': 'Management',
        'about': 'About',
        'language': 'Language',
        'language_section': 'Language',
        'restart_required': 'Restart required to apply language change.',
        # Left Panel
        'default_title_68k': '68k Macintosh',
        'default_title_ppc': 'PPC Macintosh',
        'launch_tooltip': 'Click to launch emulator',
        # Drives Tab
        'disk_images': 'Disk Images',
        'disk_image': 'Disk Image',
        'disabled': 'Disabled',
        'new_disk': 'New',
        'add': 'Add',
        'remove': 'Remove',
        'create_disk_title': 'Create Disk Image',
        'disk_size_mb': 'Size (MB):',
        'disk_create_success': 'Disk image created successfully.',
        'disk_create_error': 'Failed to create disk image.',
        'up': '▲ Up',
        'down': '▼ Down',
        'cdrom_column': 'CD-ROM',
        'storage_options': 'Storage Options',
        'extfs_path': 'ExtFS Path:',
        'rom_file': 'ROM File:',
        'boot_from': 'Boot From:',
        'boot_any': 'Any',
        'boot_cdrom': 'CD-ROM',
        'boot_drive': 'Boot Drive:',
        'boot_driver': 'Boot Driver:',
        'disable_cdrom': 'Disable CD-ROM',
        'browse': 'Browse',
        # Graphics Tab
        'display': 'Display',
        'screen_mode': 'Screen Mode:',
        'width': 'Width:',
        'height': 'Height:',
        'color_depth': 'Color Depth:',
        'frame_skip': 'Frame Skip:',
        'sdl_render': 'SDL Render:',
        'gfx_acceleration': 'GFX Acceleration',
        'scaling': 'Scaling',
        'nearest_neighbor': 'Nearest Neighbor',
        'integer_scaling': 'Integer Scaling',
        'shader_list': 'Shaders',
        'shader_file': 'Shader File',
        'shader_params': 'Shader Parameters',
        'configure': 'Configure',
        # Sound Tab
        'audio': 'Audio',
        'audio_output': 'Audio Output:',
        'disable_sound': 'Disable Sound',
        # Network Tab
        'ethernet': 'Ethernet',
        'ethernet_mode': 'Ethernet Mode:',
        'ethernet_port': 'Ethernet Port:',
        'none': 'None',
        # CPU/Memory Tab
        'memory': 'Memory',
        'ram_size': 'RAM Size:',
        'cpu': 'CPU',
        'cpu_type': 'CPU Type:',
        'model_id': 'Model ID:',
        'enable_fpu': 'Enable FPU',
        'cpu_clock': 'CPU Clock (0=auto):',
        'jit_compiler': 'JIT Compiler',
        'enable_jit': 'Enable JIT',
        'jit_fpu': 'JIT FPU',
        'jit_68k': 'JIT 68K',
        'cache_size': 'Cache Size (KB):',
        'lazy_flush': 'Lazy Flush',
        'inline': 'Inline',
        'debug': 'Debug',
        # Input Tab
        'keyboard': 'Keyboard',
        'keyboard_type': 'Keyboard Type:',
        'use_keycodes': 'Use Keycodes',
        'keycode_file': 'Keycode File:',
        'hotkey': 'Hotkey:',
        'swap_opt_cmd': 'Swap Option/Command',
        'mouse': 'Mouse',
        'wheel_mode': 'Wheel Mode:',
        'wheel_lines': 'Wheel Lines:',
        'initial_grab': 'Initial Grab',
        'hardware_cursor': 'Hardware Cursor',
        # Serial Tab
        'serial_ports': 'Serial Ports',
        'serial_a': 'Serial A:',
        'serial_b': 'Serial B:',
        # Misc Tab
        'title_model': 'Title & Model',
        'title': 'Title:',
        'model': 'Model:',
        'miscellaneous': 'Miscellaneous',
        'no_gui': 'No GUI',
        'no_clip_conversion': 'No Clipboard Conversion',
        'ignore_segv': 'Ignore SEGV',
        'ignore_illegal': 'Ignore Illegal Instructions',
        'idle_wait': 'Idle Wait',
        'time_offset': 'Time Offset',
        'year_offset': 'Year Offset:',
        'day_offset': 'Day Offset:',
        'encoding': 'Encoding',
        'name_encoding': 'Name Encoding:',
        'performance': 'Performance',
        'delay': 'Delay:',
        # Settings Tab
        'executable': 'Executable:',
        'config_file': 'Config File:',
        'zap_pram': 'Zap PRAM',
        'save_settings': 'Save Settings',
        'settings_saved': 'Settings saved successfully!',
        # About Dialog
        'version': 'Version 2.0',
        'copyright': '© 2026 DINKI\'ssTyle',
        # Messages
        'config_saved': 'Configuration saved and reloaded successfully!',
        'error': 'Error',
        'save': 'Save',
        'save_as': 'Save As',
        'launch': 'Launch',
        'reset': 'Reset',
        'new_profile': 'New Profile',
        'profile_name': 'Profile Name:',
        'default_profile': 'Default',
        'enter_profile_name': 'Enter name for new profile:',
        'profile_exists': 'A profile with this name already exists.',
        'filter_all': 'All',
        'rename': 'Rename',
        'delete': 'Delete',
        'duplicate': 'Duplicate',
        'copy_suffix': ' copy',
        'confirm_delete': 'Confirm Delete',
        'delete_msg1': 'Are you sure you want to delete profile "{}"?',
        'delete_msg2': 'This action cannot be undone. Really delete?',
        'rename_profile': 'Rename Profile',
        'enter_new_name': 'Enter new profile name:',
        'close': 'Close',
        'config_missing_title': 'Configuration Missing',
        'config_missing_msg': 'No configuration file found.\nPlease specify the configuration file path in the Settings tab.',
    },
    'ko': {  # Korean
        'app_title': 'Sheepshaver & Basilisk II 환경설정 편집기',
        'basilisk_tab': 'Basilisk II',
        'sheepshaver_tab': 'Sheepshaver',
        'settings_tab': '설정',
        'save': '저장',
        'reload': '새로고침',
        'management': '관리',
        'about': '정보',
        'language': '언어',
        'language_section': '언어',
        'restart_required': '언어 변경을 적용하려면 재시작이 필요합니다.',
        'default_title_68k': '68k 매킨토시',
        'default_title_ppc': 'PPC 매킨토시',
        'launch_tooltip': '클릭하여 에뮬레이터 실행',
        'disk_images': '디스크 이미지',
        'disk_image': '디스크 이미지',
        'disabled': '비활성화',
        'new_disk': '새로 만들기',
        'add': '추가',
        'remove': '제거',
        'create_disk_title': '디스크 이미지 만들기',
        'disk_size_mb': '용량 (MB):',
        'disk_create_success': '디스크 이미지가 생성되었습니다.',
        'disk_create_error': '디스크 이미지 생성에 실패했습니다.',
        'up': '▲ 위로',
        'down': '▼ 아래로',
        'cdrom_column': 'CD-ROM',
        'storage_options': '저장소 옵션',
        'extfs_path': 'ExtFS 경로:',
        'rom_file': 'ROM 파일:',
        'boot_from': '부팅:',
        'boot_any': '자동 (Any)',
        'boot_cdrom': 'CD-ROM',
        'boot_drive': '부트 드라이브:',
        'boot_driver': '부트 드라이버:',
        'disable_cdrom': 'CD-ROM 비활성화',
        'browse': '찾아보기',
        'display': '디스플레이',
        'screen_mode': '화면 모드:',
        'width': '너비:',
        'height': '높이:',
        'color_depth': '색상 깊이:',
        'frame_skip': '프레임 스킵:',
        'sdl_render': 'SDL 렌더러:',
        'gfx_acceleration': 'GFX 가속',
        'scaling': '스케일링',
        'nearest_neighbor': 'Nearest Neighbor',
        'integer_scaling': '정수 스케일링',
        'shader_list': '쉐이더 목록',
        'shader_file': '쉐이더 파일',
        'shader_params': '쉐이더 파라미터',
        'configure': '설정',
        'audio': '오디오',
        'audio_output': '오디오 출력:',
        'disable_sound': '사운드 비활성화',
        'ethernet': '이더넷',
        'ethernet_mode': '이더넷 모드:',
        'ethernet_port': '이더넷 포트:',
        'none': '없음',
        'memory': '메모리',
        'ram_size': 'RAM 크기:',
        'cpu': 'CPU',
        'cpu_type': 'CPU 종류:',
        'model_id': '모델 ID:',
        'enable_fpu': 'FPU 활성화',
        'cpu_clock': 'CPU 클럭 (0=자동):',
        'jit_compiler': 'JIT 컴파일러',
        'enable_jit': 'JIT 활성화',
        'jit_fpu': 'JIT FPU',
        'jit_68k': 'JIT 68K',
        'cache_size': '캐시 크기 (KB):',
        'lazy_flush': '지연 플러시',
        'inline': '인라인',
        'debug': '디버그',
        'keyboard': '키보드',
        'keyboard_type': '키보드 종류:',
        'use_keycodes': '키코드 사용',
        'keycode_file': '키코드 파일:',
        'hotkey': '단축키:',
        'swap_opt_cmd': 'Option/Command 교환',
        'mouse': '마우스',
        'wheel_mode': '휠 모드:',
        'wheel_lines': '휠 라인:',
        'initial_grab': '시작시 커서 그랩',
        'hardware_cursor': '하드웨어 커서',
        'serial_ports': '시리얼 포트',
        'serial_a': '시리얼 A:',
        'serial_b': '시리얼 B:',
        'title_model': '제목 및 모델',
        'title': '제목:',
        'model': '모델:',
        'miscellaneous': '기타',
        'no_gui': 'GUI 없음',
        'no_clip_conversion': '클립보드 변환 없음',
        'ignore_segv': 'SEGV 무시',
        'ignore_illegal': '잘못된 명령 무시',
        'idle_wait': '유휴 대기',
        'time_offset': '시간 오프셋',
        'year_offset': '연도 오프셋:',
        'day_offset': '일 오프셋:',
        'encoding': '인코딩',
        'name_encoding': '이름 인코딩:',
        'performance': '성능',
        'delay': '지연:',
        'executable': '실행 파일:',
        'config_file': '설정 파일:',
        'zap_pram': 'PRAM 초기화',
        'save_settings': '설정 저장',
        'settings_saved': '설정이 저장되었습니다!',
        'version': '버전 2.0',
        'copyright': '© 2026 DINKI\'ssTyle',
        'config_saved': '설정이 저장되고 새로고침되었습니다!',
        'error': '오류',
        'save': '저장',
        'save_as': '다른 이름으로 저장',
        'launch': '실행',
        'reset': '초기화',
        'new_profile': '새 프로필',
        'profile_name': '프로필 이름:',
        'default_profile': '기본값',
        'enter_profile_name': '새 프로필 이름을 입력하세요:',
        'profile_exists': '같은 이름의 프로필이 이미 존재합니다.',
        'filter_all': '전체',
        'rename': '이름 변경',
        'delete': '삭제',
        'duplicate': '복제',
        'copy_suffix': ' 복사본',
        'confirm_delete': '삭제 확인',
        'delete_msg1': '프로필 "{}"을(를) 정말 삭제하시겠습니까?',
        'delete_msg2': '이 작업은 되돌릴 수 없습니다. 정말 삭제합니까?',
        'rename_profile': '프로필 이름 변경',
        'enter_new_name': '새 프로필 이름을 입력하세요:',
        'close': '닫기',
        'config_missing_title': '설정 파일 없음',
        'config_missing_msg': '설정 파일을 찾을 수 없습니다.\n설정 탭에서 환경설정 파일 경로를 지정해주세요.',
    },
    'zh': {  # Chinese (Simplified)
        'app_title': 'Sheepshaver & Basilisk II 偏好设置编辑器',
        'basilisk_tab': 'Basilisk II',
        'sheepshaver_tab': 'Sheepshaver',
        'settings_tab': '设置',
        'save': '保存',
        'reload': '重新加载',
        'management': '管理',
        'about': '关于',
        'language': '语言',
        'language_section': '语言',
        'restart_required': '需要重启以应用语言更改。',
        'default_title_68k': '68k 麦金塔',
        'default_title_ppc': 'PPC 麦金塔',
        'launch_tooltip': '点击启动模拟器',
        'disk_images': '磁盘镜像',
        'disk_image': '磁盘镜像',
        'disabled': '已禁用',
        'new_disk': '新建',
        'add': '添加',
        'remove': '删除',
        'create_disk_title': '创建磁盘镜像',
        'disk_size_mb': '大小 (MB):',
        'disk_create_success': '磁盘镜像创建成功。',
        'disk_create_error': '磁盘镜像创建失败。',
        'up': '▲ 上移',
        'down': '▼ 下移',
        'cdrom_column': 'CD-ROM',
        'storage_options': '存储选项',
        'extfs_path': 'ExtFS 路径:',
        'rom_file': 'ROM 文件:',
        'boot_from': '启动:',
        'boot_any': '任意 (Any)',
        'boot_cdrom': 'CD-ROM',
        'boot_drive': '启动驱动器:',
        'boot_driver': '启动驱动程序:',
        'disable_cdrom': '禁用 CD-ROM',
        'browse': '浏览',
        'display': '显示',
        'screen_mode': '屏幕模式:',
        'width': '宽度:',
        'height': '高度:',
        'color_depth': '色深:',
        'frame_skip': '跳帧:',
        'sdl_render': 'SDL 渲染器:',
        'gfx_acceleration': '图形加速',
        'scaling': '缩放',
        'nearest_neighbor': '最近邻',
        'integer_scaling': '整数缩放',
        'shader_list': '着色器',
        'shader_file': '着色器文件',
        'shader_params': '着色器参数',
        'configure': '配置',
        'audio': '音频',
        'audio_output': '音频输出:',
        'disable_sound': '禁用声音',
        'ethernet': '以太网',
        'ethernet_mode': '以太网模式:',
        'ethernet_port': '以太网端口:',
        'none': '无',
        'memory': '内存',
        'ram_size': 'RAM 大小:',
        'cpu': 'CPU',
        'cpu_type': 'CPU 类型:',
        'model_id': '型号 ID:',
        'enable_fpu': '启用 FPU',
        'cpu_clock': 'CPU 时钟 (0=自动):',
        'jit_compiler': 'JIT 编译器',
        'enable_jit': '启用 JIT',
        'jit_fpu': 'JIT FPU',
        'jit_68k': 'JIT 68K',
        'cache_size': '缓存大小 (KB):',
        'lazy_flush': '延迟刷新',
        'inline': '内联',
        'debug': '调试',
        'keyboard': '键盘',
        'keyboard_type': '键盘类型:',
        'use_keycodes': '使用键码',
        'keycode_file': '键码文件:',
        'hotkey': '热键:',
        'swap_opt_cmd': '交换 Option/Command',
        'mouse': '鼠标',
        'wheel_mode': '滚轮模式:',
        'wheel_lines': '滚轮行数:',
        'initial_grab': '初始抓取',
        'hardware_cursor': '硬件光标',
        'serial_ports': '串行端口',
        'serial_a': '串行 A:',
        'serial_b': '串行 B:',
        'title_model': '标题和型号',
        'title': '标题:',
        'model': '型号:',
        'miscellaneous': '杂项',
        'no_gui': '无 GUI',
        'no_clip_conversion': '无剪贴板转换',
        'ignore_segv': '忽略 SEGV',
        'ignore_illegal': '忽略非法指令',
        'idle_wait': '空闲等待',
        'time_offset': '时间偏移',
        'year_offset': '年份偏移:',
        'day_offset': '日期偏移:',
        'encoding': '编码',
        'name_encoding': '名称编码:',
        'performance': '性能',
        'delay': '延迟:',
        'executable': '可执行文件:',
        'config_file': '配置文件:',
        'zap_pram': '清除 PRAM',
        'save_settings': '保存设置',
        'settings_saved': '设置已保存!',
        'version': '版本 2.0',
        'copyright': '© 2026 DINKI\'ssTyle',
        'config_saved': '配置已保存并重新加载!',
        'error': '错误',
        'save': '保存',
        'save_as': '另存为',
        'launch': '启动',
        'reset': '重置',
        'new_profile': '新配置文件',
        'profile_name': '配置文件名称:',
        'default_profile': '默认',
        'enter_profile_name': '输入新配置文件的名称:',
        'profile_exists': '具有此名称的配置文件已存在。',
        'config_missing_title': '缺少配置',
        'config_missing_msg': '未找到配置文件。\n请在设置选项卡中指定配置文件路径。',
    },
    'ja': {  # Japanese
        'app_title': 'Sheepshaver & Basilisk II 環境設定エディタ',
        'basilisk_tab': 'Basilisk II',
        'sheepshaver_tab': 'Sheepshaver',
        'settings_tab': '設定',
        'save_all': 'すべて保存',
        'reload': '再読み込み',
        'about': 'について',
        'language': '言語',
        'language_section': '言語',
        'restart_required': '言語変更を適用するには再起動が必要です。',
        'default_title_68k': '68k Macintosh',
        'default_title_ppc': 'PPC Macintosh',
        'launch_tooltip': 'クリックしてエミュレータを起動',
        'disk_images': 'ディスクイメージ',
        'disk_image': 'ディスクイメージ',
        'disabled': '無効',
        'new_disk': '新規作成',
        'add': '追加',
        'remove': '削除',
        'create_disk_title': 'ディスクイメージ作成',
        'disk_size_mb': 'サイズ (MB):',
        'disk_create_success': 'ディスクイメージが作成されました。',
        'disk_create_error': 'ディスクイメージの作成に失敗しました。',
        'up': '▲ 上へ',
        'down': '▼ 下へ',
        'cdrom_column': 'CD-ROM',
        'storage_options': 'ストレージオプション',
        'extfs_path': 'ExtFS パス:',
        'rom_file': 'ROM ファイル:',
        'boot_from': '起動:',
        'boot_any': '任意 (Any)',
        'boot_cdrom': 'CD-ROM',
        'boot_drive': 'ブートドライブ:',
        'boot_driver': 'ブートドライバ:',
        'disable_cdrom': 'CD-ROM を無効にする',
        'browse': '参照',
        'display': 'ディスプレイ',
        'screen_mode': '画面モード:',
        'width': '幅:',
        'height': '高さ:',
        'color_depth': '色深度:',
        'frame_skip': 'フレームスキップ:',
        'sdl_render': 'SDL レンダラー:',
        'gfx_acceleration': 'GFX アクセラレーション',
        'scaling': 'スケーリング',
        'nearest_neighbor': 'ニアレストネイバー',
        'integer_scaling': '整数スケーリング',
        'shader_list': 'シェーダー',
        'shader_file': 'シェーダーファイル',
        'shader_params': 'シェーダーパラメータ',
        'configure': '設定',
        'audio': 'オーディオ',
        'audio_output': 'オーディオ出力:',
        'disable_sound': 'サウンドを無効にする',
        'ethernet': 'イーサネット',
        'ethernet_mode': 'イーサネットモード:',
        'ethernet_port': 'イーサネットポート:',
        'none': 'なし',
        'memory': 'メモリ',
        'ram_size': 'RAM サイズ:',
        'cpu': 'CPU',
        'cpu_type': 'CPU タイプ:',
        'model_id': 'モデル ID:',
        'enable_fpu': 'FPU を有効にする',
        'cpu_clock': 'CPU クロック (0=自動):',
        'jit_compiler': 'JIT コンパイラ',
        'enable_jit': 'JIT を有効にする',
        'jit_fpu': 'JIT FPU',
        'jit_68k': 'JIT 68K',
        'cache_size': 'キャッシュサイズ (KB):',
        'lazy_flush': '遅延フラッシュ',
        'inline': 'インライン',
        'debug': 'デバッグ',
        'keyboard': 'キーボード',
        'keyboard_type': 'キーボードタイプ:',
        'use_keycodes': 'キーコードを使用',
        'keycode_file': 'キーコードファイル:',
        'hotkey': 'ホットキー:',
        'swap_opt_cmd': 'Option/Command を交換',
        'mouse': 'マウス',
        'wheel_mode': 'ホイールモード:',
        'wheel_lines': 'ホイール行数:',
        'initial_grab': '初期グラブ',
        'hardware_cursor': 'ハードウェアカーソル',
        'serial_ports': 'シリアルポート',
        'serial_a': 'シリアル A:',
        'serial_b': 'シリアル B:',
        'title_model': 'タイトルとモデル',
        'title': 'タイトル:',
        'model': 'モデル:',
        'miscellaneous': 'その他',
        'no_gui': 'GUI なし',
        'no_clip_conversion': 'クリップボード変換なし',
        'ignore_segv': 'SEGV を無視',
        'ignore_illegal': '不正な命令を無視',
        'idle_wait': 'アイドル待機',
        'time_offset': '時間オフセット',
        'year_offset': '年オフセット:',
        'day_offset': '日オフセット:',
        'encoding': 'エンコーディング',
        'name_encoding': '名前エンコーディング:',
        'performance': 'パフォーマンス',
        'delay': '遅延:',
        'executable': '実行ファイル:',
        'config_file': '設定ファイル:',
        'zap_pram': 'PRAM をクリア',
        'save_settings': '設定を保存',
        'settings_saved': '設定が保存されました!',
        'version': 'バージョン 2.0',
        'copyright': '© 2026 DINKI\'ssTyle',
        'config_saved': '設定が保存され、再読み込みされました!',
        'error': 'エラー',
        'save': '保存',
        'save_as': '名前を付けて保存',
        'launch': '起動',
        'reset': 'リセット',
        'new_profile': '新規プロファイル',
        'profile_name': 'プロファイル名:',
        'default_profile': 'デフォルト',
        'enter_profile_name': '新規プロファイル名を入力してください:',
        'profile_exists': 'この名前のプロファイルは既に存在します。',
        'config_missing_title': '設定が見つかりません',
        'config_missing_msg': '設定ファイルが見つかりません。\n設定タブで設定ファイルのパスを指定してください。',
    },
    'es': {  # Spanish
        'app_title': 'Editor de Preferencias de Sheepshaver y Basilisk II',
        'basilisk_tab': 'Basilisk II',
        'sheepshaver_tab': 'Sheepshaver',
        'settings_tab': 'Configuración',
        'save_all': 'Guardar Todo',
        'reload': 'Recargar',
        'about': 'Acerca de',
        'language': 'Idioma',
        'language_section': 'Idioma',
        'restart_required': 'Se requiere reiniciar para aplicar el cambio de idioma.',
        'default_title_68k': '68k Macintosh',
        'default_title_ppc': 'PPC Macintosh',
        'launch_tooltip': 'Haga clic para iniciar el emulador',
        'disk_images': 'Imágenes de Disco',
        'disk_image': 'Imagen de Disco',
        'disabled': 'Deshabilitado',
        'new_disk': 'Nuevo',
        'add': 'Agregar',
        'remove': 'Eliminar',
        'create_disk_title': 'Crear imagen de disco',
        'disk_size_mb': 'Tamaño (MB):',
        'disk_create_success': 'Imagen de disco creada exitosamente.',
        'disk_create_error': 'Error al crear la imagen de disco.',
        'up': '▲ Arriba',
        'down': '▼ Abajo',
        'cdrom_column': 'CD-ROM',
        'storage_options': 'Opciones de Almacenamiento',
        'extfs_path': 'Ruta ExtFS:',
        'rom_file': 'Archivo ROM:',
        'boot_from': 'Arrancar de:',
        'boot_any': 'Cualquiera',
        'boot_cdrom': 'CD-ROM',
        'boot_drive': 'Unidad de Arranque:',
        'boot_driver': 'Controlador de Arranque:',
        'disable_cdrom': 'Deshabilitar CD-ROM',
        'browse': 'Examinar',
        'display': 'Pantalla',
        'screen_mode': 'Modo de Pantalla:',
        'width': 'Ancho:',
        'height': 'Alto:',
        'color_depth': 'Profundidad de Color:',
        'frame_skip': 'Salto de Cuadros:',
        'sdl_render': 'Renderizador SDL:',
        'gfx_acceleration': 'Aceleración GFX',
        'scaling': 'Escalado',
        'nearest_neighbor': 'Vecino más Cercano',
        'integer_scaling': 'Escalado Entero',
        'shader_list': 'Shaders',
        'shader_file': 'Archivo de Shader',
        'shader_params': 'Parámetros del Shader',
        'configure': 'Configurar',
        'audio': 'Audio',
        'audio_output': 'Salida de Audio:',
        'disable_sound': 'Deshabilitar Sonido',
        'ethernet': 'Ethernet',
        'ethernet_mode': 'Modo Ethernet:',
        'ethernet_port': 'Puerto Ethernet:',
        'none': 'Ninguno',
        'memory': 'Memoria',
        'ram_size': 'Tamaño de RAM:',
        'cpu': 'CPU',
        'cpu_type': 'Tipo de CPU:',
        'model_id': 'ID de Modelo:',
        'enable_fpu': 'Habilitar FPU',
        'cpu_clock': 'Reloj CPU (0=auto):',
        'jit_compiler': 'Compilador JIT',
        'enable_jit': 'Habilitar JIT',
        'jit_fpu': 'JIT FPU',
        'jit_68k': 'JIT 68K',
        'cache_size': 'Tamaño de Caché (KB):',
        'lazy_flush': 'Vaciado Diferido',
        'inline': 'En Línea',
        'debug': 'Depurar',
        'keyboard': 'Teclado',
        'keyboard_type': 'Tipo de Teclado:',
        'use_keycodes': 'Usar Códigos de Tecla',
        'keycode_file': 'Archivo de Códigos:',
        'hotkey': 'Tecla de Acceso:',
        'swap_opt_cmd': 'Intercambiar Option/Command',
        'mouse': 'Ratón',
        'wheel_mode': 'Modo de Rueda:',
        'wheel_lines': 'Líneas de Rueda:',
        'initial_grab': 'Captura Inicial',
        'hardware_cursor': 'Cursor de Hardware',
        'serial_ports': 'Puertos Serie',
        'serial_a': 'Serie A:',
        'serial_b': 'Serie B:',
        'title_model': 'Título y Modelo',
        'title': 'Título:',
        'model': 'Modelo:',
        'miscellaneous': 'Miscelánea',
        'no_gui': 'Sin GUI',
        'no_clip_conversion': 'Sin Conversión de Portapapeles',
        'ignore_segv': 'Ignorar SEGV',
        'ignore_illegal': 'Ignorar Instrucciones Ilegales',
        'idle_wait': 'Espera Inactiva',
        'time_offset': 'Desfase de Tiempo',
        'year_offset': 'Desfase de Año:',
        'day_offset': 'Desfase de Día:',
        'encoding': 'Codificación',
        'name_encoding': 'Codificación de Nombre:',
        'performance': 'Rendimiento',
        'delay': 'Retraso:',
        'executable': 'Ejecutable:',
        'config_file': 'Archivo de Configuración:',
        'zap_pram': 'Borrar PRAM',
        'save_settings': 'Guardar Configuración',
        'settings_saved': '¡Configuración guardada!',
        'version': 'Versión 2.0',
        'copyright': '© 2026 DINKI\'ssTyle',
        'config_saved': '¡Configuración guardada y recargada!',
        'error': 'Error',
        'save': 'Guardar',
        'launch': 'Iniciar',
        'config_missing_title': 'Falta Configuración',
        'config_missing_msg': 'No se encontró archivo de configuración.\nPor favor, especifique la ruta del archivo en la pestaña Configuración.',
    },
}

# Language names for display (in their native language)
LANGUAGE_NAMES = {
    'en': 'English',
    'ko': '한국어',
    'zh': '中文',
    'ja': '日本語',
    'es': 'Español',
}

def tr(key):
    """Get translated string for current language."""
    lang = QSettings('DINKIssTyle', 'EmulatorPrefs').value('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


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
        shaders = []
        
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
                    disks.append((value, 0, False)) # 0 = Disk
                elif key == '#disk':
                    disks.append((value, 0, True))
                elif key == 'cdrom':
                    disks.append((value, 1, False)) # 1 = CD-ROM
                elif key == '#cdrom':
                    disks.append((value, 1, True))
                # Handle multiple shader entries
                elif key == 'shader':
                    shaders.append((value, False))
                elif key == '#shader':
                    shaders.append((value, True))
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
        config['shaders'] = shaders
        return config

    @staticmethod
    def parse_shader_params(params_str: str) -> dict:
        """Parse shader_params string into dictionary."""
        params = {}
        if not params_str:
            return params
        
        for pair in params_str.split(','):
            if '=' in pair:
                key, val = pair.split('=', 1)
                try:
                    params[key.strip()] = float(val.strip())
                except ValueError:
                    continue
        return params

    @staticmethod
    def serialize_shader_params(params: dict) -> str:
        """Serialize dictionary to shader_params string."""
        return ','.join([f"{k}={v}" for k, v in params.items()])
    
    @staticmethod
    def save(filepath: str, config: dict):
        """Save configuration dictionary to file."""
        with open(filepath, 'w') as f:
            # Write disks
            for disk_entry in config.get('disks', []):
                # Handle both old (2-tuple) and new (3-tuple) formats for robustness
                if len(disk_entry) == 3:
                     path, disk_type, disabled = disk_entry
                else:
                     path, disabled = disk_entry
                     disk_type = 0 # Default to disk
                
                prefix = "#" if disabled else ""
                key = "cdrom" if disk_type == 1 else "disk"
                f.write(f"{prefix}{key} {path}\n")

            # Write shaders
            for shader, disabled in config.get('shaders', []):
                if disabled:
                    f.write(f"#shader {shader}\n")
                else:
                    f.write(f"shader {shader}\n")
            
            # Write other settings
            for key, value in config.items():
                if key in ['disks', 'shaders']:
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

# ============================================================================
# Custom Delegates
# ============================================================================

class PathDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        path = index.data()
        if path and isinstance(path, str):
            # Show only .../parent/filename
            if os.path.sep in path:
                parts = path.split(os.path.sep)
                if len(parts) > 2:
                    # Linux/Unix paths start with empty string due to leading /
                    # e.g. /home/user -> ['', 'home', 'user']
                    # We want the last two parts
                    option.text = f"...{os.path.sep}{parts[-2]}{os.path.sep}{parts[-1]}"
                else:
                    option.text = path
            
    def paint(self, painter, option, index):
        # We don't need ElideLeft anymore since we manually shortened it, 
        # but keep ElideMiddle just in case the shortened path is still too long
        option.textElideMode = Qt.ElideMiddle
        super().paint(painter, option, index)


# ============================================================================
# Sub-Tab Widgets
# ============================================================================

class ShaderParamsDialog(QDialog):
    """Dialog to edit shader parameters."""
    
    def __init__(self, parent, shader_path, current_params):
        super().__init__(parent)
        self.shader_path = shader_path
        self.current_params = current_params.copy() # Local copy
        self.setWindowTitle(tr('shader_params'))
        self.setMinimumWidth(400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Scroll area for parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QFormLayout(scroll_content)
        
        self.params_found = self._parse_shader_file()
        self.inputs = {}
        
        if not self.params_found:
            layout.addWidget(QLabel("No parameters found in this shader."))
        else:
            for param in self.params_found:
                name, desc, default, min_val, max_val, step = param
                
                # Get current value or default
                val = self.current_params.get(name, default)
                
                # Create control
                spin = QDoubleSpinBox()
                spin.setRange(min_val, max_val)
                spin.setSingleStep(step)
                spin.setValue(val)
                spin.setDecimals(4) # Support high precision
                
                self.inputs[name] = spin
                self.form_layout.addRow(f"{desc} ({name}):", spin)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton(tr('reset'))
        reset_btn.clicked.connect(self.reset_params)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def _parse_shader_file(self):
        """Parse #pragma parameter lines from shader file."""
        params = []
        if not os.path.exists(self.shader_path):
            return params
            
        import re
        # Regex for: #pragma parameter NAME "Description" DEFAULT MIN MAX STEP
        # Allow loosely formatted floats
        pattern = re.compile(r'#pragma\s+parameter\s+(\w+)\s+"([^"]+)"\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)')
        
        try:
            with open(self.shader_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = pattern.search(line)
                    if match:
                        name = match.group(1)
                        desc = match.group(2)
                        default = float(match.group(3))
                        min_val = float(match.group(4))
                        max_val = float(match.group(5))
                        step = float(match.group(6))
                        params.append((name, desc, default, min_val, max_val, step))
        except Exception as e:
            print(f"Error parsing shader: {e}")
            
        return params
    
    def reset_params(self):
        """Reset all parameters to their default values."""
        if not self.params_found:
            return
            
        for param in self.params_found:
            name, desc, default, min_val, max_val, step = param
            if name in self.inputs:
                self.inputs[name].setValue(default)

    def get_params(self):
        """Return updated parameters dictionary."""
        updates = {}
        for name, spin in self.inputs.items():
            updates[name] = spin.value()
        
        # Merge updates into current_params
        result = self.current_params.copy()
        result.update(updates)
        return result


class CreateDiskDialog(QDialog):
    """Dialog to create a new disk image file."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('create_disk_title'))
        self.setMinimumWidth(400)
        self.file_path = None
        self.size_mb = 100
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Size input
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel(tr('disk_size_mb')))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 4096)
        self.size_spin.setValue(100)
        self.size_spin.setSuffix(" MB")
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept_and_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def accept_and_save(self):
        """Show file save dialog and create the disk image."""
        path, _ = QFileDialog.getSaveFileName(
            self, tr('create_disk_title'),
            "new_disk.img", "Disk Images (*.img *.hfv);;All Files (*)"
        )
        if path:
            self.file_path = path
            self.size_mb = self.size_spin.value()
            self.accept()


class DrivesTab(QWidget):
    """Disk and storage configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Disk Images Group
        disk_group = QGroupBox(tr('disk_images'))
        disk_layout = QVBoxLayout(disk_group)
        
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(3)
        self.disk_table.setHorizontalHeaderLabels([tr('disk_image'), tr('cdrom_column'), tr('disabled')])
        self.disk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.disk_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.disk_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.disk_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.disk_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.disk_table.verticalHeader().setFixedWidth(25)  # Make numbering column wider
        # self.disk_table.setTextElideMode(Qt.ElideLeft) # Handled by delegate
        self.disk_table.setItemDelegateForColumn(0, PathDelegate(self.disk_table))
        
        # self.disk_table.setDragDropMode(QAbstractItemView.InternalMove) # Drag drop rows in TableWidget is complex, relying on buttons
        disk_layout.addWidget(self.disk_table)

        # self.disk_table.setMaximumHeight(100)
        
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton(tr('new_disk'))
        self.btn_add = QPushButton(tr('add'))
        self.btn_remove = QPushButton(tr('remove'))
        self.btn_up = QPushButton(tr('up'))
        self.btn_down = QPushButton(tr('down'))
        
        self.btn_new.clicked.connect(self.new_disk)
        self.btn_add.clicked.connect(self.add_disk)
        self.btn_remove.clicked.connect(self.remove_disk)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addStretch()
        disk_layout.addLayout(btn_layout)
        
        layout.addWidget(disk_group)
        
        # Other Storage Options - Grid Layout
        storage_group = QGroupBox(tr('storage_options'))
        storage_layout = QGridLayout(storage_group)
        
        # Row 0: ExtFS
        storage_layout.addWidget(QLabel(tr('extfs_path')), 0, 0)
        extfs_layout = QHBoxLayout()
        self.extfs_edit = QLineEdit()
        extfs_btn = QPushButton(tr('browse'))
        extfs_btn.clicked.connect(lambda: self.browse_dir(self.extfs_edit))
        extfs_layout.addWidget(self.extfs_edit)
        extfs_layout.addWidget(extfs_btn)
        storage_layout.addLayout(extfs_layout, 0, 1, 1, 5)
        
        # Row 1: ROM
        storage_layout.addWidget(QLabel(tr('rom_file')), 1, 0)
        rom_layout = QHBoxLayout()
        self.rom_edit = QLineEdit()
        rom_btn = QPushButton(tr('browse'))
        rom_btn.clicked.connect(lambda: self.browse_file(self.rom_edit, "ROM Files (*.rom);;All Files (*)"))
        rom_layout.addWidget(self.rom_edit)
        rom_layout.addWidget(rom_btn)
        storage_layout.addLayout(rom_layout, 1, 1, 1, 5)
        
        # Row 2: Boot Drive | Boot From | Disable CD-ROM
        storage_layout.addWidget(QLabel(tr('boot_drive')), 2, 0)
        self.boot_drive = QSpinBox()
        self.boot_drive.setRange(0, 255)
        storage_layout.addWidget(self.boot_drive, 2, 1)
        
        storage_layout.addWidget(QLabel(tr('boot_from')), 2, 2)
        self.boot_from = QComboBox()
        self.boot_from.addItem(tr('boot_any'), 0)
        self.boot_from.addItem(tr('boot_cdrom'), -62)
        storage_layout.addWidget(self.boot_from, 2, 3)
        
        self.no_cdrom = QCheckBox(tr('disable_cdrom'))
        storage_layout.addWidget(self.no_cdrom, 2, 4, 1, 2)
        
        # Set column stretch
        storage_layout.setColumnStretch(1, 1)
        storage_layout.setColumnStretch(3, 1)
        
        layout.addWidget(storage_group)
        layout.addStretch()
    
    def new_disk(self):
        """Create a new disk image file."""
        dialog = CreateDiskDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.file_path:
            try:
                # Create empty file with specified size
                size_bytes = dialog.size_mb * 1024 * 1024
                with open(dialog.file_path, 'wb') as f:
                    f.truncate(size_bytes)
                # Add to disk list (0=Disk)
                self._add_disk_row(dialog.file_path, 0, False)
                QMessageBox.information(self, tr('disk_image'), tr('disk_create_success'))
            except Exception as e:
                QMessageBox.critical(self, tr('error'), f"{tr('disk_create_error')}\n{str(e)}")
    
    def add_disk(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Disk Image",
            "", "Disk Images (*.img *.dmg *.iso *.hfv *.toast);;All Files (*)"
        )
        if path:
            self._add_disk_row(path, 0, False)
            
    def _add_disk_row(self, path, disk_type, disabled):
        row = self.disk_table.rowCount()
        self.disk_table.insertRow(row)
        
        # Path item
        path_item = QTableWidgetItem(path)
        path_item.setFlags(path_item.flags() ^ Qt.ItemIsEditable) # Make read-only
        path_item.setToolTip(path) # Set tooltip
        self.disk_table.setItem(row, 0, path_item)
        
        # CD-ROM Checkbox (Col 1)
        cdrom_chk = QCheckBox()
        cdrom_chk.setChecked(disk_type == 1)
        cdrom_widget = QWidget()
        cdrom_layout = QHBoxLayout(cdrom_widget)
        cdrom_layout.addWidget(cdrom_chk)
        cdrom_layout.setAlignment(Qt.AlignCenter)
        cdrom_layout.setContentsMargins(0, 0, 0, 0)
        self.disk_table.setCellWidget(row, 1, cdrom_widget)
        
        # Disabled Checkbox (Col 2)
        disabled_chk = QCheckBox()
        disabled_chk.setChecked(disabled)
        disabled_widget = QWidget()
        disabled_layout = QHBoxLayout(disabled_widget)
        disabled_layout.addWidget(disabled_chk)
        disabled_layout.setAlignment(Qt.AlignCenter)
        disabled_layout.setContentsMargins(0, 0, 0, 0)
        self.disk_table.setCellWidget(row, 2, disabled_widget)
    
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
        cdrom1 = self.disk_table.cellWidget(row1, 1).findChild(QCheckBox).isChecked()
        disabled1 = self.disk_table.cellWidget(row1, 2).findChild(QCheckBox).isChecked()
        
        path2 = self.disk_table.item(row2, 0).text()
        cdrom2 = self.disk_table.cellWidget(row2, 1).findChild(QCheckBox).isChecked()
        disabled2 = self.disk_table.cellWidget(row2, 2).findChild(QCheckBox).isChecked()
        
        self.disk_table.item(row1, 0).setText(path2)
        self.disk_table.item(row1, 0).setToolTip(path2)
        self.disk_table.cellWidget(row1, 1).findChild(QCheckBox).setChecked(cdrom2)
        self.disk_table.cellWidget(row1, 2).findChild(QCheckBox).setChecked(disabled2)
        
        self.disk_table.item(row2, 0).setText(path1)
        self.disk_table.item(row2, 0).setToolTip(path1)
        self.disk_table.cellWidget(row2, 1).findChild(QCheckBox).setChecked(cdrom1)
        self.disk_table.cellWidget(row2, 2).findChild(QCheckBox).setChecked(disabled1)
    
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
            if len(disk_entry) == 3:
                path, disk_type, disabled = disk_entry
            else:
                path, disabled = disk_entry
                disk_type = 0 # Default to Disk
            self._add_disk_row(path, disk_type, disabled)
        self.extfs_edit.setText(str(config.get('extfs', '')))
        self.rom_edit.setText(str(config.get('rom', '')))
        self.boot_drive.setValue(config.get('bootdrive', 0))
        
        # Set Boot From ComboBox
        bootdriver_val = config.get('bootdriver', 0)
        index = self.boot_from.findData(bootdriver_val)
        if index != -1:
            self.boot_from.setCurrentIndex(index)
        else:
            self.boot_from.setCurrentIndex(0) # Default to Any
            
        self.no_cdrom.setChecked(config.get('nocdrom', False))
    
    def save_config(self, config: dict):
        disks = []
        for i in range(self.disk_table.rowCount()):
            path = self.disk_table.item(i, 0).text()
            # Col 1: CD-ROM
            is_cdrom = self.disk_table.cellWidget(i, 1).findChild(QCheckBox).isChecked()
            disk_type = 1 if is_cdrom else 0
            # Col 2: Disabled
            disabled = self.disk_table.cellWidget(i, 2).findChild(QCheckBox).isChecked()
            disks.append((path, disk_type, disabled))
        
        config['disks'] = disks
        config['extfs'] = self.extfs_edit.text()
        config['rom'] = self.rom_edit.text()
        config['bootdrive'] = self.boot_drive.value()
        config['bootdriver'] = self.boot_from.currentData()
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
        display_group = QGroupBox(tr('display'))
        display_layout = QGridLayout(display_group)
        
        # Row 0: Screen Mode
        display_layout.addWidget(QLabel(tr('screen_mode')), 0, 0)
        self.screen_mode = QComboBox()
        self.screen_mode.addItems(["win", "dga", "full"])
        display_layout.addWidget(self.screen_mode, 0, 1, 1, 5)
        
        # Row 1: Width | Height | Color Depth
        display_layout.addWidget(QLabel(tr('width')), 1, 0)
        self.screen_width = QSpinBox()
        self.screen_width.setRange(320, 3840)
        self.screen_width.setValue(800)
        display_layout.addWidget(self.screen_width, 1, 1)
        
        display_layout.addWidget(QLabel(tr('height')), 1, 2)
        self.screen_height = QSpinBox()
        self.screen_height.setRange(240, 2160)
        self.screen_height.setValue(600)
        display_layout.addWidget(self.screen_height, 1, 3)
        
        display_layout.addWidget(QLabel(tr('color_depth')), 1, 4)
        self.color_depth = QComboBox()
        self.color_depth.addItems(["0 (Default)", "8", "16", "24", "32"])
        display_layout.addWidget(self.color_depth, 1, 5)
        
        # Row 2: Frame Skip | SDL Render (moved from Performance and Renderer)
        display_layout.addWidget(QLabel(tr('frame_skip')), 2, 0)
        self.frameskip = QSpinBox()
        self.frameskip.setRange(0, 60)
        display_layout.addWidget(self.frameskip, 2, 1)
        
        display_layout.addWidget(QLabel(tr('sdl_render')), 2, 2)
        self.sdl_render = QComboBox()
        self.sdl_render.addItems(["software", "opengl", "opengles", "opengles2", "metal"])
        display_layout.addWidget(self.sdl_render, 2, 3, 1, 3)
        
        # GFX Acceleration (Sheepshaver only)
        self.gfx_accel = QCheckBox(tr('gfx_acceleration'))
        if self.emulator_type == 'sheepshaver':
            display_layout.addWidget(self.gfx_accel, 3, 0, 1, 2)
        
        # Set column stretch
        display_layout.setColumnStretch(1, 1)
        display_layout.setColumnStretch(3, 1)
        display_layout.setColumnStretch(5, 1)
        
        layout.addWidget(display_group)
        
        # Scaling Group - Grid layout
        scale_group = QGroupBox(tr('scaling'))
        scale_layout = QGridLayout(scale_group)
        
        # Row 0: Nearest Neighbor | Integer Scaling
        self.scale_nearest = QCheckBox(tr('nearest_neighbor'))
        scale_layout.addWidget(self.scale_nearest, 0, 0)
        
        self.scale_integer = QCheckBox(tr('integer_scaling'))
        scale_layout.addWidget(self.scale_integer, 0, 1)
        
        # Row 1: Magnification
        scale_layout.addWidget(QLabel("Magnification:"), 1, 0)
        self.mag_rate = QDoubleSpinBox()
        self.mag_rate.setRange(0.0, 4.0)
        self.mag_rate.setSingleStep(0.1)
        self.mag_rate.setValue(1.0)
        scale_layout.addWidget(self.mag_rate, 1, 1)
        
        layout.addWidget(scale_group)
        
        # Shader Group
        shader_group = QGroupBox(tr('shader_list'))
        shader_layout = QVBoxLayout(shader_group)
        
        self.shader_table = QTableWidget()
        self.shader_table.setColumnCount(3)
        self.shader_table.setHorizontalHeaderLabels([tr('path'), tr('configure'), tr('disabled')])
        self.shader_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.shader_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.shader_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.shader_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shader_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shader_table.setTextElideMode(Qt.ElideLeft)
        shader_layout.addWidget(self.shader_table)
        
        # Shader Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton(tr('add'))
        add_btn.clicked.connect(self.add_shader)
        
        remove_btn = QPushButton(tr('remove'))
        remove_btn.clicked.connect(self.remove_shader)
        
        up_btn = QPushButton(tr('up'))
        up_btn.clicked.connect(self.move_up)
        
        down_btn = QPushButton(tr('down'))
        down_btn.clicked.connect(self.move_down)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        
        shader_layout.addLayout(btn_layout)
        layout.addWidget(shader_group)

        layout.addStretch()

    def add_shader(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('shader_file'), "", "GLSL Files (*.glsl);;All Files (*)")
        if path:
            self._add_shader_row(path, False)
    
    def _add_shader_row(self, path, disabled):
        row = self.shader_table.rowCount()
        self.shader_table.insertRow(row)
        
        # Path item
        path_item = QTableWidgetItem(path)
        path_item.setFlags(path_item.flags() ^ Qt.ItemIsEditable) # Make read-only
        self.shader_table.setItem(row, 0, path_item)
        
        # Gear Button
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        gear_btn = QPushButton("⚙") 
        gear_btn.setToolTip(tr('configure'))
        gear_btn.setFixedSize(24, 24)
        gear_btn.clicked.connect(self.open_shader_params)
        
        btn_layout.addWidget(gear_btn)
        self.shader_table.setCellWidget(row, 1, btn_widget)
        
        # Checkbox item
        chk = QCheckBox()
        chk.setChecked(disabled)
        # Center the checkbox
        cell_widget = QWidget()
        layout = QHBoxLayout(cell_widget)
        layout.addWidget(chk)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.shader_table.setCellWidget(row, 2, cell_widget)
    
    def open_shader_params(self):
        start_btn = self.sender()
        if not start_btn: return
        
        # Find which row this button belongs to
        row = -1
        for i in range(self.shader_table.rowCount()):
            widget = self.shader_table.cellWidget(i, 1)
            if widget and widget.findChild(QPushButton) == start_btn:
                row = i
                break
        
        if row == -1: return
        
        path = self.shader_table.item(row, 0).text()
        
        # Open dialog
        dialog = ShaderParamsDialog(self, path, self.current_shader_params)
        if dialog.exec_() == QDialog.Accepted:
            # Update params
            self.current_shader_params = dialog.get_params()
    
    def remove_shader(self):
        row = self.shader_table.currentRow()
        if row >= 0:
            self.shader_table.removeRow(row)
    
    def move_up(self):
        row = self.shader_table.currentRow()
        if row > 0:
            self._swap_rows(row, row - 1)
            self.shader_table.setCurrentCell(row - 1, 0)
    
    def move_down(self):
        row = self.shader_table.currentRow()
        if row < self.shader_table.rowCount() - 1 and row >= 0:
            self._swap_rows(row, row + 1)
            self.shader_table.setCurrentCell(row + 1, 0)
            
    def _swap_rows(self, row1, row2):
        # Swap content
        path1 = self.shader_table.item(row1, 0).text()
        # Gear button doesn't store state, just reference to row, but row changes logic handles it by button position.
        # But we must recreate widgets or swap them. QTableWidget doesn't support swapping widgets easily.
        # It's easier to rebuild the rows or just swap values. But Button has connection.
        # Actually reusing the logic:
        chk1 = self.shader_table.cellWidget(row1, 2).findChild(QCheckBox).isChecked()
        chk2 = self.shader_table.cellWidget(row2, 2).findChild(QCheckBox).isChecked()
        
        self.shader_table.item(row1, 0).setText(self.shader_table.item(row2, 0).text())
        self.shader_table.cellWidget(row1, 2).findChild(QCheckBox).setChecked(chk2)
        
        self.shader_table.item(row2, 0).setText(path1)
        self.shader_table.cellWidget(row2, 2).findChild(QCheckBox).setChecked(chk1)
        # Note: Gear button is identical on all rows, no state to swap.
    
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
        
        # Load shaders
        self.shader_table.setRowCount(0)
        for shader_entry in config.get('shaders', []):
            if isinstance(shader_entry, tuple):
                path, disabled = shader_entry
            else:
                path, disabled = shader_entry, False
            self._add_shader_row(path, disabled)
        
        # Load shader params
        params_str = str(config.get('shader_params', ''))
        self.current_shader_params = ConfigParser.parse_shader_params(params_str)
    
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
        
        # Save shaders
        shaders = []
        for i in range(self.shader_table.rowCount()):
            path = self.shader_table.item(i, 0).text()
            disabled = self.shader_table.cellWidget(i, 2).findChild(QCheckBox).isChecked()
            shaders.append((path, disabled))
        config['shaders'] = shaders
        
        # Save shader params
        config['shader_params'] = ConfigParser.serialize_shader_params(self.current_shader_params)


class SoundTab(QWidget):
    """Sound configuration."""
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        sound_group = QGroupBox(tr('audio'))
        sound_layout = QFormLayout(sound_group)
        
        self.no_sound = QCheckBox(tr('disable_sound'))
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
        
        net_group = QGroupBox(tr('ethernet'))
        net_layout = QFormLayout(net_group)
        
        self.ether_mode = QComboBox()
        self.ether_mode.addItems(["slirp", "none", "tap", "sheep_net"])
        self.ether_mode.setEditable(True)
        net_layout.addRow(tr('ethernet_mode'), self.ether_mode)
        
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
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Add Graphics settings
        layout.addWidget(self.graphics_tab)
        
        # Add Sound settings
        layout.addWidget(self.sound_tab)
        
        layout.addStretch()
    
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
        mem_group = QGroupBox(tr('memory'))
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
        mem_layout.addRow(tr('ram_size'), self.ram_size)
        
        layout.addWidget(mem_group)
        
        # CPU Group (Basilisk specific)
        if self.emulator_type == 'basilisk':
            cpu_group = QGroupBox(tr('cpu'))
            cpu_layout = QFormLayout(cpu_group)
            
            self.cpu_type = QComboBox()
            # Combined CPU/FPU options
            # Data format: (cpu_type, fpu_enabled)
            self.cpu_options = [
                ("68020", (2, False)),
                ("68020 with FPU", (2, True)),
                ("68030", (3, False)),
                ("68030 with FPU", (3, True)),
                ("68040 with FPU", (4, True))
            ]
            for name, _ in self.cpu_options:
                self.cpu_type.addItem(name)
            cpu_layout.addRow(tr('cpu_type'), self.cpu_type)
            
            self.model_id = QComboBox()
            models = [
                ("Mac IIci (Mac OS 7.x)", 5),
                ("Quadra 900 (Mac OS 8.x)", 14)
            ]
            for name, mid in models:
                self.model_id.addItem(name, mid)
            cpu_layout.addRow(tr('model_id'), self.model_id)
            
            # self.fpu_enabled = QCheckBox(tr('enable_fpu')) # Merged into CPU select
            # cpu_layout.addRow("", self.fpu_enabled)
            
            layout.addWidget(cpu_group)
        
        # Sheepshaver CPU options
        if self.emulator_type == 'sheepshaver':
            cpu_group = QGroupBox(tr('cpu'))
            cpu_layout = QFormLayout(cpu_group)
            
            self.cpu_clock = QSpinBox()
            self.cpu_clock.setRange(0, 10000)
            cpu_layout.addRow(tr('cpu_clock'), self.cpu_clock)
            
            layout.addWidget(cpu_group)
        
        # JIT Group - 2 column layout
        jit_group = QGroupBox(tr('jit_compiler'))
        jit_layout = QGridLayout(jit_group)
        
        self.jit_enabled = QCheckBox(tr('enable_jit'))
        
        if self.emulator_type == 'basilisk':
            self.jit_fpu = QCheckBox(tr('jit_fpu'))
            self.jit_lazy_flush = QCheckBox(tr('lazy_flush'))
            self.jit_inline = QCheckBox(tr('inline'))
            self.jit_debug = QCheckBox(tr('debug'))
            
            self.jit_cache_size = QSpinBox()
            self.jit_cache_size.setRange(0, 65536)
            self.jit_cache_size.setValue(8192)
            
            # Row 0: Enable JIT | JIT FPU
            jit_layout.addWidget(self.jit_enabled, 0, 0)
            jit_layout.addWidget(self.jit_fpu, 0, 1)
            # Row 1: Cache Size label | Cache Size spinbox | Lazy Flush
            jit_layout.addWidget(QLabel(tr('cache_size')), 1, 0)
            jit_layout.addWidget(self.jit_cache_size, 1, 1)
            # Row 2: Lazy Flush | Inline
            jit_layout.addWidget(self.jit_lazy_flush, 2, 0)
            jit_layout.addWidget(self.jit_inline, 2, 1)
            # Row 3: Debug
            jit_layout.addWidget(self.jit_debug, 3, 0)
        
        if self.emulator_type == 'sheepshaver':
            self.jit_68k = QCheckBox(tr('jit_68k'))
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
            fpu = config.get('fpu', True)
            
            # Find matching index in combined options
            target_idx = 3 # Default to 68030 with FPU
            for idx, (_, (c_val, f_val)) in enumerate(self.cpu_options):
                if c_val == cpu and f_val == fpu:
                    target_idx = idx
                    break
            self.cpu_type.setCurrentIndex(target_idx)
            
            model_val = config.get('modelid', 5)
            index = self.model_id.findData(model_val)
            if index >= 0:
                self.model_id.setCurrentIndex(index)
            else:
                self.model_id.setCurrentIndex(0) # Default to first item
                
            # self.fpu_enabled.setChecked(config.get('fpu', True))
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
            idx = self.cpu_type.currentIndex()
            if 0 <= idx < len(self.cpu_options):
                cpu_val, fpu_val = self.cpu_options[idx][1]
                config['cpu'] = cpu_val
                config['fpu'] = fpu_val
            
            config['modelid'] = self.model_id.currentData()
            # config['fpu'] = self.fpu_enabled.isChecked()
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
        km_group = QGroupBox(tr('keyboard'))
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
        kb_layout.addRow(tr('keyboard_type'), self.kb_type)
        
        self.keycodes = QCheckBox(tr('use_keycodes'))
        kb_layout.addRow("", self.keycodes)
        
        keycode_layout = QHBoxLayout()
        self.keycode_file = QLineEdit()
        keycode_btn = QPushButton(tr('browse'))
        keycode_btn.clicked.connect(self.browse_keycode_file)
        keycode_layout.addWidget(self.keycode_file)
        keycode_layout.addWidget(keycode_btn)
        kb_layout.addRow(tr('keycode_file'), keycode_layout)
        
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
        kb_layout.addRow(tr('hotkey'), self.hotkey)
        
        self.swap_opt_cmd = QCheckBox(tr('swap_opt_cmd'))
        kb_layout.addRow("", self.swap_opt_cmd)
        
        layout.addWidget(km_group)
        
        # Mouse Group - 2 column layout
        mouse_group = QGroupBox(tr('mouse'))
        mouse_layout = QGridLayout(mouse_group)
        
        # Row 0: Wheel Mode | Wheel Lines
        mouse_layout.addWidget(QLabel(tr('wheel_mode')), 0, 0)
        self.mouse_wheel_mode = QComboBox()
        self.mouse_wheel_mode.addItem("Page Up/Down", 0)
        self.mouse_wheel_mode.addItem("Cursor Up/Down", 1)
        mouse_layout.addWidget(self.mouse_wheel_mode, 0, 1)
        
        mouse_layout.addWidget(QLabel(tr('wheel_lines')), 0, 2)
        self.mouse_wheel_lines = QSpinBox()
        self.mouse_wheel_lines.setRange(1, 20)
        mouse_layout.addWidget(self.mouse_wheel_lines, 0, 3)
        
        # Row 1: Checkboxes
        self.init_grab = QCheckBox(tr('initial_grab'))
        mouse_layout.addWidget(self.init_grab, 1, 0, 1, 2)
        
        if self.emulator_type == 'sheepshaver':
            self.hard_cursor = QCheckBox(tr('hardware_cursor'))
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
        serial_group = QGroupBox(tr('serial_ports'))
        serial_layout = QGridLayout(serial_group)
        
        serial_layout.addWidget(QLabel(tr('serial_a')), 0, 0)
        self.serial_a = QLineEdit()
        self.serial_a.setPlaceholderText("/dev/ttyS0")
        serial_layout.addWidget(self.serial_a, 0, 1)
        
        serial_layout.addWidget(QLabel(tr('serial_b')), 0, 2)
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
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Add Input settings
        layout.addWidget(self.input_tab)
        
        # Add Serial settings
        layout.addWidget(self.serial_tab)
        
        layout.addStretch()
    
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
        title_group = QGroupBox(tr('title_model'))
        title_layout = QGridLayout(title_group)
        
        # Title
        title_layout.addWidget(QLabel(tr('title')), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("My Macintosh")
        title_layout.addWidget(self.title_edit, 0, 1)
        
        # Model dropdown
        title_layout.addWidget(QLabel(tr('model')), 0, 2)
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
        misc_group = QGroupBox(tr('miscellaneous'))
        misc_layout = QGridLayout(misc_group)
        
        self.no_gui = QCheckBox(tr('no_gui'))
        self.no_clip_conversion = QCheckBox(tr('no_clip_conversion'))
        self.ignore_segv = QCheckBox(tr('ignore_segv'))
        self.idle_wait = QCheckBox(tr('idle_wait'))
        
        if self.emulator_type == 'sheepshaver':
            self.ignore_illegal = QCheckBox(tr('ignore_illegal'))
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
        time_group = QGroupBox(tr('time_offset'))
        time_layout = QGridLayout(time_group)
        
        time_layout.addWidget(QLabel(tr('year_offset')), 0, 0)
        self.year_offset = QSpinBox()
        self.year_offset.setRange(-100, 100)
        time_layout.addWidget(self.year_offset, 0, 1)
        
        time_layout.addWidget(QLabel(tr('day_offset')), 0, 2)
        self.day_offset = QSpinBox()
        self.day_offset.setRange(-365, 365)
        time_layout.addWidget(self.day_offset, 0, 3)
        
        # Set column stretch for even distribution
        time_layout.setColumnStretch(1, 1)
        time_layout.setColumnStretch(3, 1)
        
        layout.addWidget(time_group)
        
        # Encoding
        enc_group = QGroupBox(tr('encoding'))
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
            
        enc_layout.addRow(tr('name_encoding'), self.name_encoding)
        
        layout.addWidget(enc_group)
        
        if self.emulator_type == 'basilisk':
            delay_group = QGroupBox(tr('performance'))
            delay_layout = QFormLayout(delay_group)
            
            self.delay = QSpinBox()
            self.delay.setRange(0, 1000)
            delay_layout.addRow(tr('delay'), self.delay)
            
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
    power_clicked = Signal()
    save_clicked = Signal()
    reload_clicked = Signal()
    config_changed = Signal(str) # Path to selected config
    
    def __init__(self, emulator_type: str):
        super().__init__()
        self.emulator_type = emulator_type
        self.init_ui()
    
    def init_ui(self):
        cfg = LEFT_PANEL_CONFIG
        
        # Set panel background color if specified
        if cfg.get('panel_background_color'):
            self.setAutoFillBackground(True)
            panel_palette = self.palette()
            panel_palette.setColor(self.backgroundRole(), QColor(cfg['panel_background_color']))
            self.setPalette(panel_palette)
        
        # Main layout - no spacing between rows
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(
            cfg['panel_margin_left'],
            cfg['panel_margin_top'],
            cfg['panel_margin_right'],
            cfg['panel_margin_bottom']
        )
        
        # ==================== Row 0: Config Selector ====================
        row0 = QWidget()
        row0_layout = QVBoxLayout(row0)
        row0_layout.setContentsMargins(0, 5, 0, 5)
        
        self.config_selector = QComboBox()
        self.config_selector.setToolTip(tr('settings_tab'))
        self.config_selector.currentIndexChanged.connect(self._on_config_changed)
        
        row0_layout.addWidget(self.config_selector)
        layout.addWidget(row0)
        
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
                color: {cfg['title_color']};
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
        self.power_btn.setToolTip(tr('launch_tooltip'))
        
        # Load power switch images
        self.pixmap_normal = None
        self.pixmap_pushed = None
        
        power_img_name = "68k_pwrsw.png" if self.emulator_type == 'basilisk' else "ppc_pwrsw.png"
        power_img_path = os.path.join(os.path.dirname(__file__), 'res', power_img_name)
        
        pushed_img_name = "68k_pwrsw_pushed.png" if self.emulator_type == 'basilisk' else "ppc_pwrsw_pushed.png"
        pushed_img_path = os.path.join(os.path.dirname(__file__), 'res', pushed_img_name)
        
        if os.path.exists(power_img_path):
            self.pixmap_normal = QPixmap(power_img_path).scaled(cfg['power_btn_width'], cfg['power_btn_height'], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.power_btn.setPixmap(self.pixmap_normal)
            
        if os.path.exists(pushed_img_path):
            self.pixmap_pushed = QPixmap(pushed_img_path).scaled(cfg['power_btn_width'], cfg['power_btn_height'], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        if not self.pixmap_normal:
            self.power_btn.setText("⏻ Start")
            self.power_btn.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    border-radius: 10px;
                }
            """)
        
        self.power_btn.clicked.connect(self.animate_and_emit_power)
        
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
    
    def animate_and_emit_power(self):
        if self.pixmap_pushed:
            self.power_btn.setPixmap(self.pixmap_pushed)
            QTimer.singleShot(1000, self.reset_power_button)
        self.power_clicked.emit()

    def reset_power_button(self):
        if self.pixmap_normal:
            self.power_btn.setPixmap(self.pixmap_normal)

    def _get_default_title(self):
        if self.emulator_type == 'basilisk':
            return tr('default_title_68k')
        else:
            return tr('default_title_ppc')
    
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
                return
        
        # Clear the icon if not found or invalid
        self.icon_label.clear()

    def _on_config_changed(self, index):
        if index >= 0:
            path = self.config_selector.itemData(index)
            if path:
                self.config_changed.emit(path)

    def populate_configs(self, configs, current_path=None):
        """Populate config selector with list of (name, path) tuples."""
        self.config_selector.blockSignals(True)
        self.config_selector.clear()
        
        for name, path in configs:
            self.config_selector.addItem(name, path)
            
        if current_path:
            index = self.config_selector.findData(current_path)
            if index >= 0:
                self.config_selector.setCurrentIndex(index)
        
        self.config_selector.blockSignals(False)


# ============================================================================
# Emulator Tab (contains sub-tabs)
# ============================================================================

class EmulatorTab(QWidget):
    """Container for emulator-specific sub-tabs."""
    
    from qtpy.QtCore import Signal
    launch_requested = Signal()
    save_requested = Signal()
    save_as_requested = Signal()
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
        # self.left_panel.config_changed.connect(self._on_config_changed) # Handled by PrefsEditor
        main_layout.addWidget(self.left_panel)
        
        # Right Panel (sub-tabs)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                border: none;
                padding: 6px;
                min-width: 30px;
                min-height: 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                qproperty-iconSize: 24px 24px;
            }
            QTabBar::tab:selected {
                background: transparent;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
                background: transparent;
            }
            QTabBar::tab:!selected:hover {
                background: palette(light);
            }
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
        self.sub_tabs.setIconSize(QSize(32, 32))
        
        # Adjust tabs to fit width
        # self.sub_tabs.setUsesScrollButtons(True) 
        
        right_layout.addWidget(self.sub_tabs)
        main_layout.addWidget(right_widget, 1)

    def _on_config_changed(self, path):
        """Handle config selection change from LeftPanel."""
        # Signal parent to load this config
        # Store it temporarily? Parent (PrefsEditor) handles loading.
        pass # Signal connected in PrefsEditor
    
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
    
    from qtpy.QtCore import Signal
    settings_saved = Signal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings('DINKIssTyle', 'EmulatorPrefs')
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Language Settings
        lang_group = QGroupBox(tr('language_section'))
        lang_layout = QFormLayout(lang_group)
        
        self.language_combo = QComboBox()
        for lang_code, lang_name in LANGUAGE_NAMES.items():
            self.language_combo.addItem(lang_name, lang_code)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addRow(tr('language') + ":", self.language_combo)
        
        self.restart_label = QLabel(tr('restart_required'))
        self.restart_label.setStyleSheet("color: #E07020; font-style: italic;")
        self.restart_label.hide()
        lang_layout.addRow("", self.restart_label)
        
        layout.addWidget(lang_group)
        
        # Basilisk II Settings
        basilisk_group = QGroupBox("Basilisk II")
        basilisk_layout = QFormLayout(basilisk_group)
        
        basilisk_exe_layout = QHBoxLayout()
        self.basilisk_exe = QLineEdit()
        basilisk_exe_btn = QPushButton(tr('browse'))
        basilisk_exe_btn.clicked.connect(lambda: self.browse_exe(self.basilisk_exe))
        basilisk_exe_layout.addWidget(self.basilisk_exe)
        basilisk_exe_layout.addWidget(basilisk_exe_btn)
        basilisk_layout.addRow(tr('executable'), basilisk_exe_layout)
        
        basilisk_cfg_layout = QHBoxLayout()
        self.basilisk_cfg = QLineEdit()
        basilisk_cfg_btn = QPushButton(tr('browse'))
        basilisk_cfg_btn.clicked.connect(lambda: self.browse_file(self.basilisk_cfg))
        basilisk_cfg_layout.addWidget(self.basilisk_cfg)
        basilisk_cfg_layout.addWidget(basilisk_cfg_btn)
        basilisk_layout.addRow(tr('config_file'), basilisk_cfg_layout)
        
        zap_basilisk_btn = QPushButton(tr('zap_pram'))
        zap_basilisk_btn.clicked.connect(lambda: self.zap_pram('basilisk'))
        basilisk_layout.addRow("", zap_basilisk_btn)
        
        layout.addWidget(basilisk_group)
        
        # Sheepshaver Settings
        sheepshaver_group = QGroupBox("Sheepshaver")
        sheepshaver_layout = QFormLayout(sheepshaver_group)
        
        sheepshaver_exe_layout = QHBoxLayout()
        self.sheepshaver_exe = QLineEdit()
        sheepshaver_exe_btn = QPushButton(tr('browse'))
        sheepshaver_exe_btn.clicked.connect(lambda: self.browse_exe(self.sheepshaver_exe))
        sheepshaver_exe_layout.addWidget(self.sheepshaver_exe)
        sheepshaver_exe_layout.addWidget(sheepshaver_exe_btn)
        sheepshaver_layout.addRow(tr('executable'), sheepshaver_exe_layout)
        
        sheepshaver_cfg_layout = QHBoxLayout()
        self.sheepshaver_cfg = QLineEdit()
        sheepshaver_cfg_btn = QPushButton(tr('browse'))
        sheepshaver_cfg_btn.clicked.connect(lambda: self.browse_file(self.sheepshaver_cfg))
        sheepshaver_cfg_layout.addWidget(self.sheepshaver_cfg)
        sheepshaver_cfg_layout.addWidget(sheepshaver_cfg_btn)
        sheepshaver_layout.addRow(tr('config_file'), sheepshaver_cfg_layout)
        
        zap_sheepshaver_btn = QPushButton(tr('zap_pram'))
        zap_sheepshaver_btn.clicked.connect(lambda: self.zap_pram('sheepshaver'))
        sheepshaver_layout.addRow("", zap_sheepshaver_btn)
        
        layout.addWidget(sheepshaver_group)
        
        # Save button
        save_btn = QPushButton(tr('save_settings'))
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
        
        # Basilisk Config
        b_cfg = self.settings.value('basilisk/cfg', '')
        if not b_cfg:
             # Try default
             default_b = os.path.expanduser("~/.basilisk_ii_prefs")
             if os.path.exists(default_b):
                 b_cfg = default_b
        self.basilisk_cfg.setText(b_cfg)

        self.sheepshaver_exe.setText(self.settings.value('sheepshaver/exe', ''))
        
        # SheepShaver Config
        s_cfg = self.settings.value('sheepshaver/cfg', '')
        if not s_cfg:
             # Try default
             default_s = os.path.expanduser("~/.sheepshaver_prefs")
             if os.path.exists(default_s):
                 s_cfg = default_s
        self.sheepshaver_cfg.setText(s_cfg)
        
        # Load language setting
        current_lang = self.settings.value('language', 'en')
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def _on_language_changed(self, index):
        """Handle language change."""
        lang_code = self.language_combo.currentData()
        current_lang = self.settings.value('language', 'en')
        if lang_code != current_lang:
            self.settings.setValue('language', lang_code)
            self.restart_label.show()
    
    def save_settings(self):
        self.settings.setValue('basilisk/exe', self.basilisk_exe.text())
        self.settings.setValue('basilisk/cfg', self.basilisk_cfg.text())
        self.settings.setValue('sheepshaver/exe', self.sheepshaver_exe.text())
        self.settings.setValue('sheepshaver/cfg', self.sheepshaver_cfg.text())
        self.settings.setValue('sheepshaver/cfg', self.sheepshaver_cfg.text())
        QMessageBox.information(self, tr('settings_tab'), tr('settings_saved'))
        self.settings_saved.emit()
    
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

class ProfileManagerDialog(QDialog):
    """Dialog for managing profiles (rename, delete)."""
    
    def __init__(self, parent=None, active_emulator='basilisk', base_dirs=None):
        super().__init__(parent)
        self.active_emulator = active_emulator
        self.base_dirs = base_dirs or {}
        self.setWindowTitle(tr('management'))
        self.setMinimumSize(400, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Filter Buttons
        filter_layout = QHBoxLayout()
        self.btn_group = QButtonGroup(self)
        
        self.btn_all = QPushButton(tr('filter_all'))
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_group.addButton(self.btn_all, 0)
        filter_layout.addWidget(self.btn_all)
        
        self.btn_basilisk = QPushButton(tr('basilisk_tab'))
        self.btn_basilisk.setCheckable(True)
        self.btn_group.addButton(self.btn_basilisk, 1)
        filter_layout.addWidget(self.btn_basilisk)
        
        self.btn_sheepshaver = QPushButton(tr('sheepshaver_tab'))
        self.btn_sheepshaver.setCheckable(True)
        self.btn_group.addButton(self.btn_sheepshaver, 2)
        filter_layout.addWidget(self.btn_sheepshaver)
        
        # Select current emulator filter by default
        if self.active_emulator == 'basilisk':
            self.btn_basilisk.setChecked(True)
        elif self.active_emulator == 'sheepshaver':
             self.btn_sheepshaver.setChecked(True)

        self.btn_group.buttonClicked.connect(self.refresh_list)
        layout.addLayout(filter_layout)
        
        # Profile List
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_rename = QPushButton(tr('rename'))
        self.btn_rename.clicked.connect(self.rename_profile)
        btn_layout.addWidget(self.btn_rename)
        
        self.btn_duplicate = QPushButton(tr('duplicate'))
        self.btn_duplicate.clicked.connect(self.duplicate_profile)
        btn_layout.addWidget(self.btn_duplicate)
        
        self.btn_delete = QPushButton(tr('delete'))
        self.btn_delete.clicked.connect(self.delete_profile)
        btn_layout.addWidget(self.btn_delete)
        
        btn_close = QPushButton(tr('close'))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        self.refresh_list()
        
    def refresh_list(self):
        """Scan and populate list based on filter."""
        self.list_widget.clear()
        filter_id = self.btn_group.checkedId() # 0=All, 1=Basilisk, 2=Sheepshaver
        
        configs = []
        
        # Helper to scan a type
        def scan(emu_type):
            cfg_path_setting = self.base_dirs.get(emu_type)
            if not cfg_path_setting: return []
            
            directory = os.path.dirname(cfg_path_setting)
            if not os.path.exists(directory): return []
            
            prefix = ".basilisk_ii_" if emu_type == 'basilisk' else ".sheepshaver_"
            suffix = "_prefs"
            default_file = ".basilisk_ii_prefs" if emu_type == 'basilisk' else ".sheepshaver_prefs"
            
            found = []
            try:
                for f in os.listdir(directory):
                    full_path = os.path.join(directory, f)
                    display_name = ""
                    
                    if f == default_file:
                        display_name = tr('default_profile')
                    elif f.startswith(prefix) and f.endswith(suffix):
                        middle = f[len(prefix):-len(suffix)]
                        display_name = middle.replace("_", " ")
                    
                    if display_name:
                         # Append type to display name if showing all
                         label = f"[{tr('basilisk_tab' if emu_type == 'basilisk' else 'sheepshaver_tab')}] {display_name}"
                         found.append((label, full_path, emu_type, f))
            except Exception:
                pass
            return found

        if filter_id == 0 or filter_id == 1:
            configs.extend(scan('basilisk'))
        
        if filter_id == 0 or filter_id == 2:
            configs.extend(scan('sheepshaver'))
            
        configs.sort(key=lambda x: x[0])
        
        for label, path, emu, filename in configs:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, path)
            item.setData(Qt.UserRole + 1, emu)
            item.setData(Qt.UserRole + 2, filename)
            self.list_widget.addItem(item)
            
    def rename_profile(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        old_path = item.data(Qt.UserRole)
        emu_type = item.data(Qt.UserRole + 1)
        original_filename = item.data(Qt.UserRole + 2)
        
        # Don't rename default
        if "prefs" == original_filename or original_filename.startswith(".basilisk_ii_prefs") or original_filename == ".sheepshaver_prefs": 
             # Check exact default names
             if original_filename in [".basilisk_ii_prefs", ".sheepshaver_prefs"]:
                QMessageBox.warning(self, tr('rename'), "Cannot rename default profile.")
                return

        # Pre-fill with current display name
        current_display_name = item.text().split("] ", 1)[-1]
        name, ok = QInputDialog.getText(self, tr('rename_profile'), tr('enter_new_name'), QLineEdit.Normal, current_display_name)
        if ok and name:
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.', '(', ')')).strip()
            if not safe_name: return
            
            file_name_part = safe_name.replace(" ", "_")
            prefix = ".basilisk_ii_" if emu_type == 'basilisk' else ".sheepshaver_"
            new_filename = f"{prefix}{file_name_part}_prefs"
            
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_filename)
            
            if os.path.exists(new_path):
                QMessageBox.warning(self, tr('rename'), tr('profile_exists'))
                return
                
            try:
                os.rename(old_path, new_path)
                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, tr('error'), str(e))

    def duplicate_profile(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        old_path = item.data(Qt.UserRole)
        emu_type = item.data(Qt.UserRole + 1)
        original_filename = item.data(Qt.UserRole + 2)
        
        # Get current display name for default naming
        current_display_name = item.text().split("] ", 1)[-1]
        default_new_name = current_display_name + tr('copy_suffix')
        
        name, ok = QInputDialog.getText(self, tr('duplicate'), tr('enter_profile_name'), QLineEdit.Normal, default_new_name)
        
        if ok and name:
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.', '(', ')')).strip()
            if not safe_name: return
            
            file_name_part = safe_name.replace(" ", "_")
            prefix = ".basilisk_ii_" if emu_type == 'basilisk' else ".sheepshaver_"
            new_filename = f"{prefix}{file_name_part}_prefs"
            
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_filename)
            
            if os.path.exists(new_path):
                QMessageBox.warning(self, tr('duplicate'), tr('profile_exists'))
                # Suggest recursive suffix? For now just stop.
                return
                
            try:
                # Copy file content
                new_content_lines = []
                xpram_source = None
                xpram_target = None
                
                with open(old_path, 'r') as f_src:
                    for line in f_src:
                        # Check for xpram
                        if line.strip().startswith('xpram '):
                            parts = line.strip().split(' ', 1)
                            if len(parts) > 1:
                                xpram_source = parts[1]
                                # Determine new xpram path
                                # Convention: if prefs is .basilisk_ii_NAME_prefs, xpram is .basilisk_ii_NAME_xpram
                                if original_filename.endswith("prefs"):
                                    new_xpram_filename = new_filename.replace("_prefs", "_xpram")
                                    xpram_target = os.path.join(directory, new_xpram_filename)
                                    line = f"xpram {xpram_target}\n"
                        new_content_lines.append(line)

                # Write new config
                with open(new_path, 'w') as f_dst:
                    f_dst.writelines(new_content_lines)
                
                # Copy xpram file if it exists and we determined a target
                if xpram_source and xpram_target and os.path.exists(xpram_source):
                     try:
                         import shutil
                         shutil.copy2(xpram_source, xpram_target)
                     except Exception as ex:
                         print(f"Failed to copy xpram: {ex}")

                self.refresh_list()
            except Exception as e:
                QMessageBox.critical(self, tr('error'), str(e))

    def delete_profile(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        path = item.data(Qt.UserRole)
        label = item.text()
        original_filename = item.data(Qt.UserRole + 2)
        
        if original_filename in [".basilisk_ii_prefs", ".sheepshaver_prefs"]:
            QMessageBox.warning(self, tr('delete'), "Cannot delete default profile.")
            return

        # Double confirmation
        ret = QMessageBox.question(self, tr('confirm_delete'), tr('delete_msg1').format(label), QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            ret2 = QMessageBox.question(self, tr('confirm_delete'), tr('delete_msg2'), QMessageBox.Yes | QMessageBox.No)
            if ret2 == QMessageBox.Yes:
                try:
                    # Check for xpram to delete
                    xpram_to_delete = None
                    try:
                        with open(path, 'r') as f:
                             for line in f:
                                 if line.strip().startswith('xpram '):
                                     parts = line.strip().split(' ', 1)
                                     if len(parts) > 1:
                                         candidate = parts[1]
                                         # Only delete if it looks like a managed xpram for this profile
                                         # Construct expected name
                                         expected_xpram_name = original_filename.replace("_prefs", "_xpram")
                                         if os.path.basename(candidate) == expected_xpram_name:
                                             xpram_to_delete = candidate
                                         break
                    except:
                        pass

                    os.remove(path)
                    
                    if xpram_to_delete and os.path.exists(xpram_to_delete):
                        os.remove(xpram_to_delete)
                        
                    self.refresh_list()
                except Exception as e:
                    QMessageBox.critical(self, tr('error'), str(e))

class PrefsEditor(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('DINKIssTyle', 'EmulatorPrefs')
        self.active_configs = {} # Store active config path for each emulator
        self.init_ui()
        self.load_settings_and_profiles()
    
    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
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
        self.settings_tab.settings_saved.connect(self.scan_and_load_initial_profiles)
        
        # Connect power button signals
        self.basilisk_tab.launch_requested.connect(lambda: self.launch_emulator('basilisk'))
        self.sheepshaver_tab.launch_requested.connect(lambda: self.launch_emulator('sheepshaver'))
        
        # Connect config changed signals
        self.basilisk_tab.left_panel.config_changed.connect(lambda p: self.switch_profile('basilisk', p))
        self.sheepshaver_tab.left_panel.config_changed.connect(lambda p: self.switch_profile('sheepshaver', p))

        # Connect save and reload signals
        # Connect save and reload signals
        self.basilisk_tab.save_requested.connect(self.save_current_config)
        self.basilisk_tab.reload_requested.connect(lambda: self.load_configs())
        self.sheepshaver_tab.save_requested.connect(self.save_current_config)
        self.sheepshaver_tab.reload_requested.connect(lambda: self.load_configs())
        
        self.main_tabs.addTab(self.basilisk_tab, get_icon("68k.png"), tr('basilisk_tab'))
        self.main_tabs.addTab(self.sheepshaver_tab, get_icon("ppc.png"), tr('sheepshaver_tab'))
        self.main_tabs.addTab(self.settings_tab, get_icon("settings.png"), tr('settings_tab'))
        
        # About button in top-right corner of tab bar
        # Top-right corner buttons: Save All, Reload, About
        top_right_widget = QWidget()
        top_right_layout = QHBoxLayout(top_right_widget)
        top_right_layout.setAlignment(Qt.AlignVCenter)
        top_right_layout.setContentsMargins(0, 2, 2, 2)
        top_right_layout.setSpacing(2)
        
        btn_height = 26
        
        # Save All Button
        save_btn = QPushButton(tr('save'))
        save_btn.setIcon(get_icon("save.png"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(btn_height)
        save_btn.clicked.connect(self.save_current_config)
        top_right_layout.addWidget(save_btn)
        
        # Save As Button
        save_as_btn = QPushButton(tr('save_as'))
        save_as_btn.setIcon(get_icon("save_as.png")) # Assuming icon exists or fallback
        save_as_btn.setCursor(Qt.PointingHandCursor)
        save_as_btn.setFixedHeight(btn_height)
        save_as_btn.clicked.connect(self.save_as_config)
        top_right_layout.addWidget(save_as_btn)
        
        # Management Button
        mgmt_btn = QPushButton(tr('management'))
        mgmt_btn.setIcon(get_icon("fav.png")) # Reusing settings icon or generic
        mgmt_btn.setCursor(Qt.PointingHandCursor)
        mgmt_btn.setFixedHeight(btn_height)
        mgmt_btn.clicked.connect(self.open_management_dialog)
        top_right_layout.addWidget(mgmt_btn)
        
        # About Button
        about_btn = QPushButton(tr('about'))
        about_btn.setIcon(get_icon("about.png"))
        about_btn.setCursor(Qt.PointingHandCursor)
        about_btn.setFixedHeight(btn_height)
        about_btn.clicked.connect(self.show_about)
        top_right_layout.addWidget(about_btn)
        
        self.main_tabs.setCornerWidget(top_right_widget, Qt.TopRightCorner)

    def load_settings_and_profiles(self):
        """Load global settings and then scan/load profiles."""
        self.settings_tab.load_settings()
        self.scan_and_load_initial_profiles()
        self.check_initial_configuration()

    def check_initial_configuration(self):
        """Check if any configuration is valid on startup, else warn."""
        # Check if we have active configs for either
        basilisk_ok = self.active_configs.get('basilisk') and os.path.exists(self.active_configs['basilisk'])
        sheepshaver_ok = self.active_configs.get('sheepshaver') and os.path.exists(self.active_configs['sheepshaver'])
        
        if not basilisk_ok and not sheepshaver_ok:
             QMessageBox.warning(self, tr('config_missing_title'), tr('config_missing_msg'))
             self.main_tabs.setCurrentIndex(2) # Switch to Settings tab


    def open_management_dialog(self):
        """Open the profile management dialog."""
        idx = self.main_tabs.currentIndex()
        active_emu = 'basilisk' if idx == 0 else 'sheepshaver' if idx == 1 else 'basilisk'
        
        # Pass base directories to dialog to know where to scan
        base_dirs = {
            'basilisk': self.settings_tab.basilisk_cfg.text(),
            'sheepshaver': self.settings_tab.sheepshaver_cfg.text()
        }
        
        dlg = ProfileManagerDialog(self, active_emu, base_dirs)
        dlg.exec_()
        
        # Refresh profiles after closing management
        self.scan_and_load_initial_profiles()
    
    def scan_and_load_initial_profiles(self):
        """Scan profiles for both emulators and load the initial one."""
        # Load last used profiles
        last_basilisk = self.settings_tab.settings.value("last_profile_basilisk", "")
        last_sheepshaver = self.settings_tab.settings.value("last_profile_sheepshaver", "")
        
        if last_basilisk and os.path.exists(last_basilisk):
            self.active_configs['basilisk'] = last_basilisk
            
        if last_sheepshaver and os.path.exists(last_sheepshaver):
            self.active_configs['sheepshaver'] = last_sheepshaver

        for emu_type in ['basilisk', 'sheepshaver']:
            self.refresh_profiles(emu_type)
            # Active config is set during refresh if not already set, or reused
            self.load_config_for_emulator(emu_type)

    def refresh_profiles(self, emu_type):
        """Scan directory for profiles and update LeftPanel."""
        cfg_path_setting = self.settings_tab.basilisk_cfg.text() if emu_type == 'basilisk' else self.settings_tab.sheepshaver_cfg.text()
        
        configs = []
        if cfg_path_setting:
            directory = os.path.dirname(cfg_path_setting)
            base_name = os.path.basename(cfg_path_setting)
            
            # Determine prefix and suffix pattern
            # Default is usually .basilisk_ii_prefs or .sheepshaver_prefs
            # Custom is .basilisk_ii_NAME_prefs
            
            prefix = ".basilisk_ii_" if emu_type == 'basilisk' else ".sheepshaver_"
            suffix = "_prefs"
            
            if os.path.exists(directory):
                try:
                    for filename in os.listdir(directory):
                        if filename.startswith(prefix) and filename.endswith(suffix):
                            full_path = os.path.join(directory, filename)
                            
                            # Extract name
                            middle = filename[len(prefix):-len(suffix)]
                            
                            if middle == "":
                                display_name = tr('default_profile')
                            else:
                                # Replace underscores with spaces
                                display_name = middle.replace("_", " ")
                                
                            configs.append((display_name, full_path))
                except Exception as e:
                    print(f"Error scanning configs: {e}")
        
        # Sort by display name
        configs.sort(key=lambda x: x[0])
        
        # Update UI
        tab = self.basilisk_tab if emu_type == 'basilisk' else self.sheepshaver_tab
        
        # Determine current selection
        current = self.active_configs.get(emu_type)
        if not current and cfg_path_setting:
             current = cfg_path_setting # Default to the one in settings if nothing active
        
        # If current is not in found configs (maybe a custom path not following pattern), add it
        found_paths = [c[1] for c in configs]
        if current and current not in found_paths and os.path.exists(current):
             configs.insert(0, (tr('default_profile'), current))
             
        tab.left_panel.populate_configs(configs, current)
        
        # Ensure we have an active config
        if configs:
             # If current selection is valid, keep it. Else take first.
             if not current or not any(c[1] == current for c in configs):
                 self.active_configs[emu_type] = configs[0][1]
             else:
                 self.active_configs[emu_type] = current
        else:
             # Fallback if no configs found
             self.active_configs[emu_type] = cfg_path_setting

    def switch_profile(self, emu_type, path):
        """Switch active profile and reload."""
        if self.active_configs.get(emu_type) == path:
            return
            
        self.active_configs[emu_type] = path
        
        # Save persistence
        key = "last_profile_basilisk" if emu_type == 'basilisk' else "last_profile_sheepshaver"
        self.settings_tab.settings.setValue(key, path)
        
        self.load_config_for_emulator(emu_type)

    def load_config_for_emulator(self, emu_type):
        """Load config from file for specific emulator."""
        path = self.active_configs.get(emu_type)
        if not path or not os.path.exists(path):
            return

        config = ConfigParser.parse(path)
        tab = self.basilisk_tab if emu_type == 'basilisk' else self.sheepshaver_tab
        tab.load_config(config)

    def load_configs(self):
        """Reload all configs (refresh profiles too)."""
        self.scan_and_load_initial_profiles()
        QMessageBox.information(self, tr('settings_tab'), tr('config_saved')) # Reusing message for reload logic

    def save_current_config(self):
        """Save configuration for the active emulator tab."""
        idx = self.main_tabs.currentIndex()
        
        if idx == 0:
            # Basilisk
            b_path = self.active_configs.get('basilisk')
            if b_path:
                b_cfg = self.basilisk_tab.save_config()
                ConfigParser.save(b_path, b_cfg)
                # Reload to update left panel title
                self.basilisk_tab.load_config(b_cfg)
                QMessageBox.information(self, tr('basilisk_tab'), tr('config_saved'))
                
        elif idx == 1:
            # Sheepshaver
            s_path = self.active_configs.get('sheepshaver')
            if s_path:
                s_cfg = self.sheepshaver_tab.save_config()
                ConfigParser.save(s_path, s_cfg)
                # Reload to update left panel title
                self.sheepshaver_tab.load_config(s_cfg)
                QMessageBox.information(self, tr('sheepshaver_tab'), tr('config_saved'))
        
        else:
             # For settings tab, we might want to trigger its save, but keeping it safe for now
             pass

    def save_as_config(self):
        """Save current config as a new profile."""
        idx = self.main_tabs.currentIndex()
        if idx == 0:
            emu_type = 'basilisk'
        elif idx == 1:
            emu_type = 'sheepshaver'
        else:
            QMessageBox.warning(self, tr('save_as'), "Please select an emulator tab first.")
            return

        name, ok = QInputDialog.getText(self, tr('new_profile'), tr('enter_profile_name'))
        if ok and name:
            # Check for invalid characters
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.', '(', ')')).strip()
            if not safe_name:
                return

            # Construct filename: name with underscores
            file_name_part = safe_name.replace(" ", "_")
            prefix = ".basilisk_ii_" if emu_type == 'basilisk' else ".sheepshaver_"
            filename = f"{prefix}{file_name_part}_prefs"
            
            # Determine directory
            base_cfg = self.settings_tab.basilisk_cfg.text() if emu_type == 'basilisk' else self.settings_tab.sheepshaver_cfg.text()
            directory = os.path.dirname(base_cfg) if base_cfg else os.path.expanduser("~")
            
            new_path = os.path.join(directory, filename)
            
            if os.path.exists(new_path):
                 QMessageBox.warning(self, tr('save_as'), tr('profile_exists'))
                 return
                 
            # Save current state to new file
            tab = self.basilisk_tab if emu_type == 'basilisk' else self.sheepshaver_tab
            cfg = tab.save_config()
            ConfigParser.save(new_path, cfg)
            
            # Refresh profiles and select the new one
            self.refresh_profiles(emu_type)
            
            # Manually switch to new profile (refresh might default to something else or keep old)
            self._force_select_profile(emu_type, new_path)
            
            QMessageBox.information(self, tr('save_as'), tr('settings_saved'))

    def _force_select_profile(self, emu_type, path):
         """Helper to force select a profile after creation."""
         self.active_configs[emu_type] = path
         self.refresh_profiles(emu_type) # Re-populate list
         
    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()
    
    def launch_emulator(self, emulator_type: str):
        if emulator_type == 'basilisk':
            exe_path = self.settings_tab.basilisk_exe.text()
            # USE ACTIVE CONFIG
            config_path = self.active_configs.get('basilisk', self.settings_tab.basilisk_cfg.text())
        else:
            exe_path = self.settings_tab.sheepshaver_exe.text()
            # USE ACTIVE CONFIG
            config_path = self.active_configs.get('sheepshaver', self.settings_tab.sheepshaver_cfg.text())
        
        if not exe_path or not os.path.exists(exe_path):
            QMessageBox.critical(self, tr('error'), f"Executable not found:\n{exe_path}")
            return
            
        if not config_path or not os.path.exists(config_path):
            QMessageBox.critical(self, tr('error'), f"Config file not found:\n{config_path}")
            return
            
        try:
            # Arguments: --config <path> is standard for many, let's assume direct path or arg
            # BasiliskII/SheepShaver usually accept config file as argument or --config
            # Let's try passing the config file path as the first argument
            
            # Note: SheepShaver/BasiliskII might expect --config if it's not the default
            # Checking documentation implies they might just take the path.
            # But let's assume standard behavior.
            
            # Use subprocess Popen
            import subprocess
            subprocess.Popen([exe_path, "--config", config_path], cwd=os.path.dirname(exe_path))
            
        except Exception as e:
            QMessageBox.critical(self, tr('error'), f"Failed to launch:\n{e}")
            
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
        dialog.setWindowTitle(tr('about'))
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
        version_label = QLabel(tr('version'))
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Copyright
        copyright_label = QLabel(tr('copyright'))
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
