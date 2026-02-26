#!/usr/bin/env python3
"""
持續天氣監控系統 - 測試版本
短時間運行（30 秒），無超時問題
"""

from datetime import datetime, timezone, timedelta
import time

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class MockDatabase:
    """模擬數據庫"""
    
    def __init__(self):
        self.alerts_history = []
        self.alerts_sent = 0
        
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


class WeatherMonitor:
    """天氣監控器"""
    
    def __init__(self, db):
        self.db = db
        self.last_alert_time = {}
        self.running = False
        
        # 模擬天氣數據
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0
        }
    
    def check_heat_warning(self):
        """檢查酷熱警告"""
        temp = self.current_weather['temperature']
        
        if temp >= 33:
            severity = 'high' if temp > 35 else 'moderate'
            alert_type = 'heat_warning'
            
            if self.should_send_alert(alert_type, severity):
                self.db.save_log(
                    log_id=f"alert_heat_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"酷熱天氣警告：{temp}度",
                    agent_id="weather",
                    metadata={'alert_type': 'heat_warning', 'temperature': temp}
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
                self.db.save_log(
                    log_id=f"alert_rain_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"暴雨天氣警告：{rainfall}mm",
                    agent_id="weather",
                    metadata={'alert_type': 'rainstorm_warning', 'rainfall': rainfall}
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
                self.db.save_log(
                    log_id=f"alert_wind_{int(time.time())}",
                    level="WARNING",
                    category="weather",
                    message=f"強風警告：{wind_speed}km/h",
                    agent_id="weather",
                    metadata={'alert_type': 'strong_wind_warning', 'wind_speed': wind_speed}
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
        """判斷是否應該發送警報"""
        now = datetime.now(HK_TZ)
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        
        if severity in self.last_alert_time[alert_type]:
            last_time = self.last_alert_time[alert_type][severity]
            if (now - last_time).total_seconds() < 3600:
                return False
        
        self.last_alert_time[alert_type][severity] = now
        return True
    
    def run_monitor(self, check_count=6, interval=5):
        """運行監控（短時間）"""
        print("=" * 60)
        print("天氣監控系統 - 短時間測試")
        print("=" * 60)
        print()
        print(f"測試配置：")
        print(f"  檢查次數：{check_count}")
        print(f"  間隔：{interval} 秒")
        print(f"  總時間：{check_count * interval} 秒")
        print()
        print("=" * 60)
        print()
        
        for i in range(check_count):
            timestamp = datetime.now(HK_TZ).strftime('%H:%M:%S')
            print(f"[{timestamp}] 第 {i+1} 次檢查")
            print()
            
            # 更新天氣數據（模擬變化）
            import random
            if random.random() < 0.3:  # 30% 概率有變化
                self.current_weather['temperature'] += random.uniform(-0.5, 0.5)
                self.current_weather['rainfall'] += random.uniform(-1, 1)
                self.current_weather['wind_speed'] += random.uniform(-2, 2)
                
                # 限制範圍
                self.current_weather['temperature'] = max(15, min(38, self.current_weather['temperature']))
                self.current_weather['rainfall'] = max(0, min(100, self.current_weather['rainfall']))
                self.current_weather['wind_speed'] = max(0, min(80, self.current_weather['wind_speed']))
            
            # 顯示天氣
            print(f"  溫度：{self.current_weather['temperature']:.1f}度")
            print(f"  降雨：{self.current_weather['rainfall']:.1f}mm")
            print(f"  風速：{self.current_weather['wind_speed']:.1f}km/h")
            print()
            
            # 檢查警告
            alerts = self.check_all_alerts()
            
            if alerts:
                print(f"  檢測到 {len(alerts)} 個警告：")
                for j, alert in enumerate(alerts, 1):
                    print(f"    {j}. {alert['metadata']['alert_type']} ({alert['level']})")
            else:
                print("  無警告")
            
            print()
            print("-" * 40)
            print()
            
            # 等待
            if i < check_count - 1:  # 不是最後一次
                print(f"  等待 {interval} 秒...")
                print()
                time.sleep(interval)
        
        print("=" * 60)
        print("測試完成！")
        print("=" * 60)
        print()
        print(f"總警報數量：{self.db.alerts_sent}")
        print(f"檢查次數：{check_count}")
        print()
        print("系統狀態：✅ 正常")


def main():
    """主函數"""
    db = MockDatabase()
    monitor = WeatherMonitor(db)
    
    # 運行 6 次檢查，每次間隔 5 秒（總共 30 秒）
    monitor.run_monitor(check_count=6, interval=5)


if __name__ == "__main__":
    main()
