#!/usr/bin/env python3
"""
清理舊的天氣數據
自動刪除 7 天前的數據、30 天前的警告、3 天前的預報
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase, PostgreSQLConnector
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def clean_old_data():
    """清理舊數據"""
    db = PostgreSQLConnector()
    
    try:
        # 連接數據庫
        if not db.connect():
            print("❌ 無法連接數據庫")
            return False
        
        print("=" * 60)
        print("天氣數據庫清理")
        print("=" * 60)
        print()
            
            # 1. 清理 7 天前的天氣數據
            print("[1/4] 清理 7 天前的天氣數據...")
            
            query = """
                DELETE FROM weather_data
                WHERE observation_time < NOW() - INTERVAL '7 days'
            """
            
            result = db.execute_update(query, ())
            print(f"  ✅ 刪除天氣數據：{result} 條")
            print()
            
            # 2. 清理 30 天前的警告
            print("[2/4] 清理 30 天前的警告...")
            
            query = """
                DELETE FROM weather_alerts
                WHERE effect_start_time < NOW() - INTERVAL '30 days'
            """
            
            result = db.execute_update(query, ())
            print(f"  ✅ 刪除警告：{result} 條")
            print()
            
            # 3. 清理 3 天前的預報
            print("[3/4] 清理 3 天前的預報...")
            
            query = """
                DELETE FROM weather_forecast
                WHERE forecast_time < NOW() - INTERVAL '3 days'
            """
            
            result = db.execute_update(query, ())
            print(f"  ✅ 刪除預報：{result} 條")
            print()
            
            # 4. 清理 30 天前的日誌
            print("[4/4] 清理 30 天前的日誌...")
            
            query = """
                DELETE FROM logs
                WHERE created_at < NOW() - INTERVAL '30 days'
            """
            
            result = db.execute_update(query, ())
            print(f"  ✅ 刪除日誌：{result} 條")
            print()
            
            print("=" * 60)
            print("清理完成！")
            print("=" * 60)
            print()
            print("清理總結：")
            print("  天氣數據：保留最近 7 天")
            print("  天氣警告：保留最近 30 天")
            print("  天氣預報：保留最近 3 天")
            print("  系統日誌：保留最近 30 天")
            print()
            print("斷開數據庫連接...")
            db.disconnect()
            print("✅ 連接已斷開")
            
            return True
            
    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    success = clean_old_data()
    
    if success:
        print()
        print("✅ 清理完成！")
        print()
        print("下一步：")
        print("  1. 設置 Cron Job")
        print("  2. 每天凌晨 2 點自動清理")
        print("  3. 減少數據庫存儲")
    else:
        print()
        print("❌ 清理失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
