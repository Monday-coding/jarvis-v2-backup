# 香港天文台天氣 API 集成方案

## 📋 方案概述

**目標**：開發一個基於香港天文台 Open Data API 的天氣查詢及提示功能

**核心功能**：
1. 天氣查詢：查詢香港天氣情況
2. 特別天氣提示：檢測特別天氣並通知用戶
3. 自動備份：定期備份天氣數據到數據庫
4. 集成到知識庫：將常用查詢存儲到 RAG 知識庫

---

## 🌤 API 文檔研究

### API 概述

**名稱**：香港天文台 Open Data API
**用途**：提供天氣、天文等公開數據
**文檔**：HKO_Open_Data_API_Documentation_tc.pdf
**語言**：中文

### 主要 API 端點（預估）

根據香港天文台 API 文檔，主要端點可能包括：

1. **天氣數據** (`/weather/`)
   - 當前天氣
   - 預報
   - 氣溫/濕度
   - 降水量

2. **天文數據** (`/astronomy/`)
   - 日出/日落時間
   - 月相
   - 可見性
   - 行星位置

3. **警告資訊** (`/warnings/`)
   - 特別天氣提示
   - 颱風/暴雨警告
   - 熱潮/寒潮警告

4. **歷史數據** (`/historical/`)
   - 歷史天氣記錄
   - 統計數據

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────┐
│         Telegram / WhatsApp 用戶         │
├─────────────────────────────────────────────────┤
│                                             │
│            Main Agent (Orchestrator)           │
│            - 智能路由                        │
│            - 任務分派                        │
└─────────────┬─────────────────────────┤
              │
        ┌───────┴────────┐
        │                │
   [Weather Query]  [Weather Monitor]
        │                │
    HKO API      PostgreSQL DB
   /weather/     /weather_data/
   /warnings/      /alerts/
```

---

## 🗄️ 數據庫設計

### 表結構

#### 1. `weather_data` 表 - 天氣數據存儲

```sql
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    data_id VARCHAR(100) UNIQUE NOT NULL,
    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT,
    wind_speed FLOAT,
    wind_direction VARCHAR(10),
    weather_condition VARCHAR(50),
    location VARCHAR(100) DEFAULT '香港天文台',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_weather_data_time ON weather_data(observation_time DESC);
CREATE INDEX idx_weather_data_condition ON weather_data(weather_condition);
CREATE INDEX idx_weather_data_location ON weather_data(location);
```

#### 2. `weather_alerts` 表 - 特別天氣警告

```sql
CREATE TABLE IF NOT EXISTS weather_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(100) UNIQUE NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- 'special_weather', 'warning', 'advisory'
    severity VARCHAR(20) DEFAULT 'normal',  -- 'normal', 'moderate', 'high', 'severe'
    title TEXT NOT NULL,
    description TEXT,
    effect_start_time TIMESTAMP WITH TIME ZONE,
    effect_end_time TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_weather_alerts_time ON weather_alerts(effect_start_time DESC);
