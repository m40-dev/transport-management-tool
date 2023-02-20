import sys
# from PyQt6 import QtCore

import os
# PYTHON_INSTALL_DIR = 'C:/tools/miniconda3'
from cx_Freeze import setup, Executable

base = "Win32GUI"

packages = []

includes = ["os", "sys", "PyQt6", "PyQt6.Qsci", "lxml"]
excludes = ["tcl", "tk", "Tkinter"]
include_files = [
    "./Application.qss",
   # (
   #     os.path.join(PYTHON_INSTALL_DIR, "DLLs", "libcrypto-1_1.dll"),
   #     "lib/libcrypto-1_1-x64.dll",
   # ),
   # (
   #     os.path.join(PYTHON_INSTALL_DIR, "DLLs", "libssl-1_1.dll"),
   #     "lib/libssl-1_1-x64.dll",
   # ),
]


options = {
    "build_exe": {
        "packages": packages,
        "includes": includes,
        "excludes": excludes,
        "include_files": include_files,
        "optimize": 2,
    }
}

executables = [Executable("Main.py", target_name="TransportManager.exe", base=base)]

setup(
    name="TransportManager",
    author="EmergencyCode",
    version="0.1",
    description="Transport Management Tool",
    options=options,
    executables=executables,
)
