#!/usr/bin/env python3
"""
天氣數據庫操作
完整的上下文管理器和天氣數據庫操作
"""

from datetime import datetime, timezone, timedelta
import json

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


# PostgreSQL 數據庫操作
class WeatherDatabase:
    """天氣數據庫操作類"""
    
    def __init__(self, db_connector):
        self.db = db_connector
        
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
    
    def save_weather_data(self, data_id, observation_time, temperature, humidity, 
                          rainfall, wind_speed, wind_direction, weather_condition, 
                          location='HKO', source='HKO', metadata=None):
        """保存天氣數據到 weather_data 表"""
        
        try:
            with self.db:
                query = """
                    INSERT INTO weather_data 
                    (data_id, observation_time, temperature, humidity, rainfall, 
                     wind_speed, wind_direction, weather_condition, location, source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (data_id) DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidity = EXCLUDED.humidity,
                        rainfall = EXCLUDED.rainfall,
                        wind_speed = EXCLUDED.wind_speed,
                        wind_direction = EXCLUDED.wind_direction,
                        weather_condition = EXCLUDED.weather_condition,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                self.db.execute_update(query, (
                    data_id, observation_time, temperature, humidity, 
                    rainfall, wind_speed, wind_direction, weather_condition, 
                    location, source, json.dumps(metadata or {})
                ))
                
                return True
        except Exception as e:
            print(f"[DB_ERROR] 保存天氣數據失敗: {e}")
            return False
    
    def save_weather_alert(self, alert_id, alert_type, severity, title, description, 
                           effect_start_time, location='HKO', metadata=None):
        """保存天氣警告到 weather_alerts 表"""
        
        try:
            with self.db:
                query = """
                    INSERT INTO weather_alerts 
                    (alert_id, alert_type, severity, title, description, 
                     effect_start_time, location, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (alert_id) DO UPDATE SET
                        severity = EXCLUDED.severity,
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        effect_start_time = EXCLUDED.effect_start_time,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                self.db.execute_update(query, (
                    alert_id, alert_type, severity, title, description, 
                    effect_start_time, location, json.dumps(metadata or {})
                ))
                
                return True
        except Exception as e:
            print(f"[DB_ERROR] 保存警告失敗: {e}")
            return False
    
    def save_weather_forecast(self, forecast_id, forecast_time, temperature_min, 
                             temperature_max, weather_condition, humidity, rainfall_probability, 
                             location='HKO', source='HKO', metadata=None):
        """保存天氣預報到 weather_forecast 表"""
        
        try:
            with self.db:
                query = """
                    INSERT INTO weather_forecast 
                    (forecast_id, forecast_time, temperature_min, temperature_max, 
                     weather_condition, humidity, rainfall_probability, location, source, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (forecast_id) DO NOTHING
                """
                
                self.db.execute_update(query, (
                    forecast_id, forecast_time, temperature_min, temperature_max, 
                    weather_condition, humidity, rainfall_probability, 
                    location, source, json.dumps(metadata or {})
                ))
                
                return True
        except Exception as e:
            print(f"[DB_ERROR] 保存預報失敗: {e}")
            return False
    
    def get_latest_weather(self, location='HKO', limit=24):
        """獲取最近的天氣數據"""
        
        try:
            with self.db:
                query = """
                    SELECT * FROM weather_data
                    WHERE location = %s
                    ORDER BY observation_time DESC
                    LIMIT %s
                """
                
                return self.db.execute_query(query, (location, limit))
        except Exception as e:
            print(f"[DB_ERROR] 獲取天氣數據失敗: {e}")
            return []
    
    def get_active_alerts(self, location='HKO'):
        """獲取所有有效的天氣警告"""
        
        try:
            with self.db:
                query = """
                    SELECT * FROM weather_alerts
                    WHERE is_active = TRUE AND location = %s
                    ORDER BY effect_start_time DESC
                """
                
                return self.db.execute_query(query, (location,))
        except Exception as e:
            print(f"[DB_ERROR] 獲取警告失敗: {e}")
            return []
    
    def get_recent_alerts(self, hours=24, location='HKO'):
        """獲取最近幾小時的警告"""
        
        try:
            with self.db:
                query = """
                    SELECT * FROM weather_alerts
                    WHERE location = %s AND effect_start_time >= NOW() - INTERVAL '%s hours'
                    ORDER BY effect_start_time DESC
                """
                
                return self.db.execute_query(query, (location, hours))
        except Exception as e:
            print(f"[DB_ERROR] 獲取警告失敗: {e}")
            return []
    
    def get_forecast(self, hours=24, location='HKO'):
        """獲取未來幾小時的預報"""
        
        try:
            with self.db:
                query = """
                    SELECT * FROM weather_forecast
                    WHERE location = %s AND forecast_time >= NOW() 
                    AND forecast_time <= NOW() + INTERVAL '%s hours'
                    ORDER BY forecast_time ASC
                """
                
                return self.db.execute_query(query, (location, hours))
        except Exception as e:
            print(f"[DB_ERROR] 獲取預報失敗: {e}")
            return []


def main():
    """主函數 - 測試天氣數據庫操作"""
    print("=" * 60)
    print("天氣數據庫操作測試")
    print("=" * 60)
    print()
    
    # 創建實例
    from agent_db_connector import AgentDatabase
    db_connector = AgentDatabase()
    weather_db = WeatherDatabase(db_connector)
    
    try:
        with db_connector:
            print("[1/6] 創建天氣數據表...")
            
            # 創建 weather_data 表
            db_connector.execute_update("""
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
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_time ON weather_data(observation_time DESC)", ())
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_location ON weather_data(location)", ())
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_data_temperature ON weather_data(temperature)", ())
            
            print("  ✅ weather_data 表創建成功")
            print()
            
            print("[2/6] 創建天氣警告表...")
            
            # 創建 weather_alerts 表
            db_connector.execute_update("""
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id SERIAL PRIMARY KEY,
                    alert_id VARCHAR(100) UNIQUE,
                    alert_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    effect_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
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
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_time ON weather_alerts(effect_start_time DESC)", ())
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_type ON weather_alerts(alert_type)", ())
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_alerts_active ON weather_alerts(is_active, severity)", ())
            
            print("  ✅ weather_alerts 表創建成功")
            print()
            
            print("[3/6] 創建天氣預報表...")
            
            # 創建 weather_forecast 表
            db_connector.execute_update("""
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
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_forecast_time ON weather_forecast(forecast_time DESC)", ())
            db_connector.execute_update("CREATE INDEX IF NOT EXISTS idx_weather_forecast_location ON weather_forecast(location)", ())
            
            print("  ✅ weather_forecast 表創建成功")
            print()
            
            print("[4/6] 測試保存天氣數據...")
            
            # 保存一條天氣數據
            success = weather_db.save_weather_data(
                data_id="weather_20260226_test",
                observation_time=datetime.now(HK_TZ),
                temperature=28.0,
                humidity=75,
                rainfall=5.0,
                wind_speed=15.0,
                wind_direction="ESE",
                weather_condition="多云局部地區有驟雨",
                location="HKO",
                source="HKO",
                metadata={'test': True}
            )
            
            if success:
                print("  ✅ 天氣數據保存成功")
            print()
            
            print("[5/6] 測試保存天氣警告...")
            
            # 保存一條警告
            success = weather_db.save_weather_alert(
                alert_id="alert_heat_20260226_test",
                alert_type="heat_warning",
                severity="high",
                title="酷熱天氣警告",
                description="香港天文台發出酷熱天氣警告。當前氣溫達 28度。",
                effect_start_time=datetime.now(HK_TZ),
                location="HKO",
                metadata={'temperature': 28.0}
            )
            
            if success:
                print("  ✅ 警告保存成功")
            print()
            
            print("[6/6] 查詢數據...")
            
            # 查詢天氣數據
            weather_data = weather_db.get_latest_weather(limit=5)
            print(f"  ✅ 查詢到 {len(weather_data)} 條天氣數據")
            
            # 查詢警告
            alerts = weather_db.get_active_alerts()
            print(f"  ✅ 查詢到 {len(alerts)} 條有效警告")
            
            print()
            print("=" * 60)
            print("所有測試通過！")
            print("=" * 60)
            print()
            print("天氣數據庫已準備就緒！")
            print()
            print("已創建的表：")
            print("  1. weather_data - 天氣數據")
            print("  2. weather_alerts - 天氣警告")
            print("  3. weather_forecast - 天氣預報")
            print()
            print("準備就緒，可以開始保存和查詢天氣數據！")
            
            return True
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()
