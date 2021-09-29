# -*- mode: python ; coding: utf-8 -*-

import pathlib

# CryptnoxCLI special config

data_include = [
    ('cryptnoxcard/lib/cryptos/english.txt',
     'lib/cryptos/'),
    ('cryptnoxcard/contract_abi', 'contract_abi')
]

pkgs_remove = [
    'sqlite3',
    'tcl85',
    'tk85',
    '_sqlite3',
    '_tkinter',
    'libopenblas',
]

cryptnoxcard_path = pathlib.Path("cryptnoxcard").absolute()


def remove(pkgs):
    for pkg in pkgs:
        a.binaries = [x for x in a.binaries if not x[0].startswith(pkg)]


block_cipher = None

a = Analysis(['cryptnoxcard/main.py'],
             pathex=[cryptnoxcard_path],
             binaries=[],
             datas=data_include,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_gtkagg', '_tkagg', 'curses', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                       'Tkconstants', 'Tkinter', 'libopenblas'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
remove(pkgs_remove)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='cryptnoxcard',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon="cryptnoxcard.ico",
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='cryptnoxcard')
