@echo off
setlocal EnableDelayedExpansion

echo =====================================
echo     KoeMojiAuto Uninstaller
echo =====================================
echo.
echo 以下の項目を削除します:
echo - タスクスケジューラーの登録
echo - 設定ファイル (config.json)
echo - 処理履歴 (processed_files.json)
echo - ログファイル (koemoji.log)
echo.
set /p CONFIRM="本当にアンインストールしますか？ (y/n): "
if not "!CONFIRM!"=="y" (
    echo アンインストールをキャンセルしました
    pause
    exit /b 0
)

echo.
echo [1/4] タスクスケジューラーから削除しています...
schtasks /delete /tn "KoeMojiAutoProcessor" /f >nul 2>&1
schtasks /delete /tn "KoeMojiAutoStartup" /f >nul 2>&1
echo [OK] タスクを削除しました

echo [2/4] 設定ファイルをバックアップしています...
set BACKUP_DIR=KoeMojiAuto_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" >nul 2>&1

if exist "config.json" move "config.json" "%BACKUP_DIR%\" >nul
if exist "processed_files.json" move "processed_files.json" "%BACKUP_DIR%\" >nul
if exist "koemoji.log" move "koemoji.log" "%BACKUP_DIR%\" >nul
if exist "reports" xcopy "reports" "%BACKUP_DIR%\reports\" /E /I /Q >nul

echo [OK] バックアップを作成しました: %BACKUP_DIR%

echo [3/4] 依存関係をアンインストールしています...
echo アンインストールする依存関係:
echo - faster-whisper
echo - psutil
echo.
set /p UNINSTALL_DEPS="依存関係もアンインストールしますか？ (y/n): "
if "!UNINSTALL_DEPS!"=="y" (
    pip uninstall faster-whisper psutil -y
    echo [OK] 依存関係をアンインストールしました
) else (
    echo [!] 依存関係はそのまま残します
)

echo [4/4] クリーンアップ中...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
echo [OK] クリーンアップ完了

echo.
echo アンインストール完了！
echo.
echo バックアップ: %BACKUP_DIR%
echo.
echo 再インストールするには:
echo   install_windows.bat を実行
echo.

rem フォルダを開く
echo.
set /p OPEN_BACKUP="バックアップフォルダを開きますか？ (y/n): "
if "!OPEN_BACKUP!"=="y" (
    explorer "%BACKUP_DIR%"
)

pause
exit /b 0