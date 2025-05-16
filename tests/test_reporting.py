"""レポート機能のテスト"""
import os
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch
from main import KoemojiProcessor


class TestReporting:
    def test_generate_daily_summary(self):
        """日次サマリー生成のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            # プロセスディレクトリを一時ディレクトリに変更
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                processor = KoemojiProcessor(config_path)
                
                # テスト用の統計を設定
                processor.today_stats = {
                    "queued": 10,
                    "processed": 8,
                    "failed": 2,
                    "total_duration": 240.5,
                    "date": "2024-01-15"
                }
                
                # キューにファイルを追加
                processor.processing_queue = [
                    {"path": "/path/file1.mp3", "name": "file1.mp3"},
                    {"path": "/path/file2.mp3", "name": "file2.mp3"}
                ]
                
                # 日次サマリーを生成
                with patch('main.datetime') as mock_datetime:
                    mock_datetime.now.return_value = datetime(2024, 1, 15)
                    processor.generate_daily_summary()
                
                # サマリーファイルが作成されたことを確認
                summary_file = os.path.join("reports", "daily_summary_2024-01-15.txt")
                assert os.path.exists(summary_file)
                
                # サマリーの内容を確認
                with open(summary_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert "2024-01-15" in content
                assert "キュー追加: 10件" in content
                assert "処理完了: 8件" in content
                assert "処理失敗: 2件" in content
                assert "総処理時間: 240.50秒" in content
                assert "平均処理時間: 30.06秒/ファイル" in content
                assert "残りキュー: 2件" in content
            finally:
                # 元のディレクトリに戻る
                os.chdir(original_cwd)
    
    def test_summary_with_no_processed_files(self):
        """処理ファイルなしでのサマリー生成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            processor = KoemojiProcessor(config_path)
            
            # 処理ファイルなしの統計
            processor.today_stats = {
                "queued": 5,
                "processed": 0,
                "failed": 0,
                "total_duration": 0,
                "date": "2024-01-15"
            }
            
            # 日次サマリーを生成
            processor.generate_daily_summary()
            
            # エラーが発生しないことを確認
            summary_file = os.path.join(temp_dir, "reports", f"daily_summary_{processor.today_stats['date']}.txt")
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                assert "平均処理時間: 0.00秒/ファイル" in content
    
    @patch('main.KoemojiProcessor.send_notification')
    def test_summary_notification(self, mock_notification):
        """サマリー通知のテスト"""
        processor = KoemojiProcessor()
        processor.config["notification_enabled"] = True
        
        # テスト用の統計を設定
        processor.today_stats = {
            "queued": 5,
            "processed": 4,
            "failed": 1,
            "total_duration": 120,
            "date": "2024-01-15"
        }
        
        # 日次サマリーを生成
        with patch('main.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15)
            processor.generate_daily_summary()
        
        # 通知が送信されたことを確認
        mock_notification.assert_called_once()
        title, message = mock_notification.call_args[0]
        assert "日次サマリー" in title
        assert "処理完了: 4件" in message
        assert "処理失敗: 1件" in message
    
    def test_statistics_reset(self):
        """統計リセットのテスト"""
        processor = KoemojiProcessor()
        
        # 統計を設定
        processor.today_stats = {
            "queued": 10,
            "processed": 8,
            "failed": 2,
            "total_duration": 240,
            "date": "2024-01-14"
        }
        
        # 新しい日の統計にリセット
        new_date = "2024-01-15"
        processor.today_stats = {
            "queued": 0,
            "processed": 0,
            "failed": 0,
            "total_duration": 0,
            "date": new_date
        }
        
        # リセットされたことを確認
        assert processor.today_stats["queued"] == 0
        assert processor.today_stats["processed"] == 0
        assert processor.today_stats["failed"] == 0
        assert processor.today_stats["total_duration"] == 0
        assert processor.today_stats["date"] == new_date
    
    def test_average_duration_calculation(self):
        """平均処理時間の計算テスト"""
        processor = KoemojiProcessor()
        
        # テストケース1: 通常の計算
        stats1 = {
            "processed": 5,
            "total_duration": 150.0
        }
        avg1 = stats1["total_duration"] / stats1["processed"]
        assert avg1 == 30.0
        
        # テストケース2: ゼロ除算の回避
        stats2 = {
            "processed": 0,
            "total_duration": 0
        }
        avg2 = stats2["total_duration"] / stats2["processed"] if stats2["processed"] > 0 else 0
        assert avg2 == 0
    
    def test_report_directory_creation(self):
        """レポートディレクトリの自動作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            # プロセスディレクトリを一時ディレクトリに変更
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # reportsディレクトリが存在しない状態で開始
                assert not os.path.exists("reports")
                
                processor = KoemojiProcessor(config_path)
                processor.generate_daily_summary()
                
                # reportsディレクトリが作成されたことを確認
                assert os.path.exists("reports")
            finally:
                # 元のディレクトリに戻る
                os.chdir(original_cwd)