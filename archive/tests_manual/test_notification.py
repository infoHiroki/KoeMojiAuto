#!/usr/bin/env python3
"""通知機能のテスト"""

from main import KoemojiProcessor

# プロセッサーを初期化
processor = KoemojiProcessor()

# テスト通知を送信
processor.send_notification(
    "KoemojiAutoテスト",
    "macOS通知機能が正常に動作しています！"
)

print("通知を送信しました。画面右上に表示されるはずです。")