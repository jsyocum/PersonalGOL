import os
import platform
import shutil
import PyInstaller.__main__
from main import get_version_number
from pathlib import Path
from zipfile import ZipFile

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
og_filename = 'main'
filename = 'PersonalGOL_' + version + '_' + platform

if platform == 'Windows':
    og_filename = og_filename + '.exe'
    filename = filename + '.exe'
print('Platform:', platform, 'App version:', version, 'Filename:', filename)

release_path = Path('releases/' + version)
if os.path.exists(release_path) is not True:
    release_path.mkdir(parents=True, exist_ok=True)
    print('Created release path at:', release_path)
else:
    print('Using release path at:', release_path)

og_file_path = Path('dist/' + og_filename)
release_file_path = Path(release_path + '/' + filename)
try:
    shutil.move(og_file_path, release_file_path)
    print('Moved executable from', og_file_path, 'to', release_file_path)
except:
    print('Failed to move', og_file_path, 'to', release_file_path)
    exit()

zip_file_path = Path(release_file_path + '.zip')
zipObj = ZipFile(zip_file_path, 'w')
zipObj.write(release_file_path)
zipObj.close()
print('Zipped executable into', zip_file_path)

os.remove(release_file_path)
print('Removed executable at:', release_file_path)
