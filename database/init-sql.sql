-- OpenClaw PostgreSQL 數據庫初始化腳本
-- 創建所有必要的表和索引

-- ============================================
-- 1. AGENTS 表 - 存儲 Agent 相關信息
-- ============================================

CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    workspace VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE agents IS 'OpenClaw Agents 配置信息';

-- ============================================
-- 2. CONVERSATIONS 表 - 存儲對話會話
-- ============================================

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(100) UNIQUE NOT NULL,
    channel VARCHAR(50) NOT NULL,
    user_id VARCHAR(100),
    title TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE conversations IS 'OpenClaw 對話會話';

CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(channel);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- ============================================
-- 3. MESSAGES 表 - 存儲對話消息
-- ============================================

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100) UNIQUE NOT NULL,
    conversation_id VARCHAR(100) NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    token_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_agent_id ON messages(agent_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

COMMENT ON TABLE messages IS 'OpenClaw 對話消息';

-- ============================================
-- 4. KNOWLEDGE_BASE 表 - 存儲知識庫內容
-- ============================================

CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    entry_id VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    conversation_state VARCHAR(50) DEFAULT 'new_conversation',
    confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'neur-opt',
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_tags ON knowledge_base USING gin(tags);
CREATE INDEX idx_kb_conversation_state ON knowledge_base(conversation_state);
CREATE INDEX idx_kb_created_at ON knowledge_base(created_at DESC);

COMMENT ON TABLE knowledge_base IS 'OpenClaw 知識庫';

-- ============================================
-- 5. MEMORY 表 - 存儲長期記憶
-- ============================================

CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    memory_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    importance INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_memory_importance ON memory(importance DESC);
CREATE INDEX idx_memory_category ON memory(category);
CREATE INDEX idx_memory_created_at ON memory(created_at DESC);
CREATE INDEX idx_memory_is_active ON memory(is_active);

COMMENT ON TABLE memory IS 'OpenClaw 長期記憶';

-- ============================================
-- 6. LOGS 表 - 存儲系統日誌
-- ============================================

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(100) UNIQUE NOT NULL,
    level VARCHAR(20) NOT NULL,
    category VARCHAR(50),
    message TEXT NOT NULL,
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_category ON logs(category);
CREATE INDEX idx_logs_agent_id ON logs(agent_id);
CREATE INDEX idx_logs_created_at ON logs(created_at DESC);

COMMENT ON TABLE logs IS 'OpenClaw 系統日誌';

-- ============================================
-- 7. USER_ACTIONS 表 - 存儲用戶操作記錄
-- ============================================

CREATE TABLE IF NOT EXISTS user_actions (
    id SERIAL PRIMARY KEY,
    action_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_action_type ON user_actions(action_type);
CREATE INDEX idx_user_actions_target_id ON user_actions(target_id);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at DESC);

COMMENT ON TABLE user_actions IS 'OpenClaw 用戶操作記錄';

-- ============================================
-- 8. SESSION_STATE 表 - 存儲對話狀態
-- ============================================

CREATE TABLE IF NOT EXISTS session_state (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    conversation_id VARCHAR(100) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    current_agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    context_window INTEGER[],
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_state_session_id ON session_state(session_id);
CREATE INDEX idx_session_state_conversation_id ON session_state(conversation_id);
CREATE INDEX idx_session_state_current_agent ON session_state(current_agent_id);

COMMENT ON TABLE session_state IS 'OpenClaw 對話狀態';

-- ============================================
-- 9. TASKS 表 - 存儲任務隊列
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 3,
    assigned_agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    conversation_id VARCHAR(100) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC);
CREATE INDEX idx_tasks_assigned_agent ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_due_at ON tasks(due_at);

COMMENT ON TABLE tasks IS 'OpenClaw 任務列表';

-- ============================================
-- 10. SYSTEM_METRICS 表 - 存儲系統指標
-- ============================================

CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT,
    metric_type VARCHAR(50),
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

COMMENT ON TABLE system_metrics IS 'OpenClaw 系統指標';

-- ============================================
-- 初始化數據
-- ============================================

-- 創建默認的 Agents
INSERT INTO agents (agent_id, name, model, provider, workspace, metadata) VALUES
('main', 'Main Agent', 'zai/glm-4.7', 'zai', '~/.openclaw/workspace', '{"role": "orchestrator", "type": "main"}'),
('classifier', 'Classifier', 'ollama/qwen2.5:1.5b', 'ollama', '~/.openclaw/workspace-classifier', '{"role": "classifier", "type": "local"}'),
('chat', 'Chat Agent', 'zai/glm-4.7-flashx', 'zai', '~/.openclaw/workspace-chat', '{"role": "chat", "type": "cloud"}'),
('task', 'Task Agent', 'zai/glm-4.7-flash', 'zai', '~/.openclaw/workspace-task', '{"role": "task", "type": "cloud"}'),
('coding', 'Coding Agent', 'zai/glm-4.7', 'zai', '~/.openclaw/workspace-coding', '{"role": "coding", "type": "cloud"}'),
('data', 'Data Agent', 'zai/glm-4.7-flash', 'zai', '~/.openclaw/workspace-data', '{"role": "data", "type": "cloud"}'),
('qa', 'QA Agent', 'zai/glm-4.7-flash', 'zai', '~/.openclaw/workspace-qa', '{"role": "qa", "type": "cloud"}')
ON CONFLICT (agent_id) DO NOTHING;

-- ============================================
-- 顯示完成信息
-- ============================================

SELECT '✅ OpenClaw PostgreSQL 數據庫初始化完成！' AS status;

SELECT '📊 創建的表：' AS info;

SELECT 
    '  agents' AS table_name,
    (SELECT COUNT(*) FROM agents) AS row_count
UNION ALL
SELECT 
    '  conversations' AS table_name,
    (SELECT COUNT(*) FROM conversations) AS row_count
UNION ALL
SELECT 
    '  messages' AS table_name,
    (SELECT COUNT(*) FROM messages) AS row_count
UNION ALL
SELECT 
    '  knowledge_base' AS table_name,
    (SELECT COUNT(*) FROM knowledge_base) AS row_count
UNION ALL
SELECT 
    '  memory' AS table_name,
    (SELECT COUNT(*) FROM memory) AS row_count
UNION ALL
SELECT 
    '  logs' AS table_name,
    (SELECT COUNT(*) FROM logs) AS row_count
UNION ALL
SELECT 
    '  user_actions' AS table_name,
    (SELECT COUNT(*) FROM user_actions) AS row_count
UNION ALL
SELECT 
    '  session_state' AS table_name,
    (SELECT COUNT(*) FROM session_state) AS row_count
UNION ALL
SELECT 
    '  tasks' AS table_name,
    (SELECT COUNT(*) FROM tasks) AS row_count
UNION ALL
SELECT 
    '  system_metrics' AS table_name,
    (SELECT COUNT(*) FROM system_metrics) AS row_count;

-- ============================================
-- 顯示 Agents 信息
-- ============================================

SELECT '🤖 配置的 Agents：' AS info;

SELECT 
    agent_id AS "Agent ID",
    name AS "名稱",
    model AS "模型",
    provider AS "Provider",
    CASE is_active 
        WHEN TRUE THEN '✅ 活躍'
        ELSE '❌ 非活躍'
    END AS "狀態"
FROM agents
ORDER BY id;
