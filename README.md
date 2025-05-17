# KoemojiAuto - 自動文字起こしシステム

音声・動画ファイルから自動で文字起こしを行うクロスプラットフォーム対応ツールです。
Whisperモデルを使用した高精度な文字起こしを、手動実行で開始し、バックグラウンドで継続動作します。

## 使い方

1. **音声・動画ファイルを配置**
   ```
   inputフォルダに音声・動画ファイルを入れる
   ```

2. **実行方法（3つから選択）**

   ### 方法A: TUIで実行（推奨）
   ```bash
   ./tui.sh  # macOS/Linux
   tui.bat   # Windows
   ```
   TUIから `[r] 実行` を選択

   ### 方法B: コマンドラインで実行
   ```bash
   # 実行（バックグラウンドで動作開始）
   ./start_koemoji.sh  # macOS/Linux
   start_koemoji.bat   # Windows

   # 停止
   ./stop_koemoji.sh   # macOS/Linux
   stop_koemoji.bat    # Windows

   # ステータス確認
   ./status_koemoji.sh # macOS/Linux
   status_koemoji.bat  # Windows
   ```
   ※ 実行後はターミナルを閉じても処理は継続されます

   ### 方法C: Pythonで直接実行（フォアグラウンド）
   ```bash
   python main.py
   ```
   ※ この方法ではターミナルを閉じると処理も停止します（開発・デバッグ用）

3. **文字起こし結果を確認**
   ```
   outputフォルダに text ファイルが生成される
   ```

4. **日次サマリーを確認**
   ```
   reportsフォルダに毎日0時に前日の処理サマリーが生成される
   例: daily_summary_2025-01-17.txt
   ```
   サマリー内容：
   - キュー追加数
   - 処理完了数
   - 処理失敗数
   - 平均処理時間

## 主な機能

- **高精度文字起こし**: Whisperモデル（tiny/small/medium/large）を選択可能
- **バックグラウンド実行**: 起動後はターミナルを閉じても動作継続
- **フレキシブルな実行**: 24時間連続（デフォルト）または時間指定モード
- **ファイルスキャン**: 30分毎にinputフォルダをスキャンして新しいファイルを自動処理
- **シンプルな管理**: TUI（ターミナルUI）で簡単設定・操作
- **安全な制御**: 実行・停止・ステータス確認コマンド
- **クロスプラットフォーム**: Windows/macOS/Linux対応
- **同時実行制御**: 複数プロセスの同時実行を防止
- **ログ記録**: 処理完了やエラーの詳細をログファイルに記録
- **処理済みファイル管理**: 一度処理したファイルは自動的にスキップ
- **エラーリカバリー**: 処理中にエラーが発生しても他のファイルの処理を継続
- **リソース管理**: CPU使用率制限とメモリ効率的な処理
- **日次サマリー**: 毎日0時に前日の処理統計を自動生成

## クイックスタート

### 1. 必要な環境

- Python 3.9以上
- FFmpeg（音声・動画処理用）

### 2. セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/infoHiroki/KoeMojiAuto.git
cd KoeMojiAuto

# 依存関係を自動インストール（推奨）
python install_dependencies.py

# または手動インストール
pip install -r requirements.txt
# FFmpegは別途インストールが必要
```

依存関係インストーラーは以下を自動的に設定します：
- FFmpeg のインストール（OS別に最適な方法を選択）
- Faster Whisper のインストール（GPU/CPU自動判定）
- その他の必要なPythonパッケージ

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
    "input_folder": "input",              // 入力フォルダ（音声・動画ファイルを置く場所）
    "output_folder": "output",            // 出力フォルダ（文字起こしファイルの保存先）
    "continuous_mode": true,              // 実行モード（true: 24時間連続、false: 時間指定）
    "process_start_time": "19:00",        // 開始時刻（continuous_mode=false時のみ有効）
    "process_end_time": "07:00",          // 終了時刻（continuous_mode=false時のみ有効）
    "scan_interval_minutes": 30,          // ファイルスキャン間隔（分）
    "max_concurrent_files": 3,            // 同時処理ファイル数
    "whisper_model": "large",             // Whisperモデルサイズ
    "language": "ja",                     // 言語設定
    "compute_type": "int8",               // 計算精度
    "max_cpu_percent": 80                 // CPU使用率上限（%）
}
```

### 主要設定項目の詳細

#### Whisperモデルサイズ
処理速度と精度のバランスを選択：

| モデル | サイズ | 精度 | 速度 | 推奨用途 |
|--------|--------|------|------|----------|
| tiny   | 39MB   | ★★☆☆☆ | ★★★★★ | 高速処理・字幕確認 |
| small  | 244MB  | ★★★☆☆ | ★★★★☆ | バランス型 |
| medium | 769MB  | ★★★★☆ | ★★★☆☆ | 高品質バランス |
| large  | 1550MB | ★★★★★ | ★★☆☆☆ | 最高精度（推奨） |

#### 計算精度（compute_type）とスペック目安
メモリ使用量とパフォーマンスのバランス：

| 設定 | メモリ使用 | 速度 | 推奨環境 |
|------|------------|------|----------|
| int8 | 低 | 高速 | CPU専用・一般的なPC（8GB RAM以上） |
| float16 | 中 | 中速 | GPU推奨（NVIDIA GPU + 16GB RAM以上） |
| float32 | 高 | 低速 | 高性能GPU推奨（RTX 3060以上 + 32GB RAM） |

