
Remove-Item -R .\build\TransportManager -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager.* -ErrorAction SilentlyContinue

python .\setup.py build

# remove unnecessary python libraries
Remove-Item -R .\build\TransportManager\lib\lib2to3 -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\logging -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\multiprocessing -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\pydoc_data -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\test -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\unittest -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\concurrent -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\asyncio -ErrorAction SilentlyContinue

#Remove unnecesary PyQT libraries
Get-ChildItem .\build\TransportManager\lib\PyQt6\bindings -Exclude Qsci,QtCore,QtGui,QtWidgets | Remove-Item -R -Force -ErrorAction SilentlyContinue
Get-ChildItem .\build\TransportManager\lib\PyQt6\Qt6\plugins -Exclude imageformats,platforms,styles | Remove-Item -R -Force -ErrorAction SilentlyContinue
Get-ChildItem .\build\TransportManager\lib\PyQt6\Qt6\bin -Exclude msvcp140.dll,Qt6Svg.dll,msvcp140_2.dll,vcruntime140_1.dll,msvcp140_1.dll | Remove-Item -R -Force -ErrorAction SilentlyContinue
Get-ChildItem .\build\TransportManager\lib\PyQt6 -Exclude bindings, Qt, Qt6, py.typed, __init__.pyc, sip.pyi, sip.cp39-win_amd64.pyd, Qsci.pyi, QtPrintSupport.pyd, QtGui.pyi, QtCore.pyi, Qt6PrintSupport.dll, QtWidgets.pyi, QtGui.pyd, QtCore.pyd, Qsci.pyd, QtWidgets.pyd, Qt6Core.dll, Qt6Widgets.dll, Qt6Gui.dll | Remove-Item -R -Force -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\PyQt6\Qt6\qml -Force -ErrorAction SilentlyContinue
Remove-Item -R .\build\TransportManager\lib\PyQt6\Qt6\translations -Force -ErrorAction SilentlyContinue

#Pack it up
& 'C:\Program Files\7-Zip\7z.exe' a .\build\TransportManager.7z .\build\TransportManager
# Compress-Archive -LiteralPath .\build\TransportManager -DestinationPath .\build\TransportManager.zip

