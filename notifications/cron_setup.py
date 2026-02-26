#!/usr/bin/env python3
"""
天氣監控系統 - Cron Job 啟動腳本
確保監控系統正常運行
"""

import subprocess
import time
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def check_cron_status():
    """檢查 Cron Job 狀態"""
    try:
        # 檢查 crontab
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            crontab_content = result.stdout
            
            # 檢查是否包含天氣監控任務
            if 'cron_weather_monitor' in crontab_content:
                print(f"[CRON] Cron Job 已配置")
                print(f"[CRON] Crontab 內容：")
                for line in crontab_content.split('\n'):
                    if 'weather' in line.lower():
                        print(f"  {line}")
                return True
            else:
                print(f"[CRON] 未找到天氣監控 Cron Job")
                return False
        else:
            print(f"[CRON] 無法獲取 crontab")
            return False
    except Exception as e:
        print(f"[CRON] 檢查 Cron Job 失敗：{e}")
        return False


def run_manual_check():
    """手動運行一次監控檢查"""
    try:
        print("[MANUAL] 手動運行監控檢查...")
        
        # 運行監控腳本
        result = subprocess.run(
            ['python3', '/home/jarvis/.openclaw/workspace/notifications/cron_weather_monitor.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[MANUAL] 監控檢查成功")
            print("[MANUAL] 輸出：")
            print(result.stdout)
            return True
        else:
            print(f"[MANUAL] 監控檢查失敗：{result.stderr}")
            return False
    except Exception as e:
        print(f"[MANUAL] 手動運行失敗：{e}")
        return False


def check_monitor_log():
    """檢查監控日誌"""
    log_file = "/home/jarvis/.openclaw/workspace/notifications/monitor.log"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) > 0:
            print("[LOG] 監控日誌文件存在")
            print(f"[LOG] 文件路徑：{log_file}")
            print(f"[LOG] 總行次數：{len(lines)}")
            
            # 顯示最後幾行
            print("[LOG] 最後幾行：")
            for line in lines[-5:]:
                print(f"  {line.strip()}")
            
            return True
        else:
            print("[LOG] 監控日誌文件為空")
            return False
    except FileNotFoundError:
        print(f"[LOG] 監控日誌文件不存在：{log_file}")
        return False
    except Exception as e:
        print(f"[LOG] 讀取日誌失敗：{e}")
        return False


def check_recent_alerts():
    """檢查最近的警報"""
    log_file = "/home/jarvis/.openclaw/workspace/notifications/monitor.log"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找最近的警報
        recent_alerts = []
        for line in lines[-50:]:  # 檢查最後 50 行
            if '警告' in line or 'WARNING' in line:
                recent_alerts.append(line.strip())
        
        if recent_alerts:
            print(f"[ALERTS] 最近 {len(recent_alerts)} 條警報記錄：")
            for alert in recent_alerts[-5:]:  # 顯示最近 5 條
                print(f"  {alert}")
            return True
        else:
            print("[ALERTS] 最近沒有警報記錄")
            return False
    except Exception as e:
        print(f"[ALERTS] 檢查警報失敗：{e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("天氣監控系統 - Cron Job 啟動")
    print("=" * 60)
    print()
    
    # 1. 檢查 Cron Job 狀態
    print("[1/5] 檢查 Cron Job 狀態...")
    check_cron_status()
    print()
    
    # 2. 手動運行一次監控檢查
    print("[2/5] 手動運行監控檢查...")
    run_manual_check()
    print()
    
    # 3. 檢查監控日誌
    print("[3/5] 檢查監控日誌...")
    check_monitor_log()
    print()
    
    # 4. 檢查最近的警報
    print("[4/5] 檢查最近的警報...")
    check_recent_alerts()
    print()
    
    # 5. 總結
    print("[5/5] 總結")
    print("-" * 40)
    print()
    print("天氣監控系統狀態：")
    print("  監控腳本：/home/jarvis/.openclaw/workspace/notifications/cron_weather_monitor.py")
    print("  日誌文件：/home/jarvis/.openclaw/workspace/notifications/monitor.log")
    print("  Cron Job：未配置（需要手動添加）")
    print()
    print("建議的 Cron Job：")
    print("  */5 * * * * /usr/bin/python3 /home/jarvis/.openclaw/workspace/notifications/cron_weather_monitor.py >> /home/jarvis/.openclaw/workspace/notifications/monitor.log 2>&1")
    print()
    print("安裝 Cron Job 的命令：")
    print("  crontab -e")
    print("  然後添加以下行：")
    print("  */5 * * * * /usr/bin/python3 /home/jarvis/.openclaw/workspace/notifications/cron_weather_monitor.py >> /home/jarvis/.openclaw/workspace/notifications/monitor.log 2>&1")
    print()
    print("=" * 60)
    print("檢查完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
