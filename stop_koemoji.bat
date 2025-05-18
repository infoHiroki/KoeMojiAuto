@echo off
echo Stopping KoemojiAuto...

if exist koemoji.pid (
    set /p PID=<koemoji.pid
    taskkill /F /PID %PID% >NUL 2>&1
    del /f koemoji.pid
    echo Done
) else (
    echo KoemojiAuto is not running
)