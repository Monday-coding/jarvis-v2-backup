#!/usr/bin/env python3
"""
OpenClaw PostgreSQL 連接腳本
提供各 Agent 共用的數據庫訪問
"""

import psycopg2
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class OpenClawDatabase:
    """OpenClaw 數據庫管理類"""
    
    def __init__(self, host="localhost", port=5432, 
                 database="openclaw", user="openclaw", 
                 password="openclaw_password_2024"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self):
        """連接到數據庫"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = True
            print(f"✓ 已連接到 PostgreSQL: {self.host}:{self.port}/{self.database}")
            return True
        except psycopg2.Error as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """斷開連接"""
        if self.connection:
            self.connection.close()
            print("✓ 已斷開 PostgreSQL 連接")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List[Dict]]:
        """執行查詢並返回結果"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                
                # 獲取列名
                columns = [desc[0] for desc in cursor.description]
                
                # 轉換為字典列表
                results = []
                for row in cursor:
                    results.append(dict(zip(columns, row)))
                
                return results
        except psycopg2.Error as e:
            print(f"❌ 查詢失敗: {e}")
            return None
    
    def get_agents(self) -> List[Dict]:
        """獲取所有 Agents"""
        query = "SELECT * FROM agents ORDER BY id"
        return self.execute_query(query)
    
    def get_active_agents(self) -> List[Dict]:
        """獲取活躍的 Agents"""
        query = "SELECT * FROM agents WHERE is_active = TRUE ORDER BY id"
        return self.execute_query(query)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """獲取特定對話"""
        query = "SELECT * FROM conversations WHERE conversation_id = %s"
        return self.execute_query(query, (conversation_id,))
    
    def get_knowledge_base(self, category: Optional[str] = None, 
                         limit: int = 100) -> List[Dict]:
        """獲取知識庫條目"""
        if category:
            query = """
                SELECT * FROM knowledge_base 
                WHERE category = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            return self.execute_query(query, (category, limit))
        else:
            query = """
                SELECT * FROM knowledge_base 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            return self.execute_query(query, (limit,))
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索知識庫（使用 LIKE 查詢）"""
        search_query = f"%{query}%"
        sql_query = """
            SELECT * FROM knowledge_base 
            WHERE title ILIKE %s OR content ILIKE %s OR array_to_string(tags, ',') ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.execute_query(sql_query, (search_query, search_query, search_query, top_k))
    
    def add_to_knowledge_base(self, category: str, title: str, 
                           content: str, summary: str = "", 
                           tags: List[str] = [], 
                           conversation_state: str = "new") -> bool:
        """添加條目到知識庫"""
        query = """
            INSERT INTO knowledge_base 
            (entry_id, category, title, content, summary, tags, 
             conversation_state, source, created_at)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, ARRAY[%s]::text[], %s, 'neur-opt', NOW())
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (category, title, content, summary, 
                                       ', '.join(tags), conversation_state))
            print(f"✓ 已添加到知識庫: {title}")
            return True
        except psycopg2.Error as e:
            print(f"❌ 添加失敗: {e}")
            return False
    
    def get_memory(self, limit: int = 100, 
                 category: Optional[str] = None) -> List[Dict]:
        """獲取記憶"""
        if category:
            query = "SELECT * FROM memory WHERE category = %s AND is_active = TRUE ORDER BY updated_at DESC LIMIT %s"
            return self.execute_query(query, (category, limit))
        else:
            query = "SELECT * FROM memory WHERE is_active = TRUE ORDER BY updated_at DESC LIMIT %s"
            return self.execute_query(query, (limit,))
    
    def add_log(self, level: str, category: str, message: str,
                  agent_id: Optional[str] = None, metadata: Dict = None) -> bool:
        """添加日誌"""
        query = """
            INSERT INTO logs (log_id, level, category, message, agent_id, context, created_at, metadata)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s::jsonb, NOW(), %s::jsonb)
        """
        
        context_json = json.dumps(metadata, ensure_ascii=False) if metadata else '{}'
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else {}
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (level, category, message, agent_id, context_json, metadata_json))
            print(f"✓ 已添加日誌: [{level}] {message[:50]}")
            return True
        except psycopg2.Error as e:
            print(f"❌ 添加日誌失敗: {e}")
            return False
    
    def get_session_state(self, session_id: str) -> Optional[Dict]:
        """獲取對話狀態"""
        query = "SELECT * FROM session_state WHERE session_id = %s ORDER BY updated_at DESC LIMIT 1"
        return self.execute_query(query, (session_id,))
    
    def update_session_state(self, session_id: str, current_agent_id: str,
                          state: Dict) -> bool:
        """更新對話狀態"""
        query = """
            INSERT INTO session_state (session_id, conversation_id, current_agent_id, state, 
                                    context_window, created_at, updated_at)
            VALUES (%s, %s, %s, %s::jsonb, ARRAY[]::integer[], NOW(), NOW())
            ON CONFLICT (session_id)
            DO UPDATE SET current_agent_id = %s, state = %s::jsonb, updated_at = NOW()
        """
        
        state_json = json.dumps(state, ensure_ascii=False)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (session_id, session_id, current_agent_id, state_json))
            print(f"✓ 已更新對話狀態: {session_id}")
            return True
        except psycopg2.Error as e:
            print(f"❌ 更新對話狀態失敗: {e}")
            return False
    
    def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """獲取最近的對話消息"""
        query = """
            SELECT m.*, a.name as agent_name
            FROM messages m
            JOIN agents a ON m.agent_id = a.agent_id
            WHERE m.conversation_id = %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (conversation_id, limit))
    
    def get_agent_performance(self, agent_id: str, days: int = 7) -> List[Dict]:
        """獲取 Agent 性能統計"""
        query = """
            SELECT 
                COUNT(*) as total_messages,
                COUNT(DISTINCT conversation_id) as total_conversations,
                AVG(token_count) as avg_tokens,
                MAX(created_at) as last_activity
            FROM messages
            WHERE agent_id = %s 
              AND created_at >= NOW() - INTERVAL '%s days'
            GROUP BY agent_id
        """
        return self.execute_query(query, (agent_id, days))


