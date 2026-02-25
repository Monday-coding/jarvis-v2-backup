# DuckDuckGo 搜尋範例

## 1. 基本搜尋

```bash
# 搜尋 Python 程式設計教程
ddgr -x "Python programming tutorial for beginners"

# 獲取3個結果
ddgr -x -n 3 "Hong Kong weather"
```

**輸出示例：**
```
1.  Python.org - The Python Software Foundation
    https://www.python.org/
2.  Learn Python - Free Interactive Tutorial
    https://www.learnpython.org/
3.  Python Tutorial - W3Schools
    https://www.w3schools.com/python/
```

## 2. 按時間搜尋

```bash
# 最近7天的結果
ddgr -x -d 7d "artificial intelligence breakthroughs"

# 最近30天的結果
ddgr -x -d 30d "web development trends"
```

## 3. 新聞搜尋

```bash
# 最新 AI 新聞
ddgr -x --np --d 0d "artificial intelligence news"

# 最近科技新聞
ddgr -x --np --d 0d "technology news today"
```

## 4. 限定網站搜尋

```bash
# 只搜尋 GitHub
ddgr -x -w github.com "OpenClaw documentation"

# 只搜尋 Reddit
ddgr -x -w reddit.com "r programming"
```

## 5. 結合包裝腳本

```bash
# 基本使用
./scripts/duckduckgo_search.sh "your query"

# 顯示5個結果
./scripts/duckduckgo_search.sh -n 5 "your query"

# 新聞搜尋
./scripts/duckduckgo_search.sh --news "latest technology news"

# 按時間搜尋
./scripts/duckduckgo_search.sh -d 7d "recent developments"
```

## 6. 在 OpenClaw 中使用

### 在對話中使用

```bash
# 使用搜尋腳本
exec /home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh -n 5 "Hong Kong weather"
```

### 在腳本中集成

```bash
#!/bin/bash
# script.sh

QUERY="$1"
RESULTS=${2:-10}

echo "正在使用 DuckDuckGo 搜尋: $QUERY"
/home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh -n "$RESULTS" "$QUERY"
```

### 在 Git hooks 中使用

```bash
# pre-commit hook
#!/bin/bash
# 搜尋最佳實踐
exec /home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh -n 3 "git best practices"
```

## 7. 高級用法

### 結合 grep 篩選結果

```bash
ddgr -x -n 10 "Python OR JavaScript" 2>&1 | grep -i "tutorial"
```

### 與 jq 整合 (JSON 格式)

```bash
ddgr -x -j "OpenClaw" 2>&1 | jq '.'
```

### 自定義 URL 處理器

```bash
# 使用自定義腳本打開結果
ddgr -x -p /path/to/open_url.sh "your query"
```

## 8. 常見使用場景

### 技術問題搜尋

```bash
# 搜尋特定錯誤解決方案
ddgr -x -n 5 "npm install error EACCES"
```

### 學習資源

```bash
# 搜尋學習資源
ddgr -x -n 10 "learning React for beginners"
```

### 產品比較

```bash
# 比較兩個產品
ddgr -x -n 5 "DuckDuckGo vs Google privacy"
```

### 程式碼範例

```bash
# 搜尋程式碼範例
ddgr -x -w stackoverflow.com "Python file read"
```

---

*這些範例可以幫助你快速開始使用 DuckDuckGo 搜尋功能。*
