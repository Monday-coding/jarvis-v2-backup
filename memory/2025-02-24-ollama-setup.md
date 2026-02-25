# Ollama + OpenClaw 設置指南

## 📋 概述

- **目的**：使用本地 ollama 運行 qwen2.5:1.5b 做 Classifier Agent
- **優點**：
  - ✅ 零 API 費用
  - ✅ 低延遲（本地運行）
  - ✅ 隱私安全（數據不出本機）
  - ✅ qwen2.5:1.5b 對分類任務夠用

---

## 🔧 步驟 1：安裝 Ollama

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS
```bash
brew install ollama
```

### 驗證安裝
```bash
ollama --version
# 應該看到類似：ollama version is 0.5.7
```

---

## 🤖 步驟 2：下載 Qwen2.5:1.5b 模型

```bash
ollama pull qwen2.5:1.5b
```

### 測試模型
```bash
ollama run qwen2.5:1.5b "你好"
```

---

## ⚙️ 步驟 3：配置 OpenClaw 使用 Ollama

### 方案 A：添加 Ollama 到配置（推薦）

編輯 `~/.openclaw/openclaw.json`，添加 ollama provider：

```json5
{
  models: {
    mode: "merge",
    providers: {
      // 現有的 zai provider...
      "zai": {
        // ... 保留
      },

      // 新增 ollama provider
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "api": "openai-completions",  // 使用 OpenAI 兼容接口
        "models": [
          {
            "id": "qwen2.5:1.5b",
            "name": "Qwen 2.5 1.5B",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 32768,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

### 方案 B：環境變量設置（快速測試）

```bash
# 設置默認 provider
export OPENCLAW_DEFAULT_PROVIDER=ollama
export OPENCLAW_OLLAMA_BASE_URL=http://localhost:11434

# 重啟 Gateway
openclaw gateway restart
```

---

## 🎯 步驟 4：更新 Classifier Agent 配置

更新 `~/.openclaw/openclaw.json` 中的 classifier agent：

```json5
{
  agents: {
    list: [
      // ... 其他 agents ...
      {
        "id": "classifier",
        "name": "Classifier (意圖分類)",
        "workspace": "~/.openclaw/workspace-classifier",
        "agentDir": "~/.openclaw/agents/classifier/agent",
        "model": "ollama/qwen2.5:1.5b",  // 使用 ollama 的 qwen2.5:1.5b
        "sandbox": {
          "mode": "all",
          "scope": "shared"
        },
        "tools": {
          "allow": ["read", "memory_search", "memory_get"],
          "deny": ["exec", "write", "edit", "message", "sessions_spawn", "web_search", "web_fetch"]
        }
      }
    ]
  }
}
```

---

## 🔄 步驟 5：重啟 Gateway

```bash
openclaw gateway restart
```

---

## 🧪 步驟 6：測試

### 測試 1：檢查模型列表

```bash
openclaw status
```

應該看到 ollama/qwen2.5:1.5b 在模型列表中。

### 測試 2：手動測試 Classifier

在 WhatsApp 發送：
```
/test classify 幫我寫個 Python 腳本
```

應該返回：
```json
{
  "intent": "code",
  "confidence": 0.92,
  // ...
}
```

---

## ⚠️ 注意事項

### 性能考慮

| 配置 | 上下文窗口 | 最大輸出 | 適用場景 |
|------|-----------|---------|---------|
| qwen2.5:1.5b | 32K | 8K | 簡單分類、意圖識別 |
| qwen2.5:3b | 32K | 8K | 中等複雜度 |
| qwen2.5:7b | 32K | 8K | 複雜分類 |

**推薦**：
- Classifier：qwen2.5:1.5b ✅（分類任務夠用）
- Chat：qwen2.5:3b 或 zai/glm-4.7-flash
- Coding：zai/glm-4.7（需要更強推理）
- Data：qwen2.5:3b

### 系統資源

運行 ollama + qwen2.5:1.5b 需要：
- CPU：任何現代 CPU 都可以
- 內存：約 2GB（1.5B 參數）
- 磁盤：約 1GB（模型文件）

### 並發處理

Ollama 默認支持多個並行請求。如果需要更多並發：

```bash
# 設置 OLLAMA_NUM_PARALLEL
export OLLAMA_NUM_PARALLEL=4
```

---

## 🔍 故障排除

### 問題 1：無法連接到 Ollama

```bash
# 檢查 Ollama 是否運行
ps aux | grep ollama

# 啟動 Ollama
ollama serve
```

### 問題 2：模型未找到

```bash
# 列出已安裝的模型
ollama list

# 下載模型
ollama pull qwen2.5:1.5b
```

### 問題 3：API 請求失敗

```bash
# 測試 API 端點
curl http://localhost:11434/api/tags

# 應該看到 JSON 響應，包含已安裝的模型
```

---

## 📊 成本對比

| 方案 | 每千 token 成本 | 延遲 | 隱私 |
|------|---------------|------|------|
| ollama qwen2.5:1.5b | $0 | 低（本地） | 高（不出本機） |
| zai glm-4.7-flash | ~$0.001 | 中 | 中 |
| zai glm-4.7 | ~$0.003 | 中 | 中 |

**假設每天調用 Classifier 1000 次，每次 200 tokens：**

- ollama：$0/天
- zai glm-4.7-flash：$0.2/天
- zai glm-4.7：$0.6/天

**每月節省**：~$6-18 🎉

---

## 🚀 進階：多模型混用

可以讓不同的 Agent 使用不同的模型：

```json5
{
  agents: {
    list: [
      {
        "id": "classifier",
        "model": "ollama/qwen2.5:1.5b",  // 本地，快速，免費
      },
      {
        "id": "chat",
        "model": "ollama/qwen2.5:3b",  // 本地，平衡
      },
      {
        "id": "coding",
        "model": "zai/glm-4.7",  // 雲端，強推理
      },
      {
        "id": "data",
        "model": "ollama/qwen2.5:3b",  // 本地，平衡
      }
    ]
  }
}
```

---

## 📝 配置檢查清單

- [ ] Ollama 已安裝
- [ ] qwen2.5:1.5b 已下載
- [ ] ollama service 正在運行
- [ ] openclaw.json 已添加 ollama provider
- [ ] classifier agent 已設置使用 ollama/qwen2.5:1.5b
- [ ] Gateway 已重啟
- [ ] 測試分類功能正常
- [ ] 檢查延遲和性能
