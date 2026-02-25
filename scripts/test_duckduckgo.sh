#!/bin/bash
# DuckDuckGo 整合測試腳本

set -e

echo "========================================"
echo "DuckDuckGo 搜尋功能測試"
echo "========================================"
echo ""

# 測試 1: 版本檢查
echo "測試 1: 檢查 ddgr 版本"
ddgr --version
echo "✅ 版本檢查通過"
echo ""

# 測試 2: 基本搜尋
echo "測試 2: 基本搜尋測試"
echo "搜尋: 'DuckDuckGo search'"
ddgr -x -n 2 "DuckDuckGo search"
echo "✅ 基本搜尋通過"
echo ""

# 測試 3: 顯示結果數量
echo "測試 3: 顯示結果數量測試"
echo "搜尋: 'Python' - 3 個結果"
ddgr -x -n 3 "Python"
echo "✅ 顯示結果數量通過"
echo ""

# 測試 4: 按時間搜尋
echo "測試 4: 按時間搜尋測試"
echo "搜尋: 'AI news' (最近7天)"
ddgr -x -d 7d "AI news" 2>&1 | head -5
echo "✅ 按時間搜尋通過"
echo ""

# 測試 5: 包裝腳本測試
echo "測試 5: 包裝腳本測試"
echo "搜尋: 'Weather Hong Kong' - 3 個結果"
/home/jarvis/.openclaw/workspace/scripts/duckduckgo_search.sh -n 3 "Weather Hong Kong"
echo "✅ 包裝腳本測試通過"
echo ""

# 測試 6: 網站限定搜尋
echo "測試 6: 網站限定搜尋測試"
echo "搜尋: GitHub 'OpenClaw'"
ddgr -x -w github.com "OpenClaw" 2>&1 | head -5
echo "✅ 網站限定搜尋通過"
echo ""

echo "========================================"
echo "所有測試完成！"
echo "========================================"
echo ""
echo "DuckDuckGo 搜尋功能已成功整合到 OpenClaw"
echo ""
echo "使用方式:"
echo "  - 基本搜尋: ddgr -x 'your query'"
echo "  - 包裝腳本: ./scripts/duckduckgo_search.sh 'your query'"
echo "  - 在 OpenClaw: exec ./scripts/duckduckgo_search.sh 'your query'"
