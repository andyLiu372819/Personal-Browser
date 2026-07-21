# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_root = Path.cwd()
src_root = project_root / "src"
app_icon = project_root / "assets" / "icons" / "app.ico"
icon_path = str(app_icon) if app_icon.exists() else None


a = Analysis(
    ["src/main.py"],
    pathex=[str(src_root)],
    binaries=[],
    datas=[
        (str(project_root / "assets"), "assets"),
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtNetwork",
        "PySide6.QtPositioning",
        "PySide6.QtPrintSupport",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtSvg",
        "PySide6.QtWebChannel",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtWidgets",
    ],
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
    name="NexusBrowser",
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
    icon=icon_path,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NexusBrowser",
)
