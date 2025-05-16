#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KoemojiAuto - 夜間処理特化版
夜間に集中的に文字起こし処理を行う自動化システム
"""

import os
import time
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import psutil
import shutil

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("koemoji_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KoemojiNightScheduler")

class KoemojiNightProcessor:
    def __init__(self, config_path="night_config.json"):
        """夜間処理のための初期化"""
        self.config_path = config_path
        self.load_config()
        self.scheduler = BackgroundScheduler()
        self.processing_queue = []  # 処理待ちファイルのキュー
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
        
        # スケジューラの設定
        self.setup_jobs()
    
    def load_config(self):
        """設定ファイルを読み込む"""
        try:
            if not os.path.exists(self.config_path):
                # デフォルト設定を作成
                self.config = {
                    "input_folder": "input",
                    "output_folder": "output",
                    "queue_scan_interval_minutes": 30,  # 日中のキュースキャン間隔
                    "night_process_start_time": "19:00",  # 夜間処理開始時間
                    "night_process_end_time": "07:00",   # 夜間処理終了時間
                    "max_concurrent_files": 2,          # 夜間の同時処理数
                    "daytime_concurrent_files": 0,      # 日中の同時処理数 (0=処理なし)
                    "whisper_model": "medium",          # 夜間は大きいモデルを使用可能
                    "daytime_whisper_model": "tiny",    # 日中は小さいモデルを使用
                    "language": "ja",
                    "compute_type": "int8",
                    "notification_enabled": True,
                    "resource_check_interval_minutes": 10,
                    "night_max_cpu_percent": 95,        # 夜間のCPU使用率上限
                    "daytime_max_cpu_percent": 30,      # 日中のCPU使用率上限
                    "weekend_processing": True,         # 週末も処理を実行するか
                    "weekly_report_day": "monday",      # 週次レポートの曜日
                    "weekly_report_time": "08:00",      # 週次レポートの時間
                    "daily_summary_time": "08:00"       # 日次サマリーの時間
                }
                # 設定を保存
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, indent=2, ensure_ascii=False, fp=f)
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
                    
            # 待機キューフォルダの作成
            queue_folder = "queue"
            if not os.path.exists(queue_folder):
                os.makedirs(queue_folder, exist_ok=True)
                logger.info(f"キューフォルダを作成しました: {queue_folder}")
                    
        except Exception as e:
            logger.error(f"設定の読み込み中にエラーが発生しました: {e}")
            # 最小限のデフォルト設定
            self.config = {
                "input_folder": "input",
                "output_folder": "output",
                "night_process_start_time": "19:00",
                "night_process_end_time": "07:00",
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
    
    def setup_jobs(self):
        """スケジューラにジョブを設定"""
        # 1. 日中のキュースキャンジョブ
        self.scheduler.add_job(
            self.scan_and_queue_files,
            IntervalTrigger(minutes=self.config.get("queue_scan_interval_minutes", 30)),
            id="queue_scan_job",
            name="キュースキャンジョブ"
        )
        
        # 2. 夜間処理開始ジョブ
        night_start = self.config.get("night_process_start_time", "19:00").split(":")
        self.scheduler.add_job(
            self.start_night_processing,
            CronTrigger(hour=int(night_start[0]), minute=int(night_start[1])),
            id="night_process_start_job",
            name="夜間処理開始ジョブ"
        )
        
        # 3. 夜間処理終了ジョブ
        night_end = self.config.get("night_process_end_time", "07:00").split(":")
        self.scheduler.add_job(
            self.stop_night_processing,
            CronTrigger(hour=int(night_end[0]), minute=int(night_end[1])),
            id="night_process_end_job",
            name="夜間処理終了ジョブ"
        )
        
        # 4. リソース確認ジョブ
        self.scheduler.add_job(
            self.check_resources,
            IntervalTrigger(minutes=self.config.get("resource_check_interval_minutes", 10)),
            id="resource_check_job",
            name="リソース確認ジョブ"
        )
        
        # 5. 日次サマリージョブ
        daily_summary = self.config.get("daily_summary_time", "08:00").split(":")
        self.scheduler.add_job(
            self.generate_daily_summary,
            CronTrigger(hour=int(daily_summary[0]), minute=int(daily_summary[1])),
            id="daily_summary_job",
            name="日次サマリージョブ"
        )
        
        # 6. 週次レポートジョブ
        if self.config.get("weekly_report_day"):
            day_of_week = self.config.get("weekly_report_day", "monday").lower()
            report_time = self.config.get("weekly_report_time", "08:00").split(":")
            self.scheduler.add_job(
                self.generate_weekly_report,
                CronTrigger(day_of_week=day_of_week, hour=int(report_time[0]), minute=int(report_time[1])),
                id="weekly_report_job",
                name="週次レポートジョブ"
            )
        
        logger.info("すべてのジョブを設定しました")
    
    def is_night_time(self):
        """夜間処理時間帯かどうかを確認"""
        now = datetime.now().time()
        start_str = self.config.get("night_process_start_time", "19:00")
        end_str = self.config.get("night_process_end_time", "07:00")
        
        start_hour, start_minute = map(int, start_str.split(":"))
        end_hour, end_minute = map(int, end_str.split(":"))
        
        start_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M").time()
        end_time = datetime.strptime(f"{end_hour}:{end_minute}", "%H:%M").time()
        
        # 夜間時間帯が日をまたぐ場合（例: 19:00-07:00）
        if start_time > end_time:
            return now >= start_time or now <= end_time
        # 同日内の場合
        else:
            return start_time <= now <= end_time
    
    def is_weekend(self):
        """週末かどうかを確認"""
        return datetime.now().weekday() >= 5  # 5=土曜日, 6=日曜日
    
    def scan_and_queue_files(self):
        """入力フォルダをスキャンしてファイルをキューに追加"""
        try:
            logger.debug("入力フォルダのスキャンを開始します")
            
            # 週末で週末処理が無効の場合はスキップ
            if self.is_weekend() and not self.config.get("weekend_processing", True):
                logger.debug("週末は処理を行いません")
                return
            
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
            
            # 夜間処理時間帯で日中処理も許可されている場合は処理開始
            if self.is_night_time() or self.config.get("daytime_concurrent_files", 0) > 0:
                self.process_queued_files()
            
            logger.info(f"現在のキュー: {len(self.processing_queue)}件")
            
        except Exception as e:
            logger.error(f"キュースキャン中にエラーが発生しました: {e}")
    
    def calculate_priority(self, file_path):
        """ファイルの処理優先度を計算"""
        # 優先度の計算ロジックを実装
        # 例: サイズが小さいファイルを優先、特定の名前パターンで優先度を変更など
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        priority = 0
        
        # サイズが小さいファイルを優先（大きいファイルは夜間の長い時間帯に）
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
    
    def start_night_processing(self):
        """夜間処理を開始"""
        try:
            logger.info("夜間処理を開始します")
            
            # 週末で週末処理が無効の場合はスキップ
            if self.is_weekend() and not self.config.get("weekend_processing", True):
                logger.info("週末は夜間処理を行いません")
                return
            
            # 通知
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    "Koemoji夜間処理開始",
                    f"キュー内の{len(self.processing_queue)}件のファイルの処理を開始します"
                )
            
            # キューにあるファイルの処理を開始
            self.process_queued_files()
        
        except Exception as e:
            logger.error(f"夜間処理開始中にエラーが発生しました: {e}")
    
    def stop_night_processing(self):
        """夜間処理を停止"""
        try:
            logger.info("夜間処理を停止します")
            
            # 現在の処理を継続するが、新しい処理は開始しない
            # （実際の実装では必要に応じて現在の処理を中断することも可能）
            
            # 通知
            remaining = len(self.processing_queue)
            processed = self.today_stats["processed"]
            
            if self.config.get("notification_enabled", True):
                if remaining > 0:
                    self.send_notification(
                        "Koemoji夜間処理終了",
                        f"処理完了: {processed}件\n残りキュー: {remaining}件（次の夜間処理時間帯に処理されます）"
                    )
                else:
                    self.send_notification(
                        "Koemoji夜間処理完了",
                        f"すべてのファイル({processed}件)の処理が完了しました"
                    )
        
        except Exception as e:
            logger.error(f"夜間処理停止中にエラーが発生しました: {e}")
    
    def process_queued_files(self):
        """キューにあるファイルを処理"""
        try:
            if not self.processing_queue:
                logger.debug("処理すべきファイルはありません")
                return
            
            # 時間帯に基づいて同時処理数を決定
            if self.is_night_time():
                max_concurrent = self.config.get("max_concurrent_files", 2)
            else:
                max_concurrent = self.config.get("daytime_concurrent_files", 0)
                
                # 日中の処理が無効な場合は処理しない
                if max_concurrent <= 0:
                    logger.debug("日中は処理を行いません")
                    return
            
            # 現在の処理数を確認
            current_running = len(self.files_in_process)
            available_slots = max(0, max_concurrent - current_running)
            
            if available_slots <= 0:
                logger.debug("同時処理数の上限に達しています")
                return
            
            # リソース使用状況を確認
            cpu_percent, _, _ = self.check_resources()
            
            # CPU使用率が高すぎる場合は処理を延期
            max_cpu = self.config.get("night_max_cpu_percent", 95) if self.is_night_time() else self.config.get("daytime_max_cpu_percent", 30)
            if cpu_percent and cpu_percent > max_cpu:
                logger.info(f"CPU使用率が高すぎるため、処理を延期します: {cpu_percent}%")
                return
            
            # 処理するファイル数を決定
            files_to_process = self.processing_queue[:available_slots]
            
            # 時間帯に応じてWhisperモデルを選択
            model_size = self.config.get("whisper_model", "medium") if self.is_night_time() else self.config.get("daytime_whisper_model", "tiny")
            
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
            logger.info(f"ファイル処理開始: {file_name} (モデル: {model_size or self.config.get('whisper_model', 'tiny')})")
            
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
                
                # 処理完了後、次のファイルをキューから処理
                if self.processing_queue and (self.is_night_time() or self.config.get("daytime_concurrent_files", 0) > 0):
                    self.process_queued_files()
                
                # 通知（夜間モードではファイルごとの通知は送らない）
                if not self.is_night_time() and self.config.get("notification_enabled", True):
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
            processing_time = time.time() - start_time
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
            model_size = model_size or self.config.get("whisper_model", "tiny")
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
    
    def check_resources(self):
        """システムリソースの確認"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            logger.debug(f"リソース状況 - CPU: {cpu_percent}%, メモリ: {memory_percent}%, ディスク: {disk_percent}%")
            
            # 警告しきい値チェック
            warnings = []
            
            # 時間帯に応じてCPU使用率の上限を変更
            max_cpu = self.config.get("night_max_cpu_percent", 95) if self.is_night_time() else self.config.get("daytime_max_cpu_percent", 30)
            
            if cpu_percent > max_cpu:
                warnings.append(f"CPU使用率が高すぎます: {cpu_percent}%")
            
            if memory_percent > 90:
                warnings.append(f"メモリ使用率が高すぎます: {memory_percent}%")
            
            if disk_percent > 90:
                warnings.append(f"ディスク使用率が高すぎます: {disk_percent}%")
            
            # 警告がある場合は通知（頻繁な通知を避けるため、夜間モードでは通知しない）
            if warnings and not self.is_night_time() and self.config.get("notification_enabled", True):
                self.send_notification(
                    "Koemojiリソース警告",
                    "\n".join(warnings)
                )
                
            return cpu_percent, memory_percent, disk_percent
        
        except Exception as e:
            logger.error(f"リソースチェック中にエラーが発生しました: {e}")
            return None, None, None
    
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
            
            # 今日の統計をリセット
            self.today_stats = {
                "queued": 0,
                "processed": 0,
                "failed": 0,
                "total_duration": 0,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        
        except Exception as e:
            logger.error(f"日次サマリー生成中にエラーが発生しました: {e}")
    
    def generate_weekly_report(self):
        """週次レポートを生成"""
        try:
            current_date = datetime.now()
            report_date = current_date.strftime("%Y-%m-%d")
            start_date = (current_date - timedelta(days=7)).strftime("%Y-%m-%d")
            
            logger.info(f"週次レポートを生成しています ({start_date} ～ {report_date})")
            
            # 過去7日間の日次サマリーファイルを収集
            summary_dir = "reports"
            if not os.path.exists(summary_dir):
                logger.warning(f"レポートディレクトリが存在しません: {summary_dir}")
                return
            
            # 週間の統計情報を収集
            weekly_stats = {
                "total_queued": 0,
                "total_processed": 0,
                "total_failed": 0,
                "total_duration": 0,
                "days_with_activity": 0
            }
            
            # 過去7日間の日付を生成
            past_dates = [(current_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, 0, -1)]
            
            daily_data = []
            
            for date in past_dates:
                summary_file = os.path.join(summary_dir, f"daily_summary_{date}.txt")
                if os.path.exists(summary_file):
                    # ファイルから統計情報を抽出
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 簡易パース（より堅牢な実装では正規表現などを使用）
                    day_stats = {}
                    for line in content.split('\n'):
                        if ': ' in line:
                            key, value = line.split(': ', 1)
                            if value.endswith('件'):
                                day_stats[key] = int(value[:-1])
                            elif value.endswith('秒'):
                                day_stats[key] = float(value[:-1])
                            else:
                                day_stats[key] = value
                    
                    if day_stats:
                        weekly_stats["days_with_activity"] += 1
                        if "キュー追加" in day_stats:
                            weekly_stats["total_queued"] += day_stats["キュー追加"]
                        if "処理完了" in day_stats:
                            weekly_stats["total_processed"] += day_stats["処理完了"]
                        if "処理失敗" in day_stats:
                            weekly_stats["total_failed"] += day_stats["処理失敗"]
                        if "総処理時間" in day_stats:
                            weekly_stats["total_duration"] += day_stats["総処理時間"]
                        
                        daily_data.append({
                            "date": date,
                            "processed": day_stats.get("処理完了", 0),
                            "failed": day_stats.get("処理失敗", 0),
                            "duration": day_stats.get("総処理時間", 0)
                        })
            
            # レポート内容を作成
            avg_duration_per_file = weekly_stats["total_duration"] / weekly_stats["total_processed"] if weekly_stats["total_processed"] > 0 else 0
            avg_files_per_day = weekly_stats["total_processed"] / weekly_stats["days_with_activity"] if weekly_stats["days_with_activity"] > 0 else 0
            
            report = (
                f"Koemoji週次レポート ({start_date} ～ {report_date})\n"
                f"============================================\n\n"
                f"概要:\n"
                f"- 総処理ファイル数: {weekly_stats['total_processed']}件\n"
                f"- 失敗数: {weekly_stats['total_failed']}件\n"
                f"- 成功率: {(weekly_stats['total_processed'] - weekly_stats['total_failed']) / weekly_stats['total_processed'] * 100:.1f}%\n"
                f"- 総処理時間: {weekly_stats['total_duration']:.2f}秒\n"
                f"- 平均処理時間: {avg_duration_per_file:.2f}秒/ファイル\n"
                f"- 1日あたりの平均ファイル数: {avg_files_per_day:.1f}件\n\n"
                f"日別処理状況:\n"
            )
            
            # 日別データを追加
            for day in daily_data:
                report += f"- {day['date']}: 処理完了 {day['processed']}件, 処理失敗 {day['failed']}件, 処理時間 {day['duration']:.2f}秒\n"
            
            report += f"\n現在のキュー: {len(self.processing_queue)}件\n"
            
            # レポートを保存
            report_file = os.path.join(summary_dir, f"weekly_report_{report_date}.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"週次レポートを生成しました: {report_file}")
            
            # 通知送信
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    f"Koemoji週次レポート ({start_date} ～ {report_date})",
                    f"総処理: {weekly_stats['total_processed']}件\n"
                    f"成功率: {(weekly_stats['total_processed'] - weekly_stats['total_failed']) / weekly_stats['total_processed'] * 100:.1f}%\n"
                    f"平均処理時間: {avg_duration_per_file:.2f}秒/ファイル"
                )
        
        except Exception as e:
            logger.error(f"週次レポート生成中にエラーが発生しました: {e}")
    
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
    
    def start(self):
        """スケジューラを開始"""
        try:
            self.scheduler.start()
            logger.info("Koemoji夜間スケジューラを開始しました")
            
            # 起動通知
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    "Koemoji夜間スケジューラ",
                    "自動文字起こしサービスが開始されました"
                )
            
            # 初回のキュースキャン
            self.scan_and_queue_files()
            
            # 現在夜間時間帯の場合は処理を開始
            if self.is_night_time():
                self.start_night_processing()
            
        except Exception as e:
            logger.error(f"スケジューラ開始中にエラーが発生しました: {e}")
    
    def stop(self):
        """スケジューラを停止"""
        try:
            self.scheduler.shutdown()
            logger.info("Koemoji夜間スケジューラを停止しました")
            
            # 停止通知
            if self.config.get("notification_enabled", True):
                self.send_notification(
                    "Koemoji夜間スケジューラ",
                    "自動文字起こしサービスが停止されました"
                )
                
        except Exception as e:
            logger.error(f"スケジューラ停止中にエラーが発生しました: {e}")


# 実行例
if __name__ == "__main__":
    night_processor = KoemojiNightProcessor()
    night_processor.start()
    
    try:
        # スケジューラをバックグラウンドで実行したまま保持
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        night_processor.stop()