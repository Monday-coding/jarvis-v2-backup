#!/usr/bin/env python3
"""
天氣監控系統 - 數據庫版本
從數據庫讀取和保存天氣數據
"""

from datetime import datetime, timezone, timedelta
import random
import json

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class WeatherDatabase:
    """天氣數據庫操作"""
    
    def __init__(self, db_connector):
        self.db = db_connector
        self.last_alert_time = {}
        
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
    
    def save_weather_data(self, weather_data):
        """保存天氣數據到數據庫"""
        try:
            with self.db:
                # 檢查 weather_data 表是否存在
                result = self.db.execute_query("""
                    SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'weather_data'
                """, ())
                
                if result:
                    # 保存天氣數據
                    data_id = f"weather_{datetime.now(HK_TZ).strftime('%Y%m%d_%H%M%S')}"
                    
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
                        weather_data['observation_time'],
                        weather_data['temperature'],
                        weather_data['humidity'],
                        weather_data['rainfall'],
                        weather_data['wind_speed'],
                        weather_data['wind_direction'],
                        weather_data['weather_condition'],
                        weather_data.get('location', 'HKO'),
                        weather_data.get('source', 'HKO'),
                        json.dumps(weather_data.get('metadata', {}))
                    ))
                    
                    print(f"[DB] 天氣數據已保存：{data_id}")
                    return True
                else:
                    print("[DB] weather_data 表不存在")
                    return False
        except Exception as e:
            print(f"[DB_ERROR] 保存天氣數據失敗: {e}")
            return False
    
    def save_weather_alert(self, alert_data):
        """保存天氣警告到數據庫"""
        try:
            with self.db:
                # 檢查 weather_alerts 表是否存在
                result = self.db.execute_query("""
                    SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = 'weather_alerts'
                """, ())
                
                if result:
                    alert_id = alert_data['alert_id']
                    
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
                        alert_data['alert_type'],
                        alert_data['severity'],
                        alert_data['title'],
                        alert_data['description'],
                        alert_data['effect_start_time'],
                        alert_data.get('location', 'HKO'),
                        json.dumps(alert_data.get('metadata', {}))
                    ))
                    
                    print(f"[DB] 警告已保存：{alert_id}")
                    return True
                else:
                    print("[DB] weather_alerts 表不存在")
                    return False
        except Exception as e:
            print(f"[DB_ERROR] 保存警告失敗: {e}")
            return False
    
    def check_heat_warning(self):
        """檢查酷熱警告"""
        temp = self.current_weather['temperature']
        
        if temp >= 33:
            severity = 'high' if temp > 35 else 'moderate'
            alert_type = 'heat_warning'
            
            alert_data = {
                'alert_id': f"alert_heat_{int(datetime.now(HK_TZ).timestamp())}",
                'alert_type': alert_type,
                'severity': severity,
                'title': '酷熱天氣警告',
                'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {temp}度。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'temperature': temp,
                    'condition': '酷熱'
                }
            }
            
            if self.should_send_alert(alert_type, severity):
                self.save_weather_alert(alert_data)
                return alert_data
        
        return None
    
    def check_rainstorm_warning(self):
        """檢查暴雨警告"""
        rainfall = self.current_weather['rainfall']
        
        if rainfall >= 30:
            severity = 'severe' if rainfall > 50 else 'high'
            alert_type = 'rainstorm_warning'
            
            alert_data = {
                'alert_id': f"alert_rain_{int(datetime.now(HK_TZ).timestamp())}",
                'alert_type': alert_type,
                'severity': severity,
                'title': '暴雨天氣警告',
                'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {int(rainfall)}毫米雨量。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'rainfall': rainfall,
                    'condition': '暴雨'
                }
            }
            
            if self.should_send_alert(alert_type, severity):
                self.save_weather_alert(alert_data)
                return alert_data
        
        return None
    
    def check_strong_wind_warning(self):
        """檢查強風警告"""
        wind_speed = self.current_weather['wind_speed']
        
        if wind_speed >= 40:
            severity = 'severe' if wind_speed > 60 else 'high'
            alert_type = 'strong_wind_warning'
            
            alert_data = {
                'alert_id': f"alert_wind_{int(datetime.now(HK_TZ).timestamp())}",
                'alert_type': alert_type,
                'severity': severity,
                'title': '強風警告',
                'description': f"香港風力正在增強，平均風速達 {int(wind_speed)}公里/小時。市民應避免在風力強勁的地方逗留。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'wind_speed': wind_speed,
                    'condition': '強風'
                }
            }
            
            if self.should_send_alert(alert_type, severity):
                self.save_weather_alert(alert_data)
                return alert_data
        
        return None
    
    def check_all_alerts(self):
        """檢查所有警告"""
        alerts = []
        
        # 1. 檢查酷熱
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
            print(f"[ALERT] 檢測到酷熱警告：{self.current_weather['temperature']}度")
        
        # 2. 檢查暴雨
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
            print(f"[ALERT] 檢測到暴雨警告：{self.current_weather['rainfall']}mm")
        
        # 3. 檢查強風
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
            print(f"[ALERT] 檢測到強風警告：{self.current_weather['wind_speed']}km/h")
        
        return alerts
    
    def should_send_alert(self, alert_type, severity):
        """判斷是否應該發送警告"""
        now = datetime.now(HK_TZ)
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:  # 1 小時內不重複
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True
    
    def update_weather(self):
        """更新天氣數據（模擬）"""
        # 20% 概率發生特殊天氣
        if random.random() < 0.2:
            weather_type = random.choice(['酷熱', '暴雨', '強風'])
            
            if weather_type == '酷熱':
                self.current_weather['temperature'] = random.uniform(33, 36)
                self.current_weather['humidity'] = random.uniform(80, 90)
                self.current_weather['rainfall'] = 0.0
                self.current_weather['wind_speed'] = random.uniform(5, 15)
                self.current_weather['weather_condition'] = '晴朗'
                self.current_weather['wind_direction'] = random.choice(['N', 'S', 'E'])
                
            elif weather_type == '暴雨':
                self.current_weather['temperature'] = random.uniform(22, 26)
                self.current_weather['humidity'] = random.uniform(90, 98)
                self.current_weather['rainfall'] = random.uniform(30, 50)
                self.current_weather['wind_speed'] = random.uniform(20, 30)
                self.current_weather['weather_condition'] = '大雨'
                self.current_weather['wind_direction'] = random.choice(['NE', 'SE', 'S'])
                
            elif weather_type == '強風':
                self.current_weather['temperature'] = random.uniform(20, 25)
                self.current_weather['humidity'] = random.uniform(70, 85)
                self.current_weather['rainfall'] = random.uniform(10, 20)
                self.current_weather['wind_speed'] = random.uniform(40, 50)
                self.current_weather['weather_condition'] = '強風'
                self.current_weather['wind_direction'] = random.choice(['NE', 'N', 'NW'])
            
            # 通知特殊天氣變化
            print(f"[HKO API] 檢測到 {weather_type} 天氣！")
        
        else:
            # 正常天氣變化（小幅度）
            self.current_weather['temperature'] += random.uniform(-0.5, 0.5)
            self.current_weather['humidity'] += random.uniform(-2, 2)
            self.current_weather['rainfall'] += random.uniform(-1, 1)
            self.current_weather['wind_speed'] += random.uniform(-2, 2)
            
            # 限制範圍
            self.current_weather['temperature'] = max(15, min(38, self.current_weather['temperature']))
            self.current_weather['humidity'] = max(30, min(95, self.current_weather['humidity']))
            self.current_weather['rainfall'] = max(0, min(100, self.current_weather['rainfall']))
            self.current_weather['wind_speed'] = max(0, min(80, self.current_weather['wind_speed']))
        
        # 添加觀測時間
        self.current_weather['observation_time'] = datetime.now(HK_TZ)
        self.current_weather['source'] = 'HKO'
        self.current_weather['location'] = 'HKO'
    
    def monitor(self):
        """監控天氣並保存到數據庫"""
        print("=" * 60)
        print("天氣監控系統 - 數據庫版本")
        print("=" * 60)
        print()
        print("監控配置：")
        print("  檢查頻率：每 5 分鐘")
        print("  數據庫：PostgreSQL")
        print("  通知發送：模擬（需集成 Telegram/WhatsApp）")
        print("  數據保留：7 天")
        print("  警告保留：30 天")
        print()
        print("=" * 60)
        print()
        
        check_count = 0
        
        while True:
            try:
                check_time = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{check_time}] 開始第 {check_count + 1} 次檢查...")
                print()
                
                # 1. 更新天氣
                print("  [1/4] 更新天氣數據...")
                self.update_weather()
                
                weather_data = self.current_weather.copy()
                weather_data['metadata'] = {
                    'check_number': check_count + 1,
                    'source': 'HKO API'
                }
                
                # 2. 保存到數據庫
                print("  [2/4] 保存到數據庫...")
                success = self.save_weather_data(weather_data)
                
                if success:
                    print(f"    溫度：{weather_data['temperature']:.1f}度")
                    print(f"    濕度：{weather_data['humidity']}%")
                    print(f"    降雨：{weather_data['rainfall']:.1f}mm")
                    print(f"    風速：{weather_data['wind_speed']:.1f}km/h")
                    print(f"    風向：{weather_data['wind_direction']}")
                    print(f"    天氣：{weather_data['weather_condition']}")
                else:
                    print("    無法保存數據庫")
                
                print()
                
                # 3. 檢查警告
                print("  [3/4] 檢查天氣警告...")
                alerts = self.check_all_alerts()
                
                if alerts:
                    print(f"    檢測到 {len(alerts)} 個警告")
                    for i, alert in enumerate(alerts, 1):
                        print(f"      {i}. {alert['title']} ({alert['severity']})")
                else:
                    print("    無警告")
                
                print()
                
                # 4. 顯示統計
                print("  [4/4] 顯示統計...")
                print(f"    檢查次數：{check_count + 1}")
                print(f"    警告數量：{len(alerts)}")
                
                check_count += 1
                
                print()
                print("=" * 60)
                print()
                
                # 等待 5 分鐘
                print(f"[{check_time}] 等待 300 秒...")
                print()
                print("-" * 40)
                print()
                
                for i in range(300, 0, -1):
                    # 每 60 秒顯示一次倒數
                    if i % 60 == 0:
                        remaining = i // 60
                        print(f"  剩餘：{remaining} 分鐘")
                        sys.stdout.flush()
                    
                    time.sleep(1)
                
            except KeyboardInterrupt:
                print()
                print("=" * 60)
                print("監控已停止")
                print("=" * 60)
                break
            except Exception as e:
                print(f"[ERROR] 監控過程出錯：{e}")
                time.sleep(60)


def main():
    """主函數"""
    print("天氣監控系統")
    print("=" * 60)
    print()
    print("功能：")
    print("  1. 持續監控天氣")
    print("  2. 保存數據到數據庫")
    print("  3. 自動檢測所有警告")
    print("  4. 智能頻率控制")
    print()
    print("=" * 60)
    print()
    
    # 創建數據庫連接
    import sys
    sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')
    from agent_db_connector import PostgreSQLConnector
    
    # 創建數據庫連接
    db = PostgreSQLConnector(
        host="localhost",
        port=5432,
        database="openclaw",
        user="openclaw",
        password="openclaw_password_2024"
    )
    
    # 連接數據庫
    if db.connect():
        print("✅ 數據庫連接成功")
    else:
        print("❌ 數據庫連接失敗")
        return
    
    # 創建監控器
    monitor = WeatherDatabase(db)
    
    # 啟動監控
    monitor.monitor()


if __name__ == "__main__":
    main()
