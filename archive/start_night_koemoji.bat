@echo off
chcp 65001 > nul
echo KoemojiAuto夜間処理を開始しています...
python "%~dp0night_processor.py"
pause
