#!/bin/bash
# 神經元優化 - 每日執行腳本

# 設置
WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE/neur-opt"
PYTHON_SCRIPT="$SCRIPT_DIR/neur-opt.py"
LOG_FILE="$WORKSPACE/neur-opt/cron.log"
SUMMARY_DIR="$WORKSPACE/neur-opt/summary"

# 確保目錄存在
mkdir -p "$SCRIPT_DIR"
mkdir -p "$SUMMARY_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# 設置日期
TODAY=$(date +%Y-%m-%d)

# 執行日誌
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🧠 開始神經元優化..." | tee -a "$LOG_FILE"
echo "   工作區: $WORKSPACE" | tee -a "$LOG_FILE"
echo "   腳本: $PYTHON_SCRIPT" | tee -a "$LOG_FILE"
echo "   日期: $TODAY" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 檢查腳本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ 腳本不存在: $PYTHON_SCRIPT" | tee -a "$LOG_FILE"
    echo "   請先創建腳本" | tee -a "$LOG_FILE"
    exit 1
fi

# 執行 Python 腳本
cd "$WORKSPACE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🐍 執行神經元優化腳本..." | tee -a "$LOG_FILE"
python3 "$PYTHON_SCRIPT" --date "$TODAY" >> "$LOG_FILE" 2>&1

# 檢查執行結果
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 神經元優化完成" | tee -a "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  神經元優化完成（有錯誤）" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "📊 執行統計：" | tee -a "$LOG_FILE"
echo "   總條目: $(cat "$LOG_FILE" | grep "總條目" | tail -1 | awk '{print $NF}')" | tee -a "$LOG_FILE"
echo "   分類數量: $(cat "$LOG_FILE" | grep "分類完成" | tail -1 | awk '{print $NF}')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 顯示日誌位置
echo "📁 日誌: $LOG_FILE"
echo "   摘要: $SUMMARY_DIR/summary-$TODAY.json"
echo "" | tee -a "$LOG_FILE"

# 知識庫位置
KB_FILE="$WORKSPACE/knowledge-base.md"
echo "📚 知識庫: $KB_FILE" | tee -a "$LOG_FILE"

# 檢查知識庫是否更新
if [ -f "$KB_FILE" ]; then
    KB_SIZE=$(wc -l < "$KB_FILE")
    echo "   知識庫大小: $KB_SIZE 行" | tee -a "$LOG_FILE"
else
    echo "   知識庫: 未創建" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "✨ 神經元優化系統就緒！" | tee -a "$LOG_FILE"
