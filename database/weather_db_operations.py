#!/usr/bin/env python3
"""
數據庫操作模塊
天氣數據、警告、預報、設置
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from datetime import datetime, timezone, timedelta
import json

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


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
    
    def save_weather_data(self, data_id, observation_time, temperature, humidity, rainfall, 
                          wind_speed, wind_direction, weather_condition, location='HKO', source='HKO', metadata=None):
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
                    data_id,
                    observation_time,
                    temperature,
                    humidity,
                    rainfall,
                    wind_speed,
                    wind_direction,
                    weather_condition,
                    location,
                    source,
                    json.dumps(metadata or {})
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
                    alert_id,
                    alert_type,
                    severity,
                    title,
                    description,
                    effect_start_time,
                    location,
                    json.dumps(metadata or {})
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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (forecast_id) DO NOTHING
                """
                
                self.db.execute_update(query, (
                    forecast_id,
                    forecast_time,
                    temperature_min,
                    temperature_max,
                    weather_condition,
                    humidity,
                    rainfall_probability,
                    location,
                    source,
                    json.dumps(metadata or {})
                ))
                
                return True
        except Exception as e:
            print(f"[DB_ERROR] 保存預報失敗: {e}")
            return False
    
    def save_setting(self, setting_id, setting_key, setting_value, 
                     setting_type='string', description=None, metadata=None):
        """保存用戶設置到 weather_settings 表"""
        
        try:
            with self.db:
                query = """
                    INSERT INTO weather_settings 
                    (setting_id, setting_key, setting_value, setting_type, description, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (setting_key) DO UPDATE SET
                        setting_value = EXCLUDED.setting_value,
                        description = EXCLUDED.description,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                self.db.execute_update(query, (
                    setting_id,
                    setting_key,
                    setting_value,
                    setting_type,
                    description,
                    json.dumps(metadata or {})
                ))
                
                return True
        except Exception as e:
            print(f"[DB_ERROR] 保存設置失敗: {e}")
            return False
    
    def get_latest_weather(self, location='HKO', limit=24) -> list:
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
    
    def get_active_alerts(self, location='HKO') -> list:
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
    
    def get_recent_alerts(self, hours=24, location='HKO') -> list:
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
    
    def get_forecast(self, hours=24, location='HKO') -> list:
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
    
    def get_setting(self, setting_key, default=None) -> str:
        """獲取用戶設置"""
        
        try:
            with self.db:
                query = """
                    SELECT setting_value FROM weather_settings
                    WHERE setting_key = %s
                """
                
                result = self.db.execute_query(query, (setting_key,))
                
                if result:
                    return result[0]['setting_value']
                else:
                    return default
        except Exception as e:
            print(f"[DB_ERROR] 獲取設置失敗: {e}")
            return default
    
    def check_alert_sent(self, alert_type, severity) -> bool:
        """檢查警告是否最近已經發送"""
        
        try:
            with self.db:
                query = """
                    SELECT sent_at FROM weather_alerts
                    WHERE alert_type = %s AND severity = %s
                    ORDER BY sent_at DESC LIMIT 1
                """
                
                result = self.db.execute_query(query, (alert_type, severity))
                
                if result:
                    last_sent = result[0]['sent_at']
                    if last_sent:
                        time_diff = datetime.now(HK_TZ) - last_sent
                        # 1 小時內不重複發送
                        return time_diff.total_seconds() < 3600
                
                return False
        except Exception as e:
            print(f"[DB_ERROR] 檢查警告發送失敗: {e}")
            return False
    
    def update_alert_status(self, alert_id, is_active=False, sent_at=None):
        """更新警告狀態"""
        
        try:
            with self.db:
                query = """
                    UPDATE weather_alerts
                    SET is_active = %s,
                        sent_at = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE alert_id = %s
                """
                
                self.db.execute_update(query, (is_active, sent_at, alert_id))
                return True
        except Exception as e:
            print(f"[DB_ERROR] 更新警告狀態失敗: {e}")
            return False
    
    def get_weather_statistics(self, location='HKO', hours=24):
        """獲取天氣統計數據"""
        
        try:
            with self.db:
                # 平均溫度
                avg_temp_query = """
                    SELECT AVG(temperature) as avg_temp 
                    FROM weather_data 
                    WHERE location = %s AND observation_time >= NOW() - INTERVAL '%s hours'
                """
                avg_temp_result = self.db.execute_query(avg_temp_query, (location, hours))
                
                # 最高溫度
                max_temp_query = """
                    SELECT MAX(temperature) as max_temp,
                           MIN(temperature) as min_temp
                    FROM weather_data 
                    WHERE location = %s AND observation_time >= NOW() - INTERVAL '%s hours'
                """
                temp_range_result = self.db.execute_query(max_temp_query, (location, hours))
                
                # 總降雨量
                total_rain_query = """
                    SELECT SUM(rainfall) as total_rain
                    FROM weather_data 
                    WHERE location = %s AND observation_time >= NOW() - INTERVAL '%s hours'
                """
                rain_result = self.db.execute_query(total_rain_query, (location, hours))
                
                # 平均風速
                avg_wind_query = """
                    SELECT AVG(wind_speed) as avg_wind,
                           MAX(wind_speed) as max_wind
                    FROM weather_data 
                    WHERE location = %s AND observation_time >= NOW() - INTERVAL '%s hours'
                """
                wind_result = self.db.execute_query(avg_wind_query, (location, hours))
                
                return {
                    'avg_temperature': round(avg_temp_result[0]['avg_temp'], 1) if avg_temp_result else 0,
                    'max_temperature': round(temp_range_result[0]['max_temp'], 1) if temp_range_result else 0,
                    'min_temperature': round(temp_range_result[0]['min_temp'], 1) if temp_range_result else 0,
                    'total_rainfall': round(rain_result[0]['total_rain'], 1) if rain_result else 0,
                    'avg_wind_speed': round(wind_result[0]['avg_wind'], 1) if wind_result else 0,
                    'max_wind_speed': round(wind_result[0]['max_wind'], 1) if wind_result else 0
                }
        except Exception as e:
            print(f"[DB_ERROR] 獲取統計數據失敗: {e}")
            return None
