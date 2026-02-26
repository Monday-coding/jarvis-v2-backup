#!/usr/bin/env python3
"""
實時天氣監控系統 - 簡化版本
持續監控、檢查警告、發送通知
"""

import sys
import os
import time
import json
from datetime import datetime, timezone, timedelta

# 模擬的數據庫連接
class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts_history = []
        self.alerts_sent = 0
        
    def save_log(self, log_id, level, category, message, agent_id, context=None, metadata=None):
        """保存日誌"""
        alert = {
            'log_id': log_id,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'category': category,
            'message': message,
            'agent_id': agent_id,
            'context': context,
            'metadata': metadata
        }
        self.alerts_history.append(alert)
        self.alerts_sent += 1
        return alert
    
    def execute_query(self, query, params=None):
        """執行查詢"""
        return []


class WeatherMonitor:
    """天氣監控器 - 簡化版本"""
    
    def __init__(self, db):
        self.db = db
        self.last_alert_time = {}
        self.running = False
        
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
    
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
                    'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {temp}度。",
                    'effect_start_time': datetime.now(timezone(timedelta(hours=8))),
                    'location': '香港天文台',
                    'metadata': {
                        'temperature': temp,
                        'condition': '酷熱'
                    }
                }
                
                self.db.save_log(
                    log_id=f"alert_heat_{int(datetime.now().timestamp())}",
                    level="WARNING",
                    category="weather",
                    message=f"酷熱天氣警告：{temp}度",
                    agent_id="weather",
                    context=alert
                )
                
                print(f"[ALERT] 酷熱警告（{severity}）：{temp}度")
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
                    'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {rainfall}毫米雨量。",
                    'effect_start_time': datetime.now(timezone(timedelta(hours=8))),
                    'location': '香港天文台',
                    'metadata': {
                        'rainfall': rainfall,
                        'condition': '暴雨'
                    }
                }
                
                self.db.save_log(
                    log_id=f"alert_rain_{int(datetime.now().timestamp())}",
                    level="WARNING",
                    category="weather",
                    message=f"暴雨天氣警告：{rainfall}mm",
                    agent_id="weather",
                    context=alert
                )
                
                print(f"[ALERT] 暴雨警告（{severity}）：{rainfall}mm")
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
                    'description': f"香港風力正在增強，平均風速達 {wind_speed}公里/小時。市民應避免在風力強勁的地方逗留。",
                    'effect_start_time': datetime.now(timezone(timedelta(hours=8))),
                    'location': '香港天文台',
                    'metadata': {
                        'wind_speed': wind_speed,
                        'condition': '強風'
                    }
                }
                
                self.db.save_log(
                    log_id=f"alert_wind_{int(datetime.now().timestamp())}",
                    level="WARNING",
                    category="weather",
                    message=f"強風警告：{wind_speed}km/h",
                    agent_id="weather",
                    context=alert
                )
                
                print(f"[ALERT] 強風警告（{severity}）：{wind_speed}km/h")
                return alert
        
        return None
    
    def check_all_alerts(self):
        """檢查所有警告"""
        alerts = []
        
        # 1. 檢查酷熱
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
        
        # 2. 檢查暴雨
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
        
        # 3. 檢查強風
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
        
        return alerts
    
    def should_send_alert(self, alert_type, severity):
        """判斷是否應該發送警告"""
        now = datetime.now(timezone(timedelta(hours=8)))
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:  # 1小時內不重複
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True
    
    def run_quick_check(self):
        """快速檢查一次（10秒）"""
        print("=" * 60)
        print("天氣監控系統 - 快速檢查")
        print("=" * 60)
        print()
        
        print("當前天氣：")
        print(f"  溫度：{self.current_weather['temperature']}度")
        print(f"  濕度：{self.current_weather['humidity']}%")
        print(f"  降雨：{self.current_weather['rainfall']}mm")
        print(f"  風速：{self.current_weather['wind_speed']}km/h")
        print()
        
        # 檢查警告
        alerts = self.check_all_alerts()
        
        if alerts:
            print(f"檢測到 {len(alerts)} 個警告：")
            for i, alert in enumerate(alerts, 1):
                print(f"  {i}. {alert['title']} ({alert['severity']})")
                print(f"     {alert['description']}")
                print()
        else:
            print("無警告")
        
        print()
        print("=" * 60)
        print(f"總警報記錄：{self.db.alerts_sent}")
        print("=" * 60)
        print()
        
        return alerts


def main():
    """主函數 - 快速檢查版本"""
    print("天氣監控系統啟動")
    print("=" * 60)
    print()
    
    # 創建數據庫和監控器
    db = MockDatabase()
    monitor = WeatherMonitor(db)
    
    # 快速檢查
    alerts = monitor.run_quick_check()
    
    print("監控系統測試完成！")
    print()
    print("注意：")
    print("  1. 持續監控需要配置超時和後台運行")
    print("  2. 通知發送需要配置 Telegram/WhatsApp API")
    print("  3. 真實數據需要連接 HKO API")
    print()
    print("準備就緒，可以開始正式運行！")


if __name__ == "__main__":
    main()
