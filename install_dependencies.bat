@echo off
echo Installing Photobooth Application Dependencies...
echo.

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install pip if not available
py -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Installing pip...
    py -m ensurepip --upgrade
)

REM Upgrade pip to latest version
echo Upgrading pip...
py -m pip install --upgrade pip

REM Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
py -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: All dependencies installed successfully!
    echo You can now run the application using runner.bat
)

echo.
pause