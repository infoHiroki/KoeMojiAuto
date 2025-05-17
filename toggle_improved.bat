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

rem Get task info in CSV format (language-neutral)
for /f "tokens=2,3 delims=," %%a in ('schtasks /query /tn "KoemojiAutoProcessor" /fo csv /nh') do (
    set TASK_STATUS=%%a
    set TASK_STATE=%%b
)

rem Remove quotes if present
set TASK_STATUS=%TASK_STATUS:"=%
set TASK_STATE=%TASK_STATE:"=%

echo Current status: %TASK_STATUS%

rem Check if task is currently disabled
:: Note: In CSV format, disabled tasks have "Disabled" in the status field
:: This works regardless of language since it's checking the actual state
if /i "%TASK_STATUS%"=="Disabled" (
    rem Disabled → Enable
    echo Enabling task...
    schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
    if %errorlevel% equ 0 (
        echo Status: Enabled
        echo.
        echo Auto-execution resumed.
        echo Will run according to schedule.
    ) else (
        echo Error: Failed to enable task
    )
) else (
    rem Enabled or other state → Disable
    echo Disabling task...
    schtasks /change /tn "KoemojiAutoProcessor" /disable >nul 2>&1
    if %errorlevel% equ 0 (
        echo Status: Disabled
        echo.
        echo Auto-execution paused.
        echo To run manually, use start_koemoji.bat.
    ) else (
        echo Error: Failed to disable task
    )
)

echo.
echo Final status:
schtasks /query /tn "KoemojiAutoProcessor" /fo csv /nh
echo.
pause