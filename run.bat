@echo off
echo Starting No-Recoil Assistant...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: Check if requirements are installed
echo Checking dependencies...
python -c "import pynput, keyboard, colorama" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b
    )
)

:: Run the application with admin rights
echo Starting application...
powershell -Command "Start-Process python -ArgumentList 'src/main.py' -Verb RunAs"

exit /b 