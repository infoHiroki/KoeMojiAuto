#!/usr/bin/env python3
"""通知機能の詳細テスト"""

import subprocess
import platform
import os

print(f"Platform: {platform.system()}")
print(f"Python version: {platform.python_version()}")

# 通知センターが有効か確認
def check_notification_center():
    try:
        result = subprocess.run(['defaults', 'read', 'com.apple.notificationcenterui'], 
                              capture_output=True, text=True)
        print("通知センターの設定を読み込みました")
    except Exception as e:
        print(f"通知センターの確認エラー: {e}")

# ターミナルの通知設定を確認
def check_terminal_notifications():
    try:
        bundle_id = subprocess.run(['osascript', '-e', 'id of app "Terminal"'], 
                                 capture_output=True, text=True)
        print(f"Terminal Bundle ID: {bundle_id.stdout.strip()}")
    except Exception as e:
        print(f"Terminal ID確認エラー: {e}")

# シンプルな通知テスト
def test_simple_notification():
    print("\n=== シンプルな通知テスト ===")
    script = 'display notification "Test Message" with title "Test Title"'
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"エラー: {e}")

# アプリケーションを指定した通知テスト
def test_app_notification():
    print("\n=== アプリ指定通知テスト ===")
    script = '''
    tell application "System Events"
        display notification "Test from System Events" with title "KoemojiAuto"
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    except Exception as e:
        print(f"エラー: {e}")

# alertダイアログテスト（通知の代替案）
def test_alert_dialog():
    print("\n=== アラートダイアログテスト ===")
    script = 'display alert "KoemojiAuto" message "これはテストアラートです"'
    try:
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"アラートを表示しました")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_notification_center()
    check_terminal_notifications()
    test_simple_notification()
    test_app_notification()
    # test_alert_dialog()  # これはポップアップが出るのでコメントアウト
    
    print("\n通知が表示されない場合:")
    print("1. システム設定 > 通知とフォーカス でTerminalの通知が有効か確認")
    print("2. おやすみモードがオフになっているか確認")
    print("3. 通知センターに通知が記録されているか確認（画面右上のアイコン）")