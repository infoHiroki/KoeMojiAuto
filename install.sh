#!/bin/bash

echo "KoemojiAuto自動起動設定をインストールしています..."

# 現在のディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# OSの判定
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "macOS環境を検出しました"
    
    # LaunchAgent設定
    PLIST_FILE="$HOME/Library/LaunchAgents/com.koemoji.auto.plist"
    
    # plistファイルの作成
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.koemoji.auto</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/start_koemoji.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/launchd.error.log</string>
</dict>
</plist>
EOF

    # LaunchAgentを読み込む
    launchctl unload "$PLIST_FILE" 2>/dev/null
    launchctl load "$PLIST_FILE"
    
    echo "完了！毎日19時にKoemojiAuto処理が自動的に開始されます。"
    echo "設定を確認: launchctl list | grep koemoji"
    
else
    # Linux
    echo "Linux環境を検出しました"
    
    # crontabに追加
    CRON_CMD="0 19 * * * $SCRIPT_DIR/start_koemoji.sh"
    
    # 既存のcrontabを取得
    crontab -l > /tmp/current_cron 2>/dev/null || true
    
    # 既に登録されているかチェック
    if grep -q "start_koemoji.sh" /tmp/current_cron; then
        echo "既に登録されています"
    else
        echo "$CRON_CMD" >> /tmp/current_cron
        crontab /tmp/current_cron
        echo "crontabに登録しました"
    fi
    
    rm -f /tmp/current_cron
    
    echo "完了！毎日19時にKoemojiAuto処理が自動的に開始されます。"
    echo "設定を確認: crontab -l"
fi

# 実行権限を付与
chmod +x "$SCRIPT_DIR/start_koemoji.sh"

echo ""
echo "手動実行: $SCRIPT_DIR/start_koemoji.sh"