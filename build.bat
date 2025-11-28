@echo off
REM Build script for Dynamic Island Timer
REM This script will create the .exe file

echo ============================================
echo   Dynamic Island Timer - Build Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Generating sound files...
python static/generate_sounds.py
if errorlevel 1 (
    echo WARNING: Failed to generate sounds, continuing...
)

echo.
echo [3/5] Generating icon files...
python static/generate_icons.py
if errorlevel 1 (
    echo WARNING: Failed to generate icons, continuing...
)

echo.
echo [4/5] Creating ICO file from PNG...
REM Try to create ICO if possible (requires Pillow)
pip install Pillow >nul 2>&1
python -c "from PIL import Image; img = Image.open('static/icons/icon.png'); img.save('static/icons/icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])" 2>nul
if errorlevel 1 (
    echo INFO: Could not create .ico file. Install Pillow for icon support.
)

echo.
echo [5/5] Building executable with PyInstaller...
python -m PyInstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo The executable is located at:
echo   dist\DynamicIslandTimer.exe
echo.
echo You can now run the application or distribute
echo the .exe file to other Windows computers.
echo.
pause
