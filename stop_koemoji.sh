#!/bin/bash

echo "Stopping KoemojiAuto..."

# ロックファイルからプロセスIDを取得
LOCK_FILE="koemoji.lock"

if [ ! -f "$LOCK_FILE" ]; then
    echo "KoemojiAuto is not running"
    exit 0
fi

# プロセスIDを読み取る
PID=$(cat "$LOCK_FILE" 2>/dev/null)

if [ -z "$PID" ]; then
    echo "Could not read process ID from lock file"
    exit 1
fi

# プロセスが実行中か確認
if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping process $PID..."
    # グレースフルシャットダウン（SIGTERM）
    kill "$PID"
    
    # プロセスが終了するまで待つ（最大10秒）
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "KoemojiAuto stopped successfully"
            exit 0
        fi
        sleep 1
    done
    
    # 強制終了が必要な場合
    echo "Force stopping..."
    kill -9 "$PID"
    sleep 1
    
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "KoemojiAuto stopped"
    else
        echo "Failed to stop KoemojiAuto"
        exit 1
    fi
else
    echo "Process $PID is not running"
    # ロックファイルをクリーンアップ
    rm -f "$LOCK_FILE"
fi