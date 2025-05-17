@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM KoemojiAuto起動時チェックスクリプト（Windows版）
REM 24時間モードの場合のみ起動する

if exist "config.json" (
    REM Pythonでconfig.jsonを読み込んでcontinuous_modeをチェック
    for /f %%i in ('python -c "import json; print(str(json.load(open('config.json')).get('continuous_mode', False)).lower())"') do set CONTINUOUS_MODE=%%i
    
    if "%CONTINUOUS_MODE%"=="true" (
        echo 24時間モードが有効です。KoemojiAutoを起動します。
        call start_koemoji.bat
    ) else (
        echo 時間指定モードです。指定時刻まで待機します。
    )
) else (
    echo 設定ファイルが見つかりません: config.json
    exit /b 1
)