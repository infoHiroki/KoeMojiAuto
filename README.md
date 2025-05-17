# KoemojiAuto - 自動文字起こしシステム

音声・動画ファイルから自動で文字起こしを行うクロスプラットフォーム対応ツールです。
Whisperモデルを使用した高精度な文字起こしを、スケジュール実行または24時間連続で実行できます。

## 🌟 v1.3.0 の新機能

- **完全なWindows対応**: ファイルロック機構をOS別に最適化
- **自動ログローテーション**: 10MBでローテーション、5ファイル保持
- **設定ファイル検証**: 起動時に設定値を自動チェック
- **TUIのクロスプラットフォーム対応**: Windowsでもログ表示機能が利用可能

## 主な機能

- **自動文字起こし**: 指定フォルダの音声・動画ファイルを自動検出して処理
- **柔軟なスケジューリング**: 時間指定または24時間連続モード
- **高精度**: Whisperモデル（tiny/small/medium/large）を選択可能
- **シンプルな管理**: TUI（ターミナルUI）で簡単設定
- **クロスプラットフォーム**: Windows/macOS/Linux対応
- **同時実行制御**: 複数プロセスの同時実行を防止
- **通知機能**: 処理完了やエラーを通知

## クイックスタート

### 1. 必要な環境

- Python 3.9以上
- FFmpeg（音声・動画処理用）

### 2. インストール

```bash
# リポジトリをクローン
git clone https://github.com/infoHiroki/KoeMojiAuto.git
cd KoeMojiAuto
```

#### Windows（推奨）
```batch
# 新しいインストーラーを使用
install_windows.bat
```

#### Windows（従来の方法）
```batch
# 依存関係をインストール
pip install -r requirements.txt

# 自動実行を設定
install.bat
```

#### macOS/Linux
```bash
# 依存関係をインストール
pip install -r requirements.txt

# 自動実行を設定（毎日19:00に開始）
./install.sh
```

### 3. TUIで管理

```bash
./tui.sh  # macOS/Linux
tui.bat   # Windows
```

TUI画面：
```
  ╔═══════════════════════════════════════╗
  ║          KoemojiAuto TUI              ║
  ╠═══════════════════════════════════════╣
  ║ 自動実行: 有効                          ║
  ║ 開始時刻: 19:00                        ║
  ║ Mode  : 時間指定 [07:00まで]            ║
  ║ Model : large                         ║
  ╚═══════════════════════════════════════╝

  Commands:
  [r] 実行  [t] 自動ON/OFF  [m] モデル  [c] モード  [h] 時刻設定
  [i] 入力フォルダ  [o] 出力フォルダ  [l] ログ表示  [q] 終了
```

## 使い方

### 基本的な流れ

1. **音声・動画ファイルを配置**
   ```bash
   # inputフォルダに音声・動画ファイルを入れる
   cp your_audio.mp3 input/
   cp your_video.mp4 input/
   ```

2. **手動実行**
   ```bash
   ./start_koemoji.sh  # macOS/Linux
   start_koemoji.bat   # Windows
   ```

3. **結果を確認**
   ```bash
   # outputフォルダに文字起こし結果が保存される
   cat output/your_audio.txt
   ```

### TUIコマンド

- `[r]` - 今すぐ実行
- `[t]` - 自動実行のON/OFF切り替え
- `[m]` - Whisperモデルの変更（tiny/small/medium/large）
- `[c]` - 動作モード切り替え（時間指定/24時間）
- `[h]` - 時刻設定（例: 19-7 で19:00開始、07:00終了）
- `[i]` - 入力フォルダの変更
- `[o]` - 出力フォルダの変更
- `[l]` - ログ表示（最新20行/エラーのみ/本日のログ/全ログ）
- `[q]` - 終了

### 時刻設定の例

TUIで`[h]`を押すと時刻設定ができます：

```
現在: 19:00 → 07:00
時間帯: 20-8

時間帯を 20:00 → 08:00 に変更しました
```

