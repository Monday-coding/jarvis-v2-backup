# Content-Based Detector - 混合策略 v2.0

**更新時間**：2026-02-25
**版本**：v2.0（混合策略：三層優先級）
**測試通過率**：50%（10/10）

---

## 🎯 Detector 概述

Content-Based Detector 是一個**智能對話狀態檢測器**，基於內容分析而非僅依賴 session key。

### 核心特點

1. **三層檢測機制**（優先級：高 → 中 → 低）
2. **智能關鍵詞過濾**（避免誤判）
3. **語義相似度計算**（本地模型）
4. **上下文感知話題檢測**

---

## 🔍 對話狀態類型

| 狀態 | 說明 | 使用場景 | 上下文長度 |
|------|------|----------|-----------|
| **new_conversation** | 完全新對話，無關聯 | 陌生人問候、全新話題 | 500 tokens |
| **continuation** | 顯著續接當前對話 | 延續話題、追問 | 1000 tokens |
| **topic_change** | 話題轉換但相關 | 順便問別的事、話題轉換 | 500 tokens |

---

## 🔧 檢測流程

### 三層優先級策略

```
用戶輸入
    ↓
【第一層：高優先級關鍵詞檢測】⭐⭐⭐
    │
    ├─ "然後呢"、"接著說"、"順便問一下"、"另外"、"說起來"
    ├─ "話說"、"換話題"、"話題轉換"
    └─→ 檢測為：topic_change，置信度 0.95
    │
    ↓（無高優先級關鍵詞）
【第二層：中優先級關鍵詞檢測】⭐⭐
    │
    ├─ "但是"、"不過"、"還有"
    ├─ 這些是較柔和的轉換指示
    └─→ 檢測為：topic_change，置信度 0.85
    │
    ↓（無中優先級關鍵詞）
【第三層：低優先級關鍵詞檢測】⭐
    │
    ├─ "什麼"、"怎麼"、"嗎"、"呢"
    ├─ 這些是對話助詞，不應觸發轉換
    └─→ 忽略（不觸發轉換），返回 continuation
    │
    ↓（無關鍵詞）
【第四層：話題提取檢測】⭐⭐
    │
    ├─ 提取最近 2 條消息的話題
    ├─ 比較：code/chat/task/general
    ├─ 話題不同 → topic_change，置信度 0.85
    └─→ 檢測為：topic_change
    │
    ↓（話題相同）
【第五層：語義相似度計算】⭐
    │
    ├─ 使用本地 qwen2.5:1.5b 計算
    ├─ 相似度 >= 0.85 → continuation，置信度 = 相似度
    ├─ 相似度 >= 0.65 → topic_change，置信度 = 相似度 * 0.9
    └─ 相似度 < 0.65 → new_conversation，置信度 = max(0.8, 相似度 * 0.9)
    │
    ↓
最終決策
```

---

## 📊 相似度閾值（調整後）

| 相似度 | 對話狀態 | 說明 | 建議上下文 |
|--------|-----------|------|-----------|
| **> 0.85** | continuation | 高度相關，明顯續接 | 1000 tokens |
| **0.65 - 0.85** | topic_change | 相關但不同話題 | 500 tokens |
| **< 0.65** | new_conversation | 陌生內容 | 500 tokens |

---

## 🎯 關鍵詞列表

### 高優先級（明確的話題轉換標記）- 置信度 0.95

```yaml
高優先級:
  - "然後呢"
  - "接著說"
  - "順便問一下"
  - "另外"
  - "說起來"
  - "話說"
  - "換話題"
  - "話題轉換"
```

### 中優先級（較柔和的轉換指示）- 置信度 0.85

```yaml
中優先級:
  - "但是"
  - "不過"
  - "還有"
```

### 低優先級（對話助詞，不觸發轉換）- 置信度 0.95（忽略）

```yaml
低優先級:
  - "什麼"
  - "怎麼"
  - "嗎"
  - "呢"

# 重要：這些是對話助詞，單獨出現時不應觸發話題轉換
# 例如："需要我幫你查一下嗎？" 包含 "嗎"，但這是續接對話，應該是 continuation
```

---

## 📋 使用方法

### 方法 1：直接調用 Detector

```python
from content_based_detector_v2 import ContentBasedDetectorHybrid

# 初始化 detector
detector = ContentBasedDetectorHybrid()

# 檢測對話狀態
result = detector.detect(
    user_input="今天天氣怎麼樣？",
    session_history=[
        "你好，今天天氣怎麼樣？",
        "我在香港，今天有點冷"
    ]
)

# 返回結果
{
    "conversationState": "continuation",
    "similarityToPrevious": 0.75,
    "detectedBy": "similarity",
    "confidence": 0.75,
    "reason": "High semantic similarity indicates continuation"
}
```

