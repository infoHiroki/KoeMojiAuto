# KoemojiAuto - 自動文字起こしシステム

音声・動画ファイルの文字起こしを自動処理するクロスプラットフォーム対応ツールです。
Whisper（large）モデルによる高精度な文字起こしを、時間指定または24時間連続で実行できます。

## 主な特徴

- 🎯 指定フォルダの音声・動画ファイルを自動検出
- 🔄 30分ごとの定期スキャンで新規ファイルを即座に処理
- 🚀 Whisperモデル（large）による高精度な文字起こし
- 📊 優先度に基づいた効率的な処理順序
- 📈 日次レポートの自動生成
- ⏰ 時間制限モードと24時間連続モードの選択可能
- 💻 Windows/macOS/Linux対応

## インストール

### 1. 必要なシステム要件

- **Python 3.8以上**
- **FFmpeg** (音声・動画処理に必須)

### 2. FFmpegのインストール

**Windows**
```cmd
# Chocolateyを使う場合
choco install ffmpeg

# または公式サイトからダウンロード
# https://ffmpeg.org/download.html
```

**macOS**
```bash
# Homebrewを使う場合
brew install ffmpeg
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Pythonパッケージのインストール

```bash
git clone https://github.com/your-repo/KoemojiAuto.git
cd KoemojiAuto
pip install -r requirements.txt
```

### 4. GPU使用時の追加設定（オプション）

NVIDIA GPUを使用する場合：
```bash
# CUDA対応版のfaster-whisperをインストール
pip install faster-whisper[gpu]
```

## 使い方

### 基本的な使用手順

1. **音声・動画ファイルを準備**
   ```bash
   # inputフォルダにファイルを配置
   cp your_audio.mp3 input/
   cp your_video.mp4 input/
   ```

2. **手動実行**
   
   **Windows**
   ```cmd
   start_koemoji.bat
   ```
   
   **macOS/Linux**
   ```bash
   ./start_koemoji.sh
   # または
   python main.py
   ```

3. **結果確認**
   ```bash
   # outputフォルダで文字起こし結果を確認
   ls output/
   cat output/your_audio.txt
   ```

### 対応ファイル形式

- 音声: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`
- 動画: `.mp4`, `.mov`, `.avi`

## 自動実行設定

### Windows - タスクスケジューラ

**自動設定（推奨）**
```cmd
# 管理者権限で実行
setup_scheduled_task.bat
```

これで毎日19:00に自動起動します。

### macOS/Linux - cron

```bash
# crontabを編集
crontab -e

# 以下を追加（パスは環境に合わせて変更）
0 19 * * * /path/to/KoemojiAuto/start_koemoji.sh
```

### Linux - systemdサービス（24時間モード推奨）

1. サービスファイル作成: `/etc/systemd/system/koemoji-auto.service`
```ini
[Unit]
Description=KoemojiAuto Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/KoemojiAuto/main.py
WorkingDirectory=/path/to/KoemojiAuto
Restart=always
User=username

[Install]
WantedBy=multi-user.target
```

2. サービスの有効化と起動
```bash
sudo systemctl daemon-reload
sudo systemctl enable koemoji-auto
sudo systemctl start koemoji-auto
```

## 設定

`config.json`で詳細な動作を設定できます：

```json
{
  "input_folder": "input",          // 入力フォルダ
  "output_folder": "output",        // 出力フォルダ
  "continuous_mode": false,         // 24時間モード（false=時間制限モード）
  "process_end_time": "07:00",      // 終了時刻（時間制限モードのみ）
  "scan_interval_minutes": 30,      // ファイルスキャン間隔
  "max_concurrent_files": 3,        // 同時処理ファイル数
  "whisper_model": "large",         // Whisperモデル（tiny/small/medium/large）
  "language": "ja",                 // 言語設定
  "compute_type": "int8",           // 計算精度
  "max_cpu_percent": 95,            // CPU使用率上限
  "notification_enabled": true,     // デスクトップ通知
  "daily_summary_time": "07:00"     // 日次サマリー生成時刻
}
```

### 動作モード

#### 1. 時間制限モード（デフォルト）
- `continuous_mode: false`
- タスクスケジューラ/cronで指定時刻に起動
- `process_end_time`で設定した時刻に自動終了
- 夜間処理に最適

