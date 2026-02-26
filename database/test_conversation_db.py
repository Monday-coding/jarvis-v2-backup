#!/usr/bin/env python3
"""
測試對話數據庫的基本操作
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import PostgreSQLConnector
from datetime import datetime, timezone, timedelta
import uuid

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def test_database_operations():
    """測試數據庫基本操作"""
    print("=" * 60)
    print("對話數據庫基本操作測試")
    print("=" * 60)
    print()
    
    # 創建數據庫連接
    db = PostgreSQLConnector()
    
    try:
        # 連接數據庫
        print("[1/8] 連接數據庫...")
        if not db.connect():
            print("  連接失敗")
            return False
        print("  連接成功")
        print()
        
        # 1. 測試 conversations 表
        print("[2/8] 測試 conversations 表...")
        
        # 創建表
        db.execute_update("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                conversation_id VARCHAR(100) UNIQUE NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                channel VARCHAR(50) DEFAULT 'telegram',
                start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'active',
                message_count INT DEFAULT 0,
                agent_id VARCHAR(50) DEFAULT 'main',
                context_summary TEXT,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """, ())
        print("  conversations 表創建成功")
        print()
        
        # 創建索引
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status, start_time DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_id)", ())
        print("  conversations 索引創建成功")
        print()
        
        # 插入測試數據
        conversation_id = f"conv_{int(datetime.now(HK_TZ).timestamp())}"
        db.execute_update("""
            INSERT INTO conversations (conversation_id, user_id, channel, context_summary, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb)
        """, (conversation_id, "test_user_001", "telegram", "測試對話會話", '{"test': True}))
        print("  插入測試數據成功")
        print()
        
        # 查詢數據
        conversations = db.execute_query("""
            SELECT * FROM conversations WHERE conversation_id = %s
        """, (conversation_id,))
        print(f"  查詢到 {len(conversations)} 條記錄")
        print()
        
        # 2. 測試 messages 表
        print("[3/8] 測試 messages 表...")
        
        # 創建表
        db.execute_update("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                message_id VARCHAR(100) UNIQUE NOT NULL,
                conversation_id VARCHAR(100) NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
                user_message TEXT NOT NULL,
                agent_message TEXT,
                topic_type VARCHAR(50),
                topic_confidence FLOAT,
                topic_keywords JSONB DEFAULT '[]'::jsonb,
                session_id VARCHAR(100),
                message_order INT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                processing_time FLOAT,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """, ())
        print("  messages 表創建成功")
        print()
        
        # 創建索引
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, message_order)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_topic ON messages(topic_type, timestamp DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, message_order)", ())
        print("  messages 索引創建成功")
        print()
        
        # 插入測試數據
        message_id = f"msg_{int(datetime.now(HK_TZ).timestamp())}"
        db.execute_update("""
            INSERT INTO messages (message_id, conversation_id, user_message, topic_type, topic_confidence, session_id, message_order, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """, (message_id, conversation_id, "測試消息", "test", 0.95, "session_001", 1, '{"test': True}))
        print("  插入測試消息成功")
        print()
        
        # 查詢數據
        messages = db.execute_query("""
            SELECT * FROM messages WHERE message_id = %s
        """, (message_id,))
        print(f"  查詢到 {len(messages)} 條消息記錄")
        print()
        
        # 3. 測試 sessions 表
        print("[4/8] 測試 sessions 表...")
        
        # 創建表
        db.execute_update("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                conversation_id VARCHAR(100) NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
                topic_type VARCHAR(50) NOT NULL,
                topic_embedding VECTOR(1536),
                topic_similarity FLOAT DEFAULT 0.0,
                topic_keywords JSONB DEFAULT '[]'::jsonb,
                message_count INT DEFAULT 0,
                start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP WITH TIME ZONE,
                status VARCHAR(20) DEFAULT 'active',
                short_memory JSONB DEFAULT '{}'::jsonb,
                context_summary TEXT,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """, ())
        print("  sessions 表創建成功")
        print()
        
        # 創建索引
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_conversation ON sessions(conversation_id, start_time DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status, start_time DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_similarity ON sessions(topic_similarity DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(topic_type)", ())
        print("  sessions 索引創建成功")
        print()
        
        # 插入測試數據
        session_id = f"session_{int(datetime.now(HK_TZ).timestamp())}"
        db.execute_update("""
            INSERT INTO sessions (session_id, conversation_id, topic_type, topic_similarity, short_memory, context_summary, metadata)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)
        """, (session_id, conversation_id, "test", 0.98, '{"test': 'short'}', "測試 Session", '{"test': True}))
        print("  插入測試 Session 成功")
        print()
        
        # 查詢數據
        sessions = db.execute_query("""
            SELECT * FROM sessions WHERE session_id = %s
        """, (session_id,))
        print(f"  查詢到 {len(sessions)} 條 Session 記錄")
        print()
        
        # 4. 測試 conversation_optimizations 表
        print("[5/8] 測試 conversation_optimizations 表...")
        
        # 創建表
        db.execute_update("""
            CREATE TABLE IF NOT EXISTS conversation_optimizations (
                id SERIAL PRIMARY KEY,
                optimization_id VARCHAR(100) UNIQUE NOT NULL,
                conversation_id VARCHAR(100) NOT NULL,
                optimization_type VARCHAR(50) NOT NULL,
                optimization_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                before_metrics JSONB NOT NULL,
                after_metrics JSONB NOT NULL,
                improvement_percentage JSONB DEFAULT '{}'::jsonb,
                parameters JSONB DEFAULT '{}'::jsonb,
                is_applied BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """, ())
        print("  conversation_optimizations 表創建成功")
        print()
        
        # 創建索引
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversation_optimizations_type ON conversation_optimizations(optimization_type, optimization_date DESC)", ())
        db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversation_optimizations_active ON conversation_optimizations(is_active, is_applied)", ())
        print("  conversation_optimizations 索引創建成功")
        print()
        
        # 插入測試數據
        optimization_id = f"opt_{int(datetime.now(HK_TZ).timestamp())}"
        db.execute_update("""
            INSERT INTO conversation_optimizations (optimization_id, conversation_id, optimization_type, before_metrics, after_metrics, improvement_percentage, parameters)
            VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb)
        """, (
            optimization_id,
            conversation_id,
            "test_optimization",
            json.dumps({'accuracy': 0.80, 'token_usage': 1000}),
            json.dumps({'accuracy': 0.90, 'token_usage': 850}),
            json.dumps({'accuracy_improvement': 0.10, 'token_reduction': 0.15}),
            json.dumps({'threshold': 0.65})
        ))
        print("  插入測試優化記錄成功")
        print()
        
        # 查詢數據
        optimizations = db.execute_query("""
            SELECT * FROM conversation_optimizations WHERE optimization_id = %s
        """, (optimization_id,))
        print(f"  查詢到 {len(optimizations)} 條優化記錄")
        print()
        
        # 5. 測試關聯查詢
        print("[6/8] 測試關聯查詢...")
        
        # 查詢會話的所有消息
        messages = db.execute_query("""
            SELECT * FROM messages WHERE conversation_id = %s ORDER BY message_order ASC
        """, (conversation_id,))
        print(f"  查詢到會話的 {len(messages)} 條消息")
        for i, msg in enumerate(messages[:3]):
            print(f"    {i+1}. {msg['user_message'][:50]}")
        print()
        
        # 查詢會話的所有 Sessions
        sessions = db.execute_query("""
            SELECT * FROM sessions WHERE conversation_id = %s ORDER BY start_time DESC
        """, (conversation_id,))
        print(f"  查詢到會話的 {len(sessions)} 條 Sessions")
        for i, sess in enumerate(sessions[:3]):
            print(f"    {i+1}. {sess['topic_type']} (相似度: {sess['topic_similarity']})")
        print()
        
        # 6. 測試更新操作
        print("[7/8] 測試更新操作...")
        
        # 更新會話狀態
        db.execute_update("""
            UPDATE conversations SET message_count = message_count + 1 WHERE conversation_id = %s
        """, (conversation_id,))
        print("  更新消息數量成功")
        print()
        
        # 更新 Session 消息數
        db.execute_update("""
            UPDATE sessions SET message_count = message_count + 1 WHERE session_id = %s
        """, (session_id,))
        print("  更新 Session 消息數成功")
        print()
        
        # 7. 測試統計查詢
        print("[8/8] 測試統計查詢...")
        
        # 統計會話數量
        conversation_count = db.execute_query("SELECT COUNT(*) as count FROM conversations")[0]['count']
        print(f"  總會話數量：{conversation_count}")
        
        # 統計消息數量
        message_count = db.execute_query("SELECT COUNT(*) as count FROM messages")[0]['count']
        print(f"  總消息數量：{message_count}")
        
        # 統計 Session 數量
        session_count = db.execute_query("SELECT COUNT(*) as count FROM sessions")[0]['count']
        print(f"  總 Session 數量：{session_count}")
        
        # 統計優化記錄數量
        optimization_count = db.execute_query("SELECT COUNT(*) as count FROM conversation_optimizations")[0]['count']
        print(f"  總優化記錄數量：{optimization_count}")
        print()
        
        # 8. 斷開連接
        print("[9/9] 斷開數據庫連接...")
        db.disconnect()
        print("  連接已斷開")
        print()
        
        print("=" * 60)
        print("所有測試完成！")
        print("=" * 60)
        print()
        print("創建的表：")
        print("  1. conversations - 對話會話")
        print("  2. messages - 對話消息")
        print("  3. sessions - 話題 Sessions")
        print("  4. conversation_optimizations - 對話優化")
        print()
        print("測試的操作：")
        print("  ✅ 創建表")
        print("  ✅ 創建索引")
        print("  ✅ 插入測試數據")
        print("  ✅ 查詢數據")
        print("  ✅ 更新數據")
        print("  ✅ 統計查詢")
        print()
        print("對話數據庫已準備就緒，可以開始存儲和優化對話！")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    print("對話數據庫測試")
    print("=" * 60)
    print()
    print("這個腳本會測試對話數據庫的基本 CRUD 操作")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    success = test_database_operations()
    
    if success:
        print()
        print("✅ 對話數據庫測試完成！")
        print()
        print("下一步：")
        print("  1. 實現話題識別系統")
        print("  2. 實現相似度計算")
        print("  3. 實現 Session 管理系統")
        print("  4. 實現每日優化系統")
    else:
        print()
        print("❌ 對話數據庫測試失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
