@echo off
echo KoemojiAuto Status
echo ==================

if exist koemoji.pid (
    echo Status: Running
    set /p PID=<koemoji.pid
    echo Process ID: %PID%
) else (
    echo Status: Not running
)