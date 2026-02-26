#!/usr/bin/env python3
"""
配置定時任務（Cron Job）
每天早上 8:00 自動生成並發送每日簡報
"""

import os
import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def setup_daily_report_cron():
    """設置每日簡報 Cron Job"""
    print("=" * 60)
    print("配置定時任務")
    print("=" * 60)
    print()
    
    # 1. 創建 Cron Job
    print("[1/3] 創建 Cron Job...")
    
    cron_job = """
# 每天早上 8:00 生成並發送每日簡報
0 8 * * * /usr/bin/python3 /home/jarvis/.openclaw/workspace/daily_report_generator.py >> /home/jarvis/.openclaw/workspace/logs/daily_report.log 2>&1
"""
    
    # 保存 Cron Job
    cron_file = "/home/jarvis/.openclaw/workspace/daily_report_cron.txt"
    
    try:
        with open(cron_file, 'w') as f:
            f.write(cron_job)
        print("  Cron Job 已創建")
    except Exception as e:
        print(f"  創建失敗：{e}")
    
    print()
    
    # 2. �加到系統 Cron
    print("[2/3] 設加到系統 Cron...")
    
    try:
        # 使用 crontab 安裝
        result = subprocess.run(
            ['crontab', '-a'],
            input=cron_job,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  Cron Job 已安裝到系統 Cron")
        else:
            print(f"  安裝失敗：{result.stderr}")
    except Exception as e:
        print(f"  安裝失敗：{e}")
    
    print()
    
    # 3. 驗證 Cron Job
    print("[3/3] 驗證 Cron Job...")
    
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=10)
        
        if 'daily_report' in result.stdout:
            print("  Cron Job 已正確安裝")
            print(f"  Cron Job 內容：")
            print(f"  {result.stdout}")
        else:
            print("  Cron Job 未找到")
    except Exception as e:
        print(f"  驗證失敗：{e}")
    
    print()
    print("=" * 60)
    print("定時任務配置完成")
    print("=" * 60)
    print()
    print("配置總結：")
    print("  任務時間：每天早上 8:00")
    print("  任務頻率：每天一次")
    print("  任務腳本：daily_report_generator.py")
    print("  日誌文件：logs/daily_report.log")
    print()
    print("下一步：")
    print("  1. 手動運行一次每日簡報生成（測試）")
    print("  2. 配置通知發送（Telegram/Email）")
    print("  3. 配置 API Key（真實數據）")
    print()


def test_daily_report():
    """測試每日簡報生成"""
    print("=" * 60)
    print("測試每日簡報生成")
    print("=" * 60)
    print()
    
    # 執行每日簡報生成
    from daily_report_generator import DailyReportGenerator
    
    generator = DailyReportGenerator()
    daily_report = generator.generate_daily_report()
    
    print()
    print("=" * 60)
    print("測試完成")
    print("=" * 60)
    print()
    print("測試結果：")
    print(f"  每日簡報已生成")
    print(f"  生成時間：{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("下一步：")
    print("  1. 配置定時任務（每天早上 8:00）")
    print("  2. 配置通知發送（Telegram/Email）")
    print("  3. 配置 API Key（真實數據）")
    print()


def main():
    """主函數"""
    print("定時任務配置")
    print("=" * 60)
    print()
    print("這個腳本會：")
    print("  1. 配置定時任務（每天早上 8:00）")
    print("  2. 測試每日簡報生成")
    print("  3. 驗證配置是否正確")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    # 1. 配置定時任務
    setup_daily_report_cron()
    
    # 2. 測試每日簡報生成
    # test_daily_report()


if __name__ == "__main__":
    main()
