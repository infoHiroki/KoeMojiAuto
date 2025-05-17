#!/bin/bash

echo "KoemojiAutoのアンインストールを開始します..."
echo

# cronから削除
echo "cronエントリを確認しています..."
if crontab -l 2>/dev/null | grep -q "KoemojiAuto"; then
    echo "cronエントリを削除しています..."
    crontab -l | grep -v "KoemojiAuto" | crontab -
    echo "cronエントリを削除しました。"
else
    echo "cronエントリは見つかりませんでした。"
fi

# launchdから削除
PLIST_FILE="$HOME/Library/LaunchAgents/com.koemoji.auto.plist"
if [ -f "$PLIST_FILE" ]; then
    echo "launchdエントリを削除しています..."
    launchctl unload "$PLIST_FILE" 2>/dev/null
    rm "$PLIST_FILE"
    echo "launchdエントリを削除しました。"
else
    echo "launchdエントリは見つかりませんでした。"
fi

echo
echo "アンインストールが完了しました。"
echo "このフォルダ（$(dirname "$0")）を手動で削除してください："
echo "rm -rf $(dirname "$0")"
echo