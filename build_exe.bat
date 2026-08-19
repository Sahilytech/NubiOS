@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ====================================
echo NubiOS - Windows Builder
echo ====================================

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv || exit /b 1
)

call ".venv\Scripts\activate.bat" || exit /b 1
python -m pip install --upgrade pip || exit /b 1
python -m pip install -r requirements.txt || exit /b 1
python -m pip install -e ".[dev]" || exit /b 1

set NUBIOS_MOCK_AI=true
python -m pytest || exit /b 1
python -m PyInstaller --noconfirm --clean --name NubiOS --windowed --paths src src\nubios\main.py || exit /b 1

echo.
echo NubiOS executable created in dist\NubiOS\NubiOS.exe
endlocal
