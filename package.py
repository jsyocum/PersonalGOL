import os
import platform
import shutil
import PyInstaller.__main__
from main import get_version_number
from pathlib import Path

PyInstaller.__main__.run([
    'main.py',
    '--noconfirm',
    '--onefile',
    '--add-data=logo.png' + os.pathsep + '.',
    '--add-data=LessDeadZoneButton.json' + os.pathsep + '.',
    '--collect-data=pygame_gui'
])

platform = platform.system()
version = get_version_number()
filename = 'PersonalGOL_' + version + '_' + platform

if platform == 'Windows':
    shutil.move(Path('dist/main.exe'), Path('releases/' + filename + '.exe'))
elif platform == 'Linux':
    shutil.move(Path('dist/main'), Path('releases/' + filename))
