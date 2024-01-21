import sys
# from PyQt6 import QtCore

import os
# PYTHON_INSTALL_DIR = 'C:/tools/miniconda3'
from cx_Freeze import setup, Executable

base = "Win32GUI"
from main import VERSION

packages = []

includes = ["os", "sys", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "PyQt6.Qsci", "lxml", "pyodbc", 
            "win32api", "win32con", "win32gui", "win32comext","winreg", "ctypes", "enum"]
excludes = ["tcl", "tk", "Tkinter", "tkinter"]

include_files = [
    "./icon.ico",
    "./Application.qss",
    ("./lib/ui/img", "./lib/ui/img")
]

options = {
    "build_exe": {
        "build_exe": "build/TransportManager",
        "packages": packages,
        "includes": includes,
        "excludes": excludes,
        "include_files": include_files,
        "optimize": 2
    }
    
}

executables = [Executable("Main.py", target_name="TransportManager.exe", base=base, icon="./icon.ico")]

setup(
    name="TransportManager",
    author="EmergencyCode",
    version=VERSION,
    description="Transport Management Tool",
    options=options,
    executables=executables
)
