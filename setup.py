import sys
# from PyQt6 import QtCore

import os
# PYTHON_INSTALL_DIR = 'C:/tools/miniconda3'
from cx_Freeze import setup, Executable

base = "Win32GUI"
from main import VERSION

packages = []

includes = ["os", "sys", "PyQt6", "PyQt6.Qsci", "lxml"]
excludes = ["tcl", "tk", "Tkinter", "tkinter"]

include_files = [
    "./Application.qss",
]


options = {
    "build_exe": {
        "packages": packages,
        "includes": includes,
        "excludes": excludes,
        "include_files": include_files,
        "optimize": 2
    }
}

executables = [Executable("Main.py", target_name="TransportManager.exe", base=base)]

setup(
    name="TransportManager",
    author="EmergencyCode",
    version=VERSION,
    description="Transport Management Tool",
    options=options,
    executables=executables
)
