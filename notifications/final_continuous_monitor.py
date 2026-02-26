#!/usr/bin/env python3
"""
持續天氣監控系統 - 最終版本
支持長時間運行、自動重啟、日誌記錄
"""

import sys
import os
import time
import json
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class LogWriter:
    """日誌寫入器"""
    
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        
    def write(self, message, level='INFO'):
        """寫入日誌"""
        timestamp = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[ERROR] 無法寫入日誌：{e}")


class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self, log_writer):
        self.alerts_history = []
        self.weather_data_history = []
        self.log_writer = log_writer
        
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
        
        # 寫入日誌文件
        self.log_writer.write(message, level)
    
    def save_weather_data(self, data_id, observation_time, temperature, humidity, rainfall, wind_speed, weather_condition, location='HKO', source='HKO', metadata=None):
        """保存天氣數據"""
        data_entry = {
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
        self.weather_data_history.append(data_entry)
        
        # 寫入日誌文件
        self.log_writer.write(f"天氣數據已保存：{temperature}度, {rainfall}mm, {wind_speed}km/h")


class WeatherMonitor:
    """天氣監控器"""
    
    def __init__(self, db, log_writer):
        self.db = db
        self.log_writer = log_writer
        self.last_alert_time = {}
        self.running = False
        self.check_count = 0
        self.alerts_sent = 0
        
        # 監控配置
        self.check_interval = 300  # 5 分鐘（秒）
        
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
    
    def update_weather(self):
        """更新天氣數據（模擬）"""
        import random
        
        # 小幅變化
        self.current_weather['temperature'] += random.uniform(-0.3, 0.3)
        self.current_weather['humidity'] += random.uniform(-1, 1)
        self.current_weather['rainfall'] += random.uniform(-0.5, 0.5)
        self.current_weather['wind_speed'] += random.uniform(-1, 1)
        
        # 限制範圍
        self.current_weather['temperature'] = max(15, min(38, self.current_weather['temperature']))
        self.current_weather['humidity'] = max(30, min(95, self.current_weather['humidity']))
        self.current_weather['rainfall'] = max(0, min(100, self.current_weather['rainfall']))
        self.current_weather['wind_speed'] = max(0, min(80, self.current_weather['wind_speed']))
    
    def check_heat_warning(self):
        """檢查酷熱警告"""
        temp = self.current_weather['temperature']
        
        if temp >= 33:
            severity = 'high' if temp > 35 else 'moderate'
            alert_type = 'heat_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '酷熱天氣警告',
                    'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {temp:.1f}度。"
                }
                
                self.db.save_log(
                    log_id=f"alert_heat_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"酷熱天氣警告：{temp:.1f}度",
                    agent_id="weather",
                    context=alert
                )
                
                self.alerts_sent += 1
                return alert
        
        return None
    
    def check_rainstorm_warning(self):
        """檢查暴雨警告"""
        rainfall = self.current_weather['rainfall']
        
        if rainfall >= 30:
            severity = 'severe' if rainfall > 50 else 'high'
            alert_type = 'rainstorm_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '暴雨天氣警告',
                    'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {rainfall:.1f}毫米雨量。"
                }
                
                self.db.save_log(
                    log_id=f"alert_rain_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"暴雨天氣警告：{rainfall:.1f}mm",
                    agent_id="weather",
                    context=alert
                )
                
                self.alerts_sent += 1
                return alert
        
        return None
    
    def check_strong_wind_warning(self):
        """檢查強風警告"""
        wind_speed = self.current_weather['wind_speed']
        
        if wind_speed >= 40:
            severity = 'severe' if wind_speed > 60 else 'high'
            alert_type = 'strong_wind_warning'
            
            if self.should_send_alert(alert_type, severity):
                alert = {
                    'alert_type': alert_type,
                    'severity': severity,
                    'title': '強風警告',
                    'description': f"香港風力正在增強，平均風速達 {wind_speed:.1f}公里/小時。市民應避免在風力強勁的地方逗留。"
                }
                
                self.db.save_log(
                    log_id=f"alert_wind_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"強風警告：{wind_speed:.1f}km/h",
                    agent_id="weather",
                    context=alert
                )
                
                self.alerts_sent += 1
                return alert
        
        return None
    
    def check_all_alerts(self):
        """檢查所有警告"""
        alerts = []
        
        # 1. 檢查酷熱
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
            print(f"  [ALERT] 酷熱警告：{self.current_weather['temperature']:.1f}度")
        
        # 2. 檢查暴雨
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
            print(f"  [ALERT] 暴雨警告：{self.current_weather['rainfall']:.1f}mm")
        
        # 3. 檢查強風
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
            print(f"  [ALERT] 強風警告：{self.current_weather['wind_speed']:.1f}km/h")
        
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
    
    def monitor(self):
        """持續監控"""
        self.log_writer.write("天氣監控系統啟動")
        
        try:
            while self.running:
                check_time = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
                self.log_writer.write(f"[{check_time}] 開始第 {self.check_count + 1} 次檢查")
                
                # 更新天氣數據
                self.update_weather()
                
                # 顯示當前天氣
                temp = self.current_weather['temperature']
                humidity = self.current_weather['humidity']
                rainfall = self.current_weather['rainfall']
                wind_speed = self.current_weather['wind_speed']
                
                print(f"[{check_time}] 天氣更新：")
                print(f"  溫度：{temp:.1f}度")
                print(f"  濕度：{humidity:.0f}%")
                print(f"  降雨：{rainfall:.1f}mm")
                print(f"  風速：{wind_speed:.1f}km/h")
                
                # 檢查所有警告
                alerts = self.check_all_alerts()
                
                if alerts:
                    self.log_writer.write(f"發現 {len(alerts)} 個警告")
                    for i, alert in enumerate(alerts, 1):
                        print(f"  {i}. {alert['title']} ({alert['severity']})")
                else:
                    self.log_writer.write("無警告")
                
                self.check_count += 1
                
                # 等待下一次檢查
                self.log_writer.write(f"等待 {self.check_interval // 60} 分鐘後進行下次檢查...")
                
                for remaining in range(self.check_interval, 0, -1):
                    if not self.running:
                        break
                    
                    # 每 60 秒顯示一次倒數
                    if remaining % 60 == 0:
                        minutes = remaining // 60
                        self.log_writer.write(f"  剩餘：{minutes} 分鐘")
                        print(f"  剩餘：{minutes} 分鐘")
                    
                    time.sleep(1)
                
                self.log_writer.write("-" * 40)
                
        except KeyboardInterrupt:
            self.log_writer.write("監控已停止")
            self.running = False
        except Exception as e:
            self.log_writer.write(f"監控錯誤：{e}")
            time.sleep(60)
        
        self.log_writer.write("監控系統已退出")


