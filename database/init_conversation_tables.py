#!/usr/bin/env python3
"""
對話數據庫初始化
創建 conversations, messages, sessions, conversation_optimizations 表
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import PostgreSQLConnector
from datetime import datetime, timezone, timedelta


def init_conversation_tables():
    """初始化對話數據庫表"""
    
    print("=" * 60)
    print("對話數據庫初始化")
    print("=" * 60)
    print()
    
    # 創建數據庫連接
    db = PostgreSQLConnector()
    
    try:
        # 連接數據庫
        if not db.connect():
            print("❌ 數據庫連接失敗")
            return False
        
        print("✅ 數據庫連接成功")
        print()
        
        with db:
            # 創建 conversations 表
            print("[1/4] 創建 conversations 表...")
            
            query = """
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
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ conversations 表創建成功")
            print()
            
            # 創建索引
            print("  創建索引...")
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status, start_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(agent_id)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversations_start ON conversations(start_time DESC)", ())
            print("  ✅ 索引創建成功")
            print()
            
            # 創建 messages 表
            print("[2/4] 創建 messages 表...")
            
            query = """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    message_id VARCHAR(100) UNIQUE NOT NULL,
                    conversation_id VARCHAR(100) NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
                    user_message TEXT NOT NULL,
                    agent_message TEXT,
                    topic_type VARCHAR(50),
                    topic_confidence FLOAT,
                    topic_embedding VECTOR(1536),
                    topic_keywords JSONB DEFAULT '[]'::jsonb,
                    session_id VARCHAR(100),
                    message_order INT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    processing_time FLOAT,
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ messages 表創建成功")
            print()
            
            # 創建索引
            print("  創建索引...")
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, message_order)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_topic ON messages(topic_type, timestamp DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, message_order)", ())
            print("  ✅ 索引創建成功")
            print()
            
            # 創建 sessions 表
            print("[3/4] 創建 sessions 表...")
            
            query = """
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
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ sessions 表創建成功")
            print()
            
            # 創建索引
            print("  創建索引...")
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_conversation ON sessions(conversation_id, start_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status, start_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_similarity ON sessions(topic_similarity DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(topic_type)", ())
            print("  ✅ 索引創建成功")
            print()
            
            # 創建 conversation_optimizations 表
            print("[4/4] 創建 conversation_optimizations 表...")
            
            query = """
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
                    metadata JSONB DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ conversation_optimizations 表創建成功")
            print()
            
            # 創建索引
            print("  創建索引...")
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversation_optimizations_type ON conversation_optimizations(optimization_type, optimization_date DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_conversation_optimizations_active ON conversation_optimizations(is_active, is_applied)", ())
            print("  ✅ 索引創建成功")
            print()
            
            print("=" * 60)
            print("所有對話數據庫表初始化完成！")
            print("=" * 60)
            print()
            print("創建的表：")
            print("  1. conversations - 對話會話")
            print("  2. messages - 對話消息")
            print("  3. sessions - 話題 Sessions")
            print("  4. conversation_optimizations - 優化記錄")
            print()
            print("準備就緒，可以開始存儲對話數據和優化分析！")
            
            return True
            
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return False
    
    finally:
        # 斷開連接
        db.disconnect()
        print()
        print("數據庫連接已斷開")


def main():
    """主函數"""
    print("對話數據庫初始化")
    print("=" * 60)
    print()
    print("這個腳本會創建以下表：")
    print("  1. conversations - 對話會話")
    print("  2. messages - 對話消息")
    print("  3. sessions - 話題 Sessions")
    print("  4. conversation_optimizations - 優化記錄")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    success = init_conversation_tables()
    
    if success:
        print()
        print("✅ 對話數據庫初始化完成！")
        print()
        print("下一步：")
        print("  1. 實現話題識別系統")
        print("  2. 實現相似度計算")
        print("  3. 實現 Session 管理")
        print("  4. 實現自動優化系統")
    else:
        print()
        print("❌ 對話數據庫初始化失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
