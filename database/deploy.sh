#!/usr/bin/env bash
# OpenClaw Data Agent - 完整部署腳本

echo "🐘 OpenClaw Data Agent - 完整部署"
echo ""

# 顏示步驟
steps=(
    "✅ 檢查 Docker 安裝"
    "✅ 檢查 Docker Compose"
    "✅ 創建工作區"
    "✅ 設置腳本權限"
    "✅ 啟動 Docker Compose"
    "✅ 初始化數據庫"
    "✅ 測試 Data Agent 連接"
    "✅ 顯示系統狀態"
)

# 執行步驟
for i in "${!steps[@]}"; do
    echo "$i"
    sleep 0.5
done

echo ""
echo "📋 部署清單"
echo ""

# 1. 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    echo "   安裝：curl -fsSL https://get.docker.com | sh"
    exit 1
fi
echo "✅ Docker 已安裝"

# 2. 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝"
    echo "   安裝：pip install docker-compose"
    exit 1
fi
echo "✅ Docker Compose 已安裝"

# 3. 創建工作區
DB_DIR="$HOME/.openclaw/workspace/database"
DATA_DIR="$HOME/.openclaw/workspace-data"

echo "✅ 工作區目錄："
echo "   數據庫：$DB_DIR"
echo "   Data Agent：$DATA_DIR"

mkdir -p "$DATA_DIR"
echo "✅ 工作區已創建"

# 4. 設置權限
chmod +x "$DATA_DIR/connector.py"
chmod +x "$DB_DIR/start.sh"
echo "✅ 腳本權限已設置"

# 5. 啟動服務
cd "$DB_DIR"
echo "🐘 啟動 Docker Compose..."
docker-compose up -d

# 6. 等待服務就緒
echo ""
echo "⏳ 等待服務就緒..."
sleep 5

# 檢查 PostgreSQL 是否就緒
for attempt in {1..30}; do
    if docker exec openclaw-postgres pg_isready -U openclaw &>/dev/null; then
        echo "✅ PostgreSQL 已就緒"
        break
    else
        echo -n "."
        sleep 1
done

echo ""

# 7. 初始化數據庫（如果未初始化）
echo "📊 初始化數據庫..."
if ! docker exec openclaw-postgres psql -U openclaw -d openclaw -c "SELECT 1 FROM agents;" &>/dev/null; then
    echo "   首次初始化..."
    docker exec -i openclaw-postgres psql -U openclaw -d openclaw < "$DB_DIR/init-sql.sql"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ 數據庫初始化成功"
    else
        echo "   ⚠️ 數據庫初始化失敗，請檢查日誌"
    fi
else
    echo "   ✅ 數據庫已初始化"
fi

echo ""

# 8. 測試 Data Agent 連接
echo "🧪 測試 Data Agent 連接..."
if [ -f "$DATA_DIR/connector.py" ]; then
    cd "$DATA_DIR"
    python3 connector.py test
else
    echo "   ❌ Data Agent 連接器未找到"
fi

echo ""

# 9. 顯示系統狀態
echo "📊 系統狀態"
echo ""
echo "📋 Docker 服務："
docker-compose ps

echo ""
echo "🌐 Web 界面："
echo "   PostgreSQL: http://localhost:5432"
echo "   pgAdmin: http://localhost:5050"
echo "   用戶：openclaw"
echo "   密碼：openclaw_password_2024"

echo ""
echo "📚 可用的腳本："
echo "   數據庫：cd $DB_DIR && ./start.sh"
echo "   Data Agent：cd $DATA_DIR && python3 connector.py [command]"
echo "   完整文檔：cd $DB_DIR && cat README.md"

echo ""
echo "🚀 部署完成！"
echo ""
echo "📝 下一步操作："
echo "   1. 訪問 pgAdmin：http://localhost:5050"
echo "   2. 測試連接：python3 workspace-data/connector.py test"
echo "   3. 查看 Agents：python3 workspace-data/connector.py agents"
echo "   4. 搜索知識庫：python3 workspace-data/connector.py kb-search 'Python'"
echo "   5. 查看日誌：docker-compose logs postgres | tail -50"
echo ""
echo "🎉 系統已就緒，開始使用！"
