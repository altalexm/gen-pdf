from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules
hiddenimports = collect_submodules('PIL')

# Collect data files
datas = collect_data_files('PIL', include_py_files=True)