# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:\\Users\\spike\\anaconda3\\envs\\ProjectFinal\\Lib\\site-packages\\basic_pitch\\saved_models', 'basic_pitch\\saved_models'),
        ('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\assets', 'assets'),
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
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [('v', None, 'OPTION')],
    name='Guitaraoke',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

import shutil
shutil.copyfile('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\config.ini', '{0}\\config.ini'.format(DISTPATH))
shutil.copytree('C:\\Users\\spike\\Documents\\GitHub\\Guitaraoke\\data', '{0}\\data'.format(DISTPATH), dirs_exist_ok=True)
