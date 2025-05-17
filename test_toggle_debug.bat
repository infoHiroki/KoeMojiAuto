@echo off
echo Testing schtasks output format and findstr behavior...
echo.

rem Show raw schtasks output
echo === Raw schtasks output ===
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST
echo.

rem Test Status line extraction
echo === Status line extraction ===
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:"
echo.

rem Test if Status contains Disabled
echo === Test if Status contains Disabled ===
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:"
echo.
echo Return code after Status search: %errorlevel%
echo.

rem Save Status line to temp file and test
echo === Test with temp file ===
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:" > temp_status.txt
type temp_status.txt
findstr /i "Disabled" temp_status.txt
echo Return code for Disabled search: %errorlevel%
del temp_status.txt

rem Test combined pipe
echo === Test combined pipe (original method) ===
schtasks /query /tn "KoemojiAutoProcessor" /fo LIST | findstr /i "Status:" | findstr /i "Disabled"
echo Return code for combined pipe: %errorlevel%

rem Test alternative without pipe
echo === Test with FOR loop ===
for /f "tokens=*" %%a in ('schtasks /query /tn "KoemojiAutoProcessor" /fo LIST ^| findstr /i "Status:"') do (
    echo Status line: %%a
    echo %%a | findstr /i "Disabled" >nul
    echo Return code in loop: %errorlevel%
)

pause