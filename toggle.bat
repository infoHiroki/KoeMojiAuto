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

rem Check current status
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:" | findstr /i "Disabled" >nul 2>&1
if %errorlevel% equ 0 (
    rem Disabled → Enable
    echo Current: Disabled
    schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
    echo After: Enabled
    echo.
    echo Auto-execution resumed.
    echo Will run daily at 19:00.
) else (
    rem Enabled → Disable
    echo Current: Enabled
    schtasks /change /tn "KoemojiAutoProcessor" /disable >nul 2>&1
    echo After: Disabled
    echo.
    echo Auto-execution paused.
    echo To run manually, use start_koemoji.bat.
)

echo.
echo Status check:
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:"
echo.
pause