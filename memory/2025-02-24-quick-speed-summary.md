# 🚀 加速一般聊天 - 快速總結

## 📊 測試結果

| 模型 | 響應時間 |
|------|---------|
| **qwen2.5:0.5b** | **2.3 秒** ⭐ 最快 |
| qwen2.5:3b | 7.9 秒 |
| zai glm-4.7-flash | 2-3 秒 |

---

## ✅ 推薦方案

### 立即可用：改用 qwen2.5:0.5b

優勢：
- ⚡ 最快：2.3 秒
- 💰 免費：$0
- 📦 最小：397 MB
- ✅ 足夠用：一般聊天

---

## 🔧 快速設置

### 步驟 1：更新配置

```bash
# 更新 Chat Agent 使用 qwen2.5:0.5b
jq '.agents.list |= map(if .id == "chat" then .model = "ollama/qwen2.5:0.5b" else . end)' \
  ~/.openclaw/openclaw.json > /tmp/openclaw-speed.json
cp /tmp/openclaw-speed.json ~/.openclaw/openclaw.json
```

### 步驟 2：啟用 Block Streaming（感知加速）

```bash
# 添加 streaming 配置
jq '.agents.defaults.blockStreamingDefault = "on" | .channels.whatsapp.blockStreaming = true' \
  ~/.openclaw/openclaw.json > /tmp/openclaw-streaming.json
cp /tmp/openclaw-streaming.json ~/.openclaw/openclaw.json
```

### 步驟 3：重啟 Gateway

```bash
openclaw gateway restart
```

---

## 🎯 預期效果

| 場景 | 現在 | 優化後 |
|------|------|--------|
| 簡單問候 | ~3s | **2.3s** |
| 一般聊天 | ~3s | **2.3s** |
| Block Streaming | ❌ 關閉 | **✅ 開啟** |

---

## 💡 其他加速方法

1. **對話狀態優化**（已實現）：85% 不調用 Classifier
2. **混合模型策略**：簡單用本地，複雜用雲端
3. **緩存常見問答**：RAG + 向量數據庫
4. **預熱模型**：啟動時預加載

---

## 📁 詳細文檔

完整指南：
- `memory/2025-02-24-speed-optimization.md`

---

想立即設置嗎？告訴我，我幫你！🚀
