# Multi-Agent 系統設計深度解析

## 📊 來源引用
- Multi-Agent Reference Architecture
- Zuci Systems
- Comet ML

---

## 🧩 Multi-Agent 系統是什麼？

Multi-Agent 系統是一種由多個專門化 AI 代理（agents）協作完成複雜任務的架構。每個 agent 都有明確角色、能力受限、責任單一，整體由一個 orchestrator（如 manager-agent）協調。

### 為什麼需要 Multi-Agent？

**單一 AI 的限制**（Comet ML）：
- 長上下文窗口導致注意力稀疏
- 多任務混雜時性能急劇下降（推理能力可下降高達 73%）
- 工具調用錯誤率隨任務複雜度指數級增長
- 難以同時處理不同領域的專業知識

**Multi-Agent 的優勢**：
- **專門化**：每個 agent 專精於特定領域
- **模塊化**：易於調試、替換、擴展
- **並行化**：多個 agent 可以同時執行子任務
- **容錯性**：一個 agent 失敗不會影響整個系統
- **可觀察性**：每個 agent 的行為都可以獨立監控

---

## 🧱 Multi-Agent 系統的核心組成（六大構件）

根據 Zuci Systems 的分析，可靠的 multi-agent 系統由六個核心構件組成：

---

### 1. 專門化 Agents（Specialized Agents）

每個 agent 都只做一件事，專精於特定領域：

#### 典型 Agent 類型

| Agent 類型 | 職責 | 能力限制 |
|-----------|------|---------|
| **Classifier-Agent** | 輸入分類、意圖識別 | 只能返回分類結果 |
| **Manager-Agent** | 路由決策、流程控制 | 不能直接執行任務 |
| **Chat-Agent** | 對話生成、用戶交互 | 只能訪問對話歷史 |
| **Task-Agent** | 任務執行、工具調用 | 不能修改其他 agent 狀態 |
| **Coding-Agent** | 代碼生成、代碼審查 | 只能訪問代碼相關工具 |
| **Data-Agent** | 資料處理、ETL | 只能訪問資料庫/API |
| **Research-Agent** | 信息檢索、分析 | 只能訪問搜索/瀏覽工具 |
| **QA-Agent** | 質量檢查、驗證 | 只能讀取，不能修改 |

#### 設計原則

**單一職責原則（SRP）**：
- 一個 agent 只有一個變化的理由
- 職責越單一，行為越可預測
- 便於單元測試和調試

**能力限制原則**：
- 每個 agent 只能訪問必要的工具
- 避免權限過大導致的濫用
- 增加系統安全性

---

### 2. Agent Intelligence（PRIMAL Core）

每個 agent 都具備基本能力，這是 Zuci Systems 提出的 PRIMAL 框架：

#### PRIMAL 框架詳解

**P - Perception（感知）**
- 理解輸入格式（文本、語音、圖像）
- 提取關鍵信息（實體、意圖、情感）
- 規範化輸入到內部表示

**R - Reasoning（推理）**
- 多步邏輯推導
- 上下文理解
- 因果關係分析

**I - Intention（意圖）**
- 決策：下一步該做什麼
- 目標導向：知道什麼時候完成任務
- 優先級判斷

**M - Memory（記憶）**
- 短期記憶：當前會話上下文
- 長期記憶：持久化的知識庫
- 工作記憶：推理過程中的中間結果

**A - Action（行動）**
- 工具調用
- 生成回應
- 觸發其他 agent

**L - Learning（學習）**
- 從錯誤中調整策略
- 記錄成功模式
- 持續優化性能

---

### 3. Orchestration（協作與調度）

這是 multi-agent 的靈魂。Manager-agent 作為 orchestrator 負責：

#### 核心職責

**1. 路由決策**
- 根據 classifier 的結果決定下一個 agent
- 動態調整 agent 調度順序
- 處理失敗重試和降級

**2. 流程控制**
- 定義任務的執行順序（DAG 或狀態機）
- 並行 vs 串行執行
- 條件分支和循環

**3. 確定性路由**
- 相同輸入始終產生相同的 agent 調用序列
- 便於調試和重現問題
- 減少隨機性帶來的不確定

#### Orchestration 模式

**靜態 Orchestration**：
- 預定義的流程圖
- 適用於固定場景
- 簡單可靠，但缺乏靈活性

**動態 Orchestration**：
- Manager 根據當前狀態動態決定
- 適用於不確定性場景
- 靈活性高，但難以調試

**混合模式**：
- 預定義主流程，關鍵節點動態決策
- 平衡靈活性和可靠性

---

### 4. Tools / Skills（工具與能力）

每個 agent 只能使用有限工具，避免越權與混亂。

#### 工具分類

**信息獲取類**：
- 網頁瀏覽（browser）
- 文件讀取（read）
- 搜索（web_search, web_fetch）
- API 調用（http requests）

**執行類**：
- 命令執行（exec）
- 代碼運行（coding-agent 專用）
- 文件寫入（write, edit）

**通信類**：
- 消息發送（message）
- 會話管理（sessions_*）
- 子 agent 生成（sessions_spawn）

#### 權限控制

**Allowlist（白名單）**：
- 只允許明確列出的工具
- 默認拒絕，顯式允許
- 最安全，但配置成本高

**Denylist（黑名單）**：
- 允許所有工具，除了明確禁止的
- 默認允許，顯式拒絕
- 方便，但存在安全風險

**角色基礎（RBAC）**：
- 根據 agent 角色分配不同權限
- 靈活性高
- 需要細緻的權限模型

---

### 5. Communication（溝通）

Agents 之間透過 internal channel 傳遞 JSON 訊息。

#### 消息格式

