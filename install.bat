@echo off
REM Installation script for RealDiag-Software on Windows

echo ======================================
echo RealDiag-Software Installation
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo Installation completed successfully!
    echo ======================================
    echo.
    echo To run RealDiag:
    echo   python main.py --help
    echo.
    echo For more information, see README.md
    echo.
) else (
    echo.
    echo Error: Installation failed
    exit /b 1
)

pause
