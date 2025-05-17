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

rem Query the task and save output to temp file
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST > "%temp%\task_status.txt" 2>&1

rem Try to find disabled status in any language
findstr /i "Disabled" "%temp%\task_status.txt" >nul 2>&1
set disabled_found=%errorlevel%

rem Also check for Japanese "無効"
findstr /i "無効" "%temp%\task_status.txt" >nul 2>&1
set disabled_jp_found=%errorlevel%

rem Check if task is disabled in any language
if %disabled_found% equ 0 goto :enable_task
if %disabled_jp_found% equ 0 goto :enable_task

rem If we're here, task is probably enabled, so disable it
:disable_task
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
goto :cleanup

:enable_task
echo Current: Disabled
schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
if %errorlevel% equ 0 (
    echo After: Enabled
    echo.
    echo Auto-execution resumed.
    echo Will run daily at configured time.
) else (
    echo Error: Failed to enable task.
)

:cleanup
rem Delete temp file
del "%temp%\task_status.txt" >nul 2>&1

echo.
echo Current task status:
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i /c:"TaskName" /c:"Status" /c:"Next Run" /c:"タスク名" /c:"状態" /c:"次回の実行時刻"
echo.
pause