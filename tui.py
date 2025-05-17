#!/usr/bin/env python3
import os
import json
import subprocess
import sys
from datetime import datetime

def clear():
    if os.name != 'nt':
        subprocess.run(['clear'])
    else:
        subprocess.run(['cls'], shell=True)

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_schedule_time():
    """スケジュールの開始時刻を取得"""
    # まずconfig.jsonから取得を試みる
    config = load_config()
    if 'process_start_time' in config:
        return config['process_start_time']
    
    # config.jsonにない場合は既存の方法で取得
    try:
        if os.name == 'nt':
            result = subprocess.run(['schtasks', '/query', '/tn', 'KoemojiAutoProcessor', '/v', '/fo', 'list'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if '開始時刻:' in line or 'Start Time:' in line:
                    time_str = line.split(':')[-2:]
                    return f"{time_str[0][-2:]}:{time_str[1][:2]}"
        else:
            # macOSの場合はplistから読み取る
            plist_path = os.path.expanduser('~/Library/LaunchAgents/com.koemoji.auto.plist')
            if os.path.exists(plist_path):
                with open(plist_path, 'r') as f:
                    content = f.read()
                    if '<key>Hour</key>' in content:
                        import re
                        hour = re.search(r'<key>Hour</key>\s*<integer>(\d+)</integer>', content)
                        minute = re.search(r'<key>Minute</key>\s*<integer>(\d+)</integer>', content)
                        if hour and minute:
                            return f"{hour.group(1).zfill(2)}:{minute.group(1).zfill(2)}"
        return "19:00"
    except:
        return "19:00"

def is_installed():
    """KoeMojiAutoがインストールされているか確認"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['schtasks', '/query', '/tn', 'KoemojiAutoProcessor'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        else:  # macOS/Linux
            if 'darwin' in os.sys.platform:
                plist_path = os.path.expanduser('~/Library/LaunchAgents/com.koemoji.auto.plist')
                return os.path.exists(plist_path)
        return False
    except:
        return False

def main():
    while True:
        clear()
        config = load_config()
        installed = is_installed()
        start_time = get_schedule_time()
        
        # ステータス表示
        def format_line(text, width=40):
            """日本語を考慮して行を整形"""
            import unicodedata
            text_len = 0
            for char in text:
                # East Asian Width でワイド文字を判定
                if unicodedata.east_asian_width(char) in ['F', 'W']:
                    text_len += 2
                else:
                    text_len += 1
            padding = width - text_len
            return text + ' ' * padding
        
        print("╔═══════════════════════════════════════╗")
        print("║          KoemojiAuto TUI              ║")
        print("╠═══════════════════════════════════════╣")
        if not installed:
            print("║                                       ║")
            print("║    KoeMojiAuto is not installed       ║")
            print("║                                       ║")
            print("║    Run install.sh or install.bat      ║")
            print("║                                       ║")
        else:
            if config.get('continuous_mode'):
                print("║" + format_line(" Mode  : 24-hour", 39) + "║")
            else:
                print("║" + format_line(f" Schedule: {start_time}", 39) + "║")
                end_time = config.get('process_end_time', '07:00')
                print("║" + format_line(f" Mode  : Time-limited [until {end_time}]", 39) + "║")
            print("║" + format_line(f" Model : {config.get('whisper_model', 'large')}", 39) + "║")
            print("╠═══════════════════════════════════════╣")
            # 現在のフォルダ設定を表示
            input_folder = config.get('input_folder', 'Not set')
            output_folder = config.get('output_folder', 'Not set')
            print("║" + format_line(f" Input : {input_folder[:30] + '...' if len(input_folder) > 30 else input_folder}", 39) + "║")
            print("║" + format_line(f" Output: {output_folder[:30] + '...' if len(output_folder) > 30 else output_folder}", 39) + "║")
        print("╚═══════════════════════════════════════╝")
        print()
        
        # コマンド
        print("Commands:")
        print("[r] 実行  [m] モデル  [c] モード  [h] 時刻設定")
        print("[i] 入力フォルダ  [o] 出力フォルダ  [l] ログ表示  [q] 終了")
        print()
        
        cmd = input("> ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 'r':
            print("\nStarting processing...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script = os.path.join(script_dir, 'start_koemoji.sh' if os.name != 'nt' else 'start_koemoji.bat')
            # バックグラウンドで実行
            try:
                subprocess.Popen([script])
                print("\nProcessing started in background.")
                print("Check progress in log file (koemoji.log).")
                print("View logs from TUI: [l] View logs")
            except Exception as e:
                print(f"\nError occurred: {e}")
            input("\nPress Enter to continue...")
        elif cmd == 'm':
            models = ['tiny', 'small', 'medium', 'large']
            current = config.get('whisper_model', 'large')
            idx = models.index(current)
            config['whisper_model'] = models[(idx + 1) % 4]
            save_config(config)
        elif cmd == 'c':
            config['continuous_mode'] = not config.get('continuous_mode', False)
            save_config(config)
        elif cmd == 'h':
            if not installed:
                print("\nKoeMojiAuto is not installed.")
                print("Please run install.sh or install.bat first.")
                input("\nPress Enter to continue...")
            elif config.get('continuous_mode', False):
                print("\nTime settings are not needed in 24-hour mode")
                input("\nPress Enter to continue...")
            else:
                end_time = config.get('process_end_time', '07:00')
                print(f"\nCurrent: {start_time} → {end_time}")
                time_range = input("Time range: ")
                
                if '-' in time_range:
                    parts = time_range.split('-')
                    if len(parts) == 2:
                        start, end = parts[0].strip(), parts[1].strip()
                        start_fmt = format_time(start)
                        end_fmt = format_time(end)
                        
                        if start_fmt and end_fmt:
                            # 開始時刻と終了時刻を更新
                            config['process_start_time'] = start_fmt
                            config['process_end_time'] = end_fmt
                            save_config(config)
                            
                            # OSごとの処理
                            if os.name == 'nt':
                                # Windowsの場合はschtasksで更新
                                subprocess.run(['schtasks', '/change', '/tn', 'KoemojiAutoProcessor', '/st', start_fmt])
                                print(f"\nTime range changed to {start_fmt} → {end_fmt}")
                            else:
                                # macOS/Linuxの場合はinstall.shを実行
                                print(f"\nChanging time range to {start_fmt} → {end_fmt}...")
                                result = subprocess.run(['./install.sh', start_fmt], 
                                                      capture_output=True, text=True)
                                if result.returncode == 0:
                                    print("Settings updated")
                                else:
                                    print("Error occurred:")
                                    print(result.stderr)
                            input("\nPress Enter to continue...")
                        else:
                            print("\nInvalid time format")
                            input("\nPress Enter to continue...")
                else:
                    print("\nPlease enter in start-end format")
                    input("\nPress Enter to continue...")
        elif cmd == 'i':
            print(f"\nCurrent input folder: {config.get('input_folder', 'Not set')}")
            new_input = input("New input folder (blank to cancel): ").strip()
            if new_input:
                new_input = os.path.expanduser(new_input)
                config['input_folder'] = new_input
                save_config(config)
                print(f"Input folder changed to: {new_input}")
            input("\nPress Enter to continue...")
        elif cmd == 'o':
            print(f"\nCurrent output folder: {config.get('output_folder', 'Not set')}")
            new_output = input("New output folder (blank to cancel): ").strip()
            if new_output:
                new_output = os.path.expanduser(new_output)
                config['output_folder'] = new_output
                save_config(config)
                print(f"Output folder changed to: {new_output}")
            input("\nPress Enter to continue...")
        elif cmd == 'l':
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_file = os.path.join(script_dir, 'koemoji.log')
            print(f"\n=== Log Display ({log_file}) ===")
            print("[1] Last 20 lines  [2] Errors only  [3] Today's logs  [4] All logs")
            log_choice = input("\nChoice: ").strip()
            
            if log_choice == '1':
                print(f"\n--- Last 20 lines ({log_file}) ---")
                try:
                    # Python内部でtail機能を実装
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-20:] if len(lines) > 20 else lines
                        for line in last_lines:
                            print(line, end='')
                except FileNotFoundError:
                    print(f"Log file not found: {log_file}")
                except Exception as e:
                    print(f"Error: {e}")
            elif log_choice == '2':
                print(f"\n--- Error logs ({log_file}) ---")
                try:
                    # Python内部でgrep機能を実装
                    with open(log_file, 'r', encoding='utf-8') as f:
                        error_lines = [line for line in f if 'ERROR' in line]
                        if error_lines:
                            for line in error_lines:
                                print(line, end='')
                        else:
                            print("No errors found")
                except FileNotFoundError:
                    print(f"Log file not found: {log_file}")
                except Exception as e:
                    print(f"Error: {e}")
            elif log_choice == '3':
                print(f"\n--- Today's logs ({log_file}) ---")
                today = datetime.now().strftime('%Y-%m-%d')
                try:
                    # Python内部でgrep機能を実装
                    with open(log_file, 'r', encoding='utf-8') as f:
                        today_lines = [line for line in f if today in line]
                        if today_lines:
                            for line in today_lines:
                                print(line, end='')
                        else:
                            print("No logs for today yet")
                except FileNotFoundError:
                    print(f"Log file not found: {log_file}")
                except Exception as e:
                    print(f"Error: {e}")
            elif log_choice == '4':
                print(f"\n--- All logs ({log_file}) ---")
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content:
                            print(content)
                        else:
                            print("Log file is empty")
                except FileNotFoundError:
                    print(f"Log file not found: {log_file}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Invalid selection")
            
            input("\nPress Enter to continue...")

def format_time(time_str):
    """時刻文字列をHH:MM形式に変換"""
    time_str = time_str.strip()
    
    # すでにコロンがある場合
    if ':' in time_str:
        if validate_time(time_str):
            return time_str
    # 数字のみの場合
    elif time_str.isdigit():
        if len(time_str) <= 2:
            # 1桁または2桁は時間のみ
            h = int(time_str)
            if 0 <= h < 24:
                return f"{h:02d}:00"
        elif len(time_str) == 3:
            # 3桁は時間1桁+分2桁
            h = int(time_str[0])
            m = int(time_str[1:3])
            if 0 <= h < 24 and 0 <= m < 60:
                return f"{h:02d}:{m:02d}"
        elif len(time_str) == 4:
            # 4桁は時間2桁+分2桁
            h = int(time_str[0:2])
            m = int(time_str[2:4])
            if 0 <= h < 24 and 0 <= m < 60:
                return f"{h:02d}:{m:02d}"
    return None

def validate_time(time_str):
    """時刻の妥当性を検証"""
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            h, m = parts
            if h.isdigit() and m.isdigit():
                return 0 <= int(h) < 24 and 0 <= int(m) < 60
    return False

if __name__ == "__main__":
    main()