def print_usage():
    """顯示使用幫助"""
    print("""
OpenClaw PostgreSQL 連接腳本

使用方法：
    python3 pg_connector.py [command] [options]

命令：
    test                     測試數據庫連接
    agents                   列出所有 Agents
    active-agents           列出活躍的 Agents
    kb                       列出知識庫條目
    kb-search <query>      搜索知識庫
    kb-add <category> <title> <content>  添加到知識庫
    memory                  列出記憶
    logs                    列出日誌
    session <id>           獲取對話狀態

選項：
    --limit <n>              限制結果數量（默認 100）
    --category <category>    按類別篩選

示例：
    python3 pg_connector.py test
    python3 pg_connector.py kb-search "Python"
    python3 pg_connector.py kb-add "code" "Python 優化" "如何優化 Python 腳本"
    python3 pg_connector.py agents --limit 5
    """)


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    db = OpenClawDatabase()
    
    if command == "test":
        print("🧪 測試數據庫連接...")
        if db.connect():
            print("\n📊 數據庫狀態：")
            agents = db.get_agents()
            print(f"  Agents: {len(agents)}")
            print(f"  活躍: {len([a for a in agents if a['is_active']])}")
            
            db.disconnect()
        else:
            print("❌ 連接失敗，請檢查 Docker 容器是否運行")
    
    elif command == "agents":
        print("🤖 列出所有 Agents")
        if db.connect():
            agents = db.get_active_agents()
            
            print("\n" + "="*50)
            print(f"{'Agent ID':<15} {'Name':<20} {'Model':<20} {'Provider':<10}")
            print("="*50)
            
            for agent in agents:
                print(f"{agent['agent_id']:<15} {agent['name']:<20} {agent['model']:<20} {agent['provider']:<10}")
            
            print("="*50)
            print(f"總計: {len(agents)} 個活躍 Agents")
            
            db.disconnect()
    
    elif command == "kb":
        print("📚 列出知識庫")
        limit = 50
        category = None
        
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit") + 1
            try:
                limit = int(sys.argv[idx])
            except:
                pass
        
        if "--category" in sys.argv:
            idx = sys.argv.index("--category") + 1
            category = sys.argv[idx]
        
        if db.connect():
            entries = db.get_knowledge_base(category=category, limit=limit)
            
            print(f"\n知識庫條目 (limit={limit}, category={category or '全部'}):")
            print("\n" + "="*70)
            
            for i, entry in enumerate(entries, 1):
                print(f"{i}. [{entry['category'].upper()}] {entry['title']}")
                print(f"   摘要: {entry['summary'][:80]}...")
                print(f"   標籤: {', '.join(entry.get('tags', []))}")
                print(f"   創建時間: {entry['created_at']}")
                print()
            
            print("="*70)
            print(f"總計: {len(entries)} 條目")
            
            db.disconnect()
    
    elif command == "kb-search":
        print("🔍 搜索知識庫")
        if len(sys.argv) < 3:
            print("❌ 請提供搜索查詢")
            print_usage()
            return
        
        query = sys.argv[2]
        limit = 5
        
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit") + 1
            try:
                limit = int(sys.argv[idx])
            except:
                pass
        
        if db.connect():
            results = db.search_knowledge_base(query, limit)
            
            print(f"\n搜索: '{query}' (top {limit})")
            print("\n" + "="*70)
            
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['category'].upper()}] {result['title']}")
                print(f"   匹配: {result['summary'][:100]}...")
                print(f"   標籤: {', '.join(result.get('tags', []))}")
                print()
            
            print("="*70)
            print(f"找到: {len(results)} 個結果")
            
            db.disconnect()
    
    elif command == "memory":
        print("🧠 列出記憶")
        limit = 100
        category = None
        
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit") + 1
            try:
                limit = int(sys.argv[idx])
            except:
                pass
        
        if "--category" in sys.argv:
            idx = sys.argv.index("--category") + 1
            category = sys.argv[idx]
        
        if db.connect():
            memories = db.get_memory(limit=limit, category=category)
            
            print(f"\n記憶 (limit={limit}, category={category or '全部'}):")
            print("\n" + "="*70)
            
            for i, memory in enumerate(memories, 1):
                print(f"{i}. [{memory['category'].upper()}] {memory['title']}")
                print(f"   重要度: {memory['importance']}/5")
                print(f"   次數: {memory['access_count']}")
                print(f"   最後訪問: {memory['last_accessed_at']}")
                print()
            
            print("="*70)
            print(f"總計: {len(memories)} 條記憶")
            
            db.disconnect()
    
    elif command == "logs":
        print("📋 列出日誌")
        limit = 50
        
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit") + 1
            try:
                limit = int(sys.argv[idx])
            except:
                pass
        
        if db.connect():
            logs = db.execute_query("SELECT * FROM logs ORDER BY created_at DESC LIMIT %s", (limit,))
            
            print(f"\n系統日誌 (最近 {limit} 條):")
            print("\n" + "="*70)
            
            for i, log in enumerate(logs, 1):
                print(f"{i}. [{log['level'].upper()}] {log['category']}")
                print(f"   消息: {log['message'][:80]}...")
                print(f"   Agent: {log['agent_id'] or 'N/A'}")
                print(f"   時間: {log['created_at']}")
                print()
            
            print("="*70)
            print(f"總計: {len(logs)} 條日誌")
            
            db.disconnect()
    
    elif command == "session":
        print("💬 對話狀態")
        if len(sys.argv) < 3:
            print("❌ 請提供 session ID")
            print_usage()
            return
        
        session_id = sys.argv[2]
        
        if db.connect():
            state = db.get_session_state(session_id)
            
            if state:
                print(f"\nSession: {session_id}")
                print("\n" + "="*70)
                print(f"當前 Agent: {state['current_agent_id']}")
                print(f"對話 ID: {state['conversation_id']}")
                print(f"狀態: {state['state']}")
                print(f"上下文窗口: {state['context_window']}")
                print(f"最後活動: {state['last_message_at']}")
                print("="*70)
            else:
                print(f"❌ 未找到 session: {session_id}")
            
            db.disconnect()
    
    else:
        print(f"❌ 未知命令: {command}")
        print_usage()


if __name__ == "__main__":
    main()
