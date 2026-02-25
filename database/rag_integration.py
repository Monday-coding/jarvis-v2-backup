#!/usr/bin/env python3
"""
OpenClaw RAG 集成腳本
將數據庫查詢集成到 Agents 中
"""

import os
import sys
import psycopg2
from pathlib import Path


class RAGIntegration:
    """RAG 集成類"""
    
    def __init__(self, db_host="localhost", db_port=5432, 
                 db_name="openclaw", db_user="openclaw", 
                 db_password="openclaw_password_2024"):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None
    
    def connect(self):
        """連接到數據庫"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            return True
        except psycopg2.Error as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """斷開連接"""
        if self.connection:
            self.connection.close()
    
    def search_knowledge_base(self, query: str, top_k: int = 5, 
                             category: str = None) -> list:
        """從知識庫搜索相關信息"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                if category:
                    search_query = """
                        SELECT * FROM knowledge_base 
                        WHERE category = %s 
                        AND (title ILIKE %s OR content ILIKE %s OR array_to_string(tags, ',') ILIKE %s)
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    cursor.execute(search_query, (category, f"%{query}%", f"%{query}%", f"%{query}%", top_k))
                else:
                    search_query = """
                        SELECT * FROM knowledge_base 
                        WHERE title ILIKE %s OR content ILIKE %s OR array_to_string(tags, ',') ILIKE %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    cursor.execute(search_query, (f"%{query}%", f"%{query}%", f"%{query}%", top_k))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor:
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            print(f"❌ 搜索失敗: {e}")
            return []
    
    def get_relevant_memory(self, query: str, top_k: int = 3, 
                            category: str = None) -> list:
        """從記憶中獲取相關信息"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                if category:
                    search_query = """
                        SELECT * FROM memory 
                        WHERE category = %s 
                        AND is_active = TRUE
                        AND (title ILIKE %s OR content ILIKE %s)
                        ORDER BY importance DESC, created_at DESC
                        LIMIT %s
                    """
                    cursor.execute(search_query, (category, f"%{query}%", f"%{query}%", top_k))
                else:
                    search_query = """
                        SELECT * FROM memory 
                        WHERE is_active = TRUE
                        AND (title ILIKE %s OR content ILIKE %s)
                        ORDER BY importance DESC, created_at DESC
                        LIMIT %s
                    """
                    cursor.execute(search_query, (f"%{query}%", f"%{query}%", top_k))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor:
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            print(f"❌ 獲取記憶失敗: {e}")
            return []
    
    def add_to_knowledge_base(self, category: str, title: str, 
                            content: str, summary: str = "", 
                            tags: list = []) -> bool:
        """添加到知識庫"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 檢查是否已存在
                cursor.execute(
                    "SELECT id FROM knowledge_base WHERE title = %s AND entry_id = %s",
                    (title, f"kb_{category}_{title}")
                )
                
                if cursor.fetchone():
                    # 更新現有記錄
                    update_query = """
                        UPDATE knowledge_base 
                        SET content = %s, summary = %s, updated_at = NOW()
                        WHERE entry_id = %s
                    """
                    cursor.execute(update_query, (content, summary, f"kb_{category}_{title}"))
                    print(f"✓ 已更新知識庫: {title}")
                else:
                    # 插入新記錄
                    insert_query = """
                        INSERT INTO knowledge_base (entry_id, category, title, content, summary, tags, 
                                               source, created_at)
                        VALUES (%s, %s, %s, %s, %s, ARRAY[%s]::text[], 'neur-opt', NOW())
                    """
                    cursor.execute(insert_query, (f"kb_{category}_{title}", category, title, 
                                                       content, summary, ', '.join(tags)))
                    print(f"✓ 已添加到知識庫: {title}")
                
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"❌ 添加到知識庫失敗: {e}")
            self.connection.rollback()
            return False
    
    def add_memory(self, title: str, content: str, 
                  category: str = "general", importance: int = 3) -> bool:
        """添加到長期記憶"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO memory (memory_id, title, content, category, importance, 
                                       is_active, created_at)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, TRUE, NOW())
                """
                cursor.execute(insert_query, (f"mem_{category}_{title[:20]}", 
                                                      title, content, category, importance))
                print(f"✓ 已添加到記憶: {title}")
                
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"❌ 添加到記憶失敗: {e}")
            self.connection.rollback()
            return False
    
    def add_log(self, level: str, category: str, message: str, 
                agent_id: str = None, metadata: dict = None) -> bool:
        """添加日誌"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                import json as json_module
                
                insert_query = """
                    INSERT INTO logs (log_id, level, category, message, agent_id, context, created_at, metadata)
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s::jsonb, NOW(), %s::jsonb)
                """
                
                context_json = json_module.dumps({"timestamp": str(datetime.now())})
                metadata_json = json_module.dumps(metadata or {})
                
                cursor.execute(insert_query, (level, category, message, agent_id, 
                                                      context_json, metadata_json))
                print(f"✓ 已添加日誌: [{level}] {message[:50]}")
                
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"❌ 添加日誌失敗: {e}")
            self.connection.rollback()
            return False


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("""
OpenClaw RAG 集成腳本

