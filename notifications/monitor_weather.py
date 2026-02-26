#!/usr/bin/env python3
"""
實時天氣監控系統
持續監控、檢查警告、發送通知
"""

import sys
import os
import time
import json
from datetime import datetime, timezone, timedelta

# 模擬數據庫連接
class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts_history = []
    
    def save_log(self, log_id, level, category, message, agent_id, context=None, metadata=None):
        """保存日誌"""
        log_entry = {
            'log_id': log_id,
            'timestamp': datetime.now(timezone(timedelta(hours=8))).isoformat(),
            'level': level,
            'category': category,
            'message': message,
            'agent_id': agent_id,
            'context': context,
            'metadata': metadata
        }
        self.alerts_history.append(log_entry)
        print(f"[{level}] {message}")


class WeatherMonitor:
    """天氣監控器"""
    
    def __init__(self, db):
        self.db = db
        self.last_alert_time = {}
        self.running = True
        
        # 模擬天氣數據（實際應該從 HKO API 獲取）
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
        
        # 模擬天氣場景
        self.weather_scenarios = [
            {
                'name': '正常天氣',
                'temperature': 28.0,
                'rainfall': 5.0,
                'wind_speed': 15.0
            },
            {
                'name': '酷熱天氣',
                'temperature': 34.0,
                'rainfall': 5.0,
                'wind_speed': 15.0
            },
            {
                'name': '暴雨天氣',
                'temperature': 25.0,
                'rainfall': 35.0,
                'wind_speed': 20.0
            },
            {
                'name': '強風天氣',
                'temperature': 22.0,
                'rainfall': 15.0,
                'wind_speed': 45.0
            },
            {
                'name': '多種警告',
                'temperature': 34.0,
                'rainfall': 40.0,
                'wind_speed': 25.0
            }
        ]
        
        self.current_scenario = 0
    
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
                    'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {temp}度。"
                }
                
                # 保存到數據庫
                self.db.save_log(
                    log_id=f"alert_heat_{int(time.time())}",
                    level="WARNING" if severity == 'high' else "INFO",
                    category="weather",
                    message=f"酷熱天氣警告：{temp}度",
                    agent_id="weather",
                    context=alert
                )
                
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
                    'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {rainfall}毫米雨量。"
                }
                
                self.db.save_log(
                    log_id=f"alert_rain_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"暴雨天氣警告：{rainfall}mm",
                    agent_id="weather",
                    context=alert
                )
                
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
                    'description': f"香港風力正在增強，平均風速達 {wind_speed}公里/小時。"
                }
                
                self.db.save_log(
                    log_id=f"alert_wind_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"強風警告：{wind_speed}km/h",
                    agent_id="weather",
                    context=alert
                )
                
                return alert
        
        return None
    
    def check_typhoon_warning(self):
        """檢查颱風警告"""
        # 模擬颱風（無條件）
        # 在實際應用中，應該從 HKO API 的警告信息獲取
        
        alert_type = 'typhoon_warning'
        severity = 'severe'
        
        # 檢查是否有颱風（僅在特定場景）
        if self.weather_scenarios[self.current_scenario]['name'] == '多種警告':
            alert = {
                'alert_type': alert_type,
                'severity': severity,
                'title': '颱風警告',
                'description': "香港天文台發出颱風警告。"
            }
            
            self.db.save_log(
                log_id=f"alert_typhoon_{int(time.time())}",
                level="WARNING",
                category="weather",
                message="颱風警告檢測到",
                agent_id="weather",
                context=alert
            )
            
            return alert
        
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
        
        # 4. 檢查颱風
        typhoon_alert = self.check_typhoon_warning()
        if typhoon_alert:
            alerts.append(typhoon_alert)
            print(f"[ALERT] 檢測到颱風警告")
        
        return alerts
    
    def should_send_alert(self, alert_type, severity):
        """判斷是否應該發送警告"""
        now = datetime.now(timezone(timedelta(hours=8)))
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:  # 1小時
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True
    
    def cycle_weather_scenario(self):
        """切換天氣場景（用於測試）"""
        self.current_scenario = (self.current_scenario + 1) % len(self.weather_scenarios)
        self.current_weather = self.weather_scenarios[self.current_scenario]
        
        scenario_name = self.current_weather['name']
        temp = self.current_weather['temperature']
        humidity = self.current_weather['humidity']
        rainfall = self.current_weather['rainfall']
        wind_speed = self.current_weather['wind_speed']
        wind_direction = self.current_weather['wind_direction']
        weather_condition = self.current_weather['weather_condition']
        
        print(f"[SCENARIO] 切換到場景：{scenario_name}")
        print(f"  溫度：{temp}度")
        print(f"  濕度：{humidity}%")
        print(f"  降雨：{rainfall}mm")
        print(f"  風速：{wind_speed}km/h")
        print(f"  風向：{wind_direction}")
        print(f"  天氣：{weather_condition}")
        print()
    
    def monitor(self):
        """持續監控"""
        print("=" * 60)
        print("天氣監控系統啟動")
        print("=" * 60)
        print()
        print("監控配置：")
        print("  檢查頻率：每 5 分鐘")
        print("  警報類型：酷熱、暴雨、強風、颱風")
        print("  通知發送：模擬（需集成 Telegram/WhatsApp）")
        print()
        print("=" * 60)
        print()
        
        cycle_count = 0
        
        while self.running:
            try:
                print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 開始檢查...")
                print()
                
                # 每 5 分鐘切換一次場景（用於測試）
                if cycle_count % 5 == 0:
                    self.cycle_weather_scenario()
                    cycle_count += 1
                
                # 檢查所有警告
                alerts = self.check_all_alerts()
                
                if alerts:
                    print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 發現 {len(alerts)} 個警告：")
                    
                    for i, alert in enumerate(alerts, 1):
                        print(f"  {i}. {alert['title']} ({alert['severity']})")
                        print(f"     {alert['description']}")
                        print()
                    
                    print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 警報已處理")
                    print()
                else:
                    print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 無警告")
                    print()
                
                print("-" * 40)
                print()
                
                # 等待 5 分鐘
                print(f"[{datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}] 等待 300 秒...")
                print()
                
                for i in range(300, 0, -1):
                    if not self.running:
                        break
                    
                    # 每 60 秒顯示一次倒數
                    if i % 60 == 0:
                        remaining = i / 60
                        print(f"  剩餘：{remaining} 分鐘")
                        sys.stdout.flush()
                    
                    time.sleep(1)
                
                print()
                print("=" * 60)
                print()
                
            except KeyboardInterrupt:
                print()
                print("=" * 60)
                print("監控已停止")
                print("=" * 60)
                self.running = False
                break
            except Exception as e:
                print(f"錯誤：{e}")
                time.sleep(60)
        
        print("監控系統已退出")


def main():
    """主函數"""
    print("天氣監控系統")
    print("=" * 60)
    print()
    print("功能：")
    print("  1. 持續監控天氣狀況")
    print("  2. 自動檢測四種警告類型")
    print("  3. 自動保存警報到數據庫")
    print("  4. 支持通知發送（需集成 Telegram/WhatsApp）")
    print()
    print("=" * 60)
    print()
    
    # 創建數據庫連接
    db = MockDatabase()
    
    # 創建監控器
    monitor = WeatherMonitor(db)
    
    # 啟動監控
    monitor.monitor()


if __name__ == "__main__":
    main()
