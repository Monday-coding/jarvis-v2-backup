#!/bin/bash
# 啟動 PostgreSQL 數據庫

echo "🐘 啟動 OpenClaw PostgreSQL 數據庫"
echo ""

# 檢查 Docker 是否運行
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    echo "   請先安裝 Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

# 進入數據庫目錄
cd ~/.openclaw/workspace/database || exit 1

# 創建必要的目錄
mkdir -p backups

echo "📊 啟動 Docker Compose..."
echo ""

# 停止現有容器
docker-compose down 2>/dev/null

# 啟動服務
docker-compose up -d

echo ""
echo "✅ Docker Compose 已啟動"
echo ""

# 等待服務就緒
echo "⏳ 等待 PostgreSQL 就緒..."

# 等待 PostgreSQL 就緒（最多 30 秒）
for i in {1..30}; do
    if docker exec openclaw-postgres pg_isready -U openclaw &>/dev/null; then
        echo "✅ PostgreSQL 已就緒"
        echo ""
        
        # 檢查連接
        docker exec openclaw-postgres psql -U openclaw -d openclaw -c "SELECT 1;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ 數據庫連接成功"
            echo ""
            echo "📊 服務狀態："
            echo "  - PostgreSQL: http://localhost:5432"
            echo "  - pgAdmin: http://localhost:5050"
            echo "  - Redis: redis://localhost:6379"
            echo ""
            echo "📋 可用的腳本："
            echo "  - python3 pg_connector.py [命令]"
            echo "  - python3 rag_integration.py [命令]"
            echo ""
            echo "🚀 可以開始使用數據庫了！"
        else
            echo "❌ 數據庫連接失敗"
        fi
        
        break
    else
        echo -n "."
        sleep 1
done

echo ""
echo "⚠️  30 秒後仍未就緒，請檢查 Docker 日誌"
echo "   查看：docker-compose logs"
echo ""
