@echo off
echo Starting KoemojiAuto processing...
start /b "" python "%~dp0main.py"
echo KoemojiAuto is running in background.
echo Check status: status_koemoji.bat
echo Stop: stop_koemoji.bat
pause