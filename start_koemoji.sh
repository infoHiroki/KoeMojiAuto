#!/bin/bash
echo "KoemojiAuto処理を開始しています..."
cd "$(dirname "$0")"

# Pythonコマンドの存在確認
if command -v python3 &> /dev/null; then
    python3 main.py
elif command -v python &> /dev/null; then
    python main.py
else
    echo "エラー: Pythonが見つかりません"
    exit 1
fi