#!/bin/bash

# KoemojiAuto起動時チェックスクリプト
# 24時間モードの場合のみ起動する

cd "$(dirname "$0")"

# 設定ファイルを読み込む
if [ -f "config.json" ]; then
    # continuous_modeがtrueかチェック
    CONTINUOUS_MODE=$(python3 -c "import json; print(json.load(open('config.json')).get('continuous_mode', False))" 2>/dev/null)
    
    # Python実行がエラーした場合（JSONパースエラーなど）
    if [ $? -ne 0 ]; then
        echo "設定ファイルの読み込みに失敗しました: config.json"
        exit 1
    fi
    
    if [ "$CONTINUOUS_MODE" == "True" ]; then
        echo "24時間モードが有効です。KoemojiAutoを起動します。"
        ./start_koemoji.sh
    else
        echo "時間指定モードです。指定時刻まで待機します。"
    fi
else
    echo "設定ファイルが見つかりません: config.json"
    exit 1
fi