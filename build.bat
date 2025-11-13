@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building Windows executable...
pyinstaller --onefile --windowed --name Jarvis jarvis/__main__.py

echo Build complete. Executable is in dist/Jarvis.exe