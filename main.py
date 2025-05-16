#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KoemojiAuto - 自動文字起こしシステム
音声・動画ファイルの文字起こしを自動処理
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, time as datetime_time
import psutil

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("koemoji.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KoemojiAuto")

class KoemojiProcessor:
    def __init__(self, config_path="config.json"):
        """初期化"""
        self.config_path = config_path
        self.load_config()
        self.processing_queue = []
        self.processed_files = set()
        
        # 処理済みファイル記録の読み込み
        self.processed_history_path = Path("processed_files.json")
        self.load_processed_history()
        
        # 処理中のファイル
        self.files_in_process = set()
        
        # 今日の処理統計
        self.today_stats = {
            "queued": 0,
            "processed": 0,
            "failed": 0,
            "total_duration": 0,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def load_config(self):
        """設定ファイルを読み込む"""
        try:
            if not os.path.exists(self.config_path):
                # デフォルト設定を作成
                self.config = {
                    "input_folder": "input",
                    "output_folder": "output",
                    "process_end_time": "07:00",
                    "scan_interval_minutes": 30,
                    "max_concurrent_files": 3,
                    "whisper_model": "large",
                    "language": "ja",
                    "compute_type": "int8",
                    "max_cpu_percent": 95,
                    "notification_enabled": True,
                    "daily_summary_time": "07:00"
                }
                # 設定を保存
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                logger.info(f"デフォルト設定を作成しました: {self.config_path}")
            else:
                # 既存の設定を読み込み
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"設定を読み込みました: {self.config_path}")
                
            # 入力・出力フォルダの確認と作成
            for folder_key in ["input_folder", "output_folder"]:
                folder_path = self.config.get(folder_key)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    logger.info(f"{folder_key}を作成しました: {folder_path}")
                    
            # レポートフォルダの作成
            if not os.path.exists("reports"):
                os.makedirs("reports", exist_ok=True)
                logger.info("レポートフォルダを作成しました: reports")
                    
        except Exception as e:
            logger.error(f"設定の読み込み中にエラーが発生しました: {e}")
            # 最小限のデフォルト設定
            self.config = {
                "input_folder": "input",
                "output_folder": "output",
                "process_end_time": "07:00",
                "max_concurrent_files": 1,
                "whisper_model": "tiny",
                "language": "ja"
            }
    
    def load_processed_history(self):
        """処理済みファイルの履歴を読み込む"""
        try:
            if self.processed_history_path.exists():
                with open(self.processed_history_path, 'r', encoding='utf-8') as f:
                    self.processed_files = set(json.load(f))
            else:
                self.processed_files = set()
        except Exception as e:
            logger.error(f"処理済み履歴の読み込みエラー: {e}")
            self.processed_files = set()
    
    def save_processed_history(self):
        """処理済みファイルの履歴を保存する"""
        try:
            with open(self.processed_history_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_files), f)
        except Exception as e:
            logger.error(f"処理済み履歴の保存エラー: {e}")
    
    def get_end_time(self):
        """終了時刻を取得"""
        end_time_str = self.config.get("process_end_time", "07:00")
        hour, minute = map(int, end_time_str.split(":"))
        return datetime_time(hour, minute)
    
    def scan_and_queue_files(self):
        """入力フォルダをスキャンしてファイルをキューに追加"""
        try:
            logger.debug("入力フォルダのスキャンを開始します")
            
            input_folder = self.config.get("input_folder")
            if not os.path.exists(input_folder):
                logger.warning(f"入力フォルダが存在しません: {input_folder}")
                os.makedirs(input_folder, exist_ok=True)
                return
            
            # メディアファイルの拡張子
            media_extensions = ('.mp3', '.mp4', '.wav', '.m4a', '.mov', '.avi', '.flac', '.ogg', '.aac')
            
            # 新しいファイルを検出
            new_files = []
            for file in os.listdir(input_folder):
                file_path = os.path.join(input_folder, file)
                
                # ディレクトリはスキップ
                if os.path.isdir(file_path):
                    continue
                
                # 対象拡張子のファイルのみ処理
                if not file.lower().endswith(media_extensions):
                    continue
                
                # 既に処理済みまたは処理中、キュー済みのファイルはスキップ
                file_id = f"{file}_{os.path.getsize(file_path)}"
                if file_id in self.processed_files or file_path in self.files_in_process or any(f["path"] == file_path for f in self.processing_queue):
                    continue
                
                new_files.append(file_path)
            
            if not new_files:
                logger.debug("新しいファイルはありません")
                return
            
            # キューに追加
            for file_path in new_files:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # ファイル情報のメタデータを作成
                file_info = {
                    "path": file_path,
                    "name": file_name,
                    "size": file_size,
                    "queued_at": datetime.now().isoformat(),
                    "priority": self.calculate_priority(file_path)
                }
                
                self.processing_queue.append(file_info)
                logger.info(f"キューに追加: {file_name} (優先度: {file_info['priority']})")
                
                # 今日の統計を更新
                self.today_stats["queued"] += 1
            
            # 優先度に基づいてキューを並べ替え
            self.processing_queue.sort(key=lambda x: x["priority"], reverse=True)
            
            logger.info(f"現在のキュー: {len(self.processing_queue)}件")
            
        except Exception as e:
            logger.error(f"キュースキャン中にエラーが発生しました: {e}")
    
    def calculate_priority(self, file_path):
        """ファイルの処理優先度を計算"""
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        priority = 0
        
        # サイズが小さいファイルを優先
        if file_size < 1024 * 1024 * 10:  # 10MB未満
            priority += 3
        elif file_size < 1024 * 1024 * 50:  # 50MB未満
            priority += 2
        elif file_size < 1024 * 1024 * 100:  # 100MB未満
            priority += 1
        
        # 優先キーワードを含むファイル名を優先
        priority_keywords = ["urgent", "priority", "important", "緊急", "優先"]
        for keyword in priority_keywords:
            if keyword.lower() in file_name.lower():
                priority += 5
                break
        
        return priority
    
    def process_queued_files(self):
        """キューにあるファイルを処理"""
        try:
            if not self.processing_queue:
                logger.debug("処理すべきファイルはありません")
                return
            
            # 同時処理数を確認
            max_concurrent = self.config.get("max_concurrent_files", 3)
            current_running = len(self.files_in_process)
            available_slots = max(0, max_concurrent - current_running)
            
            if available_slots <= 0:
                logger.debug("同時処理数の上限に達しています")
                return
            
            # リソース使用状況を確認
            cpu_percent = psutil.cpu_percent()
            max_cpu = self.config.get("max_cpu_percent", 95)
            
            if cpu_percent > max_cpu:
                logger.info(f"CPU使用率が高すぎるため、処理を延期します: {cpu_percent}%")
                return
            
            # 処理するファイル数を決定
            files_to_process = self.processing_queue[:available_slots]
            
            # Whisperモデルを取得
            model_size = self.config.get("whisper_model", "large")
            
            # ファイルを処理
            for file_info in files_to_process:
                file_path = file_info["path"]
                # キューから削除
                self.processing_queue = [f for f in self.processing_queue if f["path"] != file_path]
                
                # 処理開始
                self.process_file(file_path, model_size)
        
        except Exception as e:
            logger.error(f"キュー処理中にエラーが発生しました: {e}")
    
    def process_file(self, file_path, model_size=None):
        """ファイルを処理する"""
        start_time = time.time()
        try:
            # ファイルが存在するか確認
            if not os.path.exists(file_path):
                logger.warning(f"ファイルが存在しません: {file_path}")
                return
            
            # 処理中リストに追加
            self.files_in_process.add(file_path)
            file_name = os.path.basename(file_path)
            logger.info(f"ファイル処理開始: {file_name} (モデル: {model_size})")
            
            # 文字起こし処理を実行
            transcription = self.transcribe_audio(file_path, model_size)
            
            if transcription:
                # 出力ファイルパスを生成
                output_folder = self.config.get("output_folder")
                output_file = os.path.join(
                    output_folder, 
                    f"{os.path.splitext(file_name)[0]}.txt"
                )
                
                # 出力ディレクトリが存在するか確認
                os.makedirs(output_folder, exist_ok=True)
                
                # 結果を保存
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                
                # 処理時間を計算
                processing_time = time.time() - start_time
                logger.info(f"文字起こし完了: {file_name} -> {output_file} (処理時間: {processing_time:.2f}秒)")
                
                # 処理済みリストに追加
                file_id = f"{file_name}_{os.path.getsize(file_path)}"
                self.processed_files.add(file_id)
                self.save_processed_history()
                
                # 今日の統計を更新
                self.today_stats["processed"] += 1
                self.today_stats["total_duration"] += processing_time
                
                # 通知
                if self.config.get("notification_enabled", True):
                    self.send_notification(
                        "Koemoji文字起こし完了",
                        f"ファイル: {file_name}\n出力: {output_file}\n処理時間: {processing_time:.2f}秒"
                    )
            else:
                logger.error(f"文字起こし失敗: {file_name}")
                # 今日の統計を更新
                self.today_stats["failed"] += 1
                
                # エラー通知
                if self.config.get("notification_enabled", True):
                    self.send_notification(
                        "Koemoji文字起こしエラー",
                        f"ファイル: {file_name}\n処理に失敗しました。"
                    )
        
        except Exception as e:
            logger.error(f"ファイル処理中にエラーが発生しました: {file_path} - {e}")
            # 今日の統計を更新
            self.today_stats["failed"] += 1
            
            # エラー通知
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    "Koemoji処理エラー",
                    f"ファイル: {os.path.basename(file_path)}\nエラー: {e}"
                )
        finally:
            # 処理中リストから削除
            if file_path in self.files_in_process:
                self.files_in_process.remove(file_path)
    
    def transcribe_audio(self, file_path, model_size=None):
        """音声ファイルを文字起こし"""
        try:
            from faster_whisper import WhisperModel
            
            # モデルサイズとコンピュートタイプを設定
            model_size = model_size or self.config.get("whisper_model", "large")
            compute_type = self.config.get("compute_type", "int8")
            
            # モデルのロード
            logger.info(f"Whisperモデルをロード中: {model_size}")
            model = WhisperModel(model_size, compute_type=compute_type)
            
            # 文字起こし実行
            segments, info = model.transcribe(
                file_path,
                language=self.config.get("language", "ja"),
                beam_size=5,
                best_of=5,
                vad_filter=True
            )
            
            # セグメントをテキストに結合
            transcription = []
            for segment in segments:
                transcription.append(segment.text.strip())
            
            return "\n".join(transcription)
        
        except Exception as e:
            logger.error(f"文字起こし処理中にエラーが発生しました: {e}")
            return None
    
    def generate_daily_summary(self):
        """日次処理サマリーを生成"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            logger.info(f"{today}の日次サマリーを生成しています")
            
            # サマリー内容を収集
            stats = self.today_stats
            
            # 平均処理時間を計算
            avg_duration = stats["total_duration"] / stats["processed"] if stats["processed"] > 0 else 0
            
            # サマリーメッセージを作成
            summary = (
                f"Koemoji処理サマリー ({today})\n"
                f"------------------------\n"
                f"キュー追加: {stats['queued']}件\n"
                f"処理完了: {stats['processed']}件\n"
                f"処理失敗: {stats['failed']}件\n"
                f"総処理時間: {stats['total_duration']:.2f}秒\n"
                f"平均処理時間: {avg_duration:.2f}秒/ファイル\n"
                f"残りキュー: {len(self.processing_queue)}件\n"
                f"------------------------\n"
            )
            
            # ログに記録
            logger.info(summary.replace('\n', ' '))
            
            # サマリーファイルに保存
            summary_dir = "reports"
            os.makedirs(summary_dir, exist_ok=True)
            
            summary_file = os.path.join(summary_dir, f"daily_summary_{today}.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            # 通知送信
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    f"Koemoji日次サマリー ({today})",
                    f"処理完了: {stats['processed']}件\n"
                    f"処理失敗: {stats['failed']}件\n"
                    f"残りキュー: {len(self.processing_queue)}件"
                )
        
        except Exception as e:
            logger.error(f"日次サマリー生成中にエラーが発生しました: {e}")
    
    def send_notification(self, title, message):
        """通知を送信する"""
        try:
            logger.info(f"通知: {title} - {message}")
            
            # デスクトップ通知
            try:
                from notifypy import Notify
                notification = Notify()
                notification.title = title
                notification.message = message
                notification.send()
            except ImportError:
                logger.warning("notifypyがインストールされていません。デスクトップ通知は表示されません。")
            
        except Exception as e:
            logger.error(f"通知送信中にエラーが発生しました: {e}")
    
    def run(self):
        """メイン処理ループ"""
        try:
            logger.info("KoemojiAuto処理を開始しました")
            
            # 開始通知
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    "KoemojiAuto",
                    "自動文字起こしサービスが開始されました"
                )
            
            # 24時間モードか時間制限モードかを確認
            continuous_mode = self.config.get("continuous_mode", False)
            if continuous_mode:
                logger.info("24時間連続モードで動作します")
            else:
                end_time = self.get_end_time()
                logger.info(f"時間制限モードで動作します（終了時刻: {end_time}）")
            
            scan_interval = self.config.get("scan_interval_minutes", 30) * 60  # 秒に変換
            last_scan_time = 0
            last_summary_date = None
            
            # 初回スキャン
            self.scan_and_queue_files()
            self.process_queued_files()
            
            # メインループ
            while continuous_mode or datetime.now().time() < end_time:
                current_time = time.time()
                
                # 定期的にファイルをスキャン
                if current_time - last_scan_time >= scan_interval:
                    self.scan_and_queue_files()
                    last_scan_time = current_time
                
                # キューのファイルを処理
                self.process_queued_files()
                
                # 24時間モードの場合、日次サマリーのタイミングをチェック
                if continuous_mode:
                    current_date = datetime.now().date()
                    current_time_obj = datetime.now().time()
                    summary_time_str = self.config.get("daily_summary_time", "07:00")
                    summary_hour, summary_minute = map(int, summary_time_str.split(":"))
                    summary_time = datetime_time(summary_hour, summary_minute)
                    
                    # 日次サマリーの時刻を過ぎて、まだ今日のサマリーを作成していない場合
                    if current_time_obj >= summary_time and last_summary_date != current_date:
                        self.generate_daily_summary()
                        last_summary_date = current_date
                        
                        # 統計をリセット
                        self.today_stats = {
                            "queued": 0,
                            "processed": 0,
                            "failed": 0,
                            "total_duration": 0,
                            "date": current_date.strftime("%Y-%m-%d")
                        }
                
                # 短い待機
                time.sleep(5)
            
            # 時間制限モードの終了処理
            if not continuous_mode:
                logger.info("処理時間が終了しました")
                
                # 日次サマリーを生成
                self.generate_daily_summary()
                
                # 終了通知
                if self.config.get("notification_enabled", True):
                    remaining = len(self.processing_queue)
                    processed = self.today_stats["processed"]
                    
                    if remaining > 0:
                        self.send_notification(
                            "KoemojiAuto処理終了",
                            f"処理完了: {processed}件\n残りキュー: {remaining}件"
                        )
                    else:
                        self.send_notification(
                            "KoemojiAuto処理完了",
                            f"すべてのファイル({processed}件)の処理が完了しました"
                        )
            
        except Exception as e:
            logger.error(f"処理中にエラーが発生しました: {e}")
        finally:
            logger.info("KoemojiAutoを終了しました")


# 実行例
if __name__ == "__main__":
    processor = KoemojiProcessor()
    processor.run()