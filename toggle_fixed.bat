@echo off
echo Toggling KoemojiAuto auto-execution status...

rem Check if task exists
schtasks /query /tn "KoemojiAutoProcessor" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Error: Task not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)

rem Try to enable the task first
schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
if %errorlevel% equ 0 (
    rem If successful, it was disabled before
    echo Previous status: Disabled
    echo Current status: Enabled
    echo.
    echo Auto-execution resumed.
    echo Will run daily at configured time.
) else (
    rem If failed, it's already enabled, so disable it
    echo Previous status: Enabled
    schtasks /change /tn "KoemojiAutoProcessor" /disable >nul 2>&1
    echo Current status: Disabled
    echo.
    echo Auto-execution paused.
    echo To run manually, use start_koemoji.bat.
)

echo.
echo Task details:
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "TaskName Next Last Status"
echo.
pause