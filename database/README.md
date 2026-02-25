# 🐘 OpenClaw Data Agent - 中央數據庫存儲系統

## 📋 系統總覽

| 組件 | 說明 | 狀態 |
|--------|------|------|
| **PostgreSQL** | 數據庫 | ✅ 已配置 |
| **pgAdmin** | Web 管理界面 | ✅ 已配置 |
| **Data Agent** | 數據庫管理員 | ✅ 已實施 |
| **Python 連接器** | 數據庫查詢接口 | ✅ 已創建 |
| **Docker Compose** | 容器化部署 | ✅ 已配置 |

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│              Docker Compose 集群                      │
│                                                           │
│   ┌──────────────┬──────────────┬──────────────┐    │
│   │ PostgreSQL   │   pgAdmin   │   Data Agent │    │
│   │  (數據庫)   │  (Web 管理)  │  (數據管理員)  │    │
│   │  Port: 5432   │  Port: 5050   │  Workspace:    │    │
│   └──────────────┴──────────────┴──────────────┘    │
│                                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌───────────────────────┐
        │   PostgreSQL         │
        │   (openclaw)          │
        │                       │
        │   ┌─────────────┐    │
        │   │  10 個核心表 │    │
        │   └─────────────┘    │
        └───────────────────────┘
                           ↓
        ┌───────────────────────┐
        │   OpenClaw Agents    │
        │                       │
        │   ┌─────────────┐    │
        │   │  Main (GLM-4.7)      │    │
        │   │  Classifier (Ollama) │    │
        │   │  Chat (GLM-4.7-FlashX) │    │
        │   │  Task (GLM-4.7-Flash)   │    │
        │   │  Coding (GLM-4.7)      │    │
        │   │  Data (GLM-4.7-Flash)    │    │
        │   │  QA (GLM-4.7-Flash)      │    │
        │   └─────────────┘    │
        └───────────────────────┘
