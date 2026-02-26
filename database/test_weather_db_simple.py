#!/usr/bin/env python3
"""
測試天氣數據庫操作
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def test_weather_db_operations():
    """測試天氣數據庫操作"""
    print("=" * 60)
    print("天氣數據庫操作測試")
    print("=" * 60)
    print()
    
    # 創建數據庫實例
    db = AgentDatabase()
    
    try:
        with db:
            print("[1/6] 創建天氣數據表...")
            
            # 創建 weather_data 表
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id SERIAL PRIMARY KEY,
                    data_id VARCHAR(100) UNIQUE,
                    observation_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    temperature FLOAT,
                    humidity FLOAT,
                    rainfall FLOAT,
                    wind_speed FLOAT,
                    wind_direction VARCHAR(10),
                    weather_condition VARCHAR(50),
                    location VARCHAR(100) DEFAULT 'HKO',
                    source VARCHAR(50) DEFAULT 'HKO',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """, ())
            
            # 創建索引
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_time ON weather_data(observation_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_location ON weather_data(location)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_temperature ON weather_data(temperature)", ())
            
            print("  ✅ weather_data 表創建成功")
            print()
            
            print("[2/6] 創建天氣警告表...")
            
            # 創建 weather_alerts 表
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id SERIAL PRIMARY KEY,
                    alert_id VARCHAR(100) UNIQUE,
                    alert_type VARCHAR(50),
                    severity VARCHAR(20),
                    title TEXT,
                    description TEXT,
                    effect_start_time TIMESTAMP WITH TIME ZONE,
                    effect_end_time TIMESTAMP WITH TIME ZONE,
                    location VARCHAR(100) DEFAULT 'HKO',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP WITH TIME ZONE,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """, ())
            
            # 創建索引
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_time ON weather_alerts(effect_start_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_type ON weather_alerts(alert_type)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_active ON weather_alerts(is_active, severity)", ())
            
            print("  ✅ weather_alerts 表創建成功")
            print()
            
            print("[3/6] 創建天氣預報表...")
            
            # 創建 weather_forecast 表
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS weather_forecast (
                    id SERIAL PRIMARY KEY,
                    forecast_id VARCHAR(100) UNIQUE,
                    forecast_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    temperature_min FLOAT,
                    temperature_max FLOAT,
                    weather_condition VARCHAR(50),
                    humidity FLOAT,
                    rainfall_probability FLOAT,
                    location VARCHAR(100) DEFAULT 'HKO',
                    source VARCHAR(50) DEFAULT 'HKO',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """, ())
            
            # 創建索引
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_forecast_time ON weather_forecast(forecast_time DESC)", ())
            db.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_forecast_location ON weather_forecast(location)", ())
            
            print("  ✅ weather_forecast 表創建成功")
            print()
            
            print("[4/6] 測試保存天氣數據...")
            
            # 保存一條天氣數據
            db.execute_update("""
                INSERT INTO weather_data 
                (data_id, observation_time, temperature, humidity, rainfall, wind_speed, wind_direction, weather_condition, location, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (
                "weather_20260226_001",
                datetime.now(HK_TZ),
                28.0,
                75,
                5.0,
                15.0,
                "ESE",
                "多云局部地區有驟雨",
                "HKO",
                "HKO",
                '{"source": "test"}'
            ))
            
            print("  ✅ 天氣數據保存成功")
            print()
            
            print("[5/6] 測試保存警告...")
            
            # 保存一條警告
            db.execute_update("""
                INSERT INTO weather_alerts
                (alert_id, alert_type, severity, title, description, effect_start_time, location, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (
                "alert_20260226_001",
                "heat_warning",
                "high",
                "酷熱天氣警告",
                "香港天文台發出酷熱天氣警告。當前氣溫達 28度。",
                datetime.now(HK_TZ),
                "HKO",
                '{"temperature": 28.0}'
            ))
            
            print("  ✅ 警告保存成功")
            print()
            
            print("[6/6] 測試查詢數據...")
            
            # 查詢天氣數據
            weather_data = db.execute_query("""
                SELECT * FROM weather_data
                ORDER BY observation_time DESC
                LIMIT 5
            """, ())
            
            print(f"  ✅ 查詢到 {len(weather_data)} 條天氣數據")
            print()
            
            # 查詢警告
            alerts = db.execute_query("""
                SELECT * FROM weather_alerts
                ORDER BY effect_start_time DESC
                LIMIT 5
            """, ())
            
            print(f"  ✅ 查詢到 {len(alerts)} 條警告")
            print()
            
            print("=" * 60)
            print("所有測試通過！")
            print("=" * 60)
            print()
            print("天氣數據庫已準備就緒，可以開始存儲和查詢天氣數據！")
            
            return True
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函數"""
    print("天氣數據庫初始化")
    print("=" * 60)
    print()
    
    success = test_weather_db_operations()
    
    if success:
        print()
        print("✅ 天氣數據庫已初始化完成！")
        print()
        print("創建的表：")
        print("  1. weather_data - 天氣數據")
        print("  2. weather_alerts - 天氣警告")
        print("  3. weather_forecast - 天氣預報")
        print()
        print("準備就緒，可以開始存儲天氣數據到數據庫！")
    else:
        print()
        print("❌ 天氣數據庫初始化失敗")


if __name__ == "__main__":
    main()
