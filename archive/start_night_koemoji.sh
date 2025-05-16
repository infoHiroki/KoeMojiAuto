#!/bin/bash
echo "KoemojiAuto夜間処理を開始しています..."
python3 "$(dirname "$0")/night_processor.py"
