# 🎯 OpenClaw Multi-Agent 架構設置總結（只有 Classifier 用 Ollama）

## 📊 架構概覽

```
┌─────────────────────────────────────────────────────────┐
│                    User (WhatsApp)                       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Main Agent (zai/glm-4.7)                    │
│  - 對話狀態檢測                                          │
│  - 簡單意圖判斷                                          │
│  - 路由決策                                              │
└─────────────────────────────────────────────────────────┘
                           ↓
                   ┌───────────────┐
                   │  Manager      │
                   │  (決策)        │
                   └───────────────┘
                           ↓
        ┌──────────┬──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓          ↓
   Classifier  Chat      Task      Coding     Data
  (ollama)   (zai)     (zai)     (zai)      (zai)
  qwen2.5:   glm-4.7-  glm-4.7-  glm-4.7    glm-4.7-
   1.5b     flash     flash               flash
        │          │          │          │          │
        └──────────┴──────────┴──────────┴──────────┘
                           ↓
                       QA Agent
                   (zai glm-4.7-flash)
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Chat Agent (zai glm-4.7-flash)              │
│              生成友好回應                                  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    User (WhatsApp)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ 完整設置清單

### 步驟 1：安裝 Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama
```

### 步驟 2：下載 qwen2.5:1.5b 模型

```bash
# 只下載這一個模型（用於 Classifier）
ollama pull qwen2.5:1.5b

# 驗證
ollama list
```

### 步驟 3：啟動 Ollama 服務

```bash
# 方式 1：直接啟動（終端會占用）
ollama serve

# 方式 2：後台啟動（推薦）
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 方式 3：使用 systemd（持久化）
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 步驟 4：合併配置

```bash
# 使用 jq 合併配置（需要安裝 jq）
jq -s '.[0] * .[1]' \
  ~/.openclaw/openclaw.json \
  ~/.openclaw/openclaw-multi-agent.json \
  > /tmp/openclaw-merged.json

cp /tmp/openclaw-merged.json ~/.openclaw/openclaw.json
```

**或者手動合併：**

打開 `~/.openclaw/openclaw.json`，添加/修改：

1. **添加 ollama provider**（在 `models.providers` 下）
2. **更新 classifier agent** 使用 `ollama/qwen2.5:1.5b`
3. **其他 agents 保持使用 zai**（glm-4.7 或 glm-4.7-flash）

### 步驟 5：重啟 Gateway

```bash
openclaw gateway restart
```

### 步驟 6：測試

```bash
# 檢查 Gateway 狀態
openclaw status

# 檢查 Ollama 服務
curl http://localhost:11434/api/tags

# 在 WhatsApp 測試
/test classify 幫我寫個 Python 腳本
```

---

## 📋 Agent 配置總覽

| Agent | 模型 | Provider | 用途 | 工具權限 |
|-------|------|----------|------|----------|
| **Main** | glm-4.7 | zai | Orchestrator | 全部（除 gateway） |
| **Classifier** | qwen2.5:1.5b | ollama ✅ | 意圖分類 | 只讀 |
| **Chat** | glm-4.7-flash | zai | 對話生成 | 只讀 + web_search |
| **Task** | glm-4.7-flash | zai | 任務執行 | 读写 + exec + message |
| **Coding** | glm-4.7 | zai | 代碼生成 | 读写 + exec（沙箱） |
| **Data** | glm-4.7-flash | zai | 數據查詢 | 只讀 + exec |
| **QA** | glm-4.7-flash | zai | 質量檢查 | 只讀 |

---

## 💰 成本分析

### 假設每天調用次數

| Agent | 每天調用 | 每次平均 tokens | 模型 | 成本/天 |
|-------|---------|----------------|------|---------|
| Classifier | 100 | 200 | ollama qwen2.5:1.5b | **$0** ✅ |
| Chat | 500 | 300 | zai glm-4.7-flash | ~$0.15 |
| Task | 50 | 400 | zai glm-4.7-flash | ~$0.02 |
| Coding | 20 | 1000 | zai glm-4.7 | ~$0.06 |
| Data | 30 | 500 | zai glm-4.7-flash | ~$0.015 |
| QA | 50 | 300 | zai glm-4.7-flash | ~$0.015 |
| **總計** | **750** | - | - | **~$0.26/天** |

### 對比全雲端方案

**全部使用 zai glm-4.7-flash：**
- 每天成本：~$0.26（與現在相同）
- Classifier 部分節省：每天 ~$0.06
- **每月節省**：**~$1.8**
- **每年節省**：**~$21.6**

**全部使用 zai glm-4.7：**
- 每天成本：~$0.39
- Classifier 部分節省：每天 ~$0.19
- **每月節省**：**~$5.7** 🎉
- **每年節省**：**~$68.4** 🎉

---

## 🚀 快速設置腳本

```bash
# 執行快速設置腳本
~/.openclaw/workspace/setup-multi-agent-ollama.sh
```

腳本會自動：
1. ✅ 檢查 Ollama 安裝
2. ✅ 檢查/下載 qwen2.5:1.5b 模型
3. ✅ 備份現有配置
4. ✅ 合併配置
5. ✅ 重啟 Gateway

---

## 📁 文件結構

```
~/.openclaw/
├── openclaw.json                          # 主配置文件（需合併）
├── openclaw-multi-agent.json              # Multi-Agent 配置模板
├── workspace/
│   ├── setup-multi-agent-ollama.sh         # 快速設置腳本
│   └── MULTI-AGENT-SETUP.md               # 總結文檔
├── memory/
│   ├── 2025-02-24-multi-agent-research.md  # Multi-Agent 研究文檔
│   ├── 2025-02-24-openclaw-multi-agent-flow.md  # 流程說明
│   ├── 2025-02-24-conversation-state.md   # 對話狀態管理
│   └── 2025-02-24-ollama-setup.md         # Ollama 設置指南
└── workspace-{classifier,chat,task,coding,data,qa}/
    └── {AGENTS.md, SOUL.md, IDENTITY.md, TOOLS.md}
