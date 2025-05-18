#!/bin/bash
echo "KoemojiAuto処理を開始しています..."
cd "$(dirname "$0")"

# Pythonコマンドの存在確認
if command -v python3 &> /dev/null; then
    nohup python3 main.py >> koemoji.log 2>&1 &
    echo "KoemojiAutoがバックグラウンドで起動しました。"
else
    echo "エラー: Python3が見つかりません"
    exit 1
fi