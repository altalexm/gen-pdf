# hooks/hook-src.py

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('src.modules')