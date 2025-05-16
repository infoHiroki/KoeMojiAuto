@echo off
chcp 65001 > nul
echo KoemojiAuto処理を開始しています...
python "%~dp0main.py"
pause