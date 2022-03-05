import os
import platform
import shutil
import PyInstaller.__main__
from main import get_version_number

PyInstaller.__main__.run([
    'main.py',
    '--noconfirm',
    '--onefile',
    '--add-data=logo.png' + os.pathsep + '.',
    '--add-data=LessDeadZoneButton.json' + os.pathsep + '.'
])

platform = platform.system()
version = get_version_number()
filename = 'PersonalGOL_' + version + '_' + platform + '.exe'

shutil.move('dist\\main.exe', 'releases\\' + filename)