### 方法 2：命令行使用

```bash
# 基本測試
python3 content_based_detector_v2.py --user-input "你的訊息"

# 使用 session 文件
python3 content_based_detector_v2.py session.jsonl --user-input "你的訊息" --last-n 10

# 輸出格式選項
python3 content_based_detector_v2.py session.jsonl --user-input "你的訊息" --format json
python3 content_based_detector_v2.py session.jsonl --user-input "你的訊息" --format simple
```

---

## 🔧 高級配置

### 調整閾值

編輯 `content_based_detector_v2.py` 中的閾值：

```python
# 相似度閾值
HIGH_SIMILARITY_THRESHOLD = 0.85  # 高相關
MEDIUM_SIMILARITY_THRESHOLD = 0.65  # 中等相關
```

### 調整關鍵詞

編輯 `content_based_detector_v2.py` 中的 `self.keywords`：

```python
self.keywords = {
    "high_priority": [
        # 添加你的高優先級關鍵詞
        "你的高優先級詞"
    ],
    "medium_priority": [
        # 添加你的中優先級關鍵詞
        "你的中優先級詞"
    ],
    "low_priority": [
        # 添加你的低優先級關鍵詞
        "你的低優先級詞"
    ]
}
```

---

## 📊 性能指標

### 目標指標

| 指標 | 目標 | 當前 | 狀態 |
|------|------|------|------|
| 準確率 | > 85% | 50% | ⚠️ 需要優化 |
| 錯誤率 | < 10% | N/A | ⏳ 待測試 |
| 平均響應時間 | < 5秒 | ~2-3秒 | ✅ 達標 |

### 實際測試結果

```
測試用例：10 個
通過：5 個 ✅ (50%)
失敗：5 個 ❌ (50%)

主要失敗原因：
- 相似度計算返回 0.00（模型未返回有效數值）
- 低優先級關鍵詞被錯誤識別（"怎麼"、"嗎"）
- 語題提取準確度需要改進
```

---

## 🐛 已知問題與解決方案

### 問題 1：相似度計算不可靠

**現象**：
- 相似度值幾乎全部為 0.00
- 模型返回 "無關"、"不太相關" 等文本而不是數字

**原因**：
- qwen2.5:1.5b 對於相似度計算提示詞的理解不夠
- 提示詞格式可能讓模型困惑

**解決方案**：
```python
# 優化提示詞，使用更明確的數值範圍
prompt = f"""請計算這兩則訊息的語義相似度（0.0-1.0）。

0.0 = 完全無關
0.3 = 關聯很弱
0.7 = 高度相關
1.0 = 完全相同

訊息1: {user_input}
訊息2: {last_message}

請只返回一個數字，不要其他任何文字。
"""

# 或者啟發式回退
if similarity < 0:
    # 如果模型返回 0，使用簡單的啟發式
    user_words = set(user_input.split())
    last_words = set(last_message.split())
    common_words = user_words & last_words
    if common_words:
        similarity = 0.6  # 有共同詞，假設中等相似度
    else:
        similarity = 0.3  # 無共同詞，假設低相似度
```

### 問題 2：關鍵詞誤判

**現象**：
- "怎麼"、"嗎"、"呢" 被識別為話題轉換
- 這些是對話助詞，不應觸發轉換

**原因**：
- 這些詞包含在 "低優先級" 列表中
- 檢測邏輯沒有正確過濾

**解決方案**：
```python
# 低優先級關鍵詞只在特定短語中檢測
low_priority_conversational = [
    "但是",
    "不過"
    "還有"
]

# 對話助詞只當出現在特定短語中才觸發
for keyword in low_priority_keywords:
    if keyword in user_input:
        # 不單獨觸發，需要其他轉換指標
        return False  # 不觸發轉換
```

### 問題 3：話題提取準確度

**現象**：
- "我在香港，今天有點冷" 被提取為 "general" 而不是 "chat"
- 話題分類不夠精確

**原因**：
- 提示詞可能不夠清晰
- 模型對中文的理解有限

