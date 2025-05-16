#!/usr/bin/env python3
import os
import json

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def main():
    while True:
        config = load_config()
        mode = "24時間" if config.get('continuous_mode', False) else "時間指定"
        
        print("\n=== KoemojiAuto ===")
        print("1. 実行")
        print("2. 自動実行設定")
        print("3. 自動実行ON/OFF")
        print("4. 設定変更")
        print("0. 終了")
        print(f"\n現在: {mode}モード")
        
        choice = input("\n選択 > ")
        
        if choice == '0':
            break
        elif choice == '1':
            os.system('./start_koemoji.sh' if os.name != 'nt' else 'start_koemoji.bat')
        elif choice == '2':
            os.system('./install.sh' if os.name != 'nt' else 'install.bat')
        elif choice == '3':
            os.system('./toggle.sh' if os.name != 'nt' else 'toggle.bat')
        elif choice == '4':
            print("\n=== 設定変更 ===")
            print("1. モデル変更")
            print("2. 動作モード切替")
            print("3. 時間設定")
            print("0. 戻る")
            
            sub_choice = input("\n選択 > ")
            
            if sub_choice == '1':
                current = config.get('whisper_model', 'large')
                print(f"\n現在のモデル: {current}")
                print("1. tiny   (最速・低精度)")
                print("2. small  (高速・中精度)")
                print("3. medium (中速・高精度)")
                print("4. large  (低速・最高精度)")
                model_choice = input("\n選択 > ")
                models = {'1': 'tiny', '2': 'small', '3': 'medium', '4': 'large'}
                if model_choice in models:
                    config['whisper_model'] = models[model_choice]
                    save_config(config)
                    print(f"\nモデルを{models[model_choice]}に変更しました")
                    input("Enterで続行...")
                    
            elif sub_choice == '2':
                current_mode = config.get('continuous_mode', False)
                print(f"\n現在: {'24時間モード' if current_mode else '時間指定モード'}")
                print("1. 時間指定モード (19:00-翌7:00)")
                print("2. 24時間モード")
                mode_choice = input("\n選択 > ")
                if mode_choice in ['1', '2']:
                    config['continuous_mode'] = (mode_choice == '2')
                    save_config(config)
                    print(f"\n{'24時間' if mode_choice == '2' else '時間指定'}モードに変更しました")
                    input("Enterで続行...")
                    
            elif sub_choice == '3':
                if not config.get('continuous_mode', False):
                    end_time = config.get('process_end_time', '07:00')
                    print(f"\n現在の終了時刻: {end_time}")
                    print("新しい終了時刻を入力 (例: 08:30)")
                    new_time = input("時刻 > ")
                    if ':' in new_time:
                        config['process_end_time'] = new_time
                        save_config(config)
                        print(f"\n終了時刻を{new_time}に変更しました")
                    else:
                        print("\n無効な形式です")
                else:
                    print("\n24時間モードでは時間設定は不要です")
                input("Enterで続行...")

if __name__ == "__main__":
    main()