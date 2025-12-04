# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Just Code Editor
Supports: Linux, Windows, macOS
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Determine platform
is_windows = sys.platform == 'win32'
is_mac = sys.platform == 'darwin'
is_linux = sys.platform.startswith('linux')

# Check for debug mode (set by build.py)
debug_mode = os.environ.get('JUSTCODE_DEBUG', '0') == '1'

# Application metadata
APP_NAME = 'JustCode'
APP_VERSION = '1.0.0'

# Paths
spec_dir = os.path.dirname(os.path.abspath(SPEC))
resources_dir = os.path.join(spec_dir, 'justcode', 'resources')

# Collect data files
datas = [
    # Default configuration files
    (os.path.join(resources_dir, 'default_configs'), 'justcode/resources/default_configs'),
]

# Add icons directory if it exists and has files
icons_dir = os.path.join(resources_dir, 'icons')
if os.path.exists(icons_dir) and os.listdir(icons_dir):
    datas.append((icons_dir, 'justcode/resources/icons'))

# Collect all submodules
hiddenimports = [
    'justcode',
    'justcode.app',
    'justcode.config',
    'justcode.editor',
    'justcode.editor.syntax',
    'justcode.editor.syntax.python',
    'justcode.editor.syntax.markdown',
    'justcode.panels',
    'justcode.plugins',
    'justcode.plugins.models',
    'justcode.plugins.loader',
    'justcode.plugins.actions',
    'justcode.plugins.scripting',
    'justcode.plugins.scripting.lua_engine',
    'justcode.plugins.scripting.python_engine',
    'justcode.plugins.scripting.editor_api',
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.Qsci',
    # Lua support
    'lupa',
    'lupa.lua54',
]

# Platform-specific options for executable icon
if is_mac:
    # macOS uses .icns format, but we can also use PNG
    icon_file = os.path.join(resources_dir, 'icons', 'justcode.icns')
    if not os.path.exists(icon_file):
        icon_file = os.path.join(resources_dir, 'icons', 'justcode.png')
elif is_windows:
    icon_file = os.path.join(resources_dir, 'icons', 'justcode.ico')
else:
    # Linux: PyInstaller doesn't embed icons in ELF, but we bundle for runtime use
    icon_file = None

# Check if icon exists
if icon_file and not os.path.exists(icon_file):
    icon_file = None

# Analysis
a = Analysis(
    ['run_justcode.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith('libQt6WebEngine')]
a.binaries = [x for x in a.binaries if not x[0].startswith('libQt6Designer')]
a.binaries = [x for x in a.binaries if not x[0].startswith('libQt6Quick')]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=debug_mode,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=debug_mode,  # Console enabled in debug mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# macOS app bundle
if is_mac:
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=icon_file,
        bundle_identifier='com.justcode.editor',
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': 'Just Code',
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )

