@echo off
setlocal
python -m pytest || exit /b 1
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --name NubiOS --windowed --paths src src\nubios\main.py
if errorlevel 1 exit /b 1
echo NubiOS executable created in dist\NubiOS\