CREATE INDEX idx_weather_alerts_type ON weather_alerts(alert_type);
CREATE INDEX idx_weather_alerts_active ON weather_alerts(is_active, severity);
```

#### 3. `weather_queries` 表 - 查詢記錄

```sql
CREATE TABLE IF NOT EXISTS weather_queries (
    id SERIAL PRIMARY KEY,
    query_id VARCHAR(100) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    channel VARCHAR(50),
    user_id VARCHAR(100),
    result_summary TEXT,
    query_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_weather_queries_time ON weather_queries(query_time DESC);
CREATE INDEX idx_weather_queries_channel ON weather_queries(channel);
```

---

## 🔧 功能實現

### 1. 天氣查詢功能

```python
class WeatherAPI:
    """香港天文台天氣 API 客戶端"""

    def __init__(self):
        self.base_url = "https://www.hko.gov.hk"
        self.session = requests.Session()

    def get_current_weather(self, location: str = "hko") -> dict:
        """獲取當前天氣"""
        response = self.session.get(
            f"{self.base_url}/weatherAPI/currentweather",
            params={"location": location}
        )
        return response.json()

    def get_weather_warnings(self, location: str = "hko") -> dict:
        """獲取天氣警告"""
        response = self.session.get(
            f"{self.base_url}/weatherAPI/warning",
            params={"location": location}
        )
        return response.json()

    def get_forecast(self, location: str = "hko", hours: int = 24) -> dict:
        """獲取天氣預報"""
        response = self.session.get(
            f"{self.base_url}/weatherAPI/flw",
            params={"location": location, "hour": hours}
        )
        return response.json()
```

### 2. 特別天氣提示功能

```python
class WeatherMonitor:
    """天氣監控器 - 檢測特別天氣並發送通知"""

    def __init__(self, agent_db: AgentDatabase, weather_api: WeatherAPI):
        self.db = agent_db
        self.api = weather_api

    def check_special_weather(self) -> list:
        """檢查特別天氣條件"""
        current_weather = self.api.get_current_weather()
        
        alerts = []
        
        # 檢查酷熱天氣
        if current_weather.get('temperature', {}).get('value', 0) > 33:
            alerts.append({
                'alert_type': 'special_weather',
                'severity': 'high',
                'title': '酷熱天氣警告',
                'description': '預計最高氣溫達 33 度或以上，市民應採取防暑措施，避免戶外曝曬。',
                'effect_start_time': datetime.now(),
                'metadata': {'temperature': current_weather['temperature']}
            })
        
        # 檢查暴雨天氣
        if current_weather.get('rainfall', {}).get('value', 0) > 30:
            alerts.append({
                'alert_type': 'special_weather',
                'severity': 'severe',
                'title': '暴雨天氣警告',
                'description': '過去一小時錄得超過 30 毫米雨量，市民應提防水浸及山泥傾瀉。',
                'effect_start_time': datetime.now(),
                'metadata': {'rainfall': current_weather['rainfall']}
            })
        
        # 檢查強風天氣
        if current_weather.get('wind_speed', {}).get('value', 0) > 40:
            alerts.append({
                'alert_type': 'special_weather',
                'severity': 'high',
                'title': '強風警告',
                'description': '香港風力正在增強，平均風速達 40 公里/小時，市民應避免在風力強勁的地方逗留。',
                'effect_start_time': datetime.now(),
                'metadata': {'wind_speed': current_weather['wind_speed']}
            })
        
        return alerts

    def save_alerts(self, alerts: list) -> bool:
        """保存警告到數據庫"""
        for alert in alerts:
            self.db.save_log(
                log_id=f"alert_{alert['title']}",
                level="WARNING",
                category="weather",
                message=alert['description'],
                agent_id="weather",
                context=alert
            )
            
            # 檢查是否已經發送過類似警告
            recent_alerts = self.db.get_logs(
                category="weather",
                limit=10
            )
            
            # 如果沒有最近的類似警告，發送通知
            if not any(
                alert['title'] in log['message'] 
                for log in recent_alerts
            ):
                self.send_alert(alert)

    def send_alert(self, alert: dict):
        """發送警報通知"""
        # TODO: 實現 Telegram/WhatsApp 通知
        print(f"🚨 發送警報：{alert['title']}")
        # 使用 Telegram/WhatsApp API 發送消息

    def monitor_weather(self):
        """監控天氣並發送通知"""
        while True:
            alerts = self.check_special_weather()
            if alerts:
                self.save_alerts(alerts)
            
            # 每小時檢查一次
            time.sleep(3600)
```

### 3. 數據庫集成

```python
class WeatherDatabase:
    """天氣數據庫操作"""

    def __init__(self, agent_db: AgentDatabase):
        self.db = agent_db

    def save_weather_data(self, weather: dict, source: str = "hko"):
        """保存天氣數據到數據庫"""
        with self.db:
            data_id = f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            query = """
                INSERT INTO weather_data 
                (data_id, observation_time, temperature, humidity, rainfall, 
                 wind_speed, wind_direction, weather_condition, location, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (data_id) DO UPDATE SET
                    temperature = EXCLUDED.temperature,
                    humidity = EXCLUDED.humidity,
                    rainfall = EXCLUDED.rainfall,
                    wind_speed = EXCLUDED.wind_speed,
                    wind_direction = EXCLUDED.wind_direction,
                    weather_condition = EXCLUDED.weather_condition,
                    metadata = EXCLUDED.metadata
            """
            
            temp = weather.get('temperature', {}).get('value')
            humidity = weather.get('humidity', {}).get('value')
            rainfall = weather.get('rainfall', {}).get('value')
            wind_speed = weather.get('wind_speed', {}).get('value')
            wind_direction = weather.get('wind_speed', {}).get('direction')
            
            return self.db.execute_update(query, (
                data_id, 
                datetime.now(),
                temp,
                humidity,
                rainfall,
                wind_speed,
                wind_direction,
                weather.get('weather_condition', 'unknown'),
                source,
                json.dumps(weather)
            ))

    def get_recent_weather(self, limit: int = 24) -> list:
        """獲取最近的天氣數據"""
        with self.db:
            query = """
                SELECT * FROM weather_data
                ORDER BY observation_time DESC
                LIMIT %s
            """
            return self.db.execute_query(query, (limit,))

    def get_weather_history(self, start_date: str, end_date: str) -> list:
        """獲取指定日期範圍的天氣數據"""
        with self.db:
            query = """
                SELECT * FROM weather_data
                WHERE observation_time >= %s AND observation_time <= %s
                ORDER BY observation_time DESC
            """
            return self.db.execute_query(query, (start_date, end_date))
```

---

## 🚀 部署計劃

### 階段 1：API 研究與文檔（1 小時）

1. 下載並分析 HKO API 文檔
2. 確定所有 API 端點和參數
3. 測試 API 連接和響應格式
4. 文檔化所有 API 功能

### 階段 2：數據庫設置（30 分鐘）

1. 創建數據庫表結構
2. 優化索引
3. 初始化測試數據
4. 驗證數據庫連接

### 階段 3：核心功能開發（2 小時）

1. 實現 WeatherAPI 客戶端
2. 實現 WeatherMonitor 監控器
3. 實現 WeatherDatabase 操作類
4. 集成到 PostgreSQL 數據庫

### 階段 4：通知系統集成（1 小時）

1. 配置 Telegram/WhatsApp 通知
2. 實現警報發送功能
3. 測試通知系統

### 階段 5：測試與優化（1 小時）

1. 測試天氣查詢功能
2. 測試特別天氣監控
3. 測試數據庫操作
4. 優化響應時間

---

## 💡 使用場景

### 場景 1：用戶查詢當前天氣

**用戶輸入**："現在幾度？" 或 "香港天氣如何？"

**系統響應**：
```
🌤 香港天文台天氣報告

📊 當前天氣：
- 溫度：28°C
- 濕度：85%
- 風速：15 km/h (東南東)
- 天氣：多雲局部地區有驟雨

⏰ 更新時間：2026-02-26 09:00

來源：香港天文台 HKO
```

---

### 場景 2：特別天氣警告

**系統檢測**：氣溫 > 33°C

**自動通知**：
```
🚨 特別天氣警告

⚠️  **酷熱天氣警告**

預計最高氣溫達 33 度或以上。

**市民應採取防暑措施：**
- 避免長時間在陽光下曝曬
- 多喝清水，補充鹽分
- 穿著淺色、透氣的衣物
- 在室內使用空調或電風扇

**生效時間**：現在起生效

來源：香港天文台 HKO
```

---

### 場景 3：天氣預報查詢

**用戶輸入**："未來 24 小時天氣預報"

**系統響應**：
```
🌤 香港未來 24 小時天氣預報

📊 **今天 (2026-02-26)**
- 最高溫度：32°C
- 最低溫度：26°C
- 天氣：多雲，間中有驟雨

📊 **明天 (2026-02-27)**
- 最高溫度：34°C
- 最低溫度：27°C
- 天氣：多雲，局部地區有雷暴

📊 **後天 (2026-02-28)**
- 最高溫度：31°C
- 最低溫度：26°C
- 天氣：大致多雲

⚠️ **注意**：明天預計氣溫較高，請注意防暑。

來源：香港天文台 HKO
```

---

## 🎯 智能特點

### 1. 自動監控

- ✅ 每小時自動檢查天氣狀況
- ✅ 檢測特別天氣條件
- ✅ 自動發送警報通知

### 2. 智能路由

- ✅ 識別天氣相關查詢
- ✅ 自動調用 Weather Agent
- ✅ 優化響應時間

### 3. 數據持久化

- ✅ 所有天氣數據存儲到數據庫
- ✅ 支持歷史查詢
- ✅ 支持數據分析

### 4. 即時通知

- ✅ 特別天氣立即通知
- ✅ 警告級別分類
- ✅ 多渠道支持（Telegram/WhatsApp）

---

## 📊 預期 API 端點

根據香港天文台 API 慣例，預期的端點可能包括：

| 端點 | 方法 | 用途 |
|--------|------|------|
| `/weatherAPI/currentweather` | GET | 獲取當前天氣 |
| `/weatherAPI/warning` | GET | 獲取天氣警告 |
| `/weatherAPI/flw` | GET | 獲取天氣預報 |
| `/weatherAPI/rhrread` | GET | 讀取氣溫數據 |
| `/weatherAPI/fnd` | GET | 搜索特定數據 |

---

## 🔐 安全與隱私

1. **API 密鑰管理**
   - 如果需要 API 密鑰，存儲在環境變量
   - 不硬編碼在腳本中

2. **數據隱私**
   - 用戶查詢記錄到數據庫
   - 不存儲敏感個人信息
   - 遵守 GDPR 和香港私隱條例

3. **通知頻率控制**
   - 避免垃圾通知
   - 合併相同類型的通知
   - 用戶可調整通知頻率

---

## 📝 實施建議

### 開發語言

- **後端**：Python 3.14+
- **API**：requests 庫
- **數據庫**：psycopg2（已安裝）
- **通知**：Telegram Bot / WhatsApp Business API

### 優化建議

1. **API 緩存**
   - 緩存天氣數據（5 分鐘）
   - 避免過度調用 API

2. **數據庫優化**
   - 定期清理舊數據
   - 使用連接池
   - 優化查詢

3. **錯誤處理**
   - API 失敗重試機制
   - 優雅的錯誤消息
   - 詳細的錯誤日誌

---

## 🎯 下一步

你想：
1. **立即開始開發** - 我開始實現天氣 API 集成
2. **先研究文檔** - 我先下載和分析 PDF 文檔
3. **查看詳細方案** - 查看完整的實現計劃
4. **其他需求** - 有其他想法嗎？

告訴我你想做什麼！
