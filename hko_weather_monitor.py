#!/usr/bin/env python3
"""
香港天文台天氣監控系統 v2.0
監控：酷熱、暴雨、颱風
"""

from datetime import datetime, timezone, timedelta
import time
import json
import urllib.request
import urllib.parse
from typing import Dict, List, Any

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class HKOWeatherMonitor:
    """香港天文台天氣監控器（使用 urllib）"""

    def __init__(self):
        self.base_url = "https://www.hko.gov.hk"
        self.current_weather = {}
        self.last_alert_time = {}
        self.alert_history = []

    def get_current_weather(self) -> Dict[str, Any]:
        """獲取當前天氣"""
        try:
            url = f"{self.base_url}/weatherAPI/opendata/hko-opendata.json"
            params = urllib.parse.urlencode({"dataType": "HRIT", "lang": "tc"}).encode('utf-8')
            req = urllib.request.Request(url, data=params, method='GET')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read())
            
        except Exception as e:
            print(f"❌ 獲取天氣失敗: {e}")
            return None

    def check_heat_warning(self) -> Dict[str, Any]:
        """檢查酷熱警告（> 33°C）"""
        if not self.current_weather:
            return None

        temp = self.current_weather.get('temperature', {}).get('value', 0)
        severity = 'high' if temp > 35 else 'moderate'
        
        if temp >= 33:
            alert = {
                'alert_type': 'heat_warning',
                'severity': severity,
                'title': '酷熱天氣警告',
                'description': (
                    f"香港天文台發出酷熱天氣警告。"
                    f"當前氣溫達 {temp}°C。"
                    f"市民應採取防暑措施，避免長時間在戶外曝曬。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'temperature': temp,
                    'condition': '酷熱'
                }
            }
            
            if self.should_send_alert('heat_warning', severity):
                self.alert_history.append(alert)
                return alert
        
        return None

    def check_rainstorm_warning(self) -> Dict[str, Any]:
        """檢查暴雨警告（> 30mm/h）"""
        if not self.current_weather:
            return None

        rainfall = self.current_weather.get('rainfall', {}).get('value', 0)
        severity = 'severe' if rainfall > 50 else 'high'
        
        if rainfall >= 30:
            alert = {
                'alert_type': 'rainstorm_warning',
                'severity': severity,
                'title': '暴雨天氣警告',
                'description': (
                    f"香港天文台發出暴雨天氣警告。"
                    f"過去一小時錄得超過 {rainfall} 毫米雨量。"
                    f"市民應提防水浸及山泥傾瀉。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'rainfall': rainfall,
                    'condition': '暴雨'
                }
            }
            
            if self.should_send_alert('rainstorm_warning', severity):
                self.alert_history.append(alert)
                return alert
        
        return None

    def check_typhoon_warning(self) -> Dict[str, Any]:
        """檢查颱風警告（從 warning message）"""
        try:
            url = f"{self.base_url}/weatherAPI/opendata/hko-opendata.json"
            params = urllib.parse.urlencode({"dataType": "WARN", "lang": "tc"}).encode('utf-8')
            req = urllib.request.Request(url, data=params, method='GET')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read())
                
                # 檢查是否包含颱風相關關鍵詞
                warnings = []
                
                if isinstance(data, dict) and 'warningMessage' in data:
                    warning_message = data['warningMessage']
                    
                    typhoon_keywords = ['颱風', '熱帶氣旋', '熱帶風暴']
                    if any(keyword in warning_message for keyword in typhoon_keywords):
                        alert = {
                            'alert_type': 'typhoon_warning',
                            'severity': 'severe',
                            'title': '颱風警告',
                            'description': f"香港天文台發出颱風警告：{warning_message}",
                            'effect_start_time': datetime.now(HK_TZ),
                            'metadata': {
                                'warning_message': warning_message,
                                'condition': '颱風'
                            }
                        }
                        
                        if self.should_send_alert('typhoon_warning', 'severe'):
                            self.alert_history.append(alert)
                            return alert
                
                return None
            
        except Exception as e:
            print(f"❌ 獲取颱風警告失敗: {e}")
            return None

    def check_strong_wind_warning(self) -> Dict[str, Any]:
        """檢查強風警告（> 40 km/h）"""
        if not self.current_weather:
            return None

        wind_data = self.current_weather.get('wind', {})
        wind_speed = wind_data.get('speed', 0) if isinstance(wind_data, dict) else 0
        severity = 'high' if wind_speed > 50 else 'moderate'
        
        if wind_speed >= 40:
            alert = {
                'alert_type': 'strong_wind_warning',
                'severity': severity,
                'title': '強風警告',
                'description': (
                    f"香港天文台發出強風警告。"
                    f"香港風力正在增強，平均風速達 {wind_speed} 公里/小時。"
                    f"市民應避免在風力強勁的地方逗留。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'wind_speed': wind_speed,
                    'condition': '強風'
                }
            }
            
            if self.should_send_alert('strong_wind_warning', severity):
                self.alert_history.append(alert)
                return alert
        
        return None

    def check_all_alerts(self) -> List[Dict[str, Any]]:
        """檢查所有警報"""
        alerts = []
        
        # 1. 檢查酷熱
        heat_alert = self.check_heat_warning()
        if heat_alert:
            alerts.append(heat_alert)
            print(f"🔥 檢測到酷熱警告：{self.current_weather['temperature']}°C")
        
        # 2. 檢查暴雨
        rain_alert = self.check_rainstorm_warning()
        if rain_alert:
            alerts.append(rain_alert)
            print(f"🌧 檢測到暴雨警告：{self.current_weather['rainfall']}mm/h")
        
        # 3. 檢查颱風
        typhoon_alert = self.check_typhoon_warning()
        if typhoon_alert:
            alerts.append(typhoon_alert)
            print(f"🌀 檢測到颱風警告")
        
        # 4. 檢查強風
        wind_alert = self.check_strong_wind_warning()
        if wind_alert:
            alerts.append(wind_alert)
            print(f"💨 檢測到強風警告：{self.current_weather['wind']}km/h")
        
        return alerts

    def should_send_alert(self, alert_type: str, severity: str) -> bool:
        """判斷是否應該發送警報"""
        now = datetime.now(HK_TZ)
        
        # 檢查最近是否發送過同類型和嚴重級別的警報
        if alert_type in self.last_alert_time:
            last_time = self.last_alert_time[alert_type]
            if severity in self.last_alert_time[alert_type]:
                # 相同嚴重級別：1 小時內不重複
                if (now - last_time[severity]) < timedelta(hours=1):
                    return False
            else:
                # 不同嚴重級別：嚴重級別優先，30 分鐘內不重複
                if severity == 'severe' and (now - last_time['severe']) < timedelta(minutes=30):
                    return False
        
        # 記錄警報時間
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = {}
        self.last_alert_time[alert_type][severity] = now
        
        return True

    def save_alerts_to_db(self, alerts: list) -> bool:
        """保存警報到數據庫"""
        try:
            import sys
            sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')
            from agent_db_connector import AgentDatabase
            
            db = AgentDatabase()
            
            with db.db:
                for alert in alerts:
                    log_id = f"alert_{alert['alert_type']}_{int(datetime.now().timestamp())}"
                    
                    # 保存到 logs 表
                    db.save_log(
                        log_id=log_id,
                        level="WARNING" if alert['severity'] in ['high', 'severe'] else "INFO",
                        category="weather",
                        message=alert['description'],
                        agent_id="weather",
                        context=alert,
                        metadata={'alert_type': alert['alert_type'], 'severity': alert['severity']}
                    )
            
            return True
        except Exception as e:
            print(f"❌ 保存警報到數據庫失敗: {e}")
            return False

    def monitor(self):
        """持續監控"""
        print("=" * 60)
        print("🌤 香港天文台天氣監控系統啟動")
        print("=" * 60)
        print()
        
        while True:
            try:
                # 獲取當前天氣
                print(f"[{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}] 獲取天氣數據...")
                
                self.current_weather = self.get_current_weather()
                
                if self.current_weather:
                    temp = self.current_weather.get('temperature', {}).get('value')
                    humidity = self.current_weather.get('humidity', {}).get('value')
                    rainfall = self.current_weather.get('rainfall', {}).get('value')
                    
                    wind_data = self.current_weather.get('wind', {})
                    wind_speed = wind_data.get('speed', 0) if isinstance(wind_data, dict) else 0
                    
                    print(f"   庫度：{temp}°C")
                    print(f"   濕度：{humidity}%")
                    print(f"   雨量：{rainfall}mm")
                    print(f"   風速：{wind_speed}km/h")
                    print()
                    
                    # 檢查所有警報
                    alerts = self.check_all_alerts()
                    
                    if alerts:
                        print(f"⚠️  檢測到 {len(alerts)} 個警報")
                        
                        # 保存到數據庫
                        self.save_alerts_to_db(alerts)
                    else:
                        print("✅ 無警報")
                else:
                    print("❌ 無法獲取天氣數據")
                
                print()
                print("-" * 40)
                print()
                
                # 每 5 分鐘檢查一次
                time.sleep(300)
                
            except KeyboardInterrupt:
                print("\n\n🛑 監控系統已停止")
                break
            except Exception as e:
                print(f"❌ 監控過程出錯: {e}")
                time.sleep(60)


