@echo off
echo KoemojiAuto Status
echo ==================

rem main.pyプロセスを探す
set "FOUND=0"
for /f "skip=1 tokens=1,2" %%A in ('wmic process where "CommandLine like '%%python%%main.py%%'" get ProcessId^,CommandLine 2^>NUL') do (
    if "%%A" neq "" (
        echo Status: Running
        echo Process ID: %%A
        set "FOUND=1"
        goto :DETAILS
    )
)

if %FOUND%==0 (
    echo Status: Not running
    exit /b 0
)

:DETAILS
echo.
echo Process details:
wmic process where "CommandLine like '%%python%%main.py%%'" get ProcessId,PageFileUsage,WorkingSetSize /format:table

rem 最新のログ
echo.
echo Recent log entries:
if exist koemoji.log (
    powershell -command "Get-Content koemoji.log -Tail 5"
)