```

---

## 📊 數據庫表結構

### 1. agents（Agents 配置）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| agent_id | VARCHAR(50) | 唯一 ID |
| name | VARCHAR(100) | 顯示名稱 |
| model | VARCHAR(100) | 模型路徑 |
| provider | VARCHAR(50) | 提供商 |
| workspace | VARCHAR(255) | 工作區路徑 |
| is_active | BOOLEAN | 是否活躍 |
| metadata | JSONB | 元數據 |

### 2. conversations（對話會話）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| conversation_id | VARCHAR(100) | 唯一對話 ID |
| channel | VARCHAR(50) | 頻道類型 |
| user_id | VARCHAR(100) | 用戶 ID |
| title | TEXT | 對話標題 |
| status | VARCHAR(20) | 狀態 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |
| metadata | JSONB | 元數據 |

### 3. messages（對話消息）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| message_id | VARCHAR(100) | 唯一消息 ID |
| conversation_id | VARCHAR(100) | 關聯的對話 |
| role | VARCHAR(20) | 角色（user, assistant, system） |
| content | TEXT | 消息內容 |
| agent_id | VARCHAR(50) | 處理該消息的 Agent |
| created_at | TIMESTAMP | 創建時間 |
| token_count | INTEGER | Token 消耗 |
| metadata | JSONB | 元數據 |

### 4. knowledge_base（知識庫）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| entry_id | VARCHAR(100) | 唯一知識條目 ID |
| category | VARCHAR(50) | 類別（code, task, data, research 等） |
| title | VARCHAR(255) | 標題 |
| content | TEXT | 內容 |
| summary | TEXT | 摘要 |
| tags | TEXT[] | 標籤數組 |
| conversation_state | VARCHAR(50) | 對話狀態 |
| confidence | FLOAT | 置信度 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |
| source | VARCHAR(50) | 數據源（neur-opt, manual） |
| metadata | JSONB | 元數據 |

### 5. memory（長期記憶）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| memory_id | VARCHAR(100) | 唯一記憶 ID |
| title | VARCHAR(255) | 標題 |
| content | TEXT | 內容 |
| category | VARCHAR(50) | 類別 |
| importance | INTEGER | 重要級（1-5） |
| is_active | BOOLEAN | 是否活躍 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |
| access_count | INTEGER | 訪問次數 |
| last_accessed_at | TIMESTAMP | 最後訪問時間 |
| metadata | JSONB | 元數據 |

### 6. logs（系統日誌）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| log_id | VARCHAR(100) | 唯一日誌 ID |
| level | VARCHAR(20) | 日誌級別（INFO, WARN, ERROR） |
| category | VARCHAR(50) | 類別（agent, system, user） |
| message | TEXT | 日誌消息 |
| agent_id | VARCHAR(50) | 相關的 Agent |
| context | JSONB | 上下文信息 |
| created_at | TIMESTAMP | 創建時間 |
| metadata | JSONB | 元數據 |

### 7. user_actions（用戶操作記錄）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| action_id | VARCHAR(100) | 唯一操作 ID |
| user_id | VARCHAR(100) | 用戶 ID |
| action_type | VARCHAR(50) | 操作類型（create, read, update, delete） |
| target_type | VARCHAR(50) | 目標類型（agent, conversation, message） |
| target_id | VARCHAR(100) | 目標 ID |
| description | TEXT | 操作描述 |
| status | VARCHAR(20) | 狀態（pending, completed, failed） |
| created_at | TIMESTAMP | 創建時間 |
| metadata | JSONB | 元數據 |

### 8. session_state（對話狀態）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| session_id | VARCHAR(100) | 唯一會話 ID |
| conversation_id | VARCHAR(100) | 關聯的對話 |
| current_agent_id | VARCHAR(50) | 當前 Agent |
| state | JSONB | 完整狀態（上下文、歷史等） |
| context_window | INTEGER[] | 上下文窗口（消息 ID 列表） |
| metadata | JSONB | 元數據 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |
| last_message_at | TIMESTAMP | 最後消息時間 |

### 9. tasks（任務列表）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| task_id | VARCHAR(100) | 唯一任務 ID |
| title | VARCHAR(255) | 標題 |
| description | TEXT | 描述 |
| status | VARCHAR(20) | 狀態（pending, in_progress, completed, failed） |
| priority | INTEGER | 優先級（1-5） |
| assigned_agent_id | VARCHAR(50) | 分配的 Agent |
| conversation_id | VARCHAR(100) | 關聯的對話 |
| created_at | TIMESTAMP | 創建時間 |
| updated_at | TIMESTAMP | 更新時間 |
| due_at | TIMESTAMP | 截止時間 |
| completed_at | TIMESTAMP | 完成時間 |
| metadata | JSONB | 元數據 |

### 10. system_metrics（系統指標）

| 字段 | 類型 | 說明 |
|------|------|------|
| id | SERIAL | 主鍵 |
| metric_id | VARCHAR(100) | 唯一指標 ID |
| metric_name | VARCHAR(100) | 指標名稱 |
| metric_value | FLOAT | 指標值 |
| metric_type | VARCHAR(50) | 指標類型（performance, usage, error） |
| agent_id | VARCHAR(50) | 相關的 Agent |
| timestamp | TIMESTAMP | 時間戳 |
| metadata | JSONB | 元數據 |

---

## 🚀 快速開始

### 步驟 1：啟動數據庫服務

```bash
# 進入數據庫目錄
cd ~/.openclaw/workspace/database

# 啟動服務
./start.sh
```

**輸出**：
```
🐘 啟動 OpenClaw Data Agent (PostgreSQL 數據庫)

📊 啟動 Docker Compose 服務...

⏳ 等待 PostgreSQL 就緒...
. . . . . . . . . . . . . . . . . .
✅ PostgreSQL 已就緒

✅ 數據庫連接成功

📊 服務狀態：
  - PostgreSQL: http://localhost:5432
  - pgAdmin: http://localhost:5050

