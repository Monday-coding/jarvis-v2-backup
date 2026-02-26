# 🗄️ PostgreSQL 數據庫方案

## 📋 方案概述

**目標**：建立一個 PostgreSQL 數據庫，供所有 Agents 存儲和管理數據。

**方案特點**：
- ✅ 完整的數據架構（10 個核心表）
- ✅ 支持所有 Agent 類型
- ✅ 高性能查詢（索引優化）
- ✅ Web 管理界面（pgAdmin）
- ✅ 自動化部署（Docker Compose）
- ✅ 數據備份機制

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────┐
│         Docker Compose                     │
├─────────────────────────────────────────────────┤
│                                           │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ PostgreSQL   │  │  pgAdmin    │   │
│  │   :5432     │  │    :5050     │   │
│  └──────┬───────┘  └──────────────┘   │
│         │                                │
│  ┌──────┴────────────────────────┐      │
│  │   OpenClaw Agents            │      │
│  ├──────────────────────────────┤      │
│  │  Main Agent               │      │
│  │  Chat Agent               │      │
│  │  Coding Agent             │      │
│  │  Task Agent               │      │
│  │  Data Agent               │      │
│  │  System Admin Agent        │      │
│  └──────────────────────────────┘      │
│                                           │
└───────────────────────────────────────────┘
```

---

## 📊 數據庫架構

### 核心表結構（10 個表）

#### 1. **AGENTS** - Agent 配置信息

存儲所有 Agents 的配置和狀態。

```sql
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,      -- main, chat, coding 等
    name VARCHAR(100) NOT NULL,              -- Agent 名稱
    model VARCHAR(100) NOT NULL,              -- 模型名稱
    provider VARCHAR(50) NOT NULL,           -- zai, ollama 等
    workspace VARCHAR(255) NOT NULL,          -- 工作區路徑
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,          -- 是否活躍
    metadata JSONB DEFAULT '{}'::jsonb      -- 額外元數據
);
```

**用途**：
- 管理 Agents 配置
- 追蹤 Agents 狀態
- 存儲模型信息

---

#### 2. **CONVERSATIONS** - 對話會話

存儲所有用戶對話會話。

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(100) UNIQUE NOT NULL,
    channel VARCHAR(50) NOT NULL,            -- telegram, whatsapp 等
    user_id VARCHAR(100),                    -- 用戶 ID
    title TEXT,                              -- 對話標題
    status VARCHAR(20) DEFAULT 'active',      -- active, closed, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**索引**：
- `idx_conversations_status`
- `idx_conversations_channel`
- `idx_conversations_user_id`
- `idx_conversations_created_at`

---

#### 3. **MESSAGES** - 對話消息

存儲所有對話消息。

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100) UNIQUE NOT NULL,
    conversation_id VARCHAR(100) NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,              -- user, assistant, system
    content TEXT NOT NULL,                   -- 消息內容
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    token_count INTEGER DEFAULT 0,            -- Token 數量
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**用途**：
- 保存對話歷史
- 追蹤 Token 使用
- 支持上下文管理

---

#### 4. **KNOWLEDGE_BASE** - 知識庫

存儲結構化知識。

```sql
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    entry_id VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,             -- CODE, TASK, RESEARCH 等
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,                             -- 摘要
    tags TEXT[],                              -- 標籤數組
    conversation_state VARCHAR(50) DEFAULT 'new_conversation',
    confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'neur-opt',   -- neur-opt, user, system
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**索引**：
- `idx_kb_category`
- `idx_kb_tags` (GIN)
- `idx_kb_conversation_state`
- `idx_kb_created_at`

---

#### 5. **MEMORY** - 長期記憶

存儲重要的長期記憶。

