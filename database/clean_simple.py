#!/usr/bin/env python3
"""
清理舊的天氣數據
簡潔版本
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import PostgreSQLConnector
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))

# 創建數據庫連接
db = PostgreSQLConnector(
    host="localhost",
    port=5432,
    database="openclaw",
    user="postgres",
    password="openclaw_password_2024"
)


def clean_old_data():
    """清理舊數據"""
    print("=" * 60)
    print("數據庫清理")
    print("=" * 60)
    print()
    
    try:
        # 連接數據庫
        print("[1/4] 連接數據庫...")
        if not db.connect():
            print("  連接失敗")
            return False
        print("  連接成功")
        print()
        
        # 清理 7 天前的天氣數據
        print("[2/4] 清理 7 天前的天氣數據...")
        query = "DELETE FROM weather_data WHERE observation_time < NOW() - INTERVAL '7 days'"
        result = db.execute_update(query, ())
        print(f"  刪除天氣數據：{result} 條")
        print()
        
        # 清理 30 天前的警告
        print("[3/4] 清理 30 天前的警告...")
        query = "DELETE FROM weather_alerts WHERE effect_start_time < NOW() - INTERVAL '30 days'"
        result = db.execute_update(query, ())
        print(f"  刪除警告：{result} 條")
        print()
        
        # 清理 30 天前的日誌
        print("[4/4] 清理 30 天前的日誌...")
        query = "DELETE FROM logs WHERE created_at < NOW() - INTERVAL '30 days'"
        result = db.execute_update(query, ())
        print(f"  刪除日誌：{result} 條")
        print()
        
        # 斷開連接
        print("斷開數據庫連接...")
        db.disconnect()
        print("  連接已斷開")
        print()
        
        print("=" * 60)
        print("清理完成！")
        print("=" * 60)
        print()
        print("清理策略：")
        print("  天氣數據：保留最近 7 天")
        print("  天氣警告：保留最近 30 天")
        print("  系統日誌：保留最近 30 天")
        print()
        print("數據庫已優化，減少了存儲空間！")
        
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
        print("✅ 數據庫清理完成！")
        print()
        print("下一步：")
        print("  1. 查看數據庫狀態")
        print("  2. 配置定期清理（每天凌晨 2 點）")
        print("  3. 繼續其他任務")
    else:
        print()
        print("❌ 數據庫清理失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