📋 可用的腳本：
  - python3 connector.py [命令]
  - python3 workspace-data/connector.py [命令]

🚀 可以開始使用數據庫了！
```

### 步驟 2：測試連接

```bash
# 測試 Data Agent 連接
python3 workspace-data/connector.py test

# 查看所有 Agents
python3 workspace-data/connector.py agents
```

### 步驟 3：訪問 Web 管理界面

1. 打開瀏覽器訪問：`http://localhost:5050`
2. 登錄信息：
   - 用戶：`openclaw`
   - 密碼：`openclaw_password_2024`

3. 功能：
   - 查看和管理數據庫表
   - 執行 SQL 查詢
   - 監控數據庫性能
   - 備份和恢復數據庫

---

## 📋 Data Agent 工具命令

### 查詢工具

```bash
# 查看所有 Agents
python3 workspace-data/connector.py agents

# 查看最近的對話
python3 workspace-data/connector.py conversations --limit 10

# 搜索知識庫
python3 workspace-data/connector.py kb-search "Python" --limit 5

# 查看記憶
python3 workspace-data/connector.py memory

# 查看日誌
python3 workspace-data/connector.py logs
```

### 批量操作

```bash
# 添加到知識庫
python3 workspace-data/connector.py kb-add "code" "Python 優化" "如何使用 Python 優化腳本的執行速度"

# 添加到記憶
python3 workspace-data/connector.py memory-add "系統配置" "完成了 Ollama 和 PostgreSQL 的配置"
```

### 其他命令

```bash
# 查詢日誌（指定 Agent）
python3 workspace-data/connector.py logs --agent "data" --limit 20

# 查詢特定類別的知識庫
python3 workspace-data/connector.py kb --category "code"

# 搜索知識庫（指定 top_k）
python3 workspace-data/connector.py kb-search "Python" --limit 10

# 查看對話狀態
python3 workspace-data/connector.py session <session_id>
```

---

## 🔍 數據庫監控

### 容器狀態檢查

```bash
# 查看所有容器狀態
docker-compose ps

# 查看 PostgreSQL 日誌
docker-compose logs postgres

# 查看 Data Agent 日誌
docker-compose logs postgres | grep "Data Agent"
```

### 連接池監控

```bash
# 進入 PostgreSQL 容器
docker exec -it openclaw-postgres psql -U openclaw -d openclaw

# 查看當前連接
SELECT state, COUNT(*) 
FROM pg_stat_activity 
WHERE state = 'active';

# 查看數據庫大小
SELECT pg_size_pretty(pg_database_size('openclaw'));

# 查看表大小
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname::regclass))
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname::regclass) DESC;
```

---

## 📊 性能優化建議

### 1. 索引優化

```sql
-- 為消息表創建索引
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
    ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_agent_id 
    ON messages(agent_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at 
    ON messages(created_at DESC);

-- 為知識庫創建索引
CREATE INDEX IF NOT EXISTS idx_kb_category 
    ON knowledge_base(category);

CREATE INDEX IF NOT EXISTS idx_kb_tags 
    ON knowledge_base USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_kb_created_at 
    ON knowledge_base(created_at DESC);
```

### 2. 查詢優化

```sql
-- 避免 SELECT *
SELECT m.id, m.role, m.content 
FROM messages m 
WHERE m.conversation_id = ? 
LIMIT 10;

-- 使用 LIMIT 和 OFFSET 分頁
SELECT m.id, m.role, m.content 
FROM messages m 
WHERE m.conversation_id = ? 
ORDER BY m.created_at DESC 
LIMIT 10 OFFSET ?;
```

### 3. 連接池配置

```python
# 最小連接：2
# 最大連接：10
# 空閒時間：30 秒
# 查詢超時：5 秒
# 連接超時：10 秒
```

---

## 💾 備份與恢復

### 備份

