from PyInstaller.utils.hooks import collect_all

# Collect everything from tkcalendar
datas, binaries, hiddenimports = collect_all('tkcalendar')

# Add additional hidden imports
hiddenimports.extend([
    'babel.numbers',
    'babel.dates'
])