# KoeMojiAuto コマンド一覧

## 基本操作

### Windows
```batch
rem 起動
start_koemoji.bat

rem 停止
stop_koemoji.bat

rem ステータス確認
status_koemoji.bat

rem ターミナルUI（対話的操作）
tui.bat
```

### macOS/Linux
```bash
# 起動
./start_koemoji.sh

# 停止
./stop_koemoji.sh

# ステータス確認
./status_koemoji.sh

# ターミナルUI（対話的操作）
./tui.sh
```

## デバッグ・監視

### Windows
```batch
rem ログをリアルタイムで監視（PowerShell）
powershell -command "Get-Content koemoji.log -Wait"

rem エラーログのみ表示
findstr ERROR koemoji.log

rem 本日のログのみ表示（PowerShell）
powershell -command "Select-String (Get-Date -Format 'yyyy-MM-dd') koemoji.log"

rem プロセス確認
wmic process where "CommandLine like '%python%main.py%'" get ProcessId,CommandLine
```

### macOS/Linux
```bash
# ログをリアルタイムで監視
tail -f koemoji.log

# エラーログのみ表示
grep ERROR koemoji.log

# 本日のログのみ表示
grep "$(date +%Y-%m-%d)" koemoji.log

# プロセス確認
ps aux | grep -E "[Pp]ython[3]*.*main\.py$"
```

## 直接実行（開発用）

```bash
# フォアグラウンドで実行
python main.py    # Windows
python3 main.py   # macOS/Linux

# 設定確認
type config.json  # Windows
cat config.json   # macOS/Linux
```

## 応用

### Windows
```batch
rem 最新の処理完了ファイル確認（PowerShell）
powershell -command "Select-String '文字起こし完了' koemoji.log | Select-Object -Last 5"

rem 処理キュー状況確認（PowerShell）
powershell -command "Select-String '現在のキュー' koemoji.log | Select-Object -Last 1"

rem 日次サマリー確認
dir reports\
type reports\daily_summary_%date:~0,4%-%date:~5,2%-%date:~8,2%.txt
```

### macOS/Linux
```bash
# 最新の処理完了ファイル確認
grep "文字起こし完了" koemoji.log | tail -5

# 処理キュー状況確認
grep "現在のキュー" koemoji.log | tail -1

# 日次サマリー確認
ls -la reports/
cat reports/daily_summary_$(date +%Y-%m-%d).txt
```