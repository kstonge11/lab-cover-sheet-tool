# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Lab Cover Sheet Tool
Build with: pyinstaller LabCoverSheet.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all qdarktheme data files (stylesheets, etc.)
qdarktheme_datas = collect_data_files('qdarktheme')

# Collect hidden imports for all required packages
hiddenimports = [
    # PyQt6 submodules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    # qdarktheme
    'qdarktheme',
    'qdarktheme.qtpy',
    'qdarktheme.qtpy.QtCore',
    'qdarktheme.qtpy.QtGui',
    'qdarktheme.qtpy.QtWidgets',
    # pandas and friends
    'pandas',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.skiplist',
    # openpyxl
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.worksheet.page',
    'openpyxl.utils',
    # defusedxml: openpyxl uses it to parse .xlsx XML safely
    'defusedxml',
    'defusedxml.ElementTree',
    # win32com for Excel printing (Windows only)
    'win32com',
    'win32com.client',
    'win32api',
    'win32con',
    'pythoncom',
    'pywintypes',
    # App modules
    'app',
    'app.main_window',
    'app.constants',
    'app.models',
    'app.models.error_entry',
    'app.services',
    'app.services.cover_sheet_service',
    'app.utils',
    'app.utils.file_utils',
    'app.widgets',
    'app.widgets.test_info_box',
    'app.widgets.add_error_box',
    'app.widgets.queue_box',
    'app.widgets.settings_dialog',
    'app.widgets.placeholder_box',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=qdarktheme_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'tkinter',
        '_tkinter',
        'tk',
        'tcl',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LabCoverSheet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment and add icon file if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LabCoverSheet',
)
