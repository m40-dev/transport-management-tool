
rm -R .\build\TransportManager
python .\setup.py build
rm .\build\TransportManager.7z -ErrorAction SilentlyContinue
& 'C:\Program Files\7-Zip\7z.exe' a .\build\TransportManager.7z .\build\TransportManager