```

---

## 🎯 對話狀態檢測策略

### Main Agent 決策樹

```
User Input
    │
    ├─→ 新 session？ → 調用 Classifier ✅ (ollama，免費)
    ├─→ 換題目（"另外"、"順便問"）？→ 調用 Classifier ✅ (ollama，免費)
    ├─→ 繼續對話（語義相似度 > 0.7）？→ 延續當前 Agent ❌
    ├─→ 簡單回應（ok/thanks）？→ 直接回應 ❌
    └─→ 複雜/不明確？→ 調用 Classifier ✅ (ollama，免費)
```

### 成本優化

| 場景 | 比例 | 是否調用 Classifier | 成本 |
|------|------|-------------------|------|
| 繼續對話 | 70% | ❌ 不調用 | $0 |
| 簡單回應 | 15% | ❌ 不調用 | $0 |
| 換題目 | 10% | ✅ 調用（本地，免費） | $0 |
| 新對話 | 5% | ✅ 調用（本地，免費） | $0 |

**Classifier 總成本**：**$0** 🎉

---

## 🔍 故障排除

### 問題 1：Ollama 無法連接

```bash
# 檢查服務狀態
ps aux | grep ollama

# 測試連接
curl http://localhost:11434/api/tags

# 重新啟動
pkill ollama
ollama serve &
```

### 問題 2：模型未找到

```bash
# 列出已安裝模型
ollama list

# 下載模型
ollama pull qwen2.5:1.5b
```

### 問題 3：Gateway 無法啟動

```bash
# 檢查配置語法
cat ~/.openclaw/openclaw.json | jq .

# 查看日誌
openclaw gateway logs

# 重新加載配置
openclaw gateway restart
```

---

## 📚 參考文檔

- ✅ `memory/2025-02-24-multi-agent-research.md` - Multi-Agent 理論
- ✅ `memory/2025-02-24-openclaw-multi-agent-flow.md` - 流程說明
- ✅ `memory/2025-02-24-conversation-state.md` - 對話狀態管理
- ✅ `memory/2025-02-24-ollama-setup.md` - Ollama 詳細設置
- ✅ `workspace-classifier/AGENTS.md` - Classifier 配置
- ✅ `workspace-*/AGENTS.md` - 其他 Agents 配置

---

## 🎉 設置完成後

### 測試流程

1. **測試 Classifier (Ollama)**
   ```
   /test classify 幫我寫個 Python 腳本
   ```
   應該返回：`{"intent": "code", ...}`
   - 速度應該比雲端快（本地運行）
   - 成本為 $0

2. **測試完整流程**
   ```
   幫我寫個 Python 腳本分析 CSV 文件
   ```
   應該：
   - Classifier 分類（ollama qwen2.5:1.5b）→ 本地免費
   - Coding Agent 生成腳本（zai glm-4.7）→ 雲端
   - QA Agent 檢查（zai glm-4.7-flash）→ 雲端
   - Chat Agent 生成回應（zai glm-4.7-flash）→ 雲端

3. **檢查對話狀態**
   ```
   再詳細點
   ```
   應該：
   - 延續 Coding Agent
   - 不調用 Classifier

---

## 🚀 下一步優化

1. **性能優化**
   - 調整 ollama 並發數
   - 優化模型溫度參數
   - 調整上下文窗口大小

2. **功能擴展**
   - 添加更多專門化 Agents
   - 實現並行執行
   - 添加 Agent 間消息隊列

3. **監控和日誌**
   - 設置性能監控
   - 添加詳細日誌
   - 實現成本追蹤

---

## 📊 總結

✅ **只有 Classifier 使用 Ollama**（qwen2.5:1.5b）
✅ **其他 Agents 全部使用雲端**（zai glm-4.7 / glm-4.7-flash）
✅ **Classifier 成本為 $0**（本地運行）
✅ **對話狀態優化**（85% 不調用 Classifier）
✅ **性能與成本的平衡**

---

**祝你使用愉快！🎉**

有任何問題，隨時查閱文檔或問我！
