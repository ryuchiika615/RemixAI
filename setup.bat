@echo off
chcp 65001 > nul
title RemixAI Setup

echo ============================================
echo   RemixAI - Setup
echo ============================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python not found in PATH.
    echo Trying Python from AppData...
    if exist "C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
        set PY="C:\Users\ryuch\AppData\Local\Python\pythoncore-3.14-64\python.exe"
        echo [OK] Python found
    ) else (
        echo [ERROR] Python not found!
        echo Please install Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )
) else (
    set PY=python
    echo [OK] Python found
)

:: Check ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ffmpeg not found in PATH.
    if exist "C:\Program Files\ffmpeg-8.0.1\bin\ffmpeg.exe" (
        echo [OK] ffmpeg found
    ) else (
        echo [ERROR] ffmpeg not found!
        echo Download from: https://ffmpeg.org/download.html
        pause
        exit /b 1
    )
) else (
    echo [OK] ffmpeg found
)

:: Install Python packages
echo.
echo Installing Python packages...
%PY% -m pip install -r "%~dp0requirements.txt" -q
if %errorlevel% equ 0 (
    echo [OK] Packages installed
) else (
    echo [WARNING] Some packages failed to install
)

:: Create desktop shortcut
echo.
set SHORTCUT="%USERPROFILE%\Desktop\RemixAI.lnk"
if not exist %SHORTCUT% (
    echo Creating desktop shortcut...
    powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\RemixAI.lnk'); $SC.TargetPath = '%~dp0start.bat'; $SC.WorkingDirectory = '%~dp0'; $SC.Description = 'RemixAI - Music Video Generator'; $SC.Save()"
    if exist %SHORTCUT% (
        echo [OK] Desktop shortcut created
    )
) else (
    echo [OK] Desktop shortcut already exists
)

echo.
echo ============================================
echo   Setup complete!
echo.
echo   Double-click start.bat to launch
echo   Or use the desktop shortcut
echo ============================================
echo.

pause
