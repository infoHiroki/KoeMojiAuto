#!/bin/bash

echo "=== インタラクティブテスト ==="
echo "各ステップで確認しながら進めます"

function wait_for_enter() {
    echo -e "\n[Enterキーを押して続行...]"
    read
}

# クリーンアップ
echo "1. クリーンアップ"
./stop_koemoji.sh
rm -f koemoji.lock
wait_for_enter

# 起動
echo "2. 起動します"
./start_koemoji.sh
wait_for_enter

# ログ確認
echo "3. ログを確認（Ctrl+Cで終了）"
tail -f koemoji.log | grep -E "(通知:|エラー:|開始|終了)" &
TAIL_PID=$!
wait_for_enter
kill $TAIL_PID 2>/dev/null

# ステータス
echo "4. ステータス確認"
./status_koemoji.sh
wait_for_enter

# 多重起動テスト
echo "5. 多重起動を試します"
./start_koemoji.sh
echo "直接Pythonでも試します..."
python3 main.py
wait_for_enter

# プロセス確認
echo "6. プロセス一覧"
ps aux | grep -E "python.*main.py" | grep -v grep
wait_for_enter

# 停止
echo "7. 停止します"
./stop_koemoji.sh
wait_for_enter

echo "=== テスト完了 ==="