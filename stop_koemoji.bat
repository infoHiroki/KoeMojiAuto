@echo off
echo Stopping KoemojiAuto...

rem main.pyを実行しているプロセスを探して終了
for /f "tokens=2" %%P in ('wmic process where "CommandLine like '%%python%%main.py%%'" get ProcessId /value 2^>NUL ^| find "="') do (
    echo Stopping process %%P...
    taskkill /PID %%P >NUL 2>&1
)

rem 少し待つ
timeout /t 2 /nobreak >NUL

rem まだ残っていれば強制終了
for /f "tokens=2" %%P in ('wmic process where "CommandLine like '%%python%%main.py%%'" get ProcessId /value 2^>NUL ^| find "="') do (
    echo Force stopping process %%P...
    taskkill /F /PID %%P >NUL 2>&1
)

rem ロックファイルがあれば削除
if exist koemoji.lock del /f koemoji.lock

echo KoemojiAuto stopped successfully