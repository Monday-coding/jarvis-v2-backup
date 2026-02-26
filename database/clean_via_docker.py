#!/usr/bin/env python3
"""
清理舊的天氣數據
通過 Docker 執行
"""

import os
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def clean_old_data():
    """清理舊數據"""
    print("=" * 60)
    print("數據庫清理 (Docker 版本)")
    print("=" * 60)
    print()
    
    # 1. 清理 7 天前的天氣數據
    print("[1/4] 清理 7 天前的天氣數據...")
    
    command = """
        docker exec openclaw-postgres psql -U openclaw -d openclaw -c "
            DELETE FROM weather_data WHERE observation_time < NOW() - INTERVAL '7 days';
        "
    """
    
    result = os.system(command)
    if result == 0:
        print("  ✅ 完成")
    else:
        print("  ❌ 失敗")
    print()
    
    # 2. 清理 30 天前的警告
    print("[2/4] 清理 30 天前的警告...")
    
    command = """
        docker exec openclaw-postgres psql -U openclaw -d openclaw -c "
            DELETE FROM weather_alerts WHERE effect_start_time < NOW() - INTERVAL '30 days';
        "
    """
    
    result = os.system(command)
    if result == 0:
        print("  ✅ 完成")
    else:
        print("  ❌ 失敗")
    print()
    
    # 3. 清理 3 天前的預報
    print("[3/4] 清理 3 天前的預報...")
    
    command = """
        docker exec openclaw-postgres psql -U openclaw -d openclaw -c "
            DELETE FROM weather_forecast WHERE forecast_time < NOW() - INTERVAL '3 days';
        "
    """
    
    result = os.system(command)
    if result == 0:
        print("  ✅ 完成")
    else:
        print("  ❌ 失敗")
    print()
    
    # 4. 清理 30 天前的日誌
    print("[4/4] 清理 30 天前的日誌...")
    
    command = """
        docker exec openclaw-postgres psql -U openclaw -d openclaw -c "
            DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days';
        "
    """
    
    result = os.system(command)
    if result == 0:
        print("  ✅ 完成")
    else:
        print("  ❌ 失敗")
    print()
    
    print("=" * 60)
    print("清理完成！")
    print("=" * 60)
    print()
    print("清理策略：")
    print("  天氣數據：保留最近 7 天")
    print("  天氣警告：保留最近 30 天")
    print("  天氣預報：保留最近 3 天")
    print("  系統日誌：保留最近 30 天")
    print()
    print("數據庫已優化，減少了存儲空間！")


def main():
    """主函數"""
    clean_old_data()
    
    print()
    print("✅ 清理完成！")
    print()
    print("下一步：")
    print("  1. 查看數據庫狀態")
    print("  2. 配置定期清理（Cron Job）")
    print("  3. 繼續其他任務")


if __name__ == "__main__":
    main()
