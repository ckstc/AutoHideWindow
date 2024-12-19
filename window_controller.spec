# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['window_controller_trayA.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['win32api', 'win32gui', 'win32con', 'win32process', 'pystray._win32'],
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
    name='WindowController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 如果有图标文件的话
    uac_admin=True,  # 请求管理员权限
) 