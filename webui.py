#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string, request, send_from_directory
import subprocess
import os
import json
import psutil

app = Flask(__name__)

def is_running():
    """KoeMojiAutoが実行中か確認"""
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and len(cmdline) > 1:
                if 'python' in cmdline[0].lower():
                    for arg in cmdline[1:]:
                        if arg == 'main.py' or arg.endswith('/main.py'):
                            return True
        except:
            pass
    return False

def load_config():
    """設定ファイルを読み込む"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    """設定ファイルを保存"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    """メインページ"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>KoemojiAuto WebUI</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
            color: #1c1e21;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        h1 {
            color: #1877f2;
            font-size: 32px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        h3 {
            color: #65676b;
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status {
            font-size: 20px;
            font-weight: 500;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .running { 
            background-color: #e7f5ed; 
            color: #0b7c3e;
            border: 1px solid #c3e9d0;
        }
        .stopped { 
            background-color: #fde8e8; 
            color: #c53030;
            border: 1px solid #fcc5c5;
        }
        button {
            padding: 12px 24px;
            margin: 6px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            border-radius: 8px;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .start { 
            background-color: #42b883; 
            color: white; 
        }
        .stop { 
            background-color: #e74c3c; 
            color: white; 
        }
        #statusBtn { 
            background-color: #3498db; 
            color: white; 
        }
        button:disabled { 
            opacity: 0.6; 
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #333;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 5px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .config {
            background-color: #f8f9fc;
            padding: 24px;
            margin: 30px 0;
            border-radius: 12px;
            border: 1px solid #e4e5e7;
        }
        .config-item {
            margin: 16px 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .config-item label {
            font-weight: 500;
            color: #65676b;
            min-width: 120px;
        }
        .log {
            background-color: #f8f9fc;
            color: #1c1e21;
            padding: 20px;
            margin: 30px 0;
            border-radius: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            height: 400px;
            overflow-y: auto;
            white-space: pre;
            line-height: 1.6;
            border: 1px solid #e4e5e7;
        }
        .log::-webkit-scrollbar {
            width: 8px;
        }
        .log::-webkit-scrollbar-track {
            background: #f0f2f5;
            border-radius: 4px;
        }
        .log::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        .log::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        select, input {
            padding: 10px 14px;
            margin: 0;
            width: 280px;
            border: 1px solid #e4e5e7;
            border-radius: 8px;
            font-size: 15px;
            background-color: white;
            transition: border-color 0.2s;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><i class="fas fa-microphone-alt"></i> KoemojiAuto WebUI</h1>
        
        <div id="status" class="status">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading...</span>
        </div>
        
        <div style="display: flex; gap: 12px; margin: 24px 0;">
            <button id="startBtn" class="start" onclick="start()">
                <i class="fas fa-play"></i> 開始
            </button>
            <button id="stopBtn" class="stop" onclick="stop()">
                <i class="fas fa-stop"></i> 停止
            </button>
            <button id="statusBtn" onclick="updateStatusManual()">
                <i class="fas fa-sync-alt"></i> ステータス更新
            </button>
        </div>
        
        <div class="config">
            <h3><i class="fas fa-cog"></i> 設定</h3>
            <div class="config-item">
                <label>モード:</label>
                <select id="mode" onchange="updateConfig()">
                    <option value="true">24時間連続</option>
                    <option value="false">時間指定</option>
                </select>
            </div>
            <div class="config-item">
                <label>Whisperモデル:</label>
                <select id="model" onchange="updateConfig()">
                    <option value="tiny">tiny</option>
                    <option value="small">small</option>
                    <option value="medium">medium</option>
                    <option value="large">large</option>
                </select>
            </div>
            <div class="config-item">
                <label>入力フォルダ:</label>
                <input type="text" id="input_folder" onblur="updateConfig()" placeholder="./input">
            </div>
            <div class="config-item">
                <label>出力フォルダ:</label>
                <input type="text" id="output_folder" onblur="updateConfig()" placeholder="./output">
            </div>
        </div>
        
        <div>
            <h3><i class="fas fa-terminal"></i> ログ</h3>
            <div id="log" class="log">Loading logs...</div>
        </div>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.running) {
                        statusDiv.className = 'status running';
                        statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> <span>ステータス: 実行中 (PID: ' + data.pid + ')</span>';
                    } else {
                        statusDiv.className = 'status stopped';
                        statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> <span>ステータス: 停止中</span>';
                    }
                });
        }
        
        function loadConfig() {
            fetch('/config')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('mode').value = String(data.continuous_mode || false);
                    document.getElementById('model').value = data.whisper_model || 'large';
                    document.getElementById('input_folder').value = data.input_folder || '';
                    document.getElementById('output_folder').value = data.output_folder || '';
                });
        }
        
        function updateConfig() {
            const config = {
                continuous_mode: document.getElementById('mode').value === 'true',
                whisper_model: document.getElementById('model').value,
                input_folder: document.getElementById('input_folder').value,
                output_folder: document.getElementById('output_folder').value
            };
            
            fetch('/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
        }
        
        function start() {
            const btn = document.getElementById('startBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 開始中';
            
            fetch('/start', {method: 'POST'})
                .then(() => {
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-play"></i> 開始';
                        updateStatus();
                    }, 2000);
                    updateLog();
                })
                .catch(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-play"></i> 開始';
                });
        }
        
        function stop() {
            const btn = document.getElementById('stopBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 停止中';
            
            fetch('/stop', {method: 'POST'})
                .then(() => {
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fas fa-stop"></i> 停止';
                        updateStatus();
                    }, 2000);
                    updateLog();
                })
                .catch(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-stop"></i> 停止';
                });
        }
        
        function updateLog() {
            fetch('/log')
                .then(response => response.text())
                .then(data => {
                    const logDiv = document.getElementById('log');
                    logDiv.textContent = data;
                });
        }
        
        function updateStatusManual() {
            const btn = document.getElementById('statusBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 更新中';
            
            updateStatus();
            updateLog();
            
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-sync-alt"></i> ステータス更新';
            }, 1000);
        }
        
        // 初期化
        updateStatus();
        loadConfig();
        updateLog();
        
        // 定期更新
        setInterval(updateStatus, 5000);
        setInterval(updateLog, 3000);
    </script>
</body>
</html>
    ''')

@app.route('/status')
def status():
    """ステータス取得"""
    running = is_running()
    pid = None
    if running:
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and len(cmdline) > 1:
                    if 'python' in cmdline[0].lower():
                        for arg in cmdline[1:]:
                            if arg == 'main.py' or arg.endswith('/main.py'):
                                pid = proc.pid
                                break
            except:
                pass
    return jsonify({"running": running, "pid": pid})

@app.route('/config', methods=['GET', 'POST'])
def config():
    """設定の取得・更新"""
    if request.method == 'GET':
        return jsonify(load_config())
    else:
        config_data = load_config()
        new_config = request.json
        config_data.update(new_config)
        save_config(config_data)
        return jsonify({"status": "updated"})

@app.route('/start', methods=['POST'])
def start():
    """KoemojiAuto開始"""
    script = './start_koemoji.sh' if os.name != 'nt' else 'start_koemoji.bat'
    subprocess.run([script])
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop():
    """KoemojiAuto停止"""
    script = './stop_koemoji.sh' if os.name != 'nt' else 'stop_koemoji.bat'
    subprocess.run([script])
    return jsonify({"status": "stopped"})

@app.route('/log')
def log():
    """ログ取得（最新30行）"""
    try:
        with open('koemoji.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return ''.join(lines[-30:])
    except:
        return "ログファイルが見つかりません"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)