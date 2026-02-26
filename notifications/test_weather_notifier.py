#!/usr/bin/env python3
"""
天氣通知系統（測試版）
Weather Agent 調用
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta

# 模擬數據庫連接
class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts_sent = []
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨'
        }
    
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
        self.alerts_sent.append(alert)
        print(f"[{level}] {message}")
    
    def save_metric(self, metric_id, metric_name, metric_value, metric_type, agent_id, metadata=None):
        """保存指標"""
        print(f"[METRIC] {metric_name}: {metric_value}")


class WeatherMonitor:
    """天氣監控器"""
    
    def __init__(self):
        self.db = MockDatabase()
        self.last_alert_time = {}
    
    def check_heat_warning(self):
        """檢查酷熱警告"""
        temp = self.db.current_weather['temperature']
        
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
                
                # 保存到數據庫
                self.db.save_log(
                    log_id=f"alert_heat_{int(datetime.now().timestamp())}",
                    level="WARNING",
                    category="weather",
                    message=f"酷熱天氣警告：{temp}度",
                    agent_id="weather",
                    context=alert
                )
                
                return alert
        
        return None
    
    def check_rainstorm_warning(self):
        """檢查暴雨警告"""
        rainfall = self.db.current_weather['rainfall']
        
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
                
                return alert
        
        return None
    
    def check_strong_wind_warning(self):
        """檢查強風警告"""
        wind_speed = self.db.current_weather['wind_speed']
        
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
                
                return alert
        
        return None
    
    def check_typhoon_warning(self):
        """檢查颱風警告"""
        # 模擬颱風警告（無條件，僅作為示例）
        typhoon_keywords = ['颱風', '熱帶氣旋', '熱帶風暴']
        
        if any(keyword in '天氣' for keyword in typhoon_keywords):
            alert_type = 'typhoon_warning'
            severity = 'severe'
            
            alert = {
                'alert_type': alert_type,
                'severity': severity,
                'title': '颱風警告',
                'description': "香港天文台發出颱風警告。",
                'effect_start_time': datetime.now(timezone(timedelta(hours=8))),
                'location': '香港天文台',
                'metadata': {
                    'condition': '颱風'
                }
            }
            
            self.db.save_log(
                log_id=f"alert_typhoon_{int(datetime.now().timestamp())}",
                level="WARNING",
                category="weather",
                message="颱風警告檢測到",
                agent_id="weather",
                context=alert
            )
            
            return alert
        
        return None
    
    def check_all_alerts(self):
        """檢查所有警報"""
        alerts = []
        
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
            print("[ALERT] 檢測到酷熱警告")
        
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
            print("[ALERT] 檢測到暴雨警告")
        
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
            print("[ALERT] 檢測到強風警告")
        
        typhoon_alert = self.check_typhoon_warning()
        if typhoon_alert:
            alerts.append(typhoon_alert)
            print("[ALERT] 檢測到颱風警告")
        
        return alerts
    
    def should_send_alert(self, alert_type, severity):
        """判斷是否應該發送警報"""
        now = datetime.now(timezone(timedelta(hours=8)))
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:  # 1小時
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True


def simulate_weather_monitor():
    """模擬天氣監控"""
    print("=" * 60)
    print("天氣監控系統（測試版）")
    print("=" * 60)
    print()
    
    monitor = WeatherMonitor()
    
    # 模擬 5 次檢查
    for i in range(5):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 第 {i+1} 次天氣檢查")
        print()
        
        # 模擬不同天氣條件
        test_cases = [
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
                'wind_speed': 45.0
            }
        ]
        
        # 測試所有情況
        for case in test_cases:
            monitor.db.current_weather = case
            alerts = monitor.check_all_alerts()
            
            if alerts:
                print(f"  檢測到 {len(alerts)} 個警告：")
                for alert in alerts:
                    print(f"    - {alert['title']} ({alert['severity']})")
            else:
                print("  無警告")
        
        print()
        
        # 等待 1 秒
        import time
        time.sleep(1)
    
    # 總結
    print()
    print("=" * 60)
    print("測試完成")
    print("=" * 60)
    print()
    print("總警報記錄：")
    print()
    
    for alert in monitor.db.alerts_sent:
        print(f"{alert['timestamp']}: {alert['message']}")
    
    print()
    print("通知系統準備就緒（實際應用需要連接 Telegram/WhatsApp）")


def main():
    """主函數"""
    print("天氣通知系統測試")
    print("=" * 60)
    print()
    
    simulate_weather_monitor()


if __name__ == "__main__":
    main()