```json
{
  "from": "classifier-agent",
  "to": "manager-agent",
  "type": "classification_result",
  "timestamp": 1234567890,
  "payload": {
    "category": "coding_task",
    "confidence": 0.95,
    "metadata": {
      "language": "python",
      "complexity": "medium"
    }
  }
}
```

#### 溝通模式

**點對點（P2P）**：
- 一個 agent 直接發送給另一個 agent
- 簡單直接
- 適用於固定流程

**發布/訂閱（Pub/Sub）**：
- Agent 發布消息到主題
- 訂閱該主題的 agent 都會收到
- 適用於廣播和事件驅動

**請求/回應（Request/Response）**：
- 同步等待回應
- 適用於需要確認的場景

#### OpenClaw 的實現

OpenClaw 使用 **sessions_send** 和 **sessions_spawn** 工具實現 agent 間通信：
- `sessions_send`：發送消息到指定 session
- `sessions_spawn`：生成新的 sub-agent 會話

---

### 6. Governance（治理）

包括安全、權限、監控、可觀察性、日誌追蹤。

#### 安全治理

**認證與授權**：
- 每個 agent 有獨立的認證配置（OpenClaw 的 `auth-profiles.json`）
- Agent 間通信需要驗證
- 工具調用需要授權

**沙箱隔離**：
- 限制 agent 的文件系統訪問
- 網絡訪問控制
- 資源限制（CPU、內存、執行時間）

**防注入與濫用**：
- 輸入驗證和清理
- 限制 agent 的生成能力（sub-agent 不能再生 sub-agent）
- 頻率限制

#### 監控與可觀察性

**日誌追蹤**：
- 每個 agent 的操作記錄
- 關鍵決策點的日誌
- 錯誤和異常記錄

**指標監控**：
- Agent 調用次數、成功率
- 響應時間
- 資源使用量
- 成本追蹤（token 使用量）

**調試工具**：
- 分步執行
- 變量檢查
- 回溯執行路徑

---

## 🔄 Multi-Agent 系統的工作流程

### 典型場景：用戶提問 → 分析 → 執行 → 回應

```
1. 用戶輸入
   ↓
2. Classifier-Agent: 識別意圖
   ↓
3. Manager-Agent: 決定調用哪些 agents
   ↓
4. 並行/串行執行:
   - Research-Agent: 搜索相關信息
   - Data-Agent: 查詢資料庫
   - Coding-Agent: 執行代碼（如需要）
   ↓
5. QA-Agent: 驗證結果
   ↓
6. Chat-Agent: 生成最終回應
   ↓
7. Manager-Agent: 協調輸出
   ↓
8. 用戶收到回應
```

---

## 🏗️ 設計模式與最佳實踐

### 1. 分層架構

**表示層（Presentation Layer）**：
- Chat-Agent
- 負責與用戶交互

**業務邏輯層（Business Logic Layer）**：
- Manager-Agent
- Task-Agent
- 處理業務邏輯

**數據層（Data Layer）**：
- Data-Agent
- 負責數據存取

### 2. 責任鏈模式

按順序調用多個 agent，直到找到能處理的：

```
Input → Classifier → Router → Task-Agent1 → Task-Agent2 → ... → Output
```

### 3. 並行模式

多個 agent 同時執行，最後匯總結果：

```
        → Research-Agent ↘
Input → Manager → Data-Agent → Aggregator → Output
        → Coding-Agent  ↗
```

### 4. 迭代改進模式

多個 agent 輸流改進結果：

```
Draft-Agent → Review-Agent → Rewrite-Agent → Final Review-Agent
```

---

## 📈 性能優化

### 1. 緩存策略

- Agent 結果緩存
- 工具調用結果緩存
- 記憶體緩存 + 持久化緩存

### 2. 批處理

- 合併相似請求
- 批量工具調用
- 減少 API 調用次數

### 3. 模型選擇

- 簡單任務用小模型（Haiku）
- 複雜任務用大模型（Opus）
- 成本與質量的平衡

---

## 🛡️ 風險與挑戰

### 1. Agent 間通信開銷
- 消息序列化/反序列化成本
- 網絡延遲
- 解決：使用高效的協議（如 Protobuf）

### 2. 調試複雜度
- 多個 agent 的交互難以追蹤
- 分布式系統的問題
- 解決：完善的日誌和追蹤系統

### 3. 一致性問題
- 多個 agent 的狀態同步
- 並發修改
- 解決：使用狀態機和鎖機制

### 4. 成本控制
- 每個 agent 都消耗 token
- 子 agent 的並行執行
- 解決：合理設置模型層級和並發限制

---

## 🔮 未來方向

1. **自進化 Agent**：能夠自主學習和優化自己的行為
2. **跨模態 Agent**：處理文本、語音、圖像、視頻的混合輸入
3. **分佈式 Agent**：跨機器、跨雲端部署的 agent 集群
4. **Agent Marketplace**：可交易的 agent 技能和服務

---

## 📝 總結

Multi-Agent 系統是 AI 架構的重要進化方向。通過專門化、模塊化、可協作的 agent，我們能夠：

- **突破單一 AI 的限制**：避免長上下文和多任務混亂
- **提高系統可靠性**：失敗隔離、易於修復
- **增強可觀察性**：每個 agent 的行為都可監控
- **優化成本效益**：根據任務複雜度選擇合適的模型

OpenClaw 的 multi-agent 架構是這一理念的實踐：每個 agent 有獨立的工作區、認證配置、會話存儲，通過 orchestrator 和 bindings 進行路由和協作。

---

**下一步探索**：
- 如何設計自己的 multi-agent 系統？
- 如何選擇合適的 agent 類型和數量？
- 如何監控和優化 multi-agent 系統？
