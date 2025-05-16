#!/usr/bin/env python3
import os
import json
import subprocess
import sys

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_schedule_time():
    """スケジュールの開始時刻を取得"""
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

def get_auto_status():
    """自動実行の状態を確認"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['schtasks', '/query', '/tn', 'KoemojiAutoProcessor'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                if '無効' in result.stdout or 'Disabled' in result.stdout:
                    return "停止"
                else:
                    return "有効"
        else:  # macOS/Linux
            if 'darwin' in os.sys.platform:
                # 特定のエージェントの状態を確認
                result = subprocess.run(['launchctl', 'list', 'com.koemoji.auto'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # エージェントが存在する場合、詳細を確認
                    result2 = subprocess.run(['launchctl', 'print', 'user/' + str(os.getuid()) + '/com.koemoji.auto'], 
                                           capture_output=True, text=True)
                    if 'disabled' in result2.stdout.lower():
                        return "停止"
                    else:
                        return "有効"
                else:
                    # エージェントが存在しない場合
                    return "未設定"
        return "未設定"
    except:
        return "未設定"

def main():
    while True:
        clear()
        config = load_config()
        auto_status = get_auto_status()
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
        if auto_status == "未設定":
            print("║                                       ║")
            print("║    KoeMojiAutoがインストール          ║")
            print("║    されていません                     ║")
            print("║                                       ║")
            print("║    install.sh または install.bat      ║")
            print("║    を実行してください                 ║")
            print("║                                       ║")
        else:
            print("║" + format_line(f" 自動実行: {auto_status}", 39) + "║")
            if config.get('continuous_mode'):
                print("║" + format_line(" Mode  : 24時間", 39) + "║")
            else:
                print("║" + format_line(f" 開始時刻: {start_time}", 39) + "║")
                end_time = config.get('process_end_time', '07:00')
                print("║" + format_line(f" Mode  : 時間指定 [{end_time}まで]", 39) + "║")
            print("║" + format_line(f" Model : {config.get('whisper_model', 'large')}", 39) + "║")
            print("╠═══════════════════════════════════════╣")
            # 現在のフォルダ設定を表示
            input_folder = config.get('input_folder', '未設定')
            output_folder = config.get('output_folder', '未設定')
            print("║" + format_line(f" 入力: {input_folder[:30] + '...' if len(input_folder) > 30 else input_folder}", 39) + "║")
            print("║" + format_line(f" 出力: {output_folder[:30] + '...' if len(output_folder) > 30 else output_folder}", 39) + "║")
        print("╚═══════════════════════════════════════╝")
        print()
        
        # コマンド
        print("Commands:")
        print("[r] 実行  [t] 自動ON/OFF  [m] モデル  [c] モード  [h] 時刻設定")
        print("[i] 入力フォルダ  [o] 出力フォルダ  [q] 終了")
        print()
        
        cmd = input("> ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 'r':
            print("\n処理中...")
            script = './start_koemoji.sh' if os.name != 'nt' else 'start_koemoji.bat'
            subprocess.run([script], check=False)
        elif cmd == 't':
            if auto_status == "未設定":
                print("\nKoeMojiAutoがインストールされていません。")
                print("先にinstall.shまたはinstall.batを実行してください。")
            else:
                script = './toggle.sh' if os.name != 'nt' else 'toggle.bat'
                result = subprocess.run([script], check=False, capture_output=True, text=True)
                if result.returncode != 0:
                    print("\n自動実行の切り替えに失敗しました。")
            input("\nEnterで続行...")
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
            if config.get('continuous_mode', False):
                print("\n24時間モードでは時刻設定は不要です")
                input("\nEnterで続行...")
            else:
                end_time = config.get('process_end_time', '07:00')
                print(f"\n現在: {start_time} → {end_time}")
                time_range = input("時間帯: ")
                
                if '-' in time_range:
                    parts = time_range.split('-')
                    if len(parts) == 2:
                        start, end = parts[0].strip(), parts[1].strip()
                        start_fmt = format_time(start)
                        end_fmt = format_time(end)
                        
                        if start_fmt and end_fmt:
                            # 開始時刻を更新
                            if os.name == 'nt':
                                os.system(f'schtasks /change /tn "KoemojiAutoProcessor" /st {start_fmt}')
                            # 終了時刻を更新
                            config['process_end_time'] = end_fmt
                            save_config(config)
                            print(f"\n時間帯を {start_fmt} → {end_fmt} に変更しました")
                            if os.name != 'nt':
                                print("※macOSでは開始時刻の変更にinstall.shの再実行が必要です")
                            input("\nEnterで続行...")
                        else:
                            print("\n無効な時刻形式です")
                            input("\nEnterで続行...")
                else:
                    print("\n開始-終了 の形式で入力してください")
                    input("\nEnterで続行...")
        elif cmd == 'i':
            print(f"\n現在の入力フォルダ: {config.get('input_folder', '未設定')}")
            new_input = input("新しい入力フォルダ (空白でキャンセル): ").strip()
            if new_input:
                new_input = os.path.expanduser(new_input)
                config['input_folder'] = new_input
                save_config(config)
                print(f"入力フォルダを変更しました: {new_input}")
            input("\nEnterで続行...")
        elif cmd == 'o':
            print(f"\n現在の出力フォルダ: {config.get('output_folder', '未設定')}")
            new_output = input("新しい出力フォルダ (空白でキャンセル): ").strip()
            if new_output:
                new_output = os.path.expanduser(new_output)
                config['output_folder'] = new_output
                save_config(config)
                print(f"出力フォルダを変更しました: {new_output}")
            input("\nEnterで続行...")

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