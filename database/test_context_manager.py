#!/usr/bin/env python3
"""
修復 AgentDatabase 上下文管理器
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase


def main():
    """測試 AgentDatabase"""
    print("=" * 60)
    print("測試 AgentDatabase 上下文管理器")
    print("=" * 60)
    print()
    
    # 創建實例
    db = AgentDatabase()
    
    try:
        # 測試上下文管理器
        print("[1/3] 測試上下文管理器...")
        with db:
            print("  上下文管理器正常")
            
            # 測試查詢
            print("[2/3] 測試查詢...")
            tables = db.get_tables()
            print(f"  找到 {len(tables)} 個表")
            
            # 測試更新
            print("[3/3] 測試更新...")
            db.save_log(
                log_id="test_log",
                level="INFO",
                category="test",
                message="測試日誌",
                agent_id="test",
                metadata={'test': True}
            )
            print("  更新正常")
        
        print()
        print("=" * 60)
        print("所有測試通過！")
        print("=" * 60)
        print()
        print("AgentDatabase 已經有上下文管理器")
        print("應該可以直接使用 with db:")
        print()
        print("✅ 上下文管理器正常工作")
        
        return True
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
