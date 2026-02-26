#!/usr/bin/env python3
"""
持續天氣監控系統 - 最終版本
實時監控、警告檢測、通知發送
"""

import sys
import os
import time
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts_history = []
        self.alerts_sent = 0
        self.weather_data_history = []
        
    def save_log(self, log_id, level, category, message, agent_id, context=None, metadata=None):
        """保存日誌"""
        log_entry = {
            'log_id': log_id,
            'timestamp': datetime.now(HK_TZ).isoformat(),
            'level': level,
            'category': category,
            'message': message,
            'agent_id': agent_id,
            'context': context,
            'metadata': metadata
        }
        self.alerts_history.append(log_entry)
        self.alerts_sent += 1
        print(f"[{level}] {message}")
    
    def save_weather_data(self, data_id, observation_time, temperature, humidity, rainfall, wind_speed, weather_condition, location='HKO', source='HKO', metadata=None):
        """保存天氣數據"""
        weather_entry = {
            'data_id': data_id,
            'observation_time': observation_time.isoformat() if isinstance(observation_time, datetime) else observation_time,
            'temperature': temperature,
            'humidity': humidity,
            'rainfall': rainfall,
            'wind_speed': wind_speed,
            'weather_condition': weather_condition,
            'location': location,
            'source': source,
            'metadata': metadata
        }
        self.weather_data_history.append(weather_entry)
        print(f"[DATA] 天氣數據已保存：{temperature}度, {rainfall}mm")
    
    def get_recent_weather(self, limit=24):
        """獲取最近的天氣數據"""
        return self.weather_data_history[-limit:]


