#!/bin/bash

echo "=== 多重起動テスト ==="

# クリーンアップ
echo "1. クリーンアップ中..."
./stop_koemoji.sh
rm -f koemoji.lock
sleep 2

# 1回目の起動
echo -e "\n2. 1回目の起動..."
./start_koemoji.sh
sleep 2

# ステータス確認
echo -e "\n3. ステータス確認..."
./status_koemoji.sh

# 2回目の起動を試す
echo -e "\n4. 2回目の起動を試す（ブロックされるはず）..."
./start_koemoji.sh
sleep 2

# 直接Pythonで起動を試す
echo -e "\n5. 直接Pythonで起動を試す（これもブロックされるはず）..."
python3 main.py &
PYTHON_PID=$!
sleep 3
ps -p $PYTHON_PID > /dev/null && echo "エラー: Pythonプロセスが起動してしまった！" || echo "成功: Pythonプロセスはブロックされた"

# プロセス確認
echo -e "\n6. 実行中のプロセス確認..."
ps aux | grep -E "python.*main.py" | grep -v grep

# 停止
echo -e "\n7. 停止..."
./stop_koemoji.sh

# 最終確認
echo -e "\n8. 最終確認..."
ps aux | grep -E "python.*main.py" | grep -v grep
[ -f koemoji.lock ] && echo "エラー: ロックファイルが残っている" || echo "成功: ロックファイルが削除された"

echo -e "\n=== テスト完了 ==="