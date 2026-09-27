@echo off
title Smart Scam Message Detection System - Server
cd /d "%~dp0"

echo ========================================================
echo  SMART SCAM MESSAGE DETECTION SYSTEM
echo  Module 1: User Account & Authentication
echo ========================================================

:: Detect Python executable
set "PYTHON_EXE="

if exist "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=py -3"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python was not found on your system!
    echo Please ensure Python 3.9+ is installed.
    pause
    exit /b 1
)

echo [OK] Using Python: %PYTHON_EXE%
echo [INFO] Starting Flask Server on http://127.0.0.1:5000 ...

:: Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Start the Python application
"%PYTHON_EXE%" run.py

pause
