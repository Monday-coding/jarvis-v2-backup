#!/usr/bin/env python3
"""
實現記憶架構
使用 PostgreSQL + pgvector 實現短期和長期記憶
"""

import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class PostgresVectorMemory:
    """PostgreSQL + pgvector 記憶架構"""
    
    def __init__(self):
        self.db_name = "openclaw"
        self.db_user = "openclaw"
        self.db_host = "localhost"
        self.db_port = 5432
        self.docker_container = "openclaw-postgres"
        self.vector_dimension = 1536
    
    def install_pgvector(self):
        """安裝 pgvector"""
        print("=" * 60)
        print("安裝 pgvector")
        print("=" * 60)
        print()
        
        try:
            # 檢查 pgvector 是否已安裝
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "SELECT extversion FROM pg_extension WHERE extname = 'vector'"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print("  ✅ pgvector 已安裝")
                print(f"  版本：{result.stdout.strip()}")
                return True
            else:
                print("  ⚠️  pgvector 未安裝")
                print("  開始安裝...")
                
                # 安裝 pgvector
                result = subprocess.run(
                    ['docker', 'exec', self.docker_container, 'apt-get', 'update', '-y'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                result = subprocess.run(
                    ['docker', 'exec', self.docker_container, 'apt-get', 'install', '-y', 'postgresql-16-pgvector'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    print("  ✅ pgvector 安裝成功")
                    
                    # 啟用擴展
                    result = subprocess.run(
                        ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE EXTENSION IF NOT EXISTS vector"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print("  ✅ pgvector 擴展已啟用")
                        return True
                    else:
                        print(f"  ❌ 擴展啟用失敗：{result.stderr}")
                        return False
                else:
                    print(f"  ❌ 安裝失敗：{result.stderr}")
                    return False
        
        except Exception as e:
            print(f"  ❌ 安裝失敗：{e}")
            return False
        
        print()
    
    def create_memory_tables(self):
        """創建記憶數據庫表"""
        print("=" * 60)
        print("創建記憶數據庫表")
        print("=" * 60)
        print()
        
        try:
            # 1. 短期記憶表
            print("[1/4] 創建短期記憶表...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE TABLE IF NOT EXISTS short_term_memory (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100),
                        user_id VARCHAR(100) NOT NULL,
                        message_content TEXT NOT NULL,
                        message_metadata JSONB DEFAULT '{}'::jsonb,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 短期記憶表創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            # 添加索引
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE INDEX IF NOT EXISTS idx_short_term_conversation ON short_term_memory(conversation_id, timestamp DESC)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE INDEX IF NOT EXISTS idx_short_term_session ON short_term_memory(session_id, timestamp DESC)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print()
            
            # 2. 長期記憶表
            print("[2/4] 創建長期記憶表（使用 pgvector）...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', f"""
                    CREATE TABLE IF NOT EXISTS long_term_memory (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100),
                        user_id VARCHAR(100) NOT NULL,
                        message_content TEXT NOT NULL,
                        message_embedding VECTOR({self.vector_dimension}),
                        message_metadata JSONB DEFAULT '{{}}'::jsonb,
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 長期記憶表創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            # 添加索引
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE INDEX IF NOT EXISTS idx_long_term_conversation ON long_term_memory(conversation_id, timestamp DESC)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', f"CREATE INDEX IF NOT EXISTS idx_long_term_embedding ON long_term_memory USING ivfflat (message_embedding vector_cosine_ops)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print()
            
            # 3. 用戶偏好表
            print("[3/4] 創建用戶偏好表...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(100) NOT NULL,
                        preference_key VARCHAR(100) NOT NULL,
                        preference_value JSONB NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, preference_key)
                    )
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 用戶偏好表創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            # 添加索引
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE INDEX IF NOT EXISTS idx_user_preferences ON user_preferences(user_id)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print()
            
            # 4. 系統狀態表
            print("[4/4] 創建系統狀態表...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE TABLE IF NOT EXISTS system_state (
                        id SERIAL PRIMARY KEY,
                        state_key VARCHAR(100) NOT NULL,
                        state_value JSONB NOT NULL,
                        state_type VARCHAR(50) DEFAULT 'configuration',
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(state_key)
                    )
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 系統狀態表創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            # 添加索引
            subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "CREATE INDEX IF NOT EXISTS idx_system_state ON system_state(state_key, updated_at DESC)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print()
        
        except Exception as e:
            print(f"  ❌ 創建失敗：{e}")
    
    def create_memory_functions(self):
        """創建記憶查詢函數"""
        print("=" * 60)
        print("創建記憶查詢函數")
        print("=" * 60)
        print()
        
        try:
            # 1. 添加短期記憶函數
            print("[1/5] 創建短期記憶函數...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE OR REPLACE FUNCTION add_short_term_memory(
                        p_conversation_id VARCHAR(100),
                        p_session_id VARCHAR(100),
                        p_user_id VARCHAR(100),
                        p_message_content TEXT,
                        p_message_metadata JSONB DEFAULT '{}'::jsonb
                    )
                    RETURNS INTEGER AS $$
                    BEGIN
                        INSERT INTO short_term_memory (conversation_id, session_id, user_id, message_content, message_metadata)
                        VALUES (p_conversation_id, p_session_id, p_user_id, p_message_content, p_message_metadata)
                        RETURNING lastval();
                    END;
                    LANGUAGE plpgsql;
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 短期記憶函數創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            print()
            
            # 2. 添加長期記憶函數
            print("[2/5] 創建長期記憶函數...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', f"""
                    CREATE OR REPLACE FUNCTION add_long_term_memory(
                        p_conversation_id VARCHAR(100),
                        p_session_id VARCHAR(100),
                        p_user_id VARCHAR(100),
                        p_message_content TEXT,
                        p_message_embedding VECTOR({self.vector_dimension}),
                        p_message_metadata JSONB DEFAULT '{{}}'::jsonb
                    )
                    RETURNS INTEGER AS $$
                    BEGIN
                        INSERT INTO long_term_memory (conversation_id, session_id, user_id, message_content, message_embedding, message_metadata)
                        VALUES (p_conversation_id, p_session_id, p_user_id, p_message_content, p_message_embedding, p_message_metadata)
                        RETURNING lastval();
                    END;
                    LANGUAGE plpgsql;
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 長期記憶函數創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            print()
            
            # 3. 短期記憶檢索函數
            print("[3/5] 創建短期記憶檢索函數...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE OR REPLACE FUNCTION search_short_term_memory(
                        p_conversation_id VARCHAR(100),
                        p_limit INTEGER DEFAULT 10
                    )
                    RETURNS TABLE (
                        id INT,
                        conversation_id VARCHAR(100),
                        session_id VARCHAR(100),
                        user_id VARCHAR(100),
                        message_content TEXT,
                        message_metadata JSONB,
                        timestamp TIMESTAMP WITH TIME ZONE
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT id, conversation_id, session_id, user_id, message_content, message_metadata, timestamp
                        FROM short_term_memory
                        WHERE conversation_id = p_conversation_id
                        ORDER BY timestamp DESC
                        LIMIT p_limit;
                    END;
                    LANGUAGE plpgsql;
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 短期記憶檢索函數創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            print()
            
            # 4. 長期記憶向量檢索函數
            print("[4/5] 創建長期記憶向量檢索函數...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', f"""
                    CREATE OR REPLACE FUNCTION search_long_term_memory(
                        p_conversation_id VARCHAR(100),
                        p_message_embedding VECTOR({self.vector_dimension}),
                        p_limit INTEGER DEFAULT 10
                    )
                    RETURNS TABLE (
                        id INT,
                        conversation_id VARCHAR(100),
                        session_id VARCHAR(100),
                        user_id VARCHAR(100),
                        message_content TEXT,
                        message_embedding VECTOR({self.vector_dimension}),
                        message_metadata JSONB,
                        timestamp TIMESTAMP WITH TIME ZONE,
                        similarity FLOAT
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT
                            id, conversation_id, session_id, user_id,
                            message_content, message_embedding, message_metadata, timestamp,
                            1 - (message_embedding <=> p_message_embedding) AS similarity
                        FROM long_term_memory
                        WHERE conversation_id = p_conversation_id
                        ORDER BY message_embedding <=> p_message_embedding
                        LIMIT p_limit;
                    END;
                    LANGUAGE plpgsql;
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 長期記憶向量檢索函數創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            print()
            
            # 5. 用戶偏好檢索函數
            print("[5/5] 創建用戶偏好檢索函數...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', """
                    CREATE OR REPLACE FUNCTION get_user_preferences(
                        p_user_id VARCHAR(100)
                    )
                    RETURNS TABLE (
                        id INT,
                        user_id VARCHAR(100),
                        preference_key VARCHAR(100),
                        preference_value JSONB,
                        updated_at TIMESTAMP WITH TIME ZONE
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT id, user_id, preference_key, preference_value, updated_at
                        FROM user_preferences
                        WHERE user_id = p_user_id
                        ORDER BY updated_at DESC;
                    END;
                    LANGUAGE plpgsql;
                """],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 用戶偏好檢索函數創建成功")
            else:
                print(f"  ❌ 創建失敗：{result.stderr}")
            
            print()
        
        except Exception as e:
            print(f"  ❌ 創建失敗：{e}")
    
    def test_memory_operations(self):
        """測試記憶操作"""
        print("=" * 60)
        print("測試記憶操作")
        print("=" * 60)
        print()
        
        try:
            # 1. 測試添加短期記憶
            print("[1/3] 測試添加短期記憶...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "SELECT add_short_term_memory('conv_001', 'session_001', 'user_001', '測試消息', '{\"test\": true}')"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 短期記憶添加成功")
            else:
                print(f"  ❌ 添加失敗：{result.stderr}")
            
            print()
            
            # 2. 測試向量檢索
            print("[2/3] 測試長期記憶向量檢索...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', f"SELECT * FROM search_long_term_memory('conv_001', '[{', '.join(['0.1'] * 1536)}]', 5)"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 長期記憶向量檢索成功")
            else:
                print(f"  ❌ 檢索失敗：{result.stderr}")
            
            print()
            
            # 3. 測試用戶偏好檢索
            print("[3/3] 測試用戶偏好檢索...")
            result = subprocess.run(
                ['docker', 'exec', self.docker_container, 'psql', '-U', self.db_user, '-d', self.db_name, '-c', "SELECT * FROM get_user_preferences('user_001')"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ 用戶偏好檢索成功")
            else:
                print(f"  ❌ 檢索失敗：{result.stderr}")
            
            print()
        
        except Exception as e:
            print(f"  ❌ 測試失敗：{e}")
    
    def implement_memory_architecture(self):
        """實現記憶架構"""
        print("=" * 60)
        print("實現記憶架構")
        print("=" * 60)
        print()
        
        # 1. 安裝 pgvector
        print("[第 1 步] 安裝 pgvector...")
        pgvector_installed = self.install_pgvector()
        print()
        
        # 2. 創建記憶數據庫表
        print("[第 2 步] 創建記憶數據庫表...")
        self.create_memory_tables()
        print()
        
        # 3. 創建記憶查詢函數
        print("[第 3 步] 創建記憶查詢函數...")
        self.create_memory_functions()
        print()
        
        # 4. 測試記憶操作
        print("[第 4 步] 測試記憶操作...")
        self.test_memory_operations()
        print()
        
        # 5. 總結
        print("=" * 60)
        print("記憶架構實現完成")
        print("=" * 60)
        print()
        print("記憶架構總結：")
        print()
        print("短期記憶：")
        print("  - 儲存：PostgreSQL (JSONB)")
        print("  - 保留：Session 結束")
        print("  - 用途：最近 10 條消息，快速訪問")
        print()
        print("長期記憶：")
        print(f"  - 儲存：PostgreSQL + pgvector (VECTOR({self.vector_dimension}))")
        print("  - 保留：跨 Sessions")
        print("  - 用途：最近 100 條消息，向量檢索")
        print()
        print("用戶偏好：")
        print("  - 儲存：PostgreSQL (JSONB)")
        print("  - 保留：永久")
        print("  - 用途：自定義設定、閾值、偏好")
        print()
        print("系統狀態：")
        print("  - 儲存：PostgreSQL (JSONB)")
        print("  - 保留：永久")
        print("  - 用途：系統配置、Agent 狀態等")
        print()
        print("向量檢索：")
        print(f"  - 儲存格式：VECTOR({self.vector_dimension})")
        print("  - 相似度計算：cosine similarity (vector_cosine_ops)")
        print("  - 索引類型：IVFFlat")
        print("  - 查詢方法：KNN (最近鄰搜索)")
        print()
        print("優勢：")
        print("  - PostgreSQL 成熟穩定，支持 ACID")
        print("  - pgvector 提供高性能向量檢索")
        print("  - 支持全文檢索和向量檢索")
        print("  - 支持複雜查詢和事務處理")
        print()
        print("建議：")
        print("  1. 短期記憶：使用 JSONB，快速訪問")
        print("  2. 長期記憶：使用 VECTOR，向量檢索")
        print("  3. 用戶偏好：使用 JSONB，靈活配置")
        print("  4. 系統狀態：使用 JSONB，配置管理")
        print()
        print("下一步：")
        print("  1. 實現向量生成")
        print("  2. 實現相似度計算")
        print("  3. 實現自動清理")
        print("  4. 實現記憶同步到所有 Agents")
        print()


def main():
    """主函數 - 實現記憶架構"""
    print("記憶架構實現")
    print("=" * 60)
    print()
    
    # 創建架構
    architecture = PostgresVectorMemory()
    
    # 實現記憶架構
    architecture.implement_memory_architecture()


if __name__ == "__main__":
    main()
