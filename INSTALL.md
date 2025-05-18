# インストール手順

## 必要なもの
- Python 3.9以上
- ffmpeg（音声・動画ファイルの処理に必要）

## セットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/KoemojiAuto.git
cd KoemojiAuto
```

### 2. ffmpegのインストール

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
[公式サイト](https://ffmpeg.org/download.html)からダウンロードしてPATHに追加

### 3. Python依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 初期設定
```bash
cp config.json.sample config.json
```

設定ファイルを編集して、必要に応じて以下を調整：
- `whisper_model`: "tiny", "small", "medium", "large" から選択

### 5. フォルダの準備
入力フォルダと出力フォルダは自動的に作成されます。

## 実行

### WebUI（推奨）
```bash
# macOS/Linux
./start_webui.sh

# Windows
start_webui.bat
```

ブラウザで http://localhost:8080 にアクセス

### TUI
```bash
# macOS/Linux
./tui.sh

# Windows
tui.bat
```

### コマンドライン
```bash
# 開始
./start_koemoji.sh  # macOS/Linux
start_koemoji.bat   # Windows

# 停止
./stop_koemoji.sh   # macOS/Linux
stop_koemoji.bat    # Windows
```

## トラブルシューティング

### Whisperモデルのダウンロードが遅い
初回実行時はモデルのダウンロードに時間がかかります。
小さいモデル（tiny, small）から始めることをおすすめします。

### メモリ不足エラー
より小さいモデルを使用するか、`max_concurrent_files`を減らしてください。

### ffmpegが見つからない
ffmpegがPATHに追加されているか確認してください：
```bash
ffmpeg -version
```