# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import tkinter

# 使用确认的Python路径
PYTHON_PATH = r"C:\Program Files\Python313"
TCL_PATH = os.path.join(PYTHON_PATH, 'tcl', 'tcl8.6')
TK_PATH = os.path.join(PYTHON_PATH, 'tcl', 'tk8.6')
TKINTER_PATH = os.path.join(PYTHON_PATH, 'Lib', 'tkinter')

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 使用确认的路径
        (TCL_PATH, 'tcl8.6'),
        (TK_PATH, 'tk8.6'),
        (os.path.join(PYTHON_PATH, 'DLLs', '_tkinter.pyd'), '.'),
        (TKINTER_PATH, 'tkinter'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        '_tkinter',
        'cv2',
        'patch'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频帧提取工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 临时设为True以查看错误信息
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)