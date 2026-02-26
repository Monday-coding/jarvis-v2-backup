#!/usr/bin/env python3
"""
PostgreSQL 數據庫連接器
供所有 Agents 使用
"""

import os
import sys
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timezone

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("⚠️  psycopg2 未安裝，正在安裝...")
    os.system("pip3 install psycopg2-binary --user")
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor


class PostgreSQLConnector:
    """PostgreSQL 數據庫連接器"""

    def __init__(self, 
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "openclaw",
                 user: str = "openclaw",
                 password: str = "openclaw_password_2024"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """連接數據庫"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"❌ 連接數據庫失敗: {e}")
            return False

    def disconnect(self):
        """斷開連接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """執行查詢"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ 執行查詢失敗: {e}")
            return []

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """執行更新/插入/刪除"""
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ 執行更新失敗: {e}")
            self.connection.rollback()
            return False

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


class AgentDatabase:
    """Agent 數據庫操作類"""

    def __init__(self):
        self.db = PostgreSQLConnector()

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """獲取 Agent 信息"""
        with self.db:
            query = "SELECT * FROM agents WHERE agent_id = %s"
            results = self.db.execute_query(query, (agent_id,))
            return results[0] if results else None

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """獲取所有 Agents"""
        with self.db:
            query = "SELECT * FROM agents WHERE is_active = TRUE"
            return self.db.execute_query(query)

    def register_agent_activity(self, agent_id: str, metadata: Dict[str, Any] = None):
        """記錄 Agent 活動"""
        with self.db:
            query = """
                UPDATE agents
                SET updated_at = CURRENT_TIMESTAMP,
                    metadata = metadata::jsonb
                WHERE agent_id = %s
            """
            self.db.execute_update(query, (json.dumps(metadata),))

    # ==================== CONVERSATIONS ====================

    def create_conversation(self, conversation_id: str, channel: str, 
                          user_id: str = None, title: str = None) -> bool:
        """創建對話會話"""
        with self.db:
            query = """
                INSERT INTO conversations (conversation_id, channel, user_id, title)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (conversation_id) DO NOTHING
            """
            return self.db.execute_update(query, (conversation_id, channel, user_id, title))

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """獲取對話會話"""
        with self.db:
            query = "SELECT * FROM conversations WHERE conversation_id = %s"
            results = self.db.execute_query(query, (conversation_id,))
            return results[0] if results else None

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的對話"""
        with self.db:
            query = """
                SELECT * FROM conversations
                WHERE status = 'active'
                ORDER BY updated_at DESC
                LIMIT %s
            """
            return self.db.execute_query(query, (limit,))

    # ==================== MESSAGES ====================

    def save_message(self, message_id: str, conversation_id: str,
                   role: str, content: str, agent_id: str = None,
                   token_count: int = 0, metadata: Dict[str, Any] = None) -> bool:
        """保存消息"""
        with self.db:
            query = """
                INSERT INTO messages (message_id, conversation_id, role, content, agent_id, token_count, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (message_id) DO NOTHING
            """
            return self.db.execute_update(query, (
                message_id, conversation_id, role, content, 
                agent_id, token_count, json.dumps(metadata or {})
            ))

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取對話消息"""
        with self.db:
            query = """
                SELECT * FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.db.execute_query(query, (conversation_id, limit))

    # ==================== KNOWLEDGE BASE ====================

    def save_knowledge(self, entry_id: str, category: str, title: str,
                      content: str, summary: str = None, 
                      tags: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """保存知識"""
        with self.db:
            query = """
                INSERT INTO knowledge_base (entry_id, category, title, content, summary, tags, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (entry_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP,
                    content = EXCLUDED.content,
                    summary = EXCLUDED.summary
            """
            return self.db.execute_update(query, (
                entry_id, category, title, content, summary, 
                tags, json.dumps(metadata or {})
            ))

    def search_knowledge(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索知識庫"""
        with self.db:
            if category:
                sql_query = """
                    SELECT * FROM knowledge_base
                    WHERE category = %s
                    AND (title ILIKE %s OR content ILIKE %s OR tags @> %s::text[])
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                return self.db.execute_query(sql_query, (category, f"%{query}%", f"%{query}%", [query], limit))
            else:
                sql_query = """
                    SELECT * FROM knowledge_base
                    WHERE title ILIKE %s OR content ILIKE %s OR tags @> %s::text[]
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                return self.db.execute_query(sql_query, (f"%{query}%", f"%{query}%", [query], limit))

    # ==================== MEMORY ====================

    def save_memory(self, memory_id: str, title: str, content: str,
                    category: str = None, importance: int = 3, 
                    metadata: Dict[str, Any] = None) -> bool:
        """保存記憶"""
        with self.db:
            query = """
                INSERT INTO memory (memory_id, title, content, category, importance, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (memory_id) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP,
                    access_count = memory.access_count + 1
            """
            return self.db.execute_update(query, (
                memory_id, title, content, category, importance, 
                json.dumps(metadata or {})
            ))

    def get_memory(self, category: str = None, importance: int = None) -> List[Dict[str, Any]]:
        """獲取記憶"""
        with self.db:
            if category and importance:
                query = """
                    SELECT * FROM memory
                    WHERE category = %s AND importance >= %s AND is_active = TRUE
                    ORDER BY importance DESC, last_accessed_at DESC
                """
                return self.db.execute_query(query, (category, importance))
            elif category:
                query = """
                    SELECT * FROM memory
                    WHERE category = %s AND is_active = TRUE
                    ORDER BY importance DESC, last_accessed_at DESC
                """
                return self.db.execute_query(query, (category,))
            else:
                query = """
                    SELECT * FROM memory
                    WHERE is_active = TRUE
                    ORDER BY importance DESC, last_accessed_at DESC
                """
                return self.db.execute_query(query)

    # ==================== LOGS ====================

    def save_log(self, log_id: str, level: str, category: str, 
                 message: str, agent_id: str = None, 
                 context: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> bool:
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

    def get_logs(self, level: str = None, category: str = None, 
                 agent_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """獲取日誌"""
        with self.db:
            conditions = []
            params = []
            
            if level:
                conditions.append("level = %s")
                params.append(level)
            if category:
                conditions.append("category = %s")
                params.append(category)
            if agent_id:
                conditions.append("agent_id = %s")
                params.append(agent_id)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            query = f"""
                SELECT * FROM logs
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.db.execute_query(query, params + [limit])

    # ==================== TASKS ====================

    def create_task(self, task_id: str, title: str, description: str = None,
                    priority: int = 3, assigned_agent_id: str = None,
                    conversation_id: str = None, metadata: Dict[str, Any] = None) -> bool:
        """創建任務"""
        with self.db:
            query = """
                INSERT INTO tasks (task_id, title, description, priority, assigned_agent_id, conversation_id, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            """
            return self.db.execute_update(query, (
                task_id, title, description, priority, 
                assigned_agent_id, conversation_id, json.dumps(metadata or {})
            ))

    def get_tasks(self, status: str = None, assigned_agent_id: str = None) -> List[Dict[str, Any]]:
        """獲取任務"""
        with self.db:
            conditions = []
            params = []
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            if assigned_agent_id:
                conditions.append("assigned_agent_id = %s")
                params.append(assigned_agent_id)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            query = f"""
                SELECT * FROM tasks
                WHERE {where_clause}
                ORDER BY priority ASC, created_at DESC
            """
            return self.db.execute_query(query, params)

    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任務狀態"""
        with self.db:
            query = """
                UPDATE tasks
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    completed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE task_id = %s
            """
            return self.db.execute_update(query, (status, status, task_id))

    def get_tables(self) -> List[Dict[str, Any]]:
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

    # ==================== SYSTEM METRICS ====================

    def save_metric(self, metric_id: str, metric_name: str, metric_value: float,
                     metric_type: str = None, agent_id: str = None,
                     metadata: Dict[str, Any] = None) -> bool:
        """保存系統指標"""
        with self.db:
            query = """
                INSERT INTO system_metrics (metric_id, metric_name, metric_value, metric_type, agent_id, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """
            return self.db.execute_update(query, (
                metric_id, metric_name, metric_value, metric_type, 
                agent_id, json.dumps(metadata or {})
            ))

    def get_metrics(self, metric_name: str = None, agent_id: str = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """獲取系統指標"""
        with self.db:
            conditions = []
            params = []
            
            if metric_name:
                conditions.append("metric_name = %s")
                params.append(metric_name)
            if agent_id:
                conditions.append("agent_id = %s")
                params.append(agent_id)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            query = f"""
                SELECT * FROM system_metrics
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT %s
            """
            return self.db.execute_query(query, params + [limit])


def main():
    """測試數據庫連接和功能"""
    print("=== PostgreSQL 數據庫連接器測試 ===\n")
    
    # 創建數據庫實例
    agent_db = AgentDatabase()
    
    # 測試 1：連接數據庫
    print("測試 1：連接數據庫...")
    with agent_db.db:
        print("✅ 數據庫連接成功！\n")
    
    # 測試 2：獲取所有 Agents
    print("測試 2：獲取所有 Agents...")
    agents = agent_db.get_all_agents()
    print(f"✅ 找到 {len(agents)} 個 Agents：")
    for agent in agents:
        print(f"  - {agent['agent_id']}: {agent['name']} ({agent['model']})")
    print()
    
    def get_tables(self) -> List[Dict[str, Any]]:
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
    
    print("=== 測試完成！數據庫連接器正常工作。===")


if __name__ == "__main__":
    main()
