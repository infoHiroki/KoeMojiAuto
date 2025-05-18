@echo off
cd /d "%~dp0"

REM KoemojiAuto startup check script (Windows version)
REM Always starts in 24-hour continuous mode

if exist "config.json" (
    echo Starting KoemojiAuto in continuous mode.
    call start_koemoji.bat
) else (
    echo Configuration file not found: config.json
    exit /b 1
)