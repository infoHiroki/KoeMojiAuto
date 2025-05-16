@echo off
chcp 65001 > nul
echo KoemojiAuto自動実行の状態を切り替えています...

rem タスクの存在確認
schtasks /query /tn "KoemojiAutoProcessor" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo エラー: タスクが見つかりません。
    echo 先にinstall.batを実行してください。
    echo.
    pause
    exit /b 1
)

rem 現在の状態を確認
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "状態:" | findstr /i "無効" >nul 2>&1
if %errorlevel% equ 0 (
    rem 無効状態 → 有効化
    echo 現在: 無効
    schtasks /change /tn "KoemojiAutoProcessor" /enable >nul 2>&1
    echo 変更後: 有効
    echo.
    echo 自動実行を再開しました。
    echo 毎日19時に実行されます。
) else (
    rem 有効状態 → 無効化
    echo 現在: 有効
    schtasks /change /tn "KoemojiAutoProcessor" /disable >nul 2>&1
    echo 変更後: 無効
    echo.
    echo 自動実行を一時停止しました。
    echo 再開するには、もう一度toggle.batを実行してください。
)

echo.
pause