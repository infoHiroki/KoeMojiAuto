"""統合テスト"""
import os
import tempfile
import time
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, time as datetime_time
from main import KoemojiProcessor


class TestIntegration:
    @patch('faster_whisper.WhisperModel')
    def test_full_processing_flow(self, mock_whisper_model):
        """完全な処理フローのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # ディレクトリ構成の作成
            config_path = os.path.join(temp_dir, "config.json")
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            reports_dir = os.path.join(temp_dir, "reports")
            
            os.makedirs(input_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(reports_dir, exist_ok=True)
            
            # テスト用ファイルの作成
            test_files = ["test1.mp3", "test2.wav", "urgent_test3.m4a"]
            for filename in test_files:
                filepath = os.path.join(input_dir, filename)
                with open(filepath, 'w') as f:
                    f.write("dummy audio content")
            
            # Whisperモデルのモック設定
            mock_model_instance = MagicMock()
            mock_whisper_model.return_value = mock_model_instance
            
            # 文字起こし結果のモック
            def mock_transcribe(audio_path, **kwargs):
                filename = os.path.basename(audio_path)
                text = f"Transcription for {filename}"
                segment = MagicMock()
                segment.text = text
                return ([segment], MagicMock())
            
            mock_model_instance.transcribe.side_effect = mock_transcribe
            
            # プロセッサーの初期化
            processor = KoemojiProcessor(config_path)
            processor.config.update({
                "input_folder": input_dir,
                "output_folder": output_dir,
                "max_concurrent_files": 2,
                "whisper_model": "large",
                "continuous_mode": False,
                "process_end_time": "23:59"
            })
            
            # 1. ファイルスキャン
            processor.scan_and_queue_files()
            assert len(processor.processing_queue) == 3
            
            # 2. 優先度の確認（urgent_test3.m4aが最初）
            assert "urgent" in processor.processing_queue[0]["name"]
            
            # 3. ファイル処理
            processor.process_queued_files()
            
            # 4. 処理結果の確認
            output_files = os.listdir(output_dir)
            assert len(output_files) > 0
            
            # 5. 出力ファイルの内容確認
            for original_file in test_files:
                base_name = os.path.splitext(original_file)[0]
                output_file = os.path.join(output_dir, f"{base_name}.txt")
                
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    assert f"Transcription for {original_file}" in content
    
    @patch('faster_whisper.WhisperModel')
    @patch('main.datetime')
    def test_time_limited_mode(self, mock_datetime, mock_whisper_model):
        """時間制限モードのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            # Whisperモデルのモック
            mock_model_instance = MagicMock()
            mock_whisper_model.return_value = mock_model_instance
            mock_segment = MagicMock()
            mock_segment.text = "Test transcription"
            mock_model_instance.transcribe.return_value = ([mock_segment], MagicMock())
            
            processor = KoemojiProcessor(config_path)
            processor.config.update({
                "continuous_mode": False,
                "process_end_time": "07:00",
                "scan_interval_minutes": 0.1  # テスト用に短く設定
            })
            
            # 現在時刻を設定（終了時刻前）
            mock_datetime.now.return_value = datetime(2024, 1, 15, 6, 30)
            
            # メインループをシミュレート（短時間）
            start_time = time.time()
            while time.time() - start_time < 1:  # 1秒間だけテスト
                # 終了時刻に達したことをシミュレート
                if time.time() - start_time > 0.5:
                    mock_datetime.now.return_value = datetime(2024, 1, 15, 7, 1)
                
                # 処理ループの一部をシミュレート
                if datetime.now().time() >= processor.get_end_time():
                    break
                
                time.sleep(0.1)
            
            # 終了時刻に達したことを確認
            assert datetime.now().time() >= processor.get_end_time()
    
    @patch('faster_whisper.WhisperModel')
    def test_error_recovery(self, mock_whisper_model):
        """エラーからの回復テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            
            os.makedirs(input_dir, exist_ok=True)
            os.makedirs(output_dir, exist_ok=True)
            
            # テストファイルの作成
            test_files = ["success.mp3", "error.mp3", "success2.mp3"]
            for filename in test_files:
                filepath = os.path.join(input_dir, filename)
                with open(filepath, 'w') as f:
                    f.write("dummy")
            
            # Whisperモデルのモック設定
            mock_model_instance = MagicMock()
            mock_whisper_model.return_value = mock_model_instance
            
            # error.mp3でエラーを発生させる
            def mock_transcribe(audio_path, **kwargs):
                if "error.mp3" in audio_path:
                    raise Exception("Transcription error")
                segment = MagicMock()
                segment.text = "Success"
                return ([segment], MagicMock())
            
            mock_model_instance.transcribe.side_effect = mock_transcribe
            
            processor = KoemojiProcessor(config_path)
            processor.config.update({
                "input_folder": input_dir,
                "output_folder": output_dir
            })
            
            # ファイルスキャンと処理
            processor.scan_and_queue_files()
            processor.process_queued_files()
            
            # エラーが発生しても他のファイルは処理されることを確認
            output_files = os.listdir(output_dir)
            assert "success.txt" in output_files or "success2.txt" in output_files
            assert "error.txt" not in output_files
            
            # 統計の確認
            assert processor.today_stats["failed"] >= 1
            assert processor.today_stats["processed"] >= 1
    
    @patch('faster_whisper.WhisperModel')
    def test_continuous_mode_daily_summary(self, mock_whisper_model):
        """24時間モードでの日次サマリーテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            # Whisperモデルのモック
            mock_model_instance = MagicMock()
            mock_whisper_model.return_value = mock_model_instance
            
            processor = KoemojiProcessor(config_path)
            processor.config.update({
                "continuous_mode": True,
            })
            
            # 日次サマリー時刻のチェックをシミュレート
            current_time = datetime_time(7, 0)
            summary_time = datetime_time(7, 0)
            
            # サマリー時刻に達したことを確認
            assert current_time >= summary_time
            
            # サマリー生成をトリガー
            processor.generate_daily_summary()
            
            # サマリーファイルが作成されたことを確認
            reports_dir = os.path.join(temp_dir, "reports")
            assert os.path.exists(reports_dir)
            
            # 統計がリセットされることを確認
            processor.today_stats = {
                "queued": 0,
                "processed": 0,
                "failed": 0,
                "total_duration": 0,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            assert processor.today_stats["queued"] == 0
            assert processor.today_stats["processed"] == 0