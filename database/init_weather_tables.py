#!/usr/bin/env python3
"""
初始化天氣數據庫表
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase


def init_weather_tables():
    """初始化天氣數據庫表"""
    
    print("=" * 60)
    print("初始化天氣數據庫表")
    print("=" * 60)
    print()
    
    # 創建數據庫實例
    db = AgentDatabase()
    
    try:
        with db:
            # 創建 weather_data 表
            print("[1/4] 創建 weather_data 表...")
            
            query = """
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
                    location VARCHAR(100) DEFAULT 'HKO',
                    source VARCHAR(50) DEFAULT 'HKO',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ weather_data 表創建成功")
            print()
            
            # 創建索引
            print("[1/4] 創建 weather_data 表索引...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_weather_data_time ON weather_data(observation_time DESC)",
                "CREATE INDEX IF NOT EXISTS idx_weather_data_location ON weather_data(location)",
                "CREATE INDEX IF NOT EXISTS idx_weather_data_temperature ON weather_data(temperature)"
            ]
            
            for idx_query in index_queries:
                db.execute_update(idx_query, ())
            
            print("  ✅ weather_data 索引創建成功")
            print()
            
            # 創建 weather_alerts 表
            print("[2/4] 創建 weather_alerts 表...")
            
            query = """
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id SERIAL PRIMARY KEY,
                    alert_id VARCHAR(100) UNIQUE NOT NULL,
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
            """
            
            db.execute_update(query, ())
            print("  ✅ weather_alerts 表創建成功")
            print()
            
            # 創建索引
            print("[2/4] 創建 weather_alerts 表索引...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_weather_alerts_time ON weather_alerts(effect_start_time DESC)",
                "CREATE INDEX IF NOT EXISTS idx_weather_alerts_type ON weather_alerts(alert_type)",
                "CREATE INDEX IF NOT EXISTS idx_weather_alerts_active ON weather_alerts(is_active, severity)"
            ]
            
            for idx_query in index_queries:
                db.execute_update(idx_query, ())
            
            print("  ✅ weather_alerts 索引創建成功")
            print()
            
            # 創建 weather_forecast 表
            print("[3/4] 創建 weather_forecast 表...")
            
            query = """
                CREATE TABLE IF NOT EXISTS weather_forecast (
                    id SERIAL PRIMARY KEY,
                    forecast_id VARCHAR(100) UNIQUE NOT NULL,
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
            """
            
            db.execute_update(query, ())
            print("  ✅ weather_forecast 表創建成功")
            print()
            
            # 創建索引
            print("[3/4] 創建 weather_forecast 表索引...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_weather_forecast_time ON weather_forecast(forecast_time DESC)",
                "CREATE INDEX IF NOT EXISTS idx_weather_forecast_location ON weather_forecast(location)"
            ]
            
            for idx_query in index_queries:
                db.execute_update(idx_query, ())
            
            print("  ✅ weather_forecast 索引創建成功")
            print()
            
            # 創建 weather_settings 表
            print("[4/4] 創建 weather_settings 表...")
            
            query = """
                CREATE TABLE IF NOT EXISTS weather_settings (
                    id SERIAL PRIMARY KEY,
                    setting_id VARCHAR(100) UNIQUE NOT NULL,
                    setting_key VARCHAR(50) NOT NULL,
                    setting_value TEXT NOT NULL,
                    setting_type VARCHAR(20) DEFAULT 'string',
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """
            
            db.execute_update(query, ())
            print("  ✅ weather_settings 表創建成功")
            print()
            
            # 創建索引
            print("[4/4] 創建 weather_settings 表索引...")
            
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_weather_settings_key ON weather_settings(setting_key)"
            ]
            
            for idx_query in index_queries:
                db.execute_update(idx_query, ())
            
            print("  ✅ weather_settings 索引創建成功")
            print()
            
            print("=" * 60)
            print("所有天氣數據庫表初始化完成！")
            print("=" * 60)
            print()
            print("創建的表：")
            print("  1. weather_data - 天氣數據")
            print("  2. weather_alerts - 天氣警告")
            print("  3. weather_forecast - 天氣預報")
            print("  4. weather_settings - 用戶設置")
            print()
            print("準備就緒，可以開始存儲天氣數據！")
            print()
            
            return True
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return False


def main():
    """主函數"""
    success = init_weather_tables()
    
    if success:
        print("✅ 天氣數據庫初始化完成！")
        print()
        print("下一步：")
        print("  1. 開始保存天氣數據")
        print("  2. 開始檢測並保存警告")
        print("  3. 更新監控系統使用數據庫")
    else:
        print("❌ 天氣數據庫初始化失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
