# KoeMojiAuto コードレビューサマリー

実施日: 2025-01-17

## KISS原則に基づく修正提案

### 1. 今すぐ修正すべきバグ

**main.py:615行目**
```python
# バグ: self.today_statsは定義されていない
processed = self.today_stats["processed"]

# 修正
today = datetime.now().strftime("%Y-%m-%d")
processed = self.daily_stats.get(today, {}).get("processed", 0)
```

### 2. シンプルにすべき箇所

#### main.py
- `KoemojiProcessor`クラスが大きすぎる（637行）
- 設定検証が過度に複雑
- エラーメッセージが多すぎる

**簡素化案:**
```python
# 設定検証をシンプルに
def validate_config(self):
    # 必須項目チェックのみ
    required = ["input_folder", "output_folder", "whisper_model", "language"]
    missing = [f for f in required if f not in self.config]
    if missing:
        raise ValueError(f"必須設定が不足: {missing}")
```

#### tui.py
- 未実装のコマンドは削除すべき
  - 'i' (入力フォルダ設定)
  - 'o' (出力フォルダ設定)  
  - 'l' (ログ表示)
  - 'h' (時間設定) - 不完全な実装

**修正案:**
```python
# 動作するコマンドのみ表示
print("Commands:")
print("[r] 実行  [s] 停止  [t] ステータス")
print("[m] モデル変更  [c] モード切替  [q] 終了")
```

### 3. 削除すべきファイル

```
archive/        # 古いスクリプト群を削除
├── check_and_start.sh
├── install.bat
├── install.sh
├── test_abnormal_exit.sh
└── ...
```

### 4. 統合・簡素化すべき機能

#### スクリプトの簡素化
```bash
# stop_koemoji.sh をシンプルに
#!/bin/bash
echo "Stopping KoemojiAuto..."
pkill -f "python.*main.py"
echo "Done"
```

```bash
# status_koemoji.sh をシンプルに
#!/bin/bash
pgrep -f "python.*main.py" && echo "Running" || echo "Not running"
```

### 5. 設定をシンプルに

現在の設定項目が多すぎる。本当に必要な項目のみに絞る：

```json
{
  "input_folder": "./input",
  "output_folder": "./output",
  "whisper_model": "large",
  "language": "ja"
}
```

その他の項目はデフォルト値をコードに埋め込む。

### 6. エラーハンドリングの簡素化

```python
# 過度な例外処理を減らす
try:
    result = process_file(file)
except Exception as e:
    logger.error(f"処理失敗: {file} - {e}")
    # 複雑なリトライロジックは不要
```

### 7. 通知機能の簡素化

現在の通知機能は実質的にログ出力のみ。
通知関連のコードは削除し、ログに統一。

### まとめ

KISS原則に従って：
1. 必須バグ修正を最優先
2. 未実装・不完全な機能は削除
3. 設定項目を最小限に
4. 複雑なエラーハンドリングを簡素化
5. クラスを分割せず、シンプルな関数構成に
6. 古いファイルは削除

これにより、コードは理解しやすく、保守しやすくなります。