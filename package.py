import os
import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--noconfirm',
    '--onefile',
    '--add-data=logo.png' + os.pathsep + '.',
    '--add-data=LessDeadZoneButton.json' + os.pathsep + '.'
])
