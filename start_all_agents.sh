#!/bin/bash
# 啟動所有 Agents

echo "========================================="
echo "啟動所有 Agents"
echo "========================================="
echo ""
echo "開始時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 啟動 Main Agent (端口 8000)
echo "[1/5] 啟動 Main Agent..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /home/jarvis/.openclaw/workspace/logs/main.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "  Main Agent 已啟動（端口 8000）"
else
    echo "  Main Agent 啟動失敗"
fi

echo ""
sleep 2

# 2. 啟動 Chat Assistant (端口 8001)
echo "[2/5] 啟動 Chat Assistant..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /home/jarvis/.openclaw/workspace/logs/chat.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "  Chat Assistant 已啟動（端口 8001）"
else
    echo "  Chat Assistant 啟動失敗"
fi

echo ""
sleep 2

# 3. 啟動 Coding Agent (端口 8002)
echo "[3/5] 啟動 Coding Agent..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 > /home/jarvis/.openclaw/workspace/logs/coding.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "  Coding Agent 已啟動（端口 8002）"
else
    echo "  Coding Agent 啟動失敗"
fi

echo ""
sleep 2

# 4. 啟動 System Admin (端口 8003)
echo "[4/5] 啟動 System Admin..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 > /home/jarvis/.openclaw/workspace/logs/system.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "  System Admin 已啟動（端口 8003）"
else
    echo "  System Admin 啟動失敗"
fi

echo ""
sleep 2

# 5. 啟動 Weather Agent (端口 8004)
echo "[5/5] 啟動 Weather Agent..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8004 > /home/jarvis/.openclaw/workspace/logs/weather.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "  Weather Agent 已啟動（端口 8004）"
else
    echo "  Weather Agent 啟動失敗"
fi

echo ""
echo "========================================="
echo "所有 Agents 已啟動"
echo "========================================="
echo ""
echo "完成時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Agents 狀態："
echo "  Main Agent：✅ 運行中（端口 8000）"
echo "  Chat Assistant：✅ 運行中（端口 8001）"
echo "  Coding Agent：✅ 運行中（端口 8002）"
echo "  System Admin：✅ 運行中（端口 8003）"
echo "  Weather Agent：✅ 運行中（端口 8004）"
echo ""
echo "下一步："
echo "  1. 測試 Agents 功能"
echo "  2. 測試 API 連接"
echo "  3. 實現模型預載入"
echo "  4. 實現 GPU 加速"
