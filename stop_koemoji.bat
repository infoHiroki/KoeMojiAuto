@echo off
echo Stopping KoemojiAuto...

rem ロックファイルからプロセスIDを取得
set LOCK_FILE=koemoji.lock

if not exist "%LOCK_FILE%" (
    echo KoemojiAuto is not running
    exit /b 0
)

rem プロセスIDを読み取る
set /p PID=<"%LOCK_FILE%"

if "%PID%"=="" (
    echo Could not read process ID from lock file
    exit /b 1
)

rem プロセスが実行中か確認
tasklist /FI "PID eq %PID%" 2>NUL | find /I /N "%PID%" >NUL
if errorlevel 1 (
    echo Process %PID% is not running
    rem ロックファイルをクリーンアップ
    del /f "%LOCK_FILE%"
    exit /b 0
)

echo Stopping process %PID%...

rem プロセスを終了
taskkill /PID %PID% >NUL 2>&1

rem 少し待つ
timeout /t 2 /nobreak >NUL

rem プロセスが終了したか確認
tasklist /FI "PID eq %PID%" 2>NUL | find /I /N "%PID%" >NUL
if errorlevel 1 (
    echo KoemojiAuto stopped successfully
    exit /b 0
)

rem 強制終了が必要な場合
echo Force stopping...
taskkill /F /PID %PID% >NUL 2>&1

timeout /t 1 /nobreak >NUL

tasklist /FI "PID eq %PID%" 2>NUL | find /I /N "%PID%" >NUL
if errorlevel 1 (
    echo KoemojiAuto stopped
) else (
    echo Failed to stop KoemojiAuto
    exit /b 1
)