#!/bin/bash

echo "Stopping KoemojiAuto..."
cd "$(dirname "$0")"

# main.pyを実行しているプロセスを探す
PIDS=$(ps aux | grep -E "python[3]?.*main\.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "KoemojiAuto is not running"
    # ロックファイルが残っていれば削除
    rm -f koemoji.lock
    exit 0
fi

# 見つかったプロセスを停止
for PID in $PIDS; do
    echo "Stopping process $PID..."
    kill "$PID" 2>/dev/null
done

# プロセスが終了するまで少し待つ
sleep 2

# まだ残っていれば強制終了
REMAINING_PIDS=$(ps aux | grep -E "python[3]?.*main\.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$REMAINING_PIDS" ]; then
    echo "Force stopping..."
    for PID in $REMAINING_PIDS; do
        kill -9 "$PID" 2>/dev/null
    done
fi

# ロックファイルを削除
rm -f koemoji.lock

echo "KoemojiAuto stopped successfully"