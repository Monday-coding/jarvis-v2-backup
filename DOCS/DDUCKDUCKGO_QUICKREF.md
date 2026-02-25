# DuckDuckGo 快速參考

## 快速開始

### 最簡單用法
```bash
ddgr -x "your query"
```

### 包裝腳本
```bash
./scripts/duckduckgo_search.sh "your query"
```

## 常用命令

### 顯示結果
```bash
# 顯示 5 個結果
ddgr -x -n 5 "query"

# 顯示 10 個結果 (預設)
ddgr -x "query"
```

### 按時間搜尋
```bash
# 最近 1 天
ddgr -d 1d "query"

# 最近 1 週
ddgr -d 1w "query"

# 最近 1 個月
ddgr -d 1m "query"

# 最近 1 年
ddgr -d 1y "query"

# 自定義時間範圍
ddgr -d 7d "query"  # 7 天
```

### 新聞搜尋
```bash
# 最新新聞
ddgr -x --np --d 0d "AI news"
```

### 限定網站
```bash
# 在 GitHub 上搜尋
ddgr -x -w github.com "OpenClaw"

# 在 Reddit 上搜尋
ddgr -x -w reddit.com "r programming"
```

## 在 OpenClaw 中使用

### 直接執行
```bash
exec /home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh "query"
```

### 響應用戶問題
```
User: 帮我搜尋 Hong Kong 天氣
Agent: exec ./scripts/duckduckgo_search.sh "Hong Kong weather"
```

## 輸出格式

```
1.  結果標題
    URL

    簡短描述...
```

## 快捷鍵 (在 ddgr 中)

- `n/p`: 下一頁/上一頁
- `x`: 切換 URL 顯示
- `d index`: 在瀏覽器打開特定結果
- `q`: 退出

## 選項完整列表

```
-h, --help            顯示幫助
-n, --num N           顯示 N 個結果 (0-25)
-r, --reg REG         區域搜尋
-d, --time SPAN       時間範圍 (d/w/m/y)
-w, --site SITE       限定網站
-x, --expand          顯示完整 URL
-j, --ducky           在瀏覽器打開第一個結果
-C, --nocolor         關閉顏色
-p, --proxy URI       代理設定
--news                新聞搜尋
--json                JSON 輸出
```

## 與 Brave Search 比較

| 功能 | DuckDuckGo | Brave Search |
|------|------------|--------------|
| 隱私保護 | ✅ 100% | ✅ 高 |
| API Key | ❌ 不需要 | ✅ 需要 |
| 需要網路 | ✅ 是 | ✅ 是 |
| 成本 | 💰 免費 | 💰 需付費 |
| 反饋速度 | ⚡ 快 | ⚡ 快 |
| 個性化 | ❌ 否 | ✅ 是 |

## 故障排除

### 無法執行
```bash
# 檢查是否安裝
which ddgr

# 如果沒有，重新安裝
brew install ddgr
```

### 結果少於預期
```bash
# 增加 NUM 值
ddgr -x -n 25 "query"
```

### 想要更多功能
```bash
# 查看完整幫助
ddgr -h
```

---

**記住:** DuckDuckGo 是你的隱私保護搜尋引擎選擇！