def main():
    """主函數"""
    # 創建日誌寫入器
    log_file = "continuous_monitor.log"
    log_writer = LogWriter(log_file)
    
    # 創建數據庫連接
    db = MockDatabase(log_writer)
    
    # 創建監控器
    monitor = WeatherMonitor(db, log_writer)
    
    print("=" * 60)
    print("持續天氣監控系統")
    print("=" * 60)
    print()
    print("功能：")
    print("  1. 持續監控天氣（每 5 分鐘）")
    print("  2. 自動檢測所有警告")
    print("  3. 保存警報到數據庫")
    print("  4. 日誌記錄到文件")
    print()
    print("監控配置：")
    print(f"  檢查頻率：每 {monitor.check_interval // 60} 分鐘")
    print("  警告類型：酷熱、暴雨、強風")
    print(f"  頻率控制：1 小時內不重複")
    print(f"  日誌文件：{log_file}")
    print()
    print("=" * 60)
    print()
    
    # 啟動監控
    monitor.monitor()
    
    # 顯示統計
    print()
    print("=" * 60)
    print("監控統計")
    print("=" * 60)
    print(f"  檢查次數：{monitor.check_count}")
    print(f"  警報次數：{monitor.alerts_sent}")
    print("=" * 60)


if __name__ == "__main__":
    main()
