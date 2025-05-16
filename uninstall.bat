@echo off
chcp 65001 > nul
echo KoemojiAutoのアンインストールを開始します...
echo.

rem タスクスケジューラから削除
echo タスクスケジューラから削除しています...
schtasks /delete /tn "KoemojiAutoProcessor" /f >nul 2>&1
if %errorlevel%==0 (
    echo タスクスケジューラから削除しました。
) else (
    echo タスクスケジューラにタスクが見つかりませんでした。
)

echo.
echo アンインストールが完了しました。
echo このフォルダ（%~dp0）を手動で削除してください。
echo.
pause