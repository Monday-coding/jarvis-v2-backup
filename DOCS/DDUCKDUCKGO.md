# DuckDuckGo 搜尋引擎集成

## 功能概述

已成功集成 DuckDuckGo 搜尋引擎到 OpenClaw 工作流中，提供隐私保護的搜尋功能。

## 已安裝的工具

- **ddgr** (v2.2) - DuckDuckGo 命令行工具

## 使用方式

### 方式 1：直接使用 ddgr 命令

```bash
# 基本搜尋
ddgr -x "your search query"

# 顯示特定數量的結果
ddgr -x -n 5 "your search query"

# 按時間搜尋 (d=1天, w=1週, m=1月, y=1年)
ddgr -x -d 7d "your search query"

# 搜尋特定網站
ddgr -x -w example.com "search term"

# 新聞搜尋 (使用時間限制為0天)
ddgr -x -np --d 0d "latest AI news"
```

### 方式 2：使用包裝腳本

```bash
# 基本搜尋
./scripts/duckduckgo_search.sh "your search query"

# 顯示5個結果
./scripts/duckduckgo_search.sh -n 5 "your search query"

# 新聞搜尋
./scripts/duckduckgo_search.sh --news "AI latest news"

# 按時間搜尋 (7天內)
ddg-search.sh -d 7d "recent developments"
```

## OpenClaw 集成

在 OpenClaw 中使用 DuckDuckGo 搜尋：

```bash
# 調用搜尋腳本
exec /home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh -n 5 "your query"
```

或使用完整路徑：
```bash
./home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh "your query"
```

## 主要優勢

- 🎯 **隱私保護**：DuckDuckGo 不追蹤使用者
- 💰 **免費**：無需 API key
- ⚡ **快速**：本地執行，響應迅速
- 🔧 **易於整合**：簡單的 CLI 工具

## 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `-x` | 搜尋後退出 | `ddgr -x "query"` |
| `-n N` | 顯示 N 個結果 | `ddgr -x -n 5 "query"` |
| `-d SPAN` | 時間範圍 (d/w/m/y) | `ddgr -d 7d "query"` |
| `-w SITE` | 限定網站 | `ddgr -w github.com "query"` |
| `-np` | 不詢問直接執行 | `ddgr -x -np "query"` |
| `--news` | 新聞搜尋 | `ddgr -x --np --d 0d "news"` |

## 狀態

- ✅ ddgr 已安裝 (v2.2)
- ✅ 包裝腳本已創建並測試
- ✅ OpenClaw 整合就緒
- ✅ 文檔完成

## 相關資源

- [ddgr GitHub](https://github.com/jarun/ddgr)
- [DuckDuckGo API 文檔](https://duckduckgo.com/api)
- [命令行參數說明](https://github.com/jarun/ddgr#usage)

---

*最後更新：2026-02-25*
