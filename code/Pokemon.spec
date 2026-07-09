import os
spec_dir = os.path.dirname(os.path.abspath(SPEC))
assets_dir = os.path.join(spec_dir, '..', 'assets')
json_dir = os.path.join(spec_dir, 'json')

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (assets_dir, 'venv/assets/'),
        (json_dir, 'venv/code/json/'),
    ],
    hiddenimports=['pygame', 'pygame._sdl2', 'pygame.mixer', 'pytmx', 'pyscroll'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Pokemon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    hiddenimports=['pygame', 'pygame._sdl2', 'pygame.mixer', 'pytmx', 'pyscroll'],
    onefile=True
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Pokemon',
)
