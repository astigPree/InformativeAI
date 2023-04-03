import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [ 'kivy' , 'kivymd' , 'pyttsx' , 'pyttsx3' , 'SpeechRecognition' , 'neuralintents' ]
for package in packages :
    install(package)