import sys
import subprocess

def install_dependencies():
    # List of required packages
    packages = ['pydub', 'gradio', 'demucs', 'ffmpeg-python']
    
    # Check for each package, install if not present
    for package in packages:
        if package not in sys.modules:
            subprocess.run(['pip', 'install', package])

    # Install ffmpeg without triggering runtime restart
    subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'])

install_dependencies()
