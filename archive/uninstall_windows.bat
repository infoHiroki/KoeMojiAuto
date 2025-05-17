@echo off
setlocal EnableDelayedExpansion

echo =====================================
echo     KoeMojiAuto Uninstaller
echo =====================================
echo.
echo The following items will be removed:
echo - Task Scheduler entries
echo - Configuration file (config.json)
echo - Processed files list (processed_files.json)
echo - Log file (koemoji.log)
echo.
set /p CONFIRM="Continue uninstall? (y/n): "
if not "!CONFIRM!"=="y" (
    echo Uninstall cancelled
    pause
    exit /b 0
)

echo.
echo [1/4] Removing from Task Scheduler...
schtasks /delete /tn "KoeMojiAutoProcessor" /f >nul 2>&1
schtasks /delete /tn "KoeMojiAutoStartup" /f >nul 2>&1
echo [OK] Tasks removed

echo [2/4] Backing up configuration files...
set BACKUP_DIR=KoeMojiAuto_Backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
mkdir "%BACKUP_DIR%" >nul 2>&1

if exist "config.json" move "config.json" "%BACKUP_DIR%\" >nul
if exist "processed_files.json" move "processed_files.json" "%BACKUP_DIR%\" >nul
if exist "koemoji.log" move "koemoji.log" "%BACKUP_DIR%\" >nul
if exist "reports" xcopy "reports" "%BACKUP_DIR%\reports\" /E /I /Q >nul

echo [OK] Backup created: %BACKUP_DIR%

echo [3/4] Uninstalling dependencies...
echo Dependencies to uninstall:
echo - faster-whisper
echo - psutil
echo.
set /p UNINSTALL_DEPS="Uninstall dependencies? (y/n): "
if "!UNINSTALL_DEPS!"=="y" (
    pip uninstall faster-whisper psutil -y
    echo [OK] Dependencies uninstalled
) else (
    echo [!] Dependencies kept
)

echo [4/4] Cleaning up...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
echo [OK] Cleanup complete

echo.
echo Uninstall complete!
echo.
echo Backup: %BACKUP_DIR%
echo.
echo To reinstall:
echo   run install_windows.bat
echo.

rem Open backup folder
echo.
set /p OPEN_BACKUP="Open backup folder? (y/n): "
if "!OPEN_BACKUP!"=="y" (
    explorer "%BACKUP_DIR%"
)

pause
exit /b 0