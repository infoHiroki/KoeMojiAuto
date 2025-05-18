#!/bin/bash

echo "Stopping KoemojiAuto..."
cd "$(dirname "$0")"

# 確実にプロセスを停止（python3も含む）
PIDS=$(ps aux | grep -E "[Pp]ython[3]*.*main\.py$" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    for PID in $PIDS; do
        echo "停止しています...　$PID..."
        kill "$PID" 2>/dev/null
    done
    
    sleep 5
    
    # まだ残っていれば強制終了（python3も含む）
    REMAINING_PIDS=$(ps aux | grep -E "[Pp]ython[3]*.*main\.py$" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING_PIDS" ]; then
        echo "強制終了中..."
        for PID in $REMAINING_PIDS; do
            kill -9 "$PID" 2>/dev/null
        done
    fi
else
    echo "KoemojiAutoは実行されていません。"
fi

echo "停止処理が完了しました。"