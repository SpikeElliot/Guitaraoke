# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:\\Users\\spike\\anaconda3\\envs\\ProjectFinal\\Lib\\site-packages\\basic_pitch\\saved_models', 'basic_pitch\\saved_models'),
        ('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\assets', 'assets'),
        ('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\demucs_models', 'demucs_models'),
        ('C:\\Users\\spike\\anaconda3\\envs\\ProjectFinal\\Library\\share\\ffmpeg', 'ffmpeg'),
        ('C:\\Users\\spike\\anaconda3\\envs\\ProjectFinal\\Library\\bin\\SDL3.dll', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    './assets/images/splash_screen.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='Guitaraoke',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\images\\guitar_pick.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Guitaraoke',
)

import shutil
shutil.copytree('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\data', '{0}\\Guitaraoke\\data'.format(DISTPATH), dirs_exist_ok=True)
