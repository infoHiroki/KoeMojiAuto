@echo off
setlocal EnableDelayedExpansion

echo =====================================
echo    KoeMojiAuto Installer
echo =====================================
echo.

rem Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Administrator privileges required
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

rem Python check
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is not installed
    echo     Please install from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python %PYVER% detected

rem FFmpeg check
echo [2/5] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] FFmpeg is not installed
    echo     FFmpeg is required for audio/video processing
    echo     Please install from https://ffmpeg.org/download.html
    set /p CONTINUE="Continue anyway? (y/n): "
    if not "!CONTINUE!"=="y" exit /b 1
) else (
    echo [OK] FFmpeg detected
)

rem Install dependencies
echo [3/5] Installing dependencies...
cd /d "%~dp0"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

rem Create folders
echo [4/5] Creating required folders...
if not exist "input" mkdir "input"
if not exist "output" mkdir "output" 
if not exist "reports" mkdir "reports"
echo [OK] Folders created

rem Task Scheduler setup
echo [5/5] Setting up auto-start...
set CURRENT_DIR=%~dp0

schtasks /delete /tn "KoeMojiAutoProcessor" /f >nul 2>&1
schtasks /delete /tn "KoeMojiAutoStartup" /f >nul 2>&1

schtasks /create /tn "KoeMojiAutoProcessor" /tr "%CURRENT_DIR%start_koemoji.bat" /sc daily /st 19:00 /f
if %errorlevel% neq 0 (
    echo [X] Failed to create scheduled task
    pause
    exit /b 1
)

schtasks /create /tn "KoeMojiAutoStartup" /tr "%CURRENT_DIR%check_and_start.bat" /sc onstart /ru "%USERNAME%" /f
if %errorlevel% neq 0 (
    echo [X] Failed to create startup task
    pause
    exit /b 1
)
echo [OK] Task Scheduler configured

rem Installation complete
echo.
echo Installation complete!
echo.
echo * Run: start_koemoji.bat
echo * Configure: tui.bat  
echo * Auto-run: Daily at 19:00
echo.

rem Launch TUI confirmation
set /p LAUNCH="Open configuration screen? (y/n): "
if "!LAUNCH!"=="y" (
    start tui.bat
)

pause
exit /b 0