```sql
CREATE TABLE memory (
    id SERIAL PRIMARY KEY,
    memory_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),                    -- preference, fact, pattern 等
    importance INTEGER DEFAULT 3,              -- 1-5，5 最重要
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**用途**：
- 存儲用戶偏好
- 保存重要事實
- 記錄使用模式

---

#### 6. **LOGS** - 系統日誌

存儲所有系統日誌。

```sql
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    log_id VARCHAR(100) UNIQUE NOT NULL,
    level VARCHAR(20) NOT NULL,               -- INFO, WARNING, ERROR
    category VARCHAR(50),                      -- agent, system, api 等
    message TEXT NOT NULL,
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    context JSONB,                            -- 日誌上下文
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**索引**：
- `idx_logs_level`
- `idx_logs_category`
- `idx_logs_agent_id`
- `idx_logs_created_at`

---

#### 7. **USER_ACTIONS** - 用戶操作記錄

存儲用戶操作歷史。

```sql
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    action_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    action_type VARCHAR(50) NOT NULL,         -- create, update, delete, query 等
    target_type VARCHAR(50),                  -- task, file, setting 等
    target_id VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'completed',   -- pending, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**用途**：
- 追蹤用戶操作
- 審計日誌
- 行為分析

---

#### 8. **SESSION_STATE** - 對話狀態

存儲對話會話的狀態。

```sql
CREATE TABLE session_state (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    conversation_id VARCHAR(100) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    current_agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    context_window INTEGER[],                  -- 上下文窗口
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**用途**：
- 管理對話狀態
- 保存上下文窗口
- 支持對話恢復

---

#### 9. **TASKS** - 任務隊列

存儲待處理的任務。

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',     -- pending, in_progress, completed, failed
    priority INTEGER DEFAULT 3,               -- 1-5，1 最高優先級
    assigned_agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    conversation_id VARCHAR(100) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_at TIMESTAMP,                          -- 截止時間
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**索引**：
- `idx_tasks_status`
- `idx_tasks_priority`
- `idx_tasks_assigned_agent`
- `idx_tasks_due_at`

---

#### 10. **SYSTEM_METRICS** - 系統指標

存儲系統性能指標。

```sql
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,         -- response_time, memory_usage 等
    metric_value FLOAT,
    metric_type VARCHAR(50),                  -- performance, resource, cost
    agent_id VARCHAR(50) REFERENCES agents(agent_id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

**用途**：
- 監控系統性能
- 追蹤資源使用
- 分析成本趨勢

---

## 🚀 部署方案

### 1. Docker Compose 配置

```yaml
version: '3.8'

services:
  # PostgreSQL 數據庫
  postgres:
    image: postgres:15-alpine
    container_name: openclaw-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: openclaw
      POSTGRES_PASSWORD: openclaw_password_2024
      POSTGRES_DB: openclaw
      TZ: Asia/Hong_Kong
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-sql:/docker-entrypoint-initdb.d
      - ./backups:/var/lib/postgresql/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U openclaw"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - openclaw-network

  # pgAdmin - Web 管理界面
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: openclaw-pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_SERVER: postgres
      PGADMIN_DEFAULT_USER: openclaw
      PGADMIN_DEFAULT_PASSWORD: openclaw_password_2024
      PGADMIN_DEFAULT_PORT: 5432
    ports:
      - "5050:80"
    depends_on:
      - postgres
    networks:
      - openclaw-network

volumes:
  postgres_data:
    driver: local

networks:
  openclaw-network:
    driver: bridge
```

---

### 2. 啟動數據庫

```bash
cd database
docker-compose up -d
```

---

### 3. 驗證部署

```bash
# 檢查容器狀態
docker ps

# 查看 PostgreSQL 日誌
docker logs openclaw-postgres

# 檢查數據庫連接
docker exec -it openclaw-postgres psql -U openclaw -d openclaw -c "SELECT version();"
```

---

## 📊 使用方案

### 1. Agent 數據存儲

#### Main Agent

```python
# 保存對話
INSERT INTO conversations (conversation_id, channel, user_id, title)
VALUES ('conv_001', 'telegram', 'user_123', '設置優化');

# 保存消息
INSERT INTO messages (message_id, conversation_id, role, content, agent_id, token_count)
VALUES ('msg_001', 'conv_001', 'user', '優化系統', 'main', 50);

# 更新會話狀態
INSERT INTO session_state (session_id, conversation_id, current_agent_id, state)
VALUES ('sess_001', 'conv_001', 'main', '{"context": "optimization"}');
```

#### Chat Agent

```python
# 查詢對話歷史
SELECT * FROM messages
WHERE conversation_id = 'conv_001'
ORDER BY created_at DESC
LIMIT 10;

# 保存知識
INSERT INTO knowledge_base (entry_id, category, title, content, summary, tags)
VALUES ('kb_001', 'CODE', 'Python 優化', '優化腳本...', '提升速度', '{python, optimization}');
```

#### Coding Agent

```python
# 創建任務
INSERT INTO tasks (task_id, title, description, status, priority, assigned_agent_id)
VALUES ('task_001', '編寫腳本', '創建備份腳本', 'pending', 1, 'coding');

# 記錄日誌
INSERT INTO logs (log_id, level, category, message, agent_id)
VALUES ('log_001', 'INFO', 'coding', '腳本已創建', 'coding');

# 記錄指標
INSERT INTO system_metrics (metric_id, metric_name, metric_value, metric_type, agent_id)
VALUES ('metric_001', 'response_time', 2.3, 'performance', 'coding');
```

---

### 2. Web 管理界面

訪問 **pgAdmin**：
- URL：http://localhost:5050
- 用戶：openclaw
- 密碼：openclaw_password_2024
- 伺服器：postgres
- 端口：5432
- 數據庫：openclaw
- 用戶：openclaw
- 密碼：openclaw_password_2024

---

### 3. 備份與恢復

#### 備份

```bash
# 手動備份
docker exec openclaw-postgres pg_dump -U openclaw openclaw > backup_$(date +%Y%m%d).sql

# 自動備份（Cron）
0 2 * * * docker exec openclaw-postgres pg_dump -U openclaw openclaw > /var/lib/postgresql/backups/daily_$(date +\%Y\%m\%d).sql
```

#### 恢復

```bash
# 恢復備份
docker exec -i openclaw-postgres psql -U openclaw openclaw < backup_20260226.sql
```

---

## 🔧 優化建議

### 1. 性能優化

- ✅ 已添加所有必要的索引
- ✅ 使用 JSONB 存儲彈性數據
- ✅ 使用 GIN 索引支持數組查詢
- ⚠️ 可定期執行 `VACUUM ANALYZE`

### 2. 安全優化

- ✅ 使用獨立的數據庫用戶
- ✅ 容器隔離
- ⚠️ 建議修改默認密碼
- ⚠️ 限制 pgAdmin 訪問（僅本地）

### 3. 擴展性

- ✅ 支持添加新的表
- ✅ 支持添加新的 Agent
- ✅ 支持數據分片（未來）
- ✅ 支持讀寫分離（未來）

---

## 📋 實施計劃

### 階段 1：部署數據庫（5 分鐘）

1. 啟動 Docker Compose
2. 驗證數據庫連接
3. 檢查表結構

### 階段 2：Agent 集成（30 分鐘）

1. 創建連接器腳本
2. 集成到 Main Agent
3. 集成到其他 Agents

### 階段 3：測試（15 分鐘）

1. 測試數據插入
2. 測試數據查詢
3. 測試性能

### 階段 4：監控（持續）

1. 設置日誌監控
2. 設置指標追蹤
3. 設置自動備份

---

## 📊 預期效果

### 數據管理改進

| 項目 | 當前 | 使用數據庫後 |
|------|------|-------------|
| 數據存儲 | 文件系統 | **結構化** ✅ |
| 查詢速度 | 文件搜索 | **SQL 查詢** ✅ |
| 數據一致性 | 低 | **ACID 保證** ✅ |
| 備份恢復 | 手動 | **自動化** ✅ |
| Web 管理 | 無 | **pgAdmin** ✅ |

---

## ✅ 總結

**方案優勢**：
- ✅ 完整的數據架構（10 個核心表）
- ✅ 支持所有 Agent 類型
- ✅ 高性能查詢（索引優化）
- ✅ Web 管理界面（pgAdmin）
- ✅ 自動化部署（Docker Compose）
- ✅ 數據備份機制

**準備就緒**：可以直接部署使用！

---

**準備開始部署嗎？**
