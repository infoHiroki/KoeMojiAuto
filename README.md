# KoemojiAuto - 自動文字起こしシステム

音声・動画ファイルから自動で文字起こしを行うクロスプラットフォーム対応ツールです。
Whisperモデルを使用した高精度な文字起こしを、手動実行または24時間連続で実行できます。

## 🌟 v2.0.0 の新機能

- **シンプルな手動実行**: 自動実行機能を削除し、より直感的な操作に
- **停止・ステータス機能**: 実行状態の確認と安全な停止が可能
- **改善されたTUI**: 実行状態がひと目でわかるUI
- **軽量化**: インストール不要で即座に使用可能

## 主な機能

- **高精度文字起こし**: Whisperモデル（tiny/small/medium/large）を選択可能
- **フレキシブルな実行**: 24時間連続または時間指定モード
- **シンプルな管理**: TUI（ターミナルUI）で簡単設定・操作
- **安全な制御**: 実行・停止・ステータス確認コマンド
- **クロスプラットフォーム**: Windows/macOS/Linux対応
- **同時実行制御**: 複数プロセスの同時実行を防止
- **通知機能**: 処理完了やエラーを通知

## クイックスタート

### 1. 必要な環境

- Python 3.9以上
- FFmpeg（音声・動画処理用）

### 2. セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/infoHiroki/KoeMojiAuto.git
cd KoeMojiAuto

# 依存関係をインストール
pip install -r requirements.txt
```

### 3. 使い方

#### TUIで管理（推奨）

```bash
./tui.sh  # macOS/Linux
tui.bat   # Windows
```

TUI画面：
```
╔═══════════════════════════════════════╗
║          KoemojiAuto TUI              ║
╠═══════════════════════════════════════╣
║ Status: STOPPED                       ║
║───────────────────────────────────────║
║ Mode  : 24-hour continuous            ║
║ Model : large                         ║
╠═══════════════════════════════════════╣
║ Input : /path/to/input                ║
║ Output: /path/to/output               ║
╚═══════════════════════════════════════╝

Commands:
[r] 実行  [s] 停止  [t] ステータス  [m] モデル  [c] モード
[i] 入力フォルダ  [o] 出力フォルダ  [l] ログ表示  [q] 終了
```

#### コマンドライン操作

```bash
# 実行
./start_koemoji.sh  # macOS/Linux
start_koemoji.bat   # Windows

# 停止
./stop_koemoji.sh   # macOS/Linux
stop_koemoji.bat    # Windows

# ステータス確認
./status_koemoji.sh # macOS/Linux
status_koemoji.bat  # Windows
```

## 動作モード

### 24時間連続モード
一度起動すると、停止するまで継続的にファイルを監視・処理します。

### 時間指定モード
指定した時間範囲内のみ動作します。例：19:00〜07:00

## 設定

`config.json` で詳細な設定が可能：

```json
{
  "input_folder": "input",
  "output_folder": "output",
  "continuous_mode": true,
  "process_start_time": "19:00",
  "process_end_time": "07:00",
  "scan_interval_minutes": 1,
  "max_concurrent_files": 3,
  "whisper_model": "large",
  "language": "ja",
  "compute_type": "int8",
  "max_cpu_percent": 80,
  "notification_enabled": true,
  "daily_summary_time": "07:00"
}
```

## 対応ファイル形式

- 音声: MP3, WAV, M4A, FLAC, OGG, AAC
- 動画: MP4, MOV, AVI

## トラブルシューティング

### プロセスが停止しない場合
```bash
# 強制終了（最終手段）
kill -9 $(cat koemoji.lock)  # Unix/macOS
taskkill /F /PID $(type koemoji.lock)  # Windows
```

### ログの確認
```bash
# 最新のログを表示
tail -n 50 koemoji.log  # Unix/macOS
Get-Content koemoji.log -Tail 50  # Windows PowerShell
```

## 開発者向け

### テストの実行
```bash
pytest tests/
```

### 開発モード
```bash
python main.py
```

## ライセンス

MIT License

## 作者

infoHiroki

## 参考リンク

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)