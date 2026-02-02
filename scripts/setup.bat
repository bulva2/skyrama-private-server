@echo off
echo ================================
echo   Skyrama Private Server Setup
echo ================================
echo.

REM Change to project root directory
cd /d "%~dp0.."

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.13+ from https://www.python.org/downloads/
    pause
    exit /b
)

echo Python found!
echo.

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ================================
echo        Setup complete!
echo ================================
echo.
echo You can now run scripts\start.bat to start the server.
echo.
pause
