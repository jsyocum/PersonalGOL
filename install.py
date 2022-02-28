import subprocess
import sys

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except:
        print('Failed to install', package)


packages = ('pygame', 'pygame_gui', 'numpy', 'scipy', 'pillow', 'typing', 'appdirs', 'pathvalidate', 'pathlib', 'configparser')
for package in packages:
    install(package)
