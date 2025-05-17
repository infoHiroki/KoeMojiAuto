#!/bin/bash
echo "KoemojiAuto WebUIを起動しています..."
cd "$(dirname "$0")"

if command -v python3 &> /dev/null; then
    python3 webui.py
else
    echo "エラー: Python3が見つかりません"
    exit 1
fi