#!/bin/bash

echo "KoemojiAuto Status"
echo "=================="

# より正確なプロセス検出（python3も含む）
PIDS=$(ps aux | grep -E "[Pp]ython[3]*.*main\.py$" | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "Status: Running"
    echo "Process ID(s): $PIDS"
else
    echo "Status: Not running"
fi

# 最新のログ
if [ -f "koemoji.log" ]; then
    echo ""
    if [ -n "$PIDS" ]; then
        # 起動中は詳細なログを表示
        echo "Recent log entries (last 20 lines):"
        echo "================================="
        tail -n 20 "koemoji.log"
    else
        # 停止中は簡潔なログ
        echo "Recent log entries:"
        tail -n 5 "koemoji.log"
    fi
fi