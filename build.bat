@echo off
REM ============================================================
REM Lab Cover Sheet Tool - Windows Build Script
REM ============================================================
REM 
REM Prerequisites:
REM   1. Python 3.11+ installed
REM   2. Run this from the project directory
REM
REM Usage:
REM   build.bat          - Build the application
REM   build.bat clean    - Clean build artifacts and rebuild
REM ============================================================

echo ============================================
echo Lab Cover Sheet Tool - Build Script
echo ============================================
echo.

REM Check for clean flag
if "%1"=="clean" (
    echo Cleaning previous build artifacts...
    rmdir /s /q build 2>nul
    rmdir /s /q dist 2>nul
    del /q *.spec.bak 2>nul
    echo Clean complete.
    echo.
)

REM Pick a Python 3.10/3.11 interpreter (pyqtdarktheme 2.x does not install on 3.12+)
set "PY=python"
py -3.11 -c "" >nul 2>&1
if not errorlevel 1 set "PY=py -3.11"
%PY% -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 11) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10 or 3.11 is required. Found:
    %PY% --version
    echo Install Python 3.11 from python.org and run this script again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    %PY% -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
python -c "import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 11) else 1)"
if errorlevel 1 (
    echo ERROR: The existing venv folder uses an unsupported Python version.
    echo Delete the venv folder and run this script again.
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo Dependencies installed.
echo.

REM Build the executable
echo Building executable...
echo.
pyinstaller LabCoverSheet.spec --noconfirm

echo.
if exist "dist\LabCoverSheet\LabCoverSheet.exe" (
    echo ============================================
    echo BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Executable location:
    echo   dist\LabCoverSheet\LabCoverSheet.exe
    echo.
    echo To distribute:
    echo   Copy the entire 'dist\LabCoverSheet' folder
    echo.
) else (
    echo ============================================
    echo BUILD FAILED
    echo ============================================
    echo Check the output above for errors.
)

pause
