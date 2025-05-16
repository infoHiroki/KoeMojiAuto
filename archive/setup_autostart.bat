@echo off
echo KoemojiAuto夜間処理の自動起動を設定しています...

rem 現在のディレクトリを取得
set CURRENT_DIR=%~dp0
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

rem ショートカット作成用のVBScriptを作成
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%STARTUP_FOLDER%\KoemojiNightProcessor.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CURRENT_DIR%start_night_koemoji.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Koemoji自動文字起こし夜間処理" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

rem VBScriptを実行
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo 完了！KoemojiAuto夜間処理が Windows 起動時に自動的に開始されます。
echo.
echo 注: システム起動時に最初のスキャンが実行されますが、
echo     実際の処理は夜間時間帯（設定ファイルで指定）に行われます。
pause
