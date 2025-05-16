#!/usr/bin/env python3
"""代替通知方法のテスト"""

import subprocess
import sys

def show_notification_alternative(title, message):
    """通知センターの代わりにアラートを使用（重要な通知用）"""
    try:
        # 通知センターが使えない場合の代替案
        script = f'''
        tell application "System Events"
            display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" giving up after 3
        end tell
        '''
        subprocess.run(['osascript', '-e', script])
    except Exception as e:
        print(f"エラー: {e}")

def show_terminal_notification(title, message):
    """ターミナルに通知を表示"""
    print(f"\n{'='*50}")
    print(f"🔔 {title}")
    print(f"📢 {message}")
    print('='*50 + '\n')
    
    # ビープ音を鳴らす（オプション）
    try:
        subprocess.run(['osascript', '-e', 'beep'])
    except:
        pass

# テスト
if __name__ == "__main__":
    print("1. 通常の通知（表示されない場合があります）")
    script = 'display notification "Test" with title "KoemojiAuto"'
    subprocess.run(['osascript', '-e', script])
    
    print("\n2. ターミナル内通知")
    show_terminal_notification("KoemojiAuto", "処理が完了しました")
    
    print("\n3. ダイアログ通知（3秒後に自動で閉じます）")
    show_notification_alternative("KoemojiAuto", "重要：すべての処理が完了しました")