import os
import subprocess

path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"mensaman_gui.sh")

subprocess.call(path)
