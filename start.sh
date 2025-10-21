#!/bin/bash

# Microburbs Dashboard 启动脚本

echo "🛑 停止所有正在运行的应用..."
pkill -f "python.*app.py" 2>/dev/null || true

sleep 1

echo ""
echo "🚀 启动 Microburbs Property Dashboard..."
echo ""

cd "$(dirname "$0")"
python3 app.py

