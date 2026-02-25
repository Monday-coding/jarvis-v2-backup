# OpenClaw Multi-Agent 對話狀態管理

## 問題：Classifier 如何識別新對話？

### 當前問題

如果每次用戶輸入都調用 Classifier：
- ❌ 成本高（每次都調用 LLM）
- ❌ 延遲高（多一次網絡調用）
- ❌ 無法識別對話上下文（新 vs 繼續）
- ❌ 簡單回應（如 "ok"）也會觸發分類

---

## 解決方案：混合模式

### 方案 1：Main Agent 自帶分類能力（推薦）

```
User Input
    ↓
┌─────────────────────────────────────────────────────────┐
│  Main Agent (有完整上下文)                                │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. 檢查對話狀態                                      │  │
│  │    - 新對話？ → 重置狀態，重新評估意圖               │  │
│  │    - 繼續對話？ → 延續當前 Agent                    │  │
│  │    - 換題目？ → 調用 Classifier 深度分析             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 2. 簡單意圖判斷（Main Agent 直接判斷）               │  │
│  │    - chat: "你好"、"ok"、"thanks"                  │  │
│  │    - task: "發郵件"、"設置提醒"                     │  │
│  │    - code: "寫個腳本"                              │  │
│  │    - data: "查詢數據"                              │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 3. 複雜場景 → 調用 Classifier                       │  │
│  │    - 意圖不明確                                    │  │
│  │    - 涉及多個領域                                  │  │
│  │    - 需要深度分析                                  │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
    ↓
Manager (路由)
    ↓
Specialized Agents
```

### 優點

- ✅ Main Agent 有完整上下文，判斷更準確
- ✅ 簡單情況不調用 Classifier，節省成本
- ✅ 能識別對話狀態（新 vs 繼續 vs 換題目）
- ✅ 響應更快

---

## 對話狀態檢測

### 狀態類型

| 狀態 | 觸發條件 | 處理方式 |
|------|----------|----------|
| **new_conversation** | 新 session、或明確重新開始 | 重置狀態，重新分類 |
| **continuation** | 語義相似度 > 0.7，或有延續標誌 | 延續當前 Agent |
| **topic_change** | 語義相似度 < 0.3，或有換題目標誌 | 調用 Classifier 重新評估 |

### 檢測方法

#### 1. 明確標誌

| 標誌類型 | 關鍵詞 | 狀態 |
|---------|--------|------|
| 新對話 | "重新開始"、"新問題"、"reset" | `new_conversation` |
| 換題目 | "另外"、"順便問"、"另一件事"、"還有個問題" | `topic_change` |
| 延續 | "再說清楚點"、"咁呢"、"仲有"、"詳細點" | `continuation` |

#### 2. 語義相似度

```python
# 偽代碼
similarity = cosine_similarity(current_input, previous_input)

if similarity > 0.7:
    state = "continuation"
elif similarity < 0.3:
    state = "topic_change"
else:
    state = "ambiguous"  # 需要進一步判斷
```

#### 3. 上下文檢查

```javascript
// 使用 memory_search 查詢最近對話
const recentContext = await memory_search({
  query: currentInput,
  maxResults: 5,
  recentMinutes: 30
});

// 檢查是否與當前主題相關
const isRelevant = recentContext.some(ctx => ctx.similarity > 0.6);
```

---

## 實現策略

### 策略 A：Main Agent 主導（推薦）

Main Agent 的 AGENTS.md 添加：

```markdown
## 對話狀態檢測

在處理用戶輸入前，先檢查對話狀態：

### 1. 檢查是否新對話
- 如果是新 session → 調用 Classifier
- 如果用戶明確說 "重新開始" → 調用 Classifier

### 2. 檢查是否繼續對話
- 如果當前正在某個 Agent 的會話中
- 且用戶輸入與當前主題相關
- → 直接交給當前 Agent，不調用 Classifier

### 3. 檢查是否換題目
- 如果檢測到換題目標誌（"另外"、"順便問"）
- 或語義相似度低
- → 調用 Classifier 重新評估

### 4. 簡單輸入直接處理
- 如果是簡單回應（"ok"、"thanks"、"明白了"）
- → 直接回應，不調用 Classifier
```

### 策略 B：Classifier 增強（已實現）

Classifier Agent 增加對話狀態檢測能力：

```json
{
  "conversationState": "continuation",
  "intent": "code",
  "confidence": 0.92,
  "contextClues": {
    "similarityToPrevious": 0.85,
    "topicContinuity": true,
    "explicitStateChange": false
  }
}
```

### 策略 C：混合模式（最佳）

```
┌─────────────────────────────────────────────────────────┐
│  Main Agent 決策樹                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Input                                             │
│    │                                                    │
│    ├─→ 新 session?                                     │
│  ┌──┴──┐                                                │
│  │ 是  │ 否                                              │
│  ↓     ↓                                                │
│  調用 Classifier  檢查是否換題目                          │
│              ┌──┴──┐                                   │
│              │ 是  │ 否                                 │
│              ↓     ↓                                   │
│         調用 Classifier  延續當前 Agent                  │
│                                                          │
│  另外路徑：                                             │
│  └─→ 簡單輸入（ok, thanks）? → 直接回應               │
│  └─→ 複雜/不明確? → 調用 Classifier                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 配置示例

### Main Agent 的 AGENTS.md

```markdown
## 對話狀態檢測

在調用 Classifier 前，先檢查：

### 簡單輸入列表（不調用 Classifier）
- "ok", "好的", "👍"
- "thanks", "謝謝", "多謝"
- "明白了", "okok", "得"

### 新對話標誌（調用 Classifier）
- "重新開始"
- "新問題"
- "reset"

### 換題目標誌（調用 Classifier）
- "另外"
- "順便問"
- "另一件事"
- "還有個問題"

### 繼續對話（不調用 Classifier）
- 語義相似度 > 0.7
- 延續標誌（"再說清楚點"、"咁呢"）
- 當前正在某個 Agent 的會話中
```

---

## 成本優化

### 分層調用策略

| 場景 | 是否調用 Classifier | 原因 |
|------|-------------------|------|
| 新對話 | ✅ 是 | 需要完整分析 |
| 換題目 | ✅ 是 | 需要重新評估 |
| 繼續對話 | ❌ 否 | 延續當前 Agent |
| 簡單回應 | ❌ 否 | 直接處理 |
| 複雜/不明確 | ✅ 是 | 需要深度分析 |

### 預期成本節省

假設：
- 70% 的輸入是繼續對話
- 15% 是簡單回應
- 10% 是換題目
- 5% 是新對話

**節省成本**：85%（簡單回應 + 繼續對話）

---

## 總結

✅ **Classifier 不需要每次都調用**
✅ **Main Agent 可以自帶分類能力**
✅ **對話狀態檢測是關鍵**
✅ **混合模式是最佳方案**

**推薦實現**：
1. Main Agent 先進行簡單判斷
2. 只在必要時調用 Classifier
3. Classifier 增強對話狀態檢測能力
4. 根據對話狀態調整路由策略
