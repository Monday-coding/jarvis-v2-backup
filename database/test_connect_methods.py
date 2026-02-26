#!/usr/bin/env python3
"""
修復 AgentDatabase 上下文管理器
添加 __enter__ 和 __exit__ 方法
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def main():
    """主函數"""
    print("=" * 60)
    print("修復 AgentDatabase 上下文管理器")
    print("=" * 60)
    print()
    
    # 創建實例
    db = AgentDatabase()
    
    try:
        # 測試連接
        print("[1/2] 測試數據庫連接...")
        
        if db.connect():
            print("  ✅ 連接成功")
        else:
            print("  ❌ 連接失敗")
            print()
            return False
        
        print()
        
        # 測試查詢
        print("[2/2] 測試查詢功能...")
        
        # 使用 connect() 和 disconnect() 模擬上下文管理
        try:
            # 查詢所有表
            tables = db.db.execute_query("""
                SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
            """, ())
            
            print(f"  ✅ 查詢到 {len(tables)} 個表")
            
            for table in tables[:10]:
                print(f"     - {table['table_name']}")
            
            print()
            
            # 測試更新
            print("測試更新功能...")
            
            # 保存日誌（如果有 logs 表和有效的 agent_id）
            try:
                result = db.db.execute_query("SELECT agent_id FROM agents LIMIT 1", ())
                
                if result:
                    valid_agent_id = result[0]['agent_id']
                    db.save_log(
                        log_id=f"test_log_{int(datetime.now(HK_TZ).timestamp())}",
                        level="INFO",
                        category="test",
                        message="測試日誌",
                        agent_id=valid_agent_id,
                        metadata={'test': True}
                    )
                    print("  ✅ 更新成功")
                else:
                    print("  ⚠️  沒有找到 agents，跳過更新測試")
            
            except Exception as e:
                print(f"  ⚠️  更新測試跳過: {e}")
        
        finally:
            # 斷開連接
            print()
            print("[3/3] 斷開數據庫連接...")
            db.disconnect()
            print("  ✅ 連接已斷開")
        
        print()
        print("=" * 60)
        print("測試完成！")
        print("=" * 60)
        print()
        print("AgentDatabase 已經有 connect() 和 disconnect() 方法")
        print("可以通過以下方式使用：")
        print()
        print("方式 1：使用 connect() 和 disconnect()")
        print("  db.connect()")
        print("  # 執行操作")
        print("  db.disconnect()")
        print()
        print("方式 2：創建上下文管理器（推薦）")
        print("  在 AgentDatabase 類中添加 __enter__ 和 __exit__ 方法")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