#### 2. 24時間連続モード
- `continuous_mode: true`
- 常時実行し続ける
- 毎日`daily_summary_time`に日次サマリーを生成
- リアルタイム処理に最適

## 優先度システム

処理順序は以下の要素で決定されます：

1. **ファイル名のキーワード**（+5ポイント）
   - `urgent` (緊急)
   - `priority` (優先)
   - `important` (重要)
   
2. **ファイルサイズ**
   - 10MB未満: +3ポイント
   - 50MB未満: +2ポイント
   - 100MB未満: +1ポイント

例: `urgent_meeting_20240105.mp3` は優先的に処理されます

## トラブルシューティング

### よくある問題と解決方法

1. **文字起こしが開始されない**
   - FFmpegがインストールされているか確認: `ffmpeg -version`
   - inputフォルダにファイルがあるか確認
   - 対応しているファイル形式か確認

2. **メモリ不足エラー**
   ```json
   // config.jsonでモデルサイズを調整
   "whisper_model": "medium"  // またはsmall
   ```

3. **CPU使用率が高すぎる**
   ```json
   // config.jsonで制限を調整
   "max_cpu_percent": 70,
   "max_concurrent_files": 1
   ```

4. **文字起こし精度が低い**
   ```json
   // より大きなモデルを使用
   "whisper_model": "large"
   ```

### ログの確認

```bash
# リアルタイムでログを監視
tail -f koemoji.log

# エラーのみ表示
grep ERROR koemoji.log
```

## 実際の運用例

### 例1: 毎晩の配信アーカイブ処理
```json
{
  "continuous_mode": false,
  "process_end_time": "06:00",
  "max_concurrent_files": 2,
  "whisper_model": "large"
}
```
- 19:00〜06:00に処理
- 配信終了後にファイルを投入
- 朝までに高精度で処理完了

### 例2: 24時間リアルタイム処理
```json
{
  "continuous_mode": true,
  "scan_interval_minutes": 10,
  "max_concurrent_files": 1,
  "whisper_model": "medium"
}
```
- 常時監視
- 10分ごとに新規ファイルチェック
- バランスの取れた処理

## ファイル構成

```
KoemojiAuto/
├── main.py                  # メインプログラム
├── config.json              # 設定ファイル
├── requirements.txt         # Python依存関係
├── setup_scheduled_task.bat # Windows自動起動設定
├── start_koemoji.bat        # Windows実行スクリプト
├── start_koemoji.sh         # Unix/Linux実行スクリプト
├── input/                   # 入力フォルダ（音声・動画を配置）
├── output/                  # 出力フォルダ（文字起こし結果）
├── reports/                 # レポートフォルダ（日次サマリー）
└── koemoji.log             # ログファイル
```

## アンインストール

### Windows

**自動アンインストール（推奨）**
```cmd
uninstall.bat
```

**手動アンインストール**
1. タスクスケジューラから削除
   ```cmd
   # 管理者権限で実行
   schtasks /delete /tn "KoemojiAutoProcessor" /f
   ```

2. フォルダを削除
   ```cmd
   rmdir /s /q KoemojiAuto
   ```

### macOS/Linux

**自動アンインストール（推奨）**
```bash
./uninstall.sh
```

**手動アンインストール**
1. cronから削除
   ```bash
   # crontabを編集
   crontab -e
   # KoemojiAuto関連の行を削除
   ```

2. systemdサービスから削除（Linuxの場合）
   ```bash
   sudo systemctl stop koemoji-auto
   sudo systemctl disable koemoji-auto
   sudo rm /etc/systemd/system/koemoji-auto.service
   sudo systemctl daemon-reload
   ```

3. launchdから削除（macOSの場合）
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.koemoji.auto.plist
   rm ~/Library/LaunchAgents/com.koemoji.auto.plist
   ```

4. フォルダを削除
   ```bash
   rm -rf KoemojiAuto
   ```

### Pythonパッケージのアンインストール（オプション）

インストールしたPythonパッケージを削除する場合：
```bash
pip uninstall faster-whisper psutil notifypy
```

## ライセンス

本ソフトウェアの商用利用をご希望の場合は、以下までご連絡ください：
info.hirokitakamura@gmail.com

## 貢献

プルリクエストを歓迎します。大きな変更を行う場合は、まずissueを作成して変更内容について議論してください。