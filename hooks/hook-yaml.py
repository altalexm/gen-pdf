from PyInstaller.utils.hooks import collect_all

# Collect everything, including data files and binary dependencies
datas, binaries, hiddenimports = collect_all('yaml')