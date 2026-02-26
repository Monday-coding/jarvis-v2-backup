#!/usr/bin/env python3
"""
修復 AgentDatabase 上下文管理器
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import PostgreSQLConnector
from datetime import datetime, timezone, timedelta
import json

# 香港時區
HK_TZ = timezone(timedelta(hours=8))
# HK_TZ = timezone(timedelta(hours=8))


class AgentDatabaseFixed:
    """修復版的 AgentDatabase，包含上下文管理器"""

    def __init__(self):
        self.db = PostgreSQLConnector()

    def __enter__(self):
        """上下文管理器入口"""
        self.db.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.db.disconnect()

    def get_tables(self):
        """獲取所有表"""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        with self.db:
            tables = self.db.execute_query(query)
            return tables

    def save_log(self, log_id, level, category, message, agent_id, context=None, metadata=None):
        """保存日誌"""
        with self.db:
            query = """
                INSERT INTO logs (log_id, level, category, message, agent_id, context, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
            """
            return self.db.execute_update(query, (
                log_id, level, category, message, agent_id, 
                json.dumps(context or {}), json.dumps(metadata or {})
            ))

    def execute_query(self, query, params=None):
        """執行查詢"""
        with self.db:
            return self.db.execute_query(query, params or ())

    def execute_update(self, query, params=None):
        """執行更新"""
        with self.db:
            return self.db.execute_update(query, params or ())

    def connect(self):
        """連接數據庫"""
        return self.db.connect()

    def disconnect(self):
        """斷開連接"""
        return self.db.disconnect()


def main():
    """測試修復的 AgentDatabase"""
    print("=" * 60)
    print("測試 AgentDatabase 上下文管理器")
    print("=" * 60)
    print()

    # 創建實例
    db = AgentDatabaseFixed()

    try:
        # 測試上下文管理器
        print("[1/3] 測試上下文管理器...")
        with db:
            print("  ✅ 上下文管理器正常工作")
            print()

        # 測試查詢
        print("[2/3] 測試查詢功能...")
        tables = db.get_tables()
        print(f"  ✅ 找到 {len(tables)} 個表")
        for table in tables[:5]:
            print(f"     - {table['table_name']}")
        print()

        # 測試更新
        print("[3/3] 測試更新功能...")
        db.save_log(
            log_id="test_log_fixed",
            level="INFO",
            category="test",
            message="測試修復的 AgentDatabase",
            agent_id="test",
            context={'test': True},
            metadata={'fixed': True}
        )
        print("  ✅ 更新功能正常")
        print()

        print("=" * 60)
        print("所有測試通過！")
        print("=" * 60)
        print()
        print("AgentDatabase 已修復，可以正常使用")
        print("包含上下文管理器：__enter__ 和 __exit__")

        return True

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