使用方法：
    python3 rag_integration.py [command] [options]

命令：
    search <query>           搜索知識庫
    memory <query>          搜索記憶
    kb-add <cat> <title>    添加到知識庫
    memory-add <title>    添加到記憶
    logs                    查看日誌

選項：
    --limit <n>            限制結果數量（默認 5）
    --category <cat>        指定類別（code, task, data, research 等）

示例：
    python3 rag_integration.py search "Python 腳本"
    python3 rag_integration.py memory "配置 Ollama"
    python3 rag_integration.py kb-add "code" "Python 優化" "如何使用 ollama"
    python3 rag_integration.py memory-add "系統設置" "完成 Ollama 配置， Classifier 使用 qwen2.5:1.5b"
        """)
        return
    
    command = sys.argv[1].lower()
    rag = RAGIntegration()
    
    # 解析選項
    limit = 5
    category = None
    idx = 2
    while idx < len(sys.argv):
        if sys.argv[idx] == "--limit":
            try:
                limit = int(sys.argv[idx+1])
                idx += 2
            except:
                pass
        elif sys.argv[idx] == "--category":
            category = sys.argv[idx+1]
            idx += 2
        else:
            idx += 1
    
    if command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        print(f"\n🔍 搜索知識庫: {query}")
        results = rag.search_knowledge_base(query, top_k=limit, category=category)
        
        if results:
            print(f"\n找到 {len(results)} 個結果:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. [{result['category'].upper()}] {result['title']}")
                print(f"   摘要: {result['summary'][:80]}")
                print(f"   標籤: {', '.join(result.get('tags', []))}")
        else:
            print("未找到相關結果")
    
    elif command == "memory":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        print(f"\n🧠 搜索記憶: {query}")
        results = rag.get_relevant_memory(query, top_k=limit, category=category)
        
        if results:
            print(f"\n找到 {len(results)} 條記憶:\n")
            for i, memory in enumerate(results, 1):
                print(f"{i}. [{memory['category'].upper()}] {memory['title']}")
                print(f"   內容: {memory['content'][:100]}")
                print(f"   重要度: {memory['importance']}/5")
        else:
            print("未找到相關記憶")
    
    elif command == "kb-add":
        if len(sys.argv) < 4:
            print("❌ kb-add 需要: <category> <title> <content>")
            return
        
        category = sys.argv[2]
        title = sys.argv[3]
        content = ' '.join(sys.argv[4:])
        
        print(f"\n📚 添加到知識庫")
        print(f"類別: {category}")
        print(f"標題: {title}")
        print(f"內容: {content}")
        
        if rag.add_to_knowledge_base(category, title, content):
            print("✅ 添加成功")
        else:
            print("❌ 添加失敗")
    
    elif command == "memory-add":
        if len(sys.argv) < 3:
            print("❌ memory-add 需要: <title> <content>")
            return
        
        title = sys.argv[2]
        content = ' '.join(sys.argv[3:])
        
        print(f"\n🧠 添加到記憶")
        print(f"標題: {title}")
        print(f"內容: {content}")
        
        if rag.add_memory(title, content):
            print("✅ 添加成功")
        else:
            print("❌ 添加失敗")
    
    elif command == "logs":
        print("\n📋 最近日誌")
        
        if not rag.connection:
            rag.connect()
        
        try:
            with rag.connection.cursor() as cursor:
                query = """
                    SELECT * FROM logs 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """
                cursor.execute(query, (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                logs = []
                for row in cursor:
                    logs.append(dict(zip(columns, row)))
                
                print("\n" + "="*70)
                for i, log in enumerate(logs, 1):
                    print(f"{i}. [{log['level'].upper()}] {log['category']}")
                    print(f"   消息: {log['message'][:100]}")
                    print(f"   Agent: {log['agent_id'] or 'N/A'}")
                    print(f"   時間: {log['created_at']}")
                
                print("="*70)
                print(f"總計: {len(logs)} 條日誌")
                
        except Exception as e:
            print(f"❌ 獲取日誌失敗: {e}")
        finally:
            rag.disconnect()
    
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
