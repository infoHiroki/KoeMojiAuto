@echo off
chcp 65001 > nul
echo KoemojiAuto処理のスケジュールタスクを設定しています...

rem 現在のディレクトリを取得
set CURRENT_DIR=%~dp0

rem 既存のタスクを削除（エラーは無視）
schtasks /delete /tn "KoemojiAutoProcessor" /f 2>nul
schtasks /delete /tn "KoemojiAutoStartup" /f 2>nul

rem 毎日19時に実行するタスクを作成
schtasks /create /tn "KoemojiAutoProcessor" /tr "%CURRENT_DIR%start_koemoji.bat" /sc daily /st 19:00 /f

rem PC起動時にチェックして起動するタスクを作成
schtasks /create /tn "KoemojiAutoStartup" /tr "%CURRENT_DIR%check_and_start.bat" /sc onstart /ru "%USERNAME%" /f

echo.
echo 完了！
echo - 24時間モード: PC起動時に自動的に開始されます
echo - 時間指定モード: 毎日19時に自動的に開始されます
echo.
echo タスクスケジューラで以下のタスクを確認してください:
echo - KoemojiAutoProcessor (定時実行)
echo - KoemojiAutoStartup (起動時実行)
echo.
pause