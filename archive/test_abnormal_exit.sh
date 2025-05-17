#!/bin/bash

echo "=== 異常終了シミュレーション ==="

# 1. 起動
echo -e "\n1. 起動..."
./start_koemoji.sh
sleep 2

# 2. PIDを取得
PID=$(cat koemoji.lock)
echo -e "\n2. 現在のPID: $PID"

# 3. 強制終了（kill -9）でプロセスだけ停止
echo -e "\n3. プロセスを強制終了（ロックファイルは残る）..."
kill -9 $PID
sleep 1

# 4. ロックファイルの状態確認
echo -e "\n4. ロックファイルの状態..."
[ -f koemoji.lock ] && echo "ロックファイルが残っています" || echo "ロックファイルはありません"

# 5. 再起動を試す（古いロックファイルを自動削除するはず）
echo -e "\n5. 再起動を試す..."
./start_koemoji.sh
sleep 2

# 6. ステータス確認
echo -e "\n6. ステータス確認..."
./status_koemoji.sh

# 7. 正常停止
echo -e "\n7. 正常停止..."
./stop_koemoji.sh

echo -e "\n=== テスト完了 ==="