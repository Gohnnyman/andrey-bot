@echo off
setlocal enabledelayedexpansion

REM ========= Step 1: Check for Python Installation =========
echo Checking for Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    REM Define the Python installer URL (adjust the version as needed)
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python_installer.exe"
    
    REM Download the Python installer using PowerShell
    echo Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"    
    if not exist "%PYTHON_INSTALLER%" (
        echo Error: Python installer was not downloaded.
        exit /b 1
    )
    
    REM Install Python silently for all users and add it to PATH
    echo Installing Python...
    start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    if %errorlevel% neq 0 (
        echo Error: Python installation failed.
        exit /b 1
    )
    
    REM Wait a moment for the PATH to update
    timeout /t 5 /nobreak >nul
) else (
    echo Python is already installed. Skipping installation.
)

REM ========= Step 2: Install Playwright package using pip =========
echo Upgrading pip...
python -m pip install --upgrade pip
echo Installing Playwright via pip (user install)...
python -m pip install playwright --user
if %errorlevel% neq 0 (
    echo Error: Failed to install Playwright package.
    exit /b 1
)

REM ========= Step 3: Run "python -m playwright install" in PowerShell =========
REM Change directory to the location of this script
cd /d "%~dp0"
echo Installing Playwright browser binaries via PowerShell...
powershell -Command "python -m playwright install"
if %errorlevel% neq 0 (
    echo Error: Failed to execute 'python -m playwright install'.
    exit /b 1
)

REM ========= Step 4: Run main.py =========
echo Running main.py...
python .\main.py
if %errorlevel% neq 0 (
    echo Error: Failed to run main.py.
    exit /b 1
)

echo All tasks completed successfully.
exit /b 0