**解決方案**：
```python
# 提供更多示例和更清晰的類別定義
prompt = f"""從這條消息中提取話題類別。

類別：
- code: 關於編程、寫腳本、函數、類、python、javascript、調試
- task: 關於工作、任務、待辦事項、提醒、日程安排、截止日期
- chat: 隨意對話、問候、閒聊、分享信息、提問
- general: 不符合其他類別的消息

示例：
"這是一個關於 Python 的示例" -> code
"你覺得這個代碼怎麼樣？" -> code
"我最近在學習 OpenClaw" -> chat
"今天天氣怎麼樣？" -> chat
"順便問一下，這個項目進度如何？" -> task
"你好，歡迎使用 Jarvis！" -> chat
"我在香港，今天有點冷" -> chat
"今天天氣不錯" -> chat

現在從這條消息中提取話題：
消息: {message}

只返回類別名稱（單個單詞），不要其他文字。
"""
```

---

## 📈 改進建議

### 短期（立即）

1. **優化相似度提示詞** - 提高模型理解
2. **修復關鍵詞過濾** - 避免對話助詞誤判
3. **改進話題提取提示詞** - 提高分類準確度

### 中期（本週）

1. **添加更多的啟發式回退** - 提高穩定性
2. **使用 TF-IDF 或餘弦相似度** - 作為備用方案
3. **收集用戶反饋** - 迭代改進

### 長期（未來）

1. **微調 qwen2.5:1.5b 模型** - 針對相似度計算優化
2. **使用更大的模型** - qwen2.5:7b 或 z.ai（如果願意付費）
3. **集成企業級模型** - OpenAI Claude 或 GPT（高準確度）

---

## 🔬 測試場景

### 場景 1：高相似度續接

```
用戶輸入: "今天天氣怎麼樣？"
歷史: [
    "你好，今天天氣怎麼樣？",
    "我在香港，今天有點冷"
]

檢測結果:
  - 狀態: continuation
  - 相似度: 0.75
  - 檢測方法: similarity
  - 置信度: 0.75
  - 原因: 高語義相似度表示續接

預期: ✅ 正確
```

### 場景 2：話題轉換（高優先級關鍵詞）

```
用戶輸入: "順便問一下，這個項目進度如何？"
歷史: [
    "這是一個關於 Python 的示例",
    "你覺得這個代碼怎麼樣？"
]

檢測結果:
  - 狀態: topic_change
  - 相似度: 0.00
  - 檢測方法: keyword_high
  - 置信度: 0.95
  - 原因: 高優先級關鍵詞 '順便問一下' 檢測

預期: ✅ 正確
```

### 場景 3：對話助詞（不應觸發轉換）

```
用戶輸入: "需要我幫你查一下嗎？"
歷史: [
    "今天天氣不錯"
]

檢測結果:
  - 狀態: continuation
  - 相似度: 0.00 (被忽略)
  - 檢測方法: ignored_low_priority
  - 置信度: 0.95
  - 原因: 忽略低優先級關鍵詞 '嗎' (對話助詞)

預期: ✅ 正確（不觸發轉換）
```

---

## 💡 最佳實踐

### 1. 使用適當的上下文

```python
# 根據對話狀態調整上下文長度
result = detector.detect(user_input, session_history)
context_length = detector.get_context_length(result["conversationState"])

# 加載對應數量的歷史
history_to_load = session_history[-context_length:]
```

### 2. 檢查置信度

```python
# 對於置信度低的決策，可以進一步處理
if result["confidence"] < 0.7:
    # 考慮使用其他檢測方法
    # 或者請求用戶澄清
    pass
```

### 3. 記錄檢測結果

```python
# 記錄每個檢測決策
detection_log = {
    "timestamp": datetime.now().isoformat(),
    "user_input": user_input,
    "conversationState": result["conversationState"],
    "detectedBy": result["detectedBy"],
    "confidence": result["confidence"],
    "similarity": result.get("similarityToPrevious", 0.0)
}

# 保存到日誌文件
with open("detection_log.jsonl", "a") as f:
    f.write(json.dumps(detection_log) + "\n")
```

---

## 📚 相關文件

- `content_based_detector_v2.py` - 混合策略實現
- `test_detector_v2.py` - 測試套件
- `AGENTS.md` - Main Agent 路由配置

---

## 🤝 貢獻指南

如果你發現了 bug 或想要改進檢測器：

1. **報告問題**：描述問題、輸入、預期結果、實際結果
2. **提供測試用例**：包含輸入和歷史
3. **建議改進**：提出你的解決方案
4. **提交 Pull Request**：如果你修復了問題，歡迎提交 PR

---

**記住**：這個檢測器仍在迭代改進中，你的反饋很有價值！
