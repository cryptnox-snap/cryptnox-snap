# -*- mode: python ; coding: utf-8 -*-

import os
import importlib
import pathlib
import plistlib

from pathlib import Path

# CryptnoxCLI special config

data_include = [
                ('cryptnoxcard/lib/cryptos/english.txt',
                'lib/cryptos/')
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
             excludes=['_gtkagg', '_tkagg', 'curses', 'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter', 'libopenblas'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
remove(pkgs_remove)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cryptnoxcard',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
