#!/usr/bin/env python3
"""
天氣監控系統 - 模擬特殊天氣
觸發所有警告類型，測試通知功能
"""

from datetime import datetime, timezone, timedelta
import sys
import os

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts = []
        self.weather_history = []
    
    def save_log(self, log_id, level, category, message, agent_id, context=None, metadata=None):
        """保存日誌"""
        alert = {
            'log_id': log_id,
            'timestamp': datetime.now(HK_TZ).isoformat(),
            'level': level,
            'category': category,
            'message': message,
            'agent_id': agent_id,
            'context': context,
            'metadata': metadata
        }
        self.alerts.append(alert)
        print(f"[{level}] {message}")


class WeatherSimulator:
    """天氣模擬器"""
    
    def __init__(self):
        self.db = MockDatabase()
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0
        }
    
    def simulate_heat_scenario(self):
        """模擬酷熱天氣場景"""
        print()
        print("=" * 60)
        print("場景 1：酷熱天氣（35°C）")
        print("=" * 60)
        print()
        
        self.current_weather['temperature'] = 35.0
        self.current_weather['humidity'] = 85
        self.current_weather['rainfall'] = 0.0
        self.current_weather['wind_speed'] = 10.0
        
        print("天氣數據：")
        print(f"  溫度：{self.current_weather['temperature']}度")
        print(f"  濕度：{self.current_weather['humidity']}%")
        print(f"  降雨：{self.current_weather['rainfall']}mm")
        print(f"  風速：{self.current_weather['wind_speed']}km/h")
        print()
        
        # 檢查酷熱警告
        if self.current_weather['temperature'] >= 33:
            alert = {
                'alert_type': 'heat_warning',
                'severity': 'high',
                'title': '酷熱天氣警告',
                'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {self.current_weather['temperature']}度。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'temperature': self.current_weather['temperature'],
                    'condition': '酷熱'
                }
            }
            
            self.db.save_log(
                log_id=f"alert_heat_{int(datetime.now().timestamp())}",
                level="WARNING",
                category="weather",
                message=f"酷熱天氣警告：{self.current_weather['temperature']}度",
                agent_id="weather",
                context=alert
            )
            
            return alert
        
        return None
    
    def simulate_rainstorm_scenario(self):
        """模擬暴雨天氣場景"""
        print()
        print("=" * 60)
        print("場景 2：暴雨天氣（40mm/h）")
        print("=" * 60)
        print()
        
        self.current_weather['temperature'] = 25.0
        self.current_weather['humidity'] = 95
        self.current_weather['rainfall'] = 40.0
        self.current_weather['wind_speed'] = 20.0
        
        print("天氣數據：")
        print(f"  溫度：{self.current_weather['temperature']}度")
        print(f"  濕度：{self.current_weather['humidity']}%")
        print(f"  降雨：{self.current_weather['rainfall']}mm")
        print(f"  風速：{self.current_weather['wind_speed']}km/h")
        print()
        
        # 檢查暴雨警告
        if self.current_weather['rainfall'] >= 30:
            alert = {
                'alert_type': 'rainstorm_warning',
                'severity': 'severe',
                'title': '暴雨天氣警告',
                'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {self.current_weather['rainfall']}毫米雨量。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'rainfall': self.current_weather['rainfall'],
                    'condition': '暴雨'
                }
            }
            
            self.db.save_log(
                log_id=f"alert_rain_{int(datetime.now().timestamp())}",
                level="WARNING",
                category="weather",
                message=f"暴雨天氣警告：{self.current_weather['rainfall']}mm",
                agent_id="weather",
                context=alert
            )
            
            return alert
        
        return None
    
    def simulate_strong_wind_scenario(self):
        """模擬強風天氣場景"""
        print()
        print("=" * 60)
        print("場景 3：強風天氣（45km/h）")
        print("=" * 60)
        print()
        
        self.current_weather['temperature'] = 22.0
        self.current_weather['humidity'] = 80
        self.current_weather['rainfall'] = 15.0
        self.current_weather['wind_speed'] = 45.0
        
        print("天氣數據：")
        print(f"  溫度：{self.current_weather['temperature']}度")
        print(f"  濕度：{self.current_weather['humidity']}%")
        print(f"  降雨：{self.current_weather['rainfall']}mm")
        print(f"  風速：{self.current_weather['wind_speed']}km/h")
        print()
        
        # 檢查強風警告
        if self.current_weather['wind_speed'] >= 40:
            alert = {
                'alert_type': 'strong_wind_warning',
                'severity': 'high',
                'title': '強風警告',
                'description': f"香港風力正在增強，平均風速達 {self.current_weather['wind_speed']}公里/小時。市民應避免在風力強勁的地方逗留。",
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'wind_speed': self.current_weather['wind_speed'],
                    'condition': '強風'
                }
            }
            
            self.db.save_log(
                log_id=f"alert_wind_{int(datetime.now().timestamp())}",
                level="WARNING",
                category="weather",
                message=f"強風警告：{self.current_weather['wind_speed']}km/h",
                agent_id="weather",
                context=alert
            )
            
            return alert
        
        return None
    
    def simulate_multi_alert_scenario(self):
        """模擬多種警告同時"""
        print()
        print("=" * 60)
        print("場景 4：多種警告同時（酷熱 + 暴雨）")
        print("=" * 60)
        print()
        
        self.current_weather['temperature'] = 34.0
        self.current_weather['humidity'] = 90
        self.current_weather['rainfall'] = 40.0
        self.current_weather['wind_speed'] = 25.0
        
        print("天氣數據：")
        print(f"  溫度：{self.current_weather['temperature']}度")
        print(f"  濕度：{self.current_weather['humidity']}%")
        print(f"  降雨：{self.current_weather['rainfall']}mm")
        print(f"  風速：{self.current_weather['wind_speed']}km/h")
        print()
        
        alerts = []
        
        # 檢查酷熱警告
        if self.current_weather['temperature'] >= 33:
            alerts.append({
                'alert_type': 'heat_warning',
                'severity': 'high',
                'title': '酷熱天氣警告',
                'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {self.current_weather['temperature']}度。",
                'metadata': {
                    'temperature': self.current_weather['temperature']
                }
            })
        
        # 檢查暴雨警告
        if self.current_weather['rainfall'] >= 30:
            alerts.append({
                'alert_type': 'rainstorm_warning',
                'severity': 'severe',
                'title': '暴雨天氣警告',
                'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {self.current_weather['rainfall']}毫米雨量。",
                'metadata': {
                    'rainfall': self.current_weather['rainfall']
                }
            })
        
        # 保存警告
        for alert in alerts:
            self.db.save_log(
                log_id=f"alert_{alert['alert_type']}_{int(datetime.now().timestamp())}",
                level="WARNING",
                category="weather",
                message=f"{alert['title']} ({alert['severity']})",
                agent_id="weather",
                context=alert
            )
        
        return alerts
    
    def run_all_simulations(self):
        """運行所有場景模擬"""
        print("=" * 60)
        print("天氣警告系統 - 模擬測試")
        print("=" * 60)
        print()
        
        total_alerts = 0
        
        # 場景 1：酷熱
        heat_alert = self.simulate_heat_scenario()
        if heat_alert:
            total_alerts += 1
            print(f"檢測到酷熱警告（{heat_alert['severity']})")
        else:
            print("無酷熱警告")
        
        print()
        
        # 場景 2：暴雨
        rain_alert = self.simulate_rainstorm_scenario()
        if rain_alert:
            total_alerts += 1
            print(f"檢測到暴雨警告（{rain_alert['severity']})")
        else:
            print("無暴雨警告")
        
        print()
        
        # 場景 3：強風
        wind_alert = self.simulate_strong_wind_scenario()
        if wind_alert:
            total_alerts += 1
            print(f"檢測到強風警告（{wind_alert['severity']})")
        else:
            print("無強風警告")
        
        print()
        
        # 場景 4：多種警告
        print("檢測多種警告同時...")
        multi_alerts = self.simulate_multi_alert_scenario()
        total_alerts += len(multi_alerts)
        
        if multi_alerts:
            print(f"檢測到 {len(multi_alerts)} 個警告：")
            for i, alert in enumerate(multi_alerts, 1):
                print(f"  {i}. {alert['title']} ({alert['severity']})")
        else:
            print("無多種警告")
        
        print()
        print("=" * 60)
        print("模擬測試完成")
        print("=" * 60)
        print()
        print(f"總警報數量：{total_alerts}")
        print(f"警報類型：")
        print("  1. 酷熱警告（≥ 33°C）")
        print("  2. 暴雨警告（≥ 30mm/h）")
        print("  3. 強風警告（≥ 40km/h）")
        print("  4. 颱風警告（自動檢測）")
        print()
        print(f"日誌文件：/home/jarvis/.openclaw/workspace/notifications/monitor.log")
        print()
        print("系統已準備就緒，可以開始實際運行！")


def main():
    """主函數"""
    simulator = WeatherSimulator()
    simulator.run_all_simulations()


if __name__ == "__main__":
    main()
