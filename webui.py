#!/usr/bin/env python3
from flask import Flask, jsonify, render_template_string, request, send_from_directory
import subprocess
import os
import json
import psutil
from datetime import datetime
import calendar

app = Flask(__name__, static_folder='static')

def is_running():
    """KoeMojiAutoが実行中か確認"""
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and len(cmdline) > 1:
                if 'python' in cmdline[0].lower() or 'python3' in cmdline[0].lower():
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

@app.route('/favicon.ico')
def favicon():
    """ファビコンを提供"""
    return send_from_directory('static', 'icon.png')

@app.route('/static/<path:path>')
def send_static(path):
    """静的ファイルを提供"""
    return send_from_directory('static', path)

@app.route('/')
def index():
    """メインページ"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>KoemojiAuto</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/static/icon.png">
    <link rel="apple-touch-icon" href="/static/icon.png">
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
        .app-icon {
            width: 40px;
            height: 40px;
            object-fit: contain;
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
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #e4e5e7;
        }
        .tab {
            background: none;
            border: none;
            padding: 12px 20px;
            color: #65676b;
            font-size: 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }
        .tab:hover {
            color: #1877f2;
            background-color: #f0f2f5;
        }
        .tab.active {
            color: #1877f2;
            border-bottom-color: #1877f2;
            font-weight: 600;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .summary-container {
            max-width: 800px;
            margin: 0 auto;
        }
        .summary-list {
            margin-top: 20px;
        }
        .summary-item {
            background-color: #f8f9fc;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 16px;
            transition: all 0.2s;
            cursor: pointer;
        }
        .summary-item:hover {
            background-color: #f0f2f5;
            transform: translateY(-1px);
        }
        .summary-date {
            font-weight: 600;
            font-size: 18px;
            color: #1c1e21;
            margin-bottom: 12px;
        }
        .summary-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .stat-count {
            font-weight: 500;
            font-size: 16px;
        }
        .stat-label {
            color: #65676b;
            font-size: 14px;
        }
        .no-data {
            text-align: center;
            color: #adb5bd;
            padding: 40px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <img src="/static/icon.png" alt="KoemojiAuto" class="app-icon">
            KoemojiAuto WebUI
        </h1>
        
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
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('config')">
                <i class="fas fa-cog"></i> 設定
            </button>
            <button class="tab" onclick="switchTab('summary')">
                <i class="fas fa-list"></i> サマリー
            </button>
        </div>
        
        <div id="configTab" class="tab-content active">
            <div class="config">
                <h3><i class="fas fa-cog"></i> 設定</h3>
            <div class="config-item">
                <label>モード:</label>
                <select id="mode" onchange="updateMode()">
                    <option value="true">24時間連続</option>
                    <option value="false">時間指定</option>
                </select>
            </div>
            <div id="timeConfig" class="config-item" style="display: none;">
                <label>処理時間:</label>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="time" id="start_time" onchange="updateConfig()" style="width: 120px;">
                    <span>〜</span>
                    <input type="time" id="end_time" onchange="updateConfig()" style="width: 120px;">
                </div>
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
        
        <div id="summaryTab" class="tab-content">
            <div class="summary-container">
                <h3><i class="fas fa-list"></i> 処理サマリー一覧</h3>
                <div class="summary-list" id="summaryList">
                    <div style="text-align: center; padding: 40px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
                        <p>読み込み中...</p>
                    </div>
                </div>
            </div>
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
                    document.getElementById('start_time').value = data.process_start_time || '19:00';
                    document.getElementById('end_time').value = data.process_end_time || '07:00';
                    updateMode();
                });
        }
        
        function updateMode() {
            const isContinuous = document.getElementById('mode').value === 'true';
            document.getElementById('timeConfig').style.display = isContinuous ? 'none' : 'block';
            updateConfig();
        }
        
        function updateConfig() {
            const config = {
                continuous_mode: document.getElementById('mode').value === 'true',
                whisper_model: document.getElementById('model').value,
                input_folder: document.getElementById('input_folder').value,
                output_folder: document.getElementById('output_folder').value,
                process_start_time: document.getElementById('start_time').value,
                process_end_time: document.getElementById('end_time').value
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
        
        // タブ切り替え
        function switchTab(tabName) {
            // タブボタンの状態を更新
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            // タブコンテンツの表示切り替え
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
            
            // サマリータブの場合は一覧を読み込み
            if (tabName === 'summary') {
                loadSummaryList();
            }
        }
        
        // カレンダー関連
        let currentDate = new Date();
        let selectedDate = null;
        let summaryCache = {};
        
        function initCalendar() {
            renderCalendar();
            loadMonthSummaries();
        }
        
        function renderCalendar() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth();
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const prevLastDay = new Date(year, month, 0);
            
            // 月表示を更新
            const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
            document.getElementById('monthYear').textContent = `${year}年 ${monthNames[month]}`;
            
            // カレンダーをクリア
            const calendar = document.getElementById('calendar');
            calendar.innerHTML = '';
            
            // 曜日ヘッダー
            const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
            weekdays.forEach(day => {
                const dayHeader = document.createElement('div');
                dayHeader.style.textAlign = 'center';
                dayHeader.style.fontWeight = 'bold';
                dayHeader.style.color = '#65676b';
                dayHeader.textContent = day;
                calendar.appendChild(dayHeader);
            });
            
            // 前月の日を追加
            const firstDayOfWeek = firstDay.getDay();
            for (let i = firstDayOfWeek - 1; i >= 0; i--) {
                const day = prevLastDay.getDate() - i;
                createDayElement(new Date(year, month - 1, day), true);
            }
            
            // 今月の日を追加
            for (let day = 1; day <= lastDay.getDate(); day++) {
                createDayElement(new Date(year, month, day), false);
            }
            
            // 翌月の日を追加
            const remainingDays = 42 - (firstDayOfWeek + lastDay.getDate());
            for (let day = 1; day <= remainingDays; day++) {
                createDayElement(new Date(year, month + 1, day), true);
            }
        }
        
        function createDayElement(date, inactive) {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'calendar-day' + (inactive ? ' inactive' : '');
            dayDiv.dataset.date = date.toISOString().split('T')[0];
            
            const dayNumber = document.createElement('div');
            dayNumber.className = 'calendar-day-number';
            dayNumber.textContent = date.getDate();
            dayDiv.appendChild(dayNumber);
            
            const dayStats = document.createElement('div');
            dayStats.className = 'calendar-day-stats';
            dayStats.innerHTML = '<span style="color: #adb5bd;">-</span>';
            dayDiv.appendChild(dayStats);
            
            dayDiv.addEventListener('click', () => selectDate(date));
            
            document.getElementById('calendar').appendChild(dayDiv);
        }
        
        function changeMonth(direction) {
            currentDate.setMonth(currentDate.getMonth() + direction);
            renderCalendar();
            loadMonthSummaries();
        }
        
        function selectDate(date) {
            selectedDate = date;
            const dateStr = date.toISOString().split('T')[0];
            
            // アクティブなクラスを更新
            document.querySelectorAll('.calendar-day').forEach(day => day.classList.remove('active'));
            const selectedDiv = document.querySelector(`[data-date="${dateStr}"]`);
            if (selectedDiv) selectedDiv.classList.add('active');
            
            // 詳細を表示
            showDayDetail(dateStr);
        }
        
        function loadMonthSummaries() {
            const year = currentDate.getFullYear();
            const month = currentDate.getMonth() + 1;
            
            fetch(`/summaries/${year}/${month}`)
                .then(response => response.json())
                .then(data => {
                    summaryCache = data;
                    updateCalendarStats();
                })
                .catch(error => console.error('Failed to load summaries:', error));
        }
        
        function updateCalendarStats() {
            document.querySelectorAll('.calendar-day').forEach(dayDiv => {
                const date = dayDiv.dataset.date;
                const stats = summaryCache[date];
                const statsDiv = dayDiv.querySelector('.calendar-day-stats');
                
                if (stats) {
                    statsDiv.innerHTML = `
                        <div style="color: #42b883;">✓ ${stats.processed}</div>
                        ${stats.failed > 0 ? `<div style="color: #e74c3c;">✗ ${stats.failed}</div>` : ''}
                    `;
                } else {
                    statsDiv.innerHTML = '<span style="color: #adb5bd;">-</span>';
                }
            });
        }
        
        function showDayDetail(dateStr) {
            const stats = summaryCache[dateStr];
            const detailDiv = document.getElementById('dayDetail');
            
            if (stats) {
                detailDiv.innerHTML = `
                    <h4>${dateStr} の処理結果</h4>
                    <div class="stat-line">
                        <span>➕ キュー追加</span>
                        <span>${stats.queued}件</span>
                    </div>
                    <div class="stat-line">
                        <span>✅ 処理完了</span>
                        <span>${stats.processed}件</span>
                    </div>
                    <div class="stat-line">
                        <span>❌ 処理失敗</span>
                        <span>${stats.failed}件</span>
                    </div>
                `;
                detailDiv.classList.add('active');
            } else {
                detailDiv.innerHTML = `
                    <h4>${dateStr}</h4>
                    <p style="text-align: center; color: #adb5bd;">この日の処理はありません</p>
                `;
                detailDiv.classList.add('active');
            }
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
                    if 'python' in cmdline[0].lower() or 'python3' in cmdline[0].lower():
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

@app.route('/summaries/<int:year>/<int:month>')
def get_month_summaries(year, month):
    """指定月のサマリーを取得"""
    summaries = {}
    
    # 月の日数を取得
    num_days = calendar.monthrange(year, month)[1]
    
    # 各日のログから統計を集計
    for day in range(1, num_days + 1):
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        stats = collect_stats_from_log(date_str)
        if stats and (stats['queued'] > 0 or stats['processed'] > 0 or stats['failed'] > 0):
            summaries[date_str] = stats
    
    return jsonify(summaries)

def collect_stats_from_log(target_date):
    """ログファイルから指定日の統計を集計"""
    try:
        stats = {
            "queued": 0,
            "processed": 0,
            "failed": 0
        }
        
        log_path = "koemoji.log"
        if not os.path.exists(log_path):
            return stats
        
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 日付が含まれているか確認
                if target_date not in line:
                    continue
                
                # 各種イベントをカウント
                if "➕ キューに追加" in line:
                    stats["queued"] += 1
                elif "✅ 文字起こし完了" in line:
                    stats["processed"] += 1
                elif "❌ 文字起こし失敗" in line:
                    stats["failed"] += 1
        
        return stats
        
    except Exception as e:
        print(f"ログファイルの読み込み中にエラーが発生しました: {e}")
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)