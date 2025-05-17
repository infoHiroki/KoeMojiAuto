#!/bin/bash

echo "Stopping KoemojiAuto..."
cd "$(dirname "$0")"

# 確実にプロセスを停止（python3も含む）
PIDS=$(ps aux | grep -E "[Pp]ython[3]*.*main\.py$" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    for PID in $PIDS; do
        echo "Stopping process $PID..."
        kill "$PID" 2>/dev/null
    done
    
    sleep 2
    
    # まだ残っていれば強制終了（python3も含む）
    REMAINING_PIDS=$(ps aux | grep -E "[Pp]ython[3]*.*main\.py$" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING_PIDS" ]; then
        echo "Force stopping..."
        for PID in $REMAINING_PIDS; do
            kill -9 "$PID" 2>/dev/null
        done
    fi
else
    echo "KoemojiAuto is not running"
fi

# ロックファイルを削除
rm -f koemoji.lock

echo "Done"