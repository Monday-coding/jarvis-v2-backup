#!/bin/bash
# OpenClaw Multi-Agent 快速設置腳本（只有 Classifier 用 Ollama）

set -e

echo "🚀 OpenClaw Multi-Agent 快速設置（Classifier 用 Ollama，其他用雲端）"
echo "======================================================================"
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查 Ollama 是否安裝
check_ollama() {
    echo -n "📦 檢查 Ollama 安裝... "
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✓ 已安裝${NC}"
        ollama --version
        return 0
    else
        echo -e "${RED}✗ 未安裝${NC}"
        return 1
    fi
}

# 檢查 Ollama 服務是否運行
check_ollama_service() {
    echo -n "🔍 檢查 Ollama 服務... "
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo -e "${GREEN}✓ 運行中${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ 未運行${NC}"
        echo "提示: 執行 'ollama serve' 啟動服務"
        return 1
    fi
}

# 檢查模型是否已下載
check_model() {
    local model=$1
    echo -n "🤖 檢查模型 $model... "
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✓ 已下載${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ 未下載${NC}"
        return 1
    fi
}

# 下載模型
download_model() {
    local model=$1
    echo -n "⬇️  下載模型 $model... "
    if ollama pull "$model" &> /dev/null; then
        echo -e "${GREEN}✓ 完成${NC}"
        return 0
    else
        echo -e "${RED}✗ 失敗${NC}"
        return 1
    fi
}

# 檢查 OpenClaw 配置
check_openclaw_config() {
    echo -n "⚙️  檢查 OpenClaw 配置... "
    if [ -f ~/.openclaw/openclaw.json ]; then
        echo -e "${GREEN}✓ 存在${NC}"
        return 0
    else
        echo -e "${RED}✗ 不存在${NC}"
        return 1
    fi
}

# 備份現有配置
backup_config() {
    local backup_file="~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)"
    echo -n "💾 備份現有配置... "
    cp ~/.openclaw/openclaw.json "$backup_file"
    echo -e "${GREEN}✓ 已備份到 $backup_file${NC}"
}

# 合併配置
merge_config() {
    echo -n "🔧 合併配置... "
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' ~/.openclaw/openclaw.json ~/.openclaw/openclaw-multi-agent.json > /tmp/openclaw-merged.json
        cp /tmp/openclaw-merged.json ~/.openclaw/openclaw.json
        echo -e "${GREEN}✓ 完成${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ jq 未安裝，需要手動合併${NC}"
        echo ""
        echo "請執行以下步驟："
        echo "1. 編輯 ~/.openclaw/openclaw.json"
        echo "2. 添加 ollama provider"
        echo "3. 更新 classifier agent 使用 ollama/qwen2.5:1.5b"
        return 1
    fi
}

# 重啟 Gateway
restart_gateway() {
    echo -n "🔄 重啟 Gateway... "
    if openclaw gateway restart &> /dev/null; then
        echo -e "${GREEN}✓ 完成${NC}"
        return 0
    else
        echo -e "${RED}✗ 失敗${NC}"
        return 1
    fi
}

# 主流程
main() {
    # 檢查 Ollama
    if ! check_ollama; then
        echo ""
        echo -e "${RED}❌ 請先安裝 Ollama:${NC}"
        echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
        echo "  macOS: brew install ollama"
        echo ""
        exit 1
    fi

    # 檢查 Ollama 服務
    if ! check_ollama_service; then
        echo ""
        echo -e "${YELLOW}⚠ 請啟動 Ollama 服務:${NC}"
        echo "  ollama serve"
        echo ""
        read -p "是否現在啟動？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "啟動 Ollama 服務..."
            ollama serve &
            sleep 3
            check_ollama_service || exit 1
        else
            echo "已取消"
            exit 1
        fi
    fi

    # 檢查並下載模型
    echo ""
    echo "📦 檢查所需模型（僅用於 Classifier）:"
    MODEL="qwen2.5:1.5b"
    if ! check_model "$MODEL"; then
        echo "  ⬇️  正在下載 $MODEL..."
        download_model "$MODEL" || exit 1
    fi

    # 檢查 OpenClaw 配置
    echo ""
    check_openclaw_config || {
        echo -e "${RED}❌ OpenClaw 配置不存在，請先初始化 OpenClaw${NC}"
        exit 1
    }

    # 備份配置
    backup_config

    # 合併配置
    merge_config

    # 詢問是否重啟 Gateway
    echo ""
    read -p "是否重啟 Gateway？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_gateway
    else
        echo "請稍後手動重啟: openclaw gateway restart"
    fi

    # 完成提示
    echo ""
    echo -e "${GREEN}✅ 設置完成！${NC}"
    echo ""
    echo "📊 架構總覽:"
    echo "  ├─ Classifier: ollama qwen2.5:1.5b (本地，免費)"
    echo "  ├─ Main: zai glm-4.7 (雲端)"
    echo "  ├─ Chat: zai glm-4.7-flash (雲端)"
    echo "  ├─ Task: zai glm-4.7-flash (雲端)"
    echo "  ├─ Coding: zai glm-4.7 (雲端)"
    echo "  ├─ Data: zai glm-4.7-flash (雲端)"
    echo "  └─ QA: zai glm-4.7-flash (雲端)"
    echo ""
    echo "📋 下一步:"
    echo "1. 確認配置已正確合併到 ~/.openclaw/openclaw.json"
    echo "2. 檢查 Ollama 服務是否運行: curl http://localhost:11434/api/tags"
    echo "3. 重啟 Gateway: openclaw gateway restart"
    echo "4. 測試 Classifier Agent"
    echo ""
    echo "💰 成本分析:"
    echo "  - Classifier: $0 (本地)"
    echo "  - 其他 Agents: 雲端計費"
    echo "  - 假設每天調用 Classifier 100 次：每月節省 ~$18 🎉"
    echo ""
    echo "📚 更多信息請查看:"
    echo "  ~/.openclaw/workspace/MULTI-AGENT-SETUP.md"
}

# 執行主流程
main
