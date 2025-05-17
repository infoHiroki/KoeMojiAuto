@echo off
echo Starting KoemojiAuto uninstall...
echo.

rem Remove from Task Scheduler
echo Removing from Task Scheduler...

rem Delete scheduled task
schtasks /delete /tn "KoemojiAutoProcessor" /f >nul 2>&1
if %errorlevel%==0 (
    echo Scheduled task removed.
) else (
    echo Scheduled task not found.
)

rem Delete startup task
schtasks /delete /tn "KoemojiAutoStartup" /f >nul 2>&1
if %errorlevel%==0 (
    echo Startup task removed.
) else (
    echo Startup task not found.
)

echo.
echo Uninstall complete.
echo Please manually delete this folder (%~dp0).
echo.
pause