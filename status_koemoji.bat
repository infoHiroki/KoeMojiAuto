@echo off
echo KoemojiAuto Status
echo ==================

set "FOUND=0"
for /f "skip=1 tokens=1" %%A in ('wmic process where "CommandLine like '%%python%%main.py%%' or CommandLine like '%%python3%%main.py%%'" get ProcessId 2^>NUL') do (
    if "%%A" neq "" (
        echo Status: Running
        echo Process ID: %%A
        set "FOUND=1"
        goto :LOGS
    )
)

if %FOUND%==0 echo Status: Not running

:LOGS
if exist koemoji.log (
    echo.
    echo Recent log entries:
    powershell -command "Get-Content koemoji.log -Tail 5"
)