class HKOAPIClient:
    """香港天文台 API 客戶端（模擬實時版本）"""
    
    def __init__(self):
        self.base_url = "https://www.hko.gov.hk"
        
        # 模擬實時天氣變化
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨',
            'observation_time': datetime.now(HK_TZ)
        }
    
    def fetch_current_weather(self) -> dict:
        """獲取當前天氣（實時更新）"""
        # 模擬天氣變化
        import random
        
        # 10% 概率發生特殊天氣
        if random.random() < 0.1:
            weather_type = random.choice(['酷熱', '暴雨', '強風'])
            
            if weather_type == '酷熱':
                self.current_weather['temperature'] = random.uniform(33, 36)
                self.current_weather['humidity'] = random.uniform(80, 90)
                self.current_weather['weather_condition'] = '晴朗'
                self.current_weather['rainfall'] = 0.0
                self.current_weather['wind_speed'] = random.uniform(5, 15)
            
            elif weather_type == '暴雨':
                self.current_weather['temperature'] = random.uniform(22, 26)
                self.current_weather['humidity'] = random.uniform(90, 98)
                self.current_weather['weather_condition'] = '大雨'
                self.current_weather['rainfall'] = random.uniform(30, 50)
                self.current_weather['wind_speed'] = random.uniform(20, 30)
                self.current_weather['wind_direction'] = random.choice(['NE', 'SE', 'S'])
            
            elif weather_type == '強風':
                self.current_weather['temperature'] = random.uniform(20, 25)
                self.current_weather['humidity'] = random.uniform(70, 85)
                self.current_weather['weather_condition'] = '強風'
                self.current_weather['rainfall'] = random.uniform(10, 20)
                self.current_weather['wind_speed'] = random.uniform(40, 55)
                self.current_weather['wind_direction'] = random.choice(['NE', 'N', 'NW'])
            
            # 通知特殊天氣變化
            print(f"[HKO API] 檢測到 {weather_type} 天氣！")
        
        else:
            # 正常天氣變化（小幅度）
            self.current_weather['temperature'] += random.uniform(-0.5, 0.5)
            self.current_weather['humidity'] += random.uniform(-2, 2)
            self.current_weather['wind_speed'] += random.uniform(-3, 3)
            
            # 限制範圍
            self.current_weather['temperature'] = max(15, min(38, self.current_weather['temperature']))
            self.current_weather['humidity'] = max(30, min(95, self.current_weather['humidity']))
            self.current_weather['wind_speed'] = max(0, min(60, self.current_weather['wind_speed']))
        
        # 更新觀測時間
        self.current_weather['observation_time'] = datetime.now(HK_TZ)
        
        # 返回數據
        return {
            'temperature': round(self.current_weather['temperature'], 1),
            'humidity': int(self.current_weather['humidity']),
            'rainfall': round(self.current_weather['rainfall'], 1),
            'wind_speed': round(self.current_weather['wind_speed'], 1),
            'wind_direction': self.current_weather['wind_direction'],
            'weather_condition': self.current_weather['weather_condition'],
            'observation_time': self.current_weather['observation_time'],
            'source': 'HKO'
        }
    
    def fetch_forecast(self, hours=24):
        """獲取天氣預報"""
        forecast = []
        base_temp = self.current_weather['temperature']
        
        for i in range(hours // 3):
            future_time = datetime.now(HK_TZ) + timedelta(hours=3 * (i + 1))
            temp_change = random.uniform(-2, 2)
            forecast_temp = max(20, min(38, base_temp + temp_change))
            
            forecast.append({
                'time': future_time,
                'temperature': round(forecast_temp, 1),
                'weather': random.choice(['多云', '局部地區有驟雨', '大致多云', '晴朗', '多云局部地區有雷暴'])
            })
        
        return forecast
    
    def fetch_weather_warnings(self):
        """獲取天氣警告（檢查當前天氣）"""
        warnings = []
        
        # 檢查酷熱警告
        if self.current_weather['temperature'] >= 33:
            warnings.append({
                'warning_type': 'heat_warning',
                'severity': 'high' if self.current_weather['temperature'] > 35 else 'moderate',
                'message': f"香港天文台發出酷熱天氣警告。當前氣溫達 {int(self.current_weather['temperature'])}度。"
            })
        
        # 檢查暴雨警告
        if self.current_weather['rainfall'] >= 30:
            warnings.append({
                'warning_type': 'rainstorm_warning',
                'severity': 'severe' if self.current_weather['rainfall'] > 50 else 'high',
                'message': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {int(self.current_weather['rainfall'])}毫米雨量。"
            })
        
        # 檢查強風警告
        if self.current_weather['wind_speed'] >= 40:
            warnings.append({
                'warning_type': 'strong_wind_warning',
                'severity': 'severe' if self.current_weather['wind_speed'] > 60 else 'high',
                'message': f"香港風力正在增強，平均風速達 {int(self.current_weather['wind_speed'])}公里/小時。"
            })
        
        return warnings


class WeatherMonitor:
    """天氣監控器 - 持續監控"""
    
    def __init__(self, db, api_client):
        self.db = db
        self.api = api_client
        self.last_alert_time = {}
        self.running = False
        
        # 監控配置
        self.check_interval = 300  # 5 分鐘（秒）
        self.forecast_hours = 24
        
        # 統計數據
        self.check_count = 0
        self.alerts_count = 0
        self.weather_updates = 0
    
    def check_heat_warning(self) -> dict:
        """檢查酷熱警告"""
        weather = self.api.fetch_current_weather()
        temp = weather['temperature']
        
        if temp >= 33:
            severity = 'high' if temp > 35 else 'moderate'
            alert_type = 'heat_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '酷熱天氣警告',
                    'description': (
                        f"香港天文台發出酷熱天氣警告。"
                        f"當前氣溫達 {temp}度。"
                        f"市民應採取防暑措施，避免長時間在戶外暴曬。"
                    ),
                    'effect_start_time': weather['observation_time'],
                    'location': '香港天文台',
                    'metadata': {
                        'temperature': temp,
                        'condition': '酷熱'
                    }
                }
                
                # 保存到數據庫
                self.db.save_log(
                    log_id=f"alert_heat_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"酷熱天氣警告：{temp}度",
                    agent_id="weather",
                    context=alert
                )
                
                # 保存天氣數據
                data_id = f"weather_{int(time.time())}"
                self.db.save_weather_data(
                    data_id=data_id,
                    observation_time=weather['observation_time'],
                    temperature=temp,
                    humidity=weather['humidity'],
                    rainfall=weather['rainfall'],
                    wind_speed=weather['wind_speed'],
                    weather_condition=weather['weather_condition'],
                    source=weather['source']
                )
                
                self.alerts_count += 1
                return alert
        
        return None
    
    def check_rainstorm_warning(self) -> dict:
        """檢查暴雨警告"""
        weather = self.api.fetch_current_weather()
        rainfall = weather['rainfall']
        
        if rainfall >= 30:
            severity = 'severe' if rainfall > 50 else 'high'
            alert_type = 'rainstorm_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '暴雨天氣警告',
                    'description': (
                        f"香港天文台發出暴雨天氣警告。"
                        f"過去一小時錄得超過 {int(rainfall)}毫米雨量。"
                        f"市民應提防水浸及山泥傾瀉。"
                    ),
                    'effect_start_time': weather['observation_time'],
                    'location': '香港天文台',
                    'metadata': {
                        'rainfall': rainfall,
                        'condition': '暴雨'
                    }
                }
                
                # 保存到數據庫
                self.db.save_log(
                    log_id=f"alert_rain_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"暴雨天氣警告：{int(rainfall)}mm",
                    agent_id="weather",
                    context=alert
                )
                
                # 保存天氣數據
                data_id = f"weather_{int(time.time())}"
                self.db.save_weather_data(
                    data_id=data_id,
                    observation_time=weather['observation_time'],
                    temperature=weather['temperature'],
                    humidity=weather['humidity'],
                    rainfall=rainfall,
                    wind_speed=weather['wind_speed'],
                    weather_condition=weather['weather_condition'],
                    source=weather['source']
                )
                
                self.alerts_count += 1
                return alert
        
        return None
    
    def check_strong_wind_warning(self) -> dict:
        """檢查強風警告"""
        weather = self.api.fetch_current_weather()
        wind_speed = weather['wind_speed']
        
        if wind_speed >= 40:
            severity = 'severe' if wind_speed > 60 else 'high'
            alert_type = 'strong_wind_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '強風警告',
                    'description': (
                        f"香港風力正在增強，平均風速達 {int(wind_speed)}公里/小時。"
                        f"市民應避免在風力強勁的地方逗留。"
                    ),
                    'effect_start_time': weather['observation_time'],
                    'location': '香港天文台',
                    'metadata': {
                        'wind_speed': wind_speed,
                        'condition': '強風'
                    }
                }
                
                # 保存到數據庫
                self.db.save_log(
                    log_id=f"alert_wind_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"強風警告：{int(wind_speed)}km/h",
                    agent_id="weather",
                    context=alert
                )
                
                # 保存天氣數據
                data_id = f"weather_{int(time.time())}"
                self.db.save_weather_data(
                    data_id=data_id,
                    observation_time=weather['observation_time'],
                    temperature=weather['temperature'],
                    humidity=weather['humidity'],
                    rainfall=weather['rainfall'],
                    wind_speed=wind_speed,
                    weather_condition=weather['weather_condition'],
                    source=weather['source']
                )
                
                self.alerts_count += 1
                return alert
        
        return None
    
    def check_all_alerts(self) -> list:
        """檢查所有警報"""
        alerts = []
        
        # 1. 檢查酷熱
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
            print(f"[ALERT] 檢測到酷熱警告：{int(heat_alert['metadata']['temperature'])}度")
        
        # 2. 檢查暴雨
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
            print(f"[ALERT] 檢測到暴雨警告：{int(rain_alert['metadata']['rainfall'])}mm")
        
        # 3. 檢查強風
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
            print(f"[ALERT] 檢測到強風警告：{int(wind_alert['metadata']['wind_speed'])}km/h")
        
        return alerts
    
    def should_send_alert(self, alert_type, severity):
        """判斷是否應該發送警報"""
        now = datetime.now(HK_TZ)
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:  # 1小時內不重複
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True
    
    def monitor(self):
        """持續監控"""
        print("=" * 60)
        print("天氣監控系統啟動")
        print("=" * 60)
        print()
        print("監控配置：")
        print(f"  檢查頻率：每 {self.check_interval // 60} 分鐘")
        print("  警告類型：酷熱、暴雨、強風、颱風")
        print("  通知發送：模擬（需集成 Telegram/WhatsApp）")
        print("  數據庫：模擬（需連接實際數據庫）")
        print()
        print("=" * 60)
        print()
        
        while self.running:
            try:
                check_time = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{check_time}] 開始第 {self.check_count + 1} 次檢查...")
                print()
                
                # 1. 獲取當前天氣
                print("  [1/3] 獲取當前天氣...")
                weather = self.api.fetch_current_weather()
                
                print(f"      溫度：{weather['temperature']}度")
                print(f"      濕度：{weather['humidity']}%")
                print(f"      降雨：{weather['rainfall']}mm")
                print(f"      風速：{weather['wind_speed']}km/h")
                print(f"      風向：{weather['wind_direction']}")
                print(f"      天氣：{weather['weather_condition']}")
                print(f"      時間：{weather['observation_time'].strftime('%H:%M:%S')}")
                
                self.weather_updates += 1
                print()
                
                # 2. 檢查警告
                print("  [2/3] 檢查天氣警告...")
                alerts = self.check_all_alerts()
                
                if alerts:
                    print(f"      檢測到 {len(alerts)} 個警告：")
                    for i, alert in enumerate(alerts, 1):
                        print(f"        {i}. {alert['title']} ({alert['severity']})")
                else:
                    print("      無警告")
                
                print()
                
                # 3. 顯示預報
                print("  [3/3] 獲取天氣預報...")
                forecast = self.api.fetch_forecast(self.forecast_hours)
                
                print(f"      未來 {self.forecast_hours} 小時預報：")
                for i, item in enumerate(forecast[:6]):  # 顯示前 6 個
                    time_str = item['time'].strftime('%H:%M')
                    print(f"        {time_str} - {item['weather']}, {item['temperature']}度")
                
                print()
                print("=" * 60)
                print()
                print(f"統計數據：")
                print(f"  檢查次數：{self.check_count + 1}")
                print(f"  警報數量：{self.alerts_count}")
                print(f"  天氣更新：{self.weather_updates}")
                print()
                print("=" * 60)
                print()
                
                # 更新檢查次數
                self.check_count += 1
                
                # 等待下一次檢查
                print(f"[{check_time}] 等待 {self.check_interval // 60} 分鐘後進行下次檢查...")
                print()
                print("-" * 60)
                print()
                
                for i in range(self.check_interval, 0, -1):
                    if not self.running:
                        break
                    
                    # 每 60 秒顯示一次倒數
                    if i % 60 == 0:
                        remaining = i // 60
                        print(f"[{datetime.now(HK_TZ).strftime('%H:%M:%S')}] 剩餘：{remaining} 分鐘")
                        sys.stdout.flush()
                    
                    time.sleep(1)
                
            except KeyboardInterrupt:
                print()
                print("=" * 60)
                print("監控已停止")
                print("=" * 60)
                self.running = False
                break
            except Exception as e:
                print(f"[ERROR] 監控過程出錯：{e}")
                time.sleep(60)
        
        print("監控系統已退出")


def main():
    """主函數"""
    print("天氣監控系統")
    print("=" * 60)
    print()
    print("功能：")
    print("  1. 持續監控天氣")
    print("  2. 自動檢測所有警告")
    print("  3. 保存警報到數據庫")
    print("  4. 顯示天氣預報")
    print()
    print("=" * 60)
    print()
    
    # 創建數據庫連接
    db = MockDatabase()
    
    # 創建 API 客戶端
    api_client = HKOAPIClient()
    
    # 創建監控器
    monitor = WeatherMonitor(db, api_client)
    
    # 啟動監控
    monitor.monitor()


if __name__ == "__main__":
    main()