```bash
# 備份整個數據庫
docker exec -i openclaw-postgres pg_dump -U openclaw openclaw > backup_$(date +%Y%m%d).sql

# 備份到本地卷
docker cp openclaw-postgres:/var/lib/postgresql/backups/backup_20260225.sql .
```

### 恢復

```bash
# 恢復數據庫
cat backup_20260225.sql | docker exec -i openclaw-postgres psql -U openclaw -d openclaw

# 進入容器恢復
docker exec -it openclaw-postgres psql -U openclaw -d openclaw < backup_20260225.sql
```

---

## 🎯 使用場景

### 場景 1：查詢知識庫

```bash
# 搜索知識庫
python3 workspace-data/connector.py kb-search "Python 腳本"

# 輸出：
# 找到 5 個結果：
# 1. [CODE] Python 腳本優化
#    匹配: 如何使用 Python 優化腳本的執行速度
# 2. [CODE] Python 數據庫連接
#    匹配: 如何使用 psycopg2 連接 PostgreSQL
```

### 場景 2：查看對話歷史

```bash
# 查看最近的對話
python3 workspace-data/connector.py conversations --limit 10

# 輸出：
# 最近的 10 個對話：
# 1. [ACTIVE] Chat with user
#    創建時間: 2026-02-25 10:30:00
# 2. [ACTIVE] Coding Task
#    創建時間: 2026-02-25 09:15:00
```

### 場景 3：監控性能

```bash
# 查看日誌
docker-compose logs postgres | tail -50

# 進入容器監控
docker exec -it openclaw-postgres psql -U openclaw -d openclaw

# 查看統計
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM knowledge_base;
```

---

## 📋 故障排除

### 問題 1：數據庫連接失敗

```bash
# 檢查容器狀態
docker-compose ps

# 重啟容器
docker-compose restart postgres

# 查看日誌
docker-compose logs postgres
```

### 問題 2：查詢超時

```bash
# 檢查查詢配置
python3 workspace-data/connector.py test

# 檢查連接池
docker exec -it openclaw-postgres psql -U openclaw -d openclaw -c "SHOW ALL;"

# 優化查詢
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
ON messages(conversation_id);
```

### 問題 3：權限錯誤

```bash
# 檢查容器權限
docker exec -it openclaw-postgres ls -la /var/lib/postgresql/data

# 檢查數據庫權限
docker exec -it openclaw-postgres psql -U openclaw -d openclaw -c "\l"

# 修復權限
docker exec -it openclaw-postgres psql -U openclaw -d openclaw -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO openclaw;"
```

---

## 📚 相關文檔

| 文檔 | 說明 |
|------|------|
| `workspace-data/AGENTS.md` | Data Agent 職責和哲學 |
| `workspace-data/IDENTITY.md` | Data Agent 身份信息 |
| `workspace-data/TOOLS.md` | 工具使用指南 |
| `workspace-data/connector.py` | Python 連接器腳本 |
| `database/docker-compose.yml` | Docker 配置 |
| `database/init-sql.sql` | 數據庫初始化腳本 |
| `database/start.sh` | 一鍵啟動腳本 |

---

## 🎉 總結

✅ **PostgreSQL 數據庫**：中央數據存儲
✅ **10 個核心表**：完整的數據結構
✅ **Python 連接器**：簡單易用的 API
✅ **Docker Compose**：容器化部署
✅ **Web 管理界面**：pgAdmin
✅ **權限控制**：Data Agent 管理數據庫操作
✅ **安全隔離**：其他 Agents 只能查詢

---

## 🚀 立即開始

```bash
# 1. 啟動數據庫
cd ~/.openclaw/workspace/database
./start.sh

# 2. 測試連接
python3 workspace-data/connector.py test

# 3. 查看所有 Agents
python3 workspace-data/connector.py agents

# 4. 搜索知識庫
python3 workspace-data/connector.py kb-search "Python"

# 5. 查看日誌
docker-compose logs postgres | tail -20
```

---

**準備好開始了嗎？你的 PostgreSQL 中央存儲系統已經完全就緒！** 🎊
