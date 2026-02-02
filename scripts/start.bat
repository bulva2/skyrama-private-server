@echo off
echo Starting Skyrama Private Server with FastAPI and Uvicorn...

cd /d "%~dp0.."

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Please run scripts\setup.bat first.
    pause
    exit /b
)

uvicorn server:app --host 0.0.0.0 --port 3800 --reload
pause
