#!/usr/bin/env python3
"""
Windows環境でのロック機構テスト
"""

import os
import time
import sys
import platform
from pathlib import Path

# OSの判定
IS_WINDOWS = platform.system() == 'Windows'
print(f"OS: {platform.system()}")
print(f"Python: {sys.version}")

# ロックファイルのパス
lock_file_path = Path("test.lock")

def test_lock():
    """ロック機構のテスト"""
    lock_file = None
    
    try:
        print(f"\n[テスト1] ロックファイル作成")
        
        if IS_WINDOWS:
            # Windows: 排他モードでファイルを開く
            try:
                lock_file = open(lock_file_path, 'x')
                print("✓ ロックファイルを作成しました")
            except FileExistsError:
                print("× ロックファイルは既に存在します")
                return False
        else:
            # Unix/Linux/macOS
            import fcntl
            lock_file = open(lock_file_path, 'w')
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            print("✓ ロックファイルを作成しました")
        
        # プロセスIDを書き込む
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        print(f"✓ プロセスID {os.getpid()} を書き込みました")
        
        print("\n[テスト2] 別プロセスからのアクセステスト")
        print("別のターミナルでこのスクリプトを実行して、ロックが機能することを確認してください")
        print("10秒待機します...")
        
        for i in range(10):
            time.sleep(1)
            print(f"{10-i}...")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False
        
    finally:
        if lock_file:
            try:
                lock_file.close()
                print("\n✓ ロックファイルを閉じました")
            except:
                pass
        
        # ロックファイルを削除
        try:
            if lock_file_path.exists():
                os.remove(lock_file_path)
                print("✓ ロックファイルを削除しました")
        except Exception as e:
            print(f"× ロックファイルの削除に失敗: {e}")

def test_existing_lock():
    """既存のロックファイルがある場合のテスト"""
    print("\n[テスト3] 既存のロックファイルのチェック")
    
    if lock_file_path.exists():
        try:
            with open(lock_file_path, 'r') as f:
                pid = int(f.read().strip())
            print(f"既存のロックファイルを検出 (PID: {pid})")
            
            # プロセスが生きているかチェック
            import psutil
            try:
                psutil.Process(pid)
                print(f"× プロセス {pid} は実行中です")
                return False
            except psutil.NoSuchProcess:
                print(f"✓ プロセス {pid} は存在しません - ロックファイルを削除します")
                os.remove(lock_file_path)
                return True
                
        except Exception as e:
            print(f"ロックファイルの読み取りエラー: {e}")
            os.remove(lock_file_path)
            return True
    else:
        print("✓ 既存のロックファイルはありません")
        return True

if __name__ == "__main__":
    print("=== Windowsロック機構テスト ===")
    
    # 既存のロックファイルをチェック
    if not test_existing_lock():
        print("\n別のプロセスが実行中です。終了します。")
        sys.exit(1)
    
    # ロックテスト
    if test_lock():
        print("\n✓ すべてのテストが成功しました")
    else:
        print("\n× テストが失敗しました")