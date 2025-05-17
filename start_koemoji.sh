#!/bin/bash
echo "KoemojiAuto処理を開始しています..."
cd "$(dirname "$0")"

# Pythonコマンドの存在確認
if command -v python3 &> /dev/null; then
    nohup python3 main.py > /dev/null 2>&1 &
    echo "KoemojiAutoがバックグラウンドで起動しました。"
    echo "ステータス確認: ./status_koemoji.sh"
    echo "停止: ./stop_koemoji.sh"
elif command -v python &> /dev/null; then
    nohup python main.py > /dev/null 2>&1 &
    echo "KoemojiAutoがバックグラウンドで起動しました。"
    echo "ステータス確認: ./status_koemoji.sh"
    echo "停止: ./stop_koemoji.sh"
else
    echo "エラー: Pythonが見つかりません"
    exit 1
fi