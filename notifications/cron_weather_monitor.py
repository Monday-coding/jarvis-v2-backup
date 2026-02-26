#!/usr/bin/env python3
"""
天氣監控系統 - Cron Job 版本
每次運行只檢查一次，然後退出
"""

from datetime import datetime, timezone, timedelta
import random

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class WeatherMonitor:
    """天氣監控器 - Cron Job 版本"""
    
    def __init__(self):
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0
        }
        
        # 警告閾值
        self.heat_threshold = 33
        self.rain_threshold = 30
        self.wind_threshold = 40
        
        # 日誌文件
        self.log_file = "/home/jarvis/.openclaw/workspace/notifications/monitor.log"
    
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
            
            elif weather_type == '暴雨':
                self.current_weather['temperature'] = random.uniform(22, 26)
                self.current_weather['humidity'] = random.uniform(90, 98)
                self.current_weather['rainfall'] = random.uniform(30, 50)
                self.current_weather['wind_speed'] = random.uniform(20, 30)
                self.current_weather['wind_direction'] = random.choice(['NE', 'SE', 'S'])
            
            elif weather_type == '強風':
                self.current_weather['temperature'] = random.uniform(20, 25)
                self.current_weather['humidity'] = random.uniform(70, 85)
                self.current_weather['rainfall'] = random.uniform(10, 20)
                self.current_weather['wind_speed'] = random.uniform(40, 50)
                self.current_weather['wind_direction'] = random.choice(['NE', 'N', 'NW'])
            
            # 通知特殊天氣變化
            self.log_message(f"[HKO API] 檢測到 {weather_type} 天氣！")
        
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
    
    def log_message(self, message, level='INFO'):
        """記錄日誌到文件"""
        timestamp = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[ERROR] 無法寫入日誌：{e}")
    
    def check_heat_warning(self):
        """檢查酷熱警告"""
        temp = self.current_weather['temperature']
        
        if temp >= self.heat_threshold:
            severity = 'HIGH' if temp > 35 else 'MODERATE'
            alert_type = 'heat_warning'
            
            self.log_message(f"酷熱天氣警告（{severity}）：{temp:.1f}度", 'WARNING')
            return {
                'alert_type': alert_type,
                'severity': severity,
                'title': '酷熱天氣警告',
                'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {temp:.1f}度。",
                'value': temp,
                'threshold': self.heat_threshold
            }
        
        return None
    
    def check_rainstorm_warning(self):
        """檢查暴雨警告"""
        rainfall = self.current_weather['rainfall']
        
        if rainfall >= self.rain_threshold:
            severity = 'SEVERE' if rainfall > 50 else 'HIGH'
            alert_type = 'rainstorm_warning'
            
            self.log_message(f"暴雨天氣警告（{severity}）：{rainfall:.1f}mm", 'WARNING')
            return {
                'alert_type': alert_type,
                'severity': severity,
                'title': '暴雨天氣警告',
                'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {rainfall:.1f}毫米雨量。",
                'value': rainfall,
                'threshold': self.rain_threshold
            }
        
        return None
    
    def check_strong_wind_warning(self):
        """檢查強風警告"""
        wind_speed = self.current_weather['wind_speed']
        
        if wind_speed >= self.wind_threshold:
            severity = 'SEVERE' if wind_speed > 60 else 'HIGH'
            alert_type = 'strong_wind_warning'
            
            self.log_message(f"強風警告（{severity}）：{wind_speed:.1f}km/h", 'WARNING')
            return {
                'alert_type': alert_type,
                'severity': severity,
                'title': '強風警告',
                'description': f"香港風力正在增強，平均風速達 {wind_speed:.1f}公里/小時。市民應避免在風力強勁的地方逗留。",
                'value': wind_speed,
                'threshold': self.wind_threshold
            }
        
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
    
    def run_monitor(self):
        """運行監控（檢查一次）"""
        print("=" * 60)
        print("天氣監控系統 - Cron Job 版本")
        print("=" * 60)
        print()
        
        # 1. 更新天氣
        print("[1/3] 獲取當前天氣...")
        self.update_weather()
        
        temp = self.current_weather['temperature']
        humidity = self.current_weather['humidity']
        rainfall = self.current_weather['rainfall']
        wind_speed = self.current_weather['wind_speed']
        wind_direction = self.current_weather.get('wind_direction', 'ESE')
        
        print(f"  溫度：{temp:.1f}度")
        print(f"  濕度：{humidity:.0f}%")
        print(f"  降雨：{rainfall:.1f}mm")
        print(f"  風速：{wind_speed:.1f}km/h")
        print(f"  風向：{wind_direction}")
        print()
        
        # 2. 檢查警告
        print("[2/3] 檢查天氣警告...")
        alerts = self.check_all_alerts()
        
        if alerts:
            print(f"  檢測到 {len(alerts)} 個警告：")
            
            for i, alert in enumerate(alerts, 1):
                print(f"    {i}. {alert['title']} ({alert['severity']})")
                print(f"       閾值：{alert['threshold']}")
                print(f"       當前值：{alert['value']:.1f}")
                print()
        else:
            print("  無警告")
        
        # 3. 顯示統計
        print("[3/3] 顯示統計信息...")
        print()
        print("統計：")
        print(f"  檢查時間：{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  警告數量：{len(alerts)}")
        
        if alerts:
            print("  警告類型：")
            for alert in alerts:
                print(f"    - {alert['alert_type']}")
        
        print()
        print("=" * 60)
        print("監控完成")
        print("=" * 60)
        print()
        print(f"日誌文件：{self.log_file}")
        print()


def main():
    """主函數"""
    print("天氣監控系統啟動")
    print("=" * 60)
    print()
    
    # 創建監控器
    monitor = WeatherMonitor()
    
    # 運行監控
    monitor.run_monitor()
    
    print("系統已退出，等待下一次 Cron 調度")
    print()


if __name__ == "__main__":
    main()
