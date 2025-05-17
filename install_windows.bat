@echo off
setlocal EnableDelayedExpansion

echo =====================================
echo    KoeMojiAuto Installer
echo =====================================
echo.

rem 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 管理者権限が必要です
    echo 右クリックして「管理者として実行」してください
    pause
    exit /b 1
)

rem Python確認
echo [1/5] Python環境を確認しています...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Pythonがインストールされていません
    echo     https://www.python.org/ からインストールしてください
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% を検出しました

rem FFmpeg確認
echo [2/5] FFmpegを確認しています...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FFmpegがインストールされていません
    echo     音声・動画処理にはFFmpegが必要です
    echo     https://ffmpeg.org/download.html からインストールしてください
    set /p CONTINUE="続行しますか？ (y/n): "
    if not "!CONTINUE!"=="y" exit /b 1
) else (
    echo [OK] FFmpegが検出されました
)

rem 依存関係インストール
echo [3/5] 依存関係をインストールしています...
cd /d "%~dp0"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [X] 依存関係のインストールに失敗しました
    pause
    exit /b 1
)
echo [OK] 依存関係をインストールしました

rem フォルダ作成
echo [4/5] 必要なフォルダを作成しています...
if not exist "input" mkdir "input"
if not exist "output" mkdir "output" 
if not exist "reports" mkdir "reports"
echo [OK] フォルダを作成しました

rem タスクスケジューラー設定
echo [5/5] 自動実行を設定しています...
set CURRENT_DIR=%~dp0

schtasks /delete /tn "KoeMojiAutoProcessor" /f >nul 2>&1
schtasks /delete /tn "KoeMojiAutoStartup" /f >nul 2>&1

schtasks /create /tn "KoeMojiAutoProcessor" /tr "%CURRENT_DIR%start_koemoji.bat" /sc daily /st 19:00 /f
if %errorlevel% neq 0 (
    echo [X] 定時実行タスクの作成に失敗しました
    pause
    exit /b 1
)

schtasks /create /tn "KoeMojiAutoStartup" /tr "%CURRENT_DIR%check_and_start.bat" /sc onstart /ru "%USERNAME%" /f
if %errorlevel% neq 0 (
    echo [X] 起動時タスクの作成に失敗しました
    pause
    exit /b 1
)
echo [OK] タスクスケジューラーを設定しました

rem 設定確認
echo.
echo インストール完了！
echo.
echo * 実行: start_koemoji.bat
echo * 設定: tui.bat
echo * 自動実行: 毎日19時
echo.

rem TUI起動の確認
set /p LAUNCH="設定画面を開きますか？ (y/n): "
if "!LAUNCH!"=="y" (
    start tui.bat
)

pause
exit /b 0