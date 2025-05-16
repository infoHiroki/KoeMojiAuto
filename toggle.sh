#!/bin/bash

echo "KoemojiAuto自動実行の状態を切り替えています..."

# OSの判定
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PLIST_FILE="$HOME/Library/LaunchAgents/com.koemoji.auto.plist"
    
    # plistファイルの存在確認
    if [ ! -f "$PLIST_FILE" ]; then
        echo ""
        echo "エラー: 設定が見つかりません。"
        echo "先にinstall.shを実行してください。"
        echo ""
        exit 1
    fi
    
    # 現在の状態を確認
    if launchctl list | grep -q "com.koemoji.auto"; then
        # 有効状態 → 無効化
        echo "現在: 有効"
        launchctl unload "$PLIST_FILE"
        echo "変更後: 無効"
        echo ""
        echo "自動実行を一時停止しました。"
        echo "再開するには、もう一度toggle.shを実行してください。"
    else
        # 無効状態 → 有効化
        echo "現在: 無効"
        launchctl load "$PLIST_FILE"
        echo "変更後: 有効"
        echo ""
        echo "自動実行を再開しました。"
        echo "毎日19時に実行されます。"
    fi
    
else
    # Linux
    # crontabから現在の状態を確認
    if crontab -l 2>/dev/null | grep -q "#.*start_koemoji.sh"; then
        # コメントアウトされている → 有効化
        echo "現在: 無効"
        crontab -l | sed 's/#\(.*start_koemoji.sh\)/\1/' | crontab -
        echo "変更後: 有効"
        echo ""
        echo "自動実行を再開しました。"
        echo "毎日19時に実行されます。"
    elif crontab -l 2>/dev/null | grep -q "start_koemoji.sh"; then
        # 有効状態 → コメントアウト
        echo "現在: 有効"
        crontab -l | sed 's/\(.*start_koemoji.sh\)/#\1/' | crontab -
        echo "変更後: 無効"
        echo ""
        echo "自動実行を一時停止しました。"
        echo "再開するには、もう一度toggle.shを実行してください。"
    else
        echo ""
        echo "エラー: 設定が見つかりません。"
        echo "先にinstall.shを実行してください。"
        echo ""
        exit 1
    fi
fi