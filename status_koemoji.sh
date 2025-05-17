#!/bin/bash

echo "KoemojiAuto Status"
echo "=================="

# ロックファイルを確認
LOCK_FILE="koemoji.lock"

if [ ! -f "$LOCK_FILE" ]; then
    echo "Status: Not running"
    exit 0
fi

# プロセスIDを読み取る
PID=$(cat "$LOCK_FILE" 2>/dev/null)

if [ -z "$PID" ]; then
    echo "Status: Unknown (cannot read lock file)"
    exit 1
fi

# プロセスが実行中か確認
if kill -0 "$PID" 2>/dev/null; then
    echo "Status: Running"
    echo "Process ID: $PID"
    
    # プロセスの詳細情報
    if command -v ps &> /dev/null; then
        echo ""
        echo "Process details:"
        ps -p "$PID" -o pid,ppid,start,etime,command 2>/dev/null | grep -v "PID"
    fi
    
    # メモリ使用量
    if command -v ps &> /dev/null; then
        echo ""
        echo "Memory usage:"
        ps -p "$PID" -o pid,vsz,rss,%mem 2>/dev/null | grep -v "PID"
    fi
    
    # 最新のログ
    LOG_FILE="koemoji.log"
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "Recent log entries:"
        tail -n 5 "$LOG_FILE"
    fi
else
    echo "Status: Not running"
    echo "Note: Stale lock file found. Cleaning up..."
    rm -f "$LOCK_FILE"
fi