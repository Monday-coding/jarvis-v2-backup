#!/usr/bin/env python3
"""
獨立測試天氣監控系統
無限循環，不受超時限制
"""

from datetime import datetime, timezone, timedelta
import time

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class SimpleWeatherMonitor:
    """簡單的天氣監控器"""
    
    def __init__(self):
        # 模擬天氣數據
        self.temperature = 28.0
        self.humidity = 75
        self.rainfall = 5.0
        self.wind_speed = 15.0
        
        # 監控狀態
        self.check_count = 0
        self.alerts_count = 0
    
    def update_weather(self):
        """更新天氣數據（模擬變化）"""
        import random
        
        # 隨機變化
        self.temperature += random.uniform(-0.5, 0.5)
        self.humidity += random.uniform(-2, 2)
        self.rainfall += random.uniform(-1, 1)
        self.wind_speed += random.uniform(-2, 2)
        
        # 限制範圍
        self.temperature = max(15, min(38, self.temperature))
        self.humidity = max(30, min(95, self.humidity))
        self.rainfall = max(0, min(100, self.rainfall))
        self.wind_speed = max(0, min(80, self.wind_speed))
        
        # 10% 概率觸發特殊天氣
        if random.random() < 0.1:
            weather_type = random.choice(['酷熱', '暴雨', '強風'])
            
            if weather_type == '酷熱':
                self.temperature = random.uniform(33, 36)
            elif weather_type == '暴雨':
                self.rainfall = random.uniform(30, 50)
            elif weather_type == '強風':
                self.wind_speed = random.uniform(40, 50)
    
    def check_alerts(self):
        """檢查所有警報"""
        alerts = []
        
        # 酷熱警告
        if self.temperature >= 33:
            alerts.append({
                'type': 'heat_warning',
                'severity': 'high' if self.temperature > 35 else 'moderate',
                'value': self.temperature,
                'threshold': 33
            })
        
        # 暴雨警告
        if self.rainfall >= 30:
            alerts.append({
                'type': 'rainstorm_warning',
                'severity': 'severe' if self.rainfall > 50 else 'high',
                'value': self.rainfall,
                'threshold': 30
            })
        
        # 強風警告
        if self.wind_speed >= 40:
            alerts.append({
                'type': 'strong_wind_warning',
                'severity': 'severe' if self.wind_speed > 60 else 'high',
                'value': self.wind_speed,
                'threshold': 40
            })
        
        return alerts
    
    def run_monitor(self):
        """運行監控（5 個循環）"""
        print("=" * 60)
        print("天氣監控系統測試")
        print("=" * 60)
        print()
        
        for i in range(5):
            print(f"循環 {i+1}/5")
            print("-" * 40)
            
            # 更新天氣
            self.update_weather()
            
            # 顯示當前天氣
            print(f"溫度：{self.temperature:.1f}度")
            print(f"濕度：{self.humidity:.0f}%")
            print(f"降雨：{self.rainfall:.1f}mm")
            print(f"風速：{self.wind_speed:.1f}km/h")
            print()
            
            # 檢查警報
            alerts = self.check_alerts()
            
            if alerts:
                print(f"檢測到 {len(alerts)} 個警告：")
                for j, alert in enumerate(alerts, 1):
                    emoji = "🔥" if alert['type'] == 'heat_warning' else "🌧" if alert['type'] == 'rainstorm_warning' else "💨"
                    severity = alert['severity']
                    value = alert['value']
                    
                    print(f"  {j}. {emoji} {alert['type'].replace('_', ' ').title()} ({severity})")
                    print(f"     當前值：{value:.1f}，閾值：{alert['threshold']}")
                
                    self.alerts_count += 1
            else:
                print("無警告")
            
            self.check_count += 1
            print()
            print("=" * 60)
            print()
            
            # 等待 2 秒
            time.sleep(2)
        
        # 總結
        print("測試完成")
        print("=" * 60)
        print()
        print(f"總檢查次數：{self.check_count}")
        print(f"總警報次數：{self.alerts_count}")
        print()
        print("監控系統測試通過！")


def main():
    """主函數"""
    monitor = SimpleWeatherMonitor()
    monitor.run_monitor()


if __name__ == "__main__":
    main()
