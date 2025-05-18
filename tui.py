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


def is_running():
    """KoeMojiAutoが実行中か確認"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and len(cmdline) > 1:
                    # Pythonプロセスであることを確認（フルパスも考慮）
                    if 'python' in cmdline[0].lower():
                        # main.pyを実行しているかチェック  
                        for arg in cmdline[1:]:
                            if arg == 'main.py' or arg.endswith('/main.py'):
                                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    except:
        # psutilが使えない場合は他の方法で確認
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return 'python' in result.stdout and 'main.py' in result.stdout
        else:  # Unix/macOS
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return 'main.py' in result.stdout

def main():
    while True:
        clear()
        config = load_config()
        running = is_running()  # 毎回ステータスをチェック
        
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
        if running:
            print("║" + format_line(" Status: RUNNING", 39) + "║")
        else:
            print("║" + format_line(" Status: STOPPED", 39) + "║")
        
        print("║───────────────────────────────────────║")
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
        print("[r] 実行  [s] 停止  [t] ステータス  [m] モデル")
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
                result = subprocess.run([script], capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                print("\nCheck progress with [t] Status or [l] View logs")
            except Exception as e:
                print(f"\nError occurred: {e}")
            input("\nPress Enter to continue...")
        elif cmd == 's':
            # 停止コマンド
            print("\nStopping KoemojiAuto...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script = os.path.join(script_dir, 'stop_koemoji.sh' if os.name != 'nt' else 'stop_koemoji.bat')
            try:
                result = subprocess.run([script], capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print(f"\nError occurred: {e}")
            input("\nPress Enter to continue...")
        elif cmd == 't':
            # ステータスコマンド  
            print("\nChecking KoemojiAuto status...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script = os.path.join(script_dir, 'status_koemoji.sh' if os.name != 'nt' else 'status_koemoji.bat')
            try:
                result = subprocess.run([script], capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            except Exception as e:
                print(f"\nError occurred: {e}")
            input("\nPress Enter to continue...")
        elif cmd == 'm':
            models = ['tiny', 'small', 'medium', 'large']
            current = config.get('whisper_model', 'large')
            idx = models.index(current)
            config['whisper_model'] = models[(idx + 1) % 4]
            save_config(config)
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
            print(f"\n=== Recent Log Entries ===")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    last_lines = lines[-20:] if len(lines) > 20 else lines
                    for line in last_lines:
                        print(line, end='')
            except FileNotFoundError:
                print(f"Log file not found: {log_file}")
            except Exception as e:
                print(f"Error: {e}")
            input("\nPress Enter to continue...")



if __name__ == "__main__":
    main()