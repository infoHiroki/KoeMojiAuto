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

rem Save current status to a temp file for multi-language support
set TEMP_FILE=%TEMP%\koemoji_status.txt
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST > "%TEMP_FILE%" 2>&1

rem Check if disabled (works for both English "Disabled" and Japanese "無効")
type "%TEMP_FILE%" | findstr /i "Disabled" >nul 2>&1
set ENGLISH_DISABLED=%errorlevel%

type "%TEMP_FILE%" | findstr /i "無効" >nul 2>&1
set JAPANESE_DISABLED=%errorlevel%

rem Delete temp file
del "%TEMP_FILE%" >nul 2>&1

rem If either English or Japanese "disabled" is found
if %ENGLISH_DISABLED% equ 0 (set IS_DISABLED=1) else (
    if %JAPANESE_DISABLED% equ 0 (set IS_DISABLED=1) else (set IS_DISABLED=0)
)

if %IS_DISABLED% equ 1 (
    rem Currently disabled - enable it
    echo Current: Disabled
    schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
    if %errorlevel% equ 0 (
        echo After: Enabled
        echo.
        echo Auto-execution resumed.
        echo Will run daily at 19:00.
    ) else (
        echo Error: Failed to enable task.
    )
) else (
    rem Currently enabled - disable it
    echo Current: Enabled
    schtasks /change /tn "KoemojiAutoProcessor" /disable >nul 2>&1
    if %errorlevel% equ 0 (
        echo After: Disabled
        echo.
        echo Auto-execution paused.
        echo To run manually, use start_koemoji.bat.
    ) else (
        echo Error: Failed to disable task.
    )
)

echo.
pause