def main():
    """主函數"""
    print("🌤 香港天文台天氣監控系統 v2.0")
    print("=" * 60)
    print()
    print("監控類型：")
    print("  🔥 酷熱警告（≥ 33°C）")
    print("  🌧 暴雨警告（≥ 30mm/h）")
    print("  💨 強風警告（≥ 40km/h）")
    print("  🌀 颱風警告（自動檢測）")
    print("=" * 60)
    print()
    
    # 創建監控器
    monitor = HKOWeatherMonitor()
    
    # 單次測試模式
    print("📋 執行單次測試...")
    print()
    
    monitor.current_weather = monitor.get_current_weather()
    
    if monitor.current_weather:
        print("✅ 天氣數據獲取成功")
        print()
        
        # 檢查所有警報
        alerts = monitor.check_all_alerts()
        
        if alerts:
            print(f"\n⚠️  檢測到 {len(alerts)} 個警報：\n")
            
            for i, alert in enumerate(alerts, 1):
                print(f"{i}. {alert['title']} ({alert['severity']})")
                print(f"   描述：{alert['description']}")
                print(f"   時間：{alert['effect_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # 保存到數據庫
                monitor.save_alerts_to_db(alerts)
        else:
            print("✅ 無警報")
    else:
        print("❌ 無法獲取天氣數據")
    
    print()
    print("=" * 60)
    print("測試完成！")
    print("=" * 60)
    print()
    print("💡 使用以下命令啟動持續監控：")
    print("   python3 hko_weather_monitor.py --monitor")
    print()
    print("監控模式：")
    print("  - 每 5 分鐘自動檢查天氣")
    print("  - 自動檢測所有警報")
    print("  - 保存到數據庫")
    print("  - Ctrl+C 停止")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        # 持續監控模式
        monitor = HKOWeatherMonitor()
        monitor.monitor()
    else:
        # 單次測試模式
        main()