**注意事項:**
- **int8**: CPU向けに最適化。GPUがなくても高速動作
- **float16**: GPU（特にNVIDIA）で最も効率的。GPUメモリが必要
- **float32**: 最高精度だが処理速度は遅い。研究用途向け

faster-whisperはCPUとGPU両方に対応していますが、GPU使用にはCUDA対応のNVIDIA GPUが必要です。

**OS別のGPU対応状況:**
- **Windows**: NVIDIA GPUがあれば自動的に使用（CUDA要インストール）
- **Linux**: NVIDIA GPUがあれば自動的に使用（CUDA要インストール）
- **macOS**: Apple Siliconの場合はCPUのみ（Metal/MPSは未対応）

**CUDA環境のセットアップ:**
```bash
# Windows/Linux でGPUを使用する場合
# 1. NVIDIA CUDAツールキットをインストール
# 2. cuDNNをインストール
# 3. PyTorchのGPU版をインストール（自動でインストールされる場合もある）
```

#### 推奨設定例

**CPU環境（macOS/GPUなしのWindows・Linux）**:
```json
{
    "whisper_model": "medium",
    "compute_type": "int8",     // CPUに最適
    "max_concurrent_files": 2,
    "max_cpu_percent": 80
}
```

**GPU搭載PC**（NVIDIA GPU + 16GB RAM）:
```json
{
    "whisper_model": "large",
    "compute_type": "float16",  // GPUに最適
    "max_concurrent_files": 3,
    "max_cpu_percent": 60      // GPUが処理するためCPU負荷は低め
}
```

**ハイエンドGPU搭載PC**（RTX 3080以上 + 32GB RAM）:
```json
{
    "whisper_model": "large",
    "compute_type": "float16",  // float32は精度重視の場合のみ
    "max_concurrent_files": 5,
    "max_cpu_percent": 50
}
```

## 対応ファイル形式

- 音声: MP3, WAV, M4A, FLAC, OGG, AAC
- 動画: MP4, MOV, AVI

## フォルダ構成

```
KoeMojiAuto/
├── input/              # 音声・動画ファイルを配置
├── output/             # 文字起こし結果（.txt）
├── reports/            # 日次サマリー
├── config.json         # 設定ファイル
├── koemoji.log         # 実行ログ
├── processed_files.json # 処理済みファイルリスト
└── koemoji.lock        # プロセスロックファイル（自動生成）
```

## よくある質問（FAQ）

### Q: ファイルが処理されない
A: 以下を確認してください：
- ファイル形式が対応しているか（MP3, WAV, M4A等）
- `processed_files.json`に記録されていないか
- CPU使用率が制限値を超えていないか

### Q: 処理速度を上げたい
A: `config.json`で以下を調整：
- `whisper_model`: "large" → "medium" や "small"
- `max_concurrent_files`: 数値を増やす（CPU負荷注意）
- `compute_type`: GPUがある場合は "float16"

### Q: 特定のファイルだけ再処理したい
A: `processed_files.json`から該当ファイルのエントリを削除

### Q: 起動しているか確認したい
A: `./status_koemoji.sh`（macOS/Linux）または `status_koemoji.bat`（Windows）を実行

### Q: 処理がすぐに始まらない
A: 以下を確認：
- CPU使用率が80%を超えていないか
- 同時処理数の上限に達していないか（デフォルト3ファイル）
- ファイル形式が対応しているか

### Q: 文字起こしの精度を上げたい
A: `whisper_model`を`large`に設定（デフォルト）。ただし処理時間は長くなります

### Q: メモリ不足エラーが出る
A: 以下を試してください：
- `whisper_model`を`medium`や`small`に変更
- `max_concurrent_files`を減らす（例：1〜2）
- `compute_type`を`int8`に設定（デフォルト）

### Q: 日本語以外の音声を処理したい
A: `config.json`の`language`を変更：
- 英語: `"en"`
- 中国語: `"zh"`
- 自動検出: `"auto"`（処理時間増加）

### Q: ログファイルが大きくなりすぎた
A: 自動でローテーションされます（10MBで5ファイル保持）。手動削除も可能

### Q: 処理完了の通知について
A: KoemojiAutoの通知はログファイルに記録される仕様です。
- 全ての通知は`koemoji.log`に「通知:」として記録されます
- 画面への通知（通知センター、ポップアップ等）は表示されません
- 処理状況の確認方法：
  ```bash
  # リアルタイムで確認
  tail -f koemoji.log | grep "通知:"
  
  # 処理完了のみ確認
  tail -f koemoji.log | grep "文字起こし完了"
  ```
- TUIの`[l] ログ表示`からも確認できます

### Q: 再起動後に処理を再開したい
A: 手動で再度実行する必要があります（自動起動機能は削除されました）

### Q: サマリーが生成されない
A: 深夜0時を過ぎてから確認。`reports`フォルダの権限も確認

## トラブルシューティング

### プロセスが停止しない場合
```bash
# 通常の停止
./stop_koemoji.sh   # macOS/Linux
stop_koemoji.bat    # Windows

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

### リセット方法
```bash
# 処理済みファイルリストをクリア
rm processed_files.json

# ロックファイルを削除（起動できない場合）
rm koemoji.lock
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

本ソフトウェアは以下の条件で利用できます：

- **個人利用**: 無料・無制限
- **教育・研究利用**: 無料・無制限  
- **商用利用**: 事前に info.hirokitakamura@gmail.com へご連絡ください

詳細は[LICENSE](LICENSE)ファイルをご確認ください。

## 作者

infoHiroki

## 参考リンク

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)