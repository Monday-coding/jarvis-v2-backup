#!/bin/bash
# RAG 緩存更新腳本
# 用於 cron 定期更新 RAG 索引

WORKSPACE="$HOME/.openclaw/workspace"
RAG_SCRIPT="$WORKSPACE/rag_cache.py"
LOG_FILE="$WORKSPACE/rag/update.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 RAG 索引更新..." >> "$LOG_FILE"

# 執行 RAG 索引更新
cd "$WORKSPACE"

if [ -f "$RAG_SCRIPT" ]; then
    python3 "$RAG_SCRIPT" >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ RAG 索引更新完成" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ RAG 腳本不存在: $RAG_SCRIPT" >> "$LOG_FILE"
fi
