@echo off
cd /d "%~dp0"

REM KoemojiAuto startup check script (Windows version)
REM Only start in 24-hour mode

if exist "config.json" (
    REM Read config.json with Python to check continuous_mode
    for /f %%i in ('python -c "import json; print(str(json.load(open('config.json')).get('continuous_mode', False)).lower())"') do set CONTINUOUS_MODE=%%i
    
    if "%CONTINUOUS_MODE%"=="true" (
        echo 24-hour mode is enabled. Starting KoemojiAuto.
        call start_koemoji.bat
    ) else (
        echo Scheduled mode. Waiting for scheduled time.
    )
) else (
    echo Configuration file not found: config.json
    exit /b 1
)