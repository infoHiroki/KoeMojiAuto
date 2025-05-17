@echo off
echo KoemojiAuto Status
echo ==================

rem ロックファイルを確認
set LOCK_FILE=koemoji.lock

if not exist "%LOCK_FILE%" (
    echo Status: Not running
    exit /b 0
)

rem プロセスIDを読み取る
set /p PID=<"%LOCK_FILE%"

if "%PID%"=="" (
    echo Status: Unknown [cannot read lock file]
    exit /b 1
)

rem プロセスが実行中か確認
tasklist /FI "PID eq %PID%" 2>NUL | find /I /N "%PID%" >NUL
if errorlevel 1 (
    echo Status: Not running
    echo Note: Stale lock file found. Cleaning up...
    del /f "%LOCK_FILE%"
    exit /b 0
)

echo Status: Running
echo Process ID: %PID%

echo.
echo Process details:
wmic process where ProcessId=%PID% get ProcessId,ParentProcessId,CreationDate 2>NUL

echo.
echo Memory usage:
wmic process where ProcessId=%PID% get ProcessId,VirtualSize,WorkingSetSize 2>NUL

rem 最新のログ表示
set LOG_FILE=koemoji.log
if exist "%LOG_FILE%" (
    echo.
    echo Recent log entries:
    powershell -Command "Get-Content '%LOG_FILE%' -Tail 5"
)