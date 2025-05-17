#!/bin/bash

echo "KoemojiAuto Status"
echo "=================="

# main.pyを実行しているプロセスを探す
PIDS=$(ps aux | grep -E "python[3]?.*main\.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "Status: Not running"
    exit 0
fi

echo "Status: Running"
echo "Process ID(s): $PIDS"

# プロセスの詳細情報
echo ""
echo "Process details:"
for PID in $PIDS; do
    ps -p "$PID" -o pid,ppid,start,etime,command 2>/dev/null | grep -v "PID"
done

# メモリ使用量
echo ""
echo "Memory usage:"
for PID in $PIDS; do
    ps -p "$PID" -o pid,vsz,rss,%mem 2>/dev/null | grep -v "PID"
done

# 最新のログ
LOG_FILE="koemoji.log"
if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "Recent log entries:"
    tail -n 5 "$LOG_FILE"
fi