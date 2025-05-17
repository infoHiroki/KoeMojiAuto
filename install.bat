@echo off
echo Setting up KoemojiAuto scheduled tasks...

rem Get current directory
set CURRENT_DIR=%~dp0

rem Delete existing tasks (ignore errors)
schtasks /delete /tn "KoemojiAutoProcessor" /f 2>nul
schtasks /delete /tn "KoemojiAutoStartup" /f 2>nul

rem Create task to run daily at 19:00
schtasks /create /tn "KoemojiAutoProcessor" /tr "%CURRENT_DIR%start_koemoji.bat" /sc daily /st 19:00 /f

rem Create task to check and start on PC startup
schtasks /create /tn "KoemojiAutoStartup" /tr "%CURRENT_DIR%check_and_start.bat" /sc onstart /ru "%USERNAME%" /f

echo.
echo Complete!
echo - 24-hour mode: Will automatically start on PC startup
echo - Scheduled mode: Will automatically start at 19:00 daily
echo.
echo Please check the following tasks in Task Scheduler:
echo - KoemojiAutoProcessor (scheduled execution)
echo - KoemojiAutoStartup (startup execution)
echo.
pause