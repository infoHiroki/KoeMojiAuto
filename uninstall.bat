@echo off
chcp 65001 > nul
echo KoemojiAutoのアンインストールを開始します...
echo.

rem タスクスケジューラから削除
echo タスクスケジューラから削除しています...

rem 定時実行タスクを削除
schtasks /delete /tn "KoemojiAutoProcessor" /f >nul 2>&1
if %errorlevel%==0 (
    echo 定時実行タスクを削除しました。
) else (
    echo 定時実行タスクが見つかりませんでした。
)

rem 起動時実行タスクを削除
schtasks /delete /tn "KoemojiAutoStartup" /f >nul 2>&1
if %errorlevel%==0 (
    echo 起動時実行タスクを削除しました。
) else (
    echo 起動時実行タスクが見つかりませんでした。
)

echo.
echo アンインストールが完了しました。
echo このフォルダ（%~dp0）を手動で削除してください。
echo.
pause