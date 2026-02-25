# Content-Based Conversation State Detector

基於內容的對話狀態檢測系統，而非僅依賴 session key。

## 🎯 目的

在用戶發送訊息時，判斷這是：
- `new_conversation` - 完全新話題/陌生人
- `continuation` - 明顯續接之前的對話
- `topic_change` - 轉換了話題但相關

## 📊 檢測流程

```
用戶輸入
    ↓
1. 檢查 Session 歷史
    ├─ 空歷史 → new_conversation
    └─ 有歷史 → 繼續步驟
    ↓
2. 語義相似度檢查
    ├─ similarity > 0.85 → continuation
    ├─ similarity 0.65-0.85 → topic_change
    └─ similarity < 0.65 → new_conversation
    ↓
3. 關鍵詞模式匹配
    ├─ 規則匹配：然後呢、接著說、順便問一下
    ├─ 語境匹配：話題完全不同
    └─ → topic_change
    ↓
4. 回退到 Session Key 檢查
    └─ 同一 peer → continuation
    └─ 不同 peer → new_conversation
```

## 🧪 測試

### 運行自動測試套件

```bash
cd ~/.openclaw/workspace/scripts
python3 test_detector.py --test
```

預期輸出：
```
================================================================================
Content-Based Conversation State Detector - Test Suite
================================================================================

✅ PASS: Continuation - High similarity
✅ PASS: New Conversation - Low similarity
✅ PASS: Topic Change - Keyword detected
✅ PASS: Topic Change - Context shift
✅ PASS: Continuation - Medium similarity
✅ PASS: New Conversation - Empty history
✅ PASS: Topic Change - Multiple keywords
✅ PASS: Chat Topic - Continuation

================================================================================
Test Summary
================================================================================
Total Tests: 8
Passed: 8 ✅
Failed: 0 ❌
Success Rate: 100.0%
```

### 互動式測試

```bash
cd ~/.openclaw/workspace/scripts
python3 test_detector.py --real
```

這會讓你輸入實際訊息，然後顯示檢測結果。

## 📖 使用方法

### 1. 基本用法

```python
from content_based_detector import ContentBasedDetector

detector = ContentBasedDetector()

user_input = "今天天氣怎麼樣？"
session_history = [
    "你好，今天天氣怎麼樣？",
    "我在香港，今天有點冷"
]

result = detector.detect(user_input, session_history)
print(result)
```

輸出：
```json
{
  "conversationState": "continuation",
  "similarityToPrevious": 0.92,
  "detectedBy": "content_similarity",
  "confidence": 0.92,
  "reason": "High semantic similarity indicates continuation"
}
```

### 2. 使用 CLI

```bash
cd ~/.openclaw/workspace/scripts
python3 get_session_history.py <session_file> --user-input "你的訊息"
```

範例：
```bash
python3 get_session_history.py ~/.openclaw/agents/main/sessions/8330e136-*.jsonl \
  --user-input "順便問一下，這個專案進度如何？" \
  --last-n 5
```

### 3. 集成到 Main Agent

在 `AGENTS.md` 中已經更新了路由流程：

```yaml
1. 調用 Classifier (ollama qwen2.5:1.5b)
2. 檢查 Session 歷史
3. 執行語義相似度計算
4. 檢測關鍵詞模式
5. 決定 conversationState
6. 根據 suggestedAgent 路由
```

## 🔧 實現細節

### 語義相似度計算

使用 `ollama qwen2.5:1.5b` 計算相似度：

```bash
ollama run qwen2.5:1.5b "Calculate semantic similarity (0-1) between these two messages:
User: 今天天氣怎麼樣？
Last message: 我在香港，今天有點冷

Just return the similarity score as a number between 0 and 1, no other text."
```

### 關鍵詞模式

```python
keywords = [
    "然後呢",
    "接著說",
    "順便問一下",
    "另外",
    "說起來",
    "話說"
]
```

### 話題提取

使用 classifier 提取話題分類：
- `code` - 代碼相關
- `task` - 任務相關
- `chat` - 對話相關
- `general` - 一般話題

## 📊 輸出格式

```json
{
  "conversationState": "new_conversation" | "continuation" | "topic_change",
  "similarityToPrevious": 0.0-1.0,
  "detectedBy": "content_similarity" | "keyword_pattern" | "context_shift" | "empty_history",
  "confidence": 0.0-1.0,
  "reason": "explain why this state was chosen",
  "sessionKey": "agent:main:telegram:direct:2673...",  // 可選
  "historyLength": 10  // 可選
}
```

## 🎯 成功指標

| 指標 | 目標 | 測量方式 |
|------|------|----------|
| 準確率 | > 85% | 手動測試 + 用戶反饋 |
| 響應時間 | < 500ms | 從輸入到結果的時間 |
| 誤報率 | < 10% | 測試套件 |
| 漏報率 | < 10% | 測試套件 |

## 🔍 調試

### 查看詳細日誌

```python
import logging

logging.basicConfig(level=logging.DEBUG)
detector = ContentBasedDetector()
```

### 測試單個功能

```python
# 測試關鍵詞檢測
detector._detect_keyword_topic_change("然後呢，接著說")

# 測試話題提取
detector._extract_topic("這是一個關於 Python 的代碼示例")

# 測試語義相似度
detector._calculate_semantic_similarity("今天天氣怎麼樣？",
                                         ["你好，今天天氣怎麼樣？"])
```

## 📝 更新日誌

### 2026-02-25
- ✅ 創建 ContentBasedDetector 類
- ✅ 實現語義相似度計算
- ✅ 實現關鍵詞模式匹配
- ✅ 實現話題轉換檢測
- ✅ 創建測試套件
- ✅ 更新 AGENTS.md 說明

## 🚀 未來改進

- [ ] 支持多模型相似度計算
- [ ] 加入時間間隔檢測
- [ ] 支持情緒分析
- [ ] 學習用戶的個人模式
- [ ] 優化性能（批處理）
- [ ] 加入更多語言支持

---

**重要提示**：這個檢測器應該無縫地在後台運行，並不會為用戶體驗增加明顯的延遲。
