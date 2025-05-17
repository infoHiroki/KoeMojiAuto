#!/bin/bash

echo "=== ロックファイル動作テスト ==="

# 1. 偽のロックファイルを作成
echo -e "\n1. 偽のロックファイルを作成（存在しないPID）..."
echo "99999" > koemoji.lock
echo "ロックファイル作成: PID=99999"

# 2. 起動を試す（古いロックファイルは削除されるはず）
echo -e "\n2. 起動を試す..."
./start_koemoji.sh
sleep 2

# 3. ロックファイルの内容を確認
echo -e "\n3. 現在のロックファイルの内容..."
if [ -f koemoji.lock ]; then
    echo "PID: $(cat koemoji.lock)"
    ps -p $(cat koemoji.lock) | grep -v PID
else
    echo "ロックファイルが存在しません"
fi

# 4. 停止
echo -e "\n4. 停止..."
./stop_koemoji.sh

echo -e "\n=== テスト完了 ==="