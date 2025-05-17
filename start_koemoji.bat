@echo off
echo KoemojiAuto処理を開始しています...
start /b "" python3 "%~dp0main.py"
echo KoemojiAutoがバックグラウンドで起動しました。
echo ステータス確認: .\status_koemoji.bat
echo 停止: .\stop_koemoji.bat