入力形式の例：
- `19-7` → 19:00開始、07:00終了
- `2000-0730` → 20:00開始、07:30終了
- `9-17` → 09:00開始、17:00終了

## 設定ファイル

`config.json`で詳細設定が可能：

```json
{
  "input_folder": "input",
  "output_folder": "output",
  "continuous_mode": false,
  "process_end_time": "07:00",
  "scan_interval_minutes": 30,
  "max_concurrent_files": 3,
  "whisper_model": "large",
  "language": "ja",
  "compute_type": "int8",
  "max_cpu_percent": 95,
  "notification_enabled": true,
  "daily_summary_time": "07:00"
}
```

### 主な設定項目

- `continuous_mode`: 24時間モード（true）または時間指定モード（false）
- `process_end_time`: 時間指定モードでの終了時刻
- `whisper_model`: 使用するモデル（tiny/small/medium/large）
- `scan_interval_minutes`: ファイルスキャン間隔（分）
- `max_concurrent_files`: 同時処理ファイル数
- `notification_enabled`: 通知機能のON/OFF

## 対応ファイル形式

- **音声**: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`
- **動画**: `.mp4`, `.mov`, `.avi`

## ファイル構成

```
KoeMojiAuto/
├── main.py              # メインプログラム
├── tui.py               # ターミナルUI
├── config.json          # 設定ファイル
├── requirements.txt     # Python依存関係
├── install_windows.bat  # Windows用インストーラー（推奨）
├── uninstall_windows.bat # Windows用アンインストーラー（推奨）
├── install.sh/bat       # 自動実行設定
├── uninstall.sh/bat     # 自動実行削除
├── toggle.sh/bat        # 自動実行ON/OFF
├── start_koemoji.sh/bat # 手動実行
├── tui.sh/bat          # TUI起動
├── input/              # 音声・動画ファイルを配置
├── output/             # 文字起こし結果
├── reports/            # 日次レポート
├── koemoji.log         # ログファイル（自動ローテーション）
└── koemoji.lock        # ロックファイル（同時実行制御）
```

## アンインストール

### Windows（推奨）
```batch
# 新しいアンインストーラーを使用（データをバックアップ）
uninstall_windows.bat
```

### 従来の方法
```bash
# 自動実行を削除
./uninstall.sh  # macOS/Linux
uninstall.bat   # Windows

# フォルダを削除（必要に応じて）
rm -rf KoemojiAuto
```

## トラブルシューティング

### FFmpegがインストールされていない

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

### メモリ不足エラー

TUIで`[m]`を押してより小さいモデルに変更：
- `large` → `medium` → `small` → `tiny`

### 文字起こしが開始されない

1. `input/`フォルダにファイルがあるか確認
2. 対応している形式か確認
3. ログファイルでエラーを確認（TUIで`[l]`押下）

### 自動実行の状態確認

```bash
# macOS
launchctl list | grep koemoji

# Windows
schtasks /query /tn "KoemojiAutoProcessor"

# またはTUIで確認
./tui.sh
```

### 複数プロセスが起動してしまう

v1.3.0以降では自動的に防止されますが、古いバージョンの場合：
1. プロセスを終了
2. `koemoji.lock`ファイルを削除
3. 最新版にアップデート

## 開発情報

### テスト実行

```bash
# 全てのテストを実行
python -m pytest tests/ -v

# カバレッジレポート付き
python -m pytest tests/ --cov
```

### バージョン履歴

- **v1.3.0** (2025-05-17)
  - 完全なWindows対応
  - 自動ログローテーション機能
  - 設定ファイル検証
  - TUIの改善

- **v1.2.0** (2025-05-17)
  - 同時実行制御の実装
  - セキュリティ修正

- **v1.0.0** (2025-05)
  - 初回リリース

## ライセンス

本ソフトウェアの商用利用については以下までご連絡ください：
info.hirokitakamura@gmail.com