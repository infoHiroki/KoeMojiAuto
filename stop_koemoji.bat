@echo off
echo Stopping KoemojiAuto...

for /f "tokens=2" %%P in ('wmic process where "CommandLine like '%%python%%main.py%%' or CommandLine like '%%python3%%main.py%%'" get ProcessId /value 2^>NUL ^| find "="') do (
    taskkill /F /PID %%P >NUL 2>&1
)

if exist koemoji.lock del /f koemoji.lock

echo Done