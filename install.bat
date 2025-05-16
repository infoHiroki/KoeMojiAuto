@echo off
chcp 65001 > nul
echo KoemojiAuto処理のスケジュールタスクを設定しています...

rem 現在のディレクトリを取得
set CURRENT_DIR=%~dp0

rem タスクスケジューラで毎日19時に実行するタスクを作成
schtasks /create /tn "KoemojiAutoProcessor" /tr "%CURRENT_DIR%start_koemoji.bat" /sc daily /st 19:00 /f

echo.
echo 完了！毎日19時にKoemojiAuto処理が自動的に開始されます。
echo タスクスケジューラで「KoemojiAutoProcessor」タスクを確認してください。
echo.
pause