#!/bin/bash
# 壓力測試腳本
# 測試系統在連續請求下的穩定性和響應時間

set -e

# 配置
REQUESTS=50
DELAY=0.1
LOG_FILE="stress_test_$(date '+%Y%m%d_%H%M%S').log"

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "壓力測試開始"
echo "=========================================="
echo "請求數量: $REQUESTS"
echo "請求間隔: ${DELAY}s"
echo "日誌文件: $LOG_FILE"
echo ""

# 初始化統計
total_time=0
success_count=0
error_count=0
min_time=99999
max_time=0

# 執行測試
for i in $(seq 1 $REQUESTS); do
    echo -n "[$i/$REQUESTS] 測試中..."

    # 開始計時
    start_time=$(date +%s.%N)

    # 發送請求（測試本地模型）
    response=$(curl -s -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"qwen2.5:0.5b\",\"prompt\":\"你好\",\"stream\":false,\"options\":{\"num_predict\":10}}" \
        2>&1)

    # 結束計時
    end_time=$(date +%s.%N)
    elapsed_time=$(echo "$end_time - $start_time" | bc)

    # 檢查是否成功
    if echo "$response" | jq -e '.response' > /dev/null 2>&1; then
        success_count=$((success_count + 1))
        total_time=$(echo "$total_time + $elapsed_time" | bc)

        # 更新最小/最大時間
        if (( $(echo "$elapsed_time < $min_time" | bc -l) )); then
            min_time=$elapsed_time
        fi
        if (( $(echo "$elapsed_time > $max_time" | bc -l) )); then
            max_time=$elapsed_time
        fi

        echo -e " ${GREEN}✓${NC} (${elapsed_time}s)"
    else
        error_count=$((error_count + 1))
        echo -e " ${RED}✗${NC} 錯誤"

        # 記錄錯誤
        echo "[$i] 錯誤: $response" >> "$LOG_FILE"
    fi

    # 記錄日誌
    echo "[$i] 時間: ${elapsed_time}s, 成功: $success_count, 失敗: $error_count" >> "$LOG_FILE"

    # 延遲
    sleep $DELAY
done

# 計算統計
if [ $success_count -gt 0 ]; then
    avg_time=$(echo "scale=3; $total_time / $success_count" | bc)
else
    avg_time=0
fi

success_rate=$(echo "scale=2; $success_count * 100 / $REQUESTS" | bc)

echo ""
echo "=========================================="
echo "測試完成"
echo "=========================================="
echo "總請求數: $REQUESTS"
echo "成功: $success_count (${GREEN}${success_rate}%${NC})"
echo "失敗: $error_count"
echo ""
echo "響應時間統計："
echo "  平均: ${avg_time}s"
echo "  最小: ${min_time}s"
echo "  最大: ${max_time}s"
echo ""
echo "日誌已保存到: $LOG_FILE"
echo ""

# 評估
if (( $(echo "$success_rate >= 95" | bc -l) )); then
    echo -e "${GREEN}✓ 系統穩定性優秀（成功率 >= 95%）${NC}"
elif (( $(echo "$success_rate >= 90" | bc -l) )); then
    echo -e "${YELLOW}⚠ 系統穩定性良好（成功率 >= 90%）${NC}"
else
    echo -e "${RED}✗ 系統穩定性需要改進（成功率 < 90%）${NC}"
fi
