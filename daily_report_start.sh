#!/bin/bash
# 每天早上 8:00 自動生成每日簡報

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日簡報啟動中..." >> /home/jarvis/.openclaw/workspace/logs/daily_report.log

# 運行每日簡報生成腳本
cd /home/jarvis/.openclaw/workspace
python3 daily_report_generator.py >> /home/jarvis/.openclaw/workspace/logs/daily_report.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日簡報完成" >> /home/jarvis/.openclaw/workspace/logs/daily_report.log
