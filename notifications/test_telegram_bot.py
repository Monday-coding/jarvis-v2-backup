#!/usr/bin/env python3
"""
Telegram Bot 通知系統
Weather Agent 調用
"""

import sys
import os
import time
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))

# 模擬的 Telegram Bot 配置
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')


class TelegramNotifier:
    """Telegram Bot 通知發送器"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot_name = "Jarvis Bot"
    
    def send_heat_warning(self, temp: float, level: str):
        """發送酷熱警告"""
        severity_emoji = 'HIGH' if level == 'high' else 'MODERATE'
        
        message = f"""
<b>Heat Warning - {severity_emoji}</b>

Hong Kong Observatory issued heat warning.
Current temperature: {temp}C.

<b>Safety measures:</b>
- Avoid prolonged exposure to direct sunlight
- Drink plenty of water and supplement salt
- Wear light, breathable clothing
- Use air conditioning or electric fans indoors
- Seek medical attention if you feel unwell

Effective time: Now

Source: HKO
"""
        
        print(f"[Telegram] Sending heat warning: {temp}C ({level})")
        print(f"[Telegram] Message preview:\n{message}")
        
        # 在實際應用中，這裡會使用 python-telegram-bot 庫
        # self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
        print("[Telegram] Heat warning sent (simulated)")
    
    def send_rainstorm_warning(self, rainfall: float, level: str):
        """發送暴雨警告"""
        severity_emoji = 'SEVERE' if level == 'severe' else 'HIGH'
        
        message = f"""
<b>Rainstorm Warning - {severity_emoji}</b>

Hong Kong Observatory issued rainstorm warning.
Rainfall recorded in the last hour: {rainfall}mm.

<b>Safety measures:</b>
- Avoid staying in low-lying areas
- Do not visit riversides or hillsides
- Carry rain gear if you need to go out
- Stay away from drainage channels
- Watch out for road conditions, drivers should be careful

Effective time: Now

Source: HKO
"""
        
        print(f"[Telegram] Sending rainstorm warning: {rainfall}mm ({level})")
        print(f"[Telegram] Message preview:\n{message}")
        
        # 在實際應用中，這裡會使用 python-telegram-bot 庫
        # self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
        print("[Telegram] Rainstorm warning sent (simulated)")
    
    def send_strong_wind_warning(self, wind_speed: float, level: str):
        """發送強風警告"""
        severity_emoji = 'SEVERE' if level == 'severe' else 'HIGH'
        
        message = f"""
<b>Strong Wind Warning - {severity_emoji}</b>

Hong Kong wind is strengthening, with average wind speeds reaching {wind_speed} km/h.
Residents should avoid staying in places with strong winds.

<b>Recommended measures:</b>
- Stay away from construction sites
- Avoid coastal activities
- Secure loose objects
- Wear suitable clothing if you need to go out
- Avoid riding bicycles

Effective time: Now

Source: HKO
"""
        
        print(f"[Telegram] Sending strong wind warning: {wind_speed}km/h ({level})")
        print(f"[Telegram] Message preview:\n{message}")
        
        # 在實際應用中，這裡會使用 python-telegram-bot 庫
        # self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
        print("[Telegram] Strong wind warning sent (simulated)")
    
    def send_typhoon_warning(self, typhoon_info: str):
        """發送颱風警告"""
        message = f"""
<b>Typhoon Warning - SEVERE</b>

Hong Kong Observatory issued typhoon warning: {typhoon_info}

<b>Important reminders:</b>
- Typhoon track may be affected
- Low-lying areas may be flooded
- Strong winds may blow down objects
- Sea waves may be very large

<b>Recommended measures:</b>
- Monitor typhoon track and reports
- Prepare typhoon protection measures in advance
- Avoid entering dangerous areas
- Stay indoors, close windows and doors
- Prepare emergency supplies

Effective time: Now

Source: HKO
"""
        
        print(f"[Telegram] Sending typhoon warning")
        print(f"[Telegram] Message preview:\n{message}")
        
        # 在實際應用中，這裡會使用 python-telegram-bot 庫
        # self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='HTML')
        print("[Telegram] Typhoon warning sent (simulated)")
    
    def send_weather_alert(self, alert_data: dict):
        """發送天氣警報（統一接口）"""
        alert_type = alert_data['alert_type']
        severity = alert_data['severity']
        description = alert_data['description']
        title = alert_data['title']
        
        if alert_type == 'heat_warning':
            temp = alert_data['metadata']['temperature']
            self.send_heat_warning(temp, severity)
        elif alert_type == 'rainstorm_warning':
            rainfall = alert_data['metadata']['rainfall']
            self.send_rainstorm_warning(rainfall, severity)
        elif alert_type == 'strong_wind_warning':
            wind_speed = alert_data['metadata']['wind_speed']
            self.send_strong_wind_warning(wind_speed, severity)
        elif alert_type == 'typhoon_warning':
            typhoon_info = alert_data['metadata'].get('warning_message', 'Typhoon')
            self.send_typhoon_warning(typhoon_info)
        else:
            print(f"[Telegram] Unknown alert type: {alert_type}")


class MockWeatherData:
    """模擬天氣數據"""
    
    def __init__(self):
        self.weather_data = [
            {
                'name': '正常天氣',
                'temperature': 28.0,
                'rainfall': 5.0,
                'wind_speed': 15.0,
                'wind_direction': 'ESE',
                'weather_condition': '多云局部地區有驟雨'
            },
            {
                'name': '酷熱天氣',
                'temperature': 34.0,
                'rainfall': 5.0,
                'wind_speed': 15.0,
                'wind_direction': 'ESE',
                'weather_condition': '多云局部地區有驟雨'
            },
            {
                'name': '暴雨天氣',
                'temperature': 25.0,
                'rainfall': 35.0,
                'wind_speed': 20.0,
                'wind_direction': 'SE',
                'weather_condition': '大雨'
            },
            {
                'name': '強風天氣',
                'temperature': 22.0,
                'humidity': 80,
                'rainfall': 15.0,
                'wind_speed': 45.0,
                'wind_direction': 'NE',
                'weather_condition': '強風'
            }
        ]
        self.current_index = 0
    
    def get_current_weather(self):
        """獲取當前天氣（模擬）"""
        return self.weather_data[self.current_index % len(self.weather_data)]
    
    def next_scenario(self):
        """切換到下一個天氣場景"""
        self.current_index += 1
        return self.get_current_weather()


def test_alerts():
    """測試警報發送"""
    print("=" * 60)
    print("Telegram Bot 通知測試")
    print("=" * 60)
    print()
    
    # 創建通知器
    notifier = TelegramNotifier(
        token=TELEGRAM_BOT_TOKEN,
        chat_id=CHAT_ID
    )
    
    # 模擬天氣數據
    weather = MockWeatherData()
    
    # 測試 1：正常天氣（無警報）
    print("測試 1：正常天氣（無警報）")
    print("-" * 40)
    
    current_weather = weather.get_current_weather()
    alerts = []
    
    # 模擬檢查警報
    if current_weather['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'high',
            'title': '酷熱天氣警告',
            'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {current_weather['temperature']}°C。",
            'metadata': {
                'temperature': current_weather['temperature'],
                'condition': '酷熱'
            }
        })
    
    if not alerts:
        print("無警報，不發送通知")
    else:
        for alert in alerts:
            notifier.send_weather_alert(alert)
    
    print()
    print("=" * 60)
    print()
    
    # 測試 2：酷熱天氣（發送警報）
    print("測試 2：酷熱天氣（34°C）")
    print("-" * 40)
    
    current_weather = weather.next_scenario()
    alerts = []
    
    if current_weather['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'high',
            'title': '酷熱天氣警告',
            'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {current_weather['temperature']}°C。",
            'metadata': {
                'temperature': current_weather['temperature'],
                'condition': '酷熱'
            }
        })
    
    for alert in alerts:
        notifier.send_weather_alert(alert)
    
    print()
    print("=" * 60)
    print()
    
    # 測試 3：暴雨天氣（發送警報）
    print("測試 3：暴雨天氣（35mm/h）")
    print("-" * 40)
    
    current_weather = weather.next_scenario()
    alerts = []
    
    if current_weather['rainfall'] >= 30:
        alerts.append({
            'alert_type': 'rainstorm_warning',
            'severity': 'high',
            'title': '暴雨天氣警告',
            'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {current_weather['rainfall']}毫米雨量。",
            'metadata': {
                'rainfall': current_weather['rainfall'],
                'condition': '暴雨'
            }
        })
    
    for alert in alerts:
        notifier.send_weather_alert(alert)
    
    print()
    print("=" * 60)
    print()
    
    # 測試 4：強風天氣（發送警報）
    print("測試 4：強風天氣（45km/h）")
    print("-" * 40)
    
    current_weather = weather.next_scenario()
    alerts = []
    
    if current_weather['wind_speed'] >= 40:
        alerts.append({
            'alert_type': 'strong_wind_warning',
            'severity': 'high',
            'title': '強風警告',
            'description': f"香港風力正在增強，平均風速達 {current_weather['wind_speed']}公里/小時。市民應避免在風力強勁的地方逗留。",
            'metadata': {
                'wind_speed': current_weather['wind_speed'],
                'condition': '強風'
            }
        })
    
    for alert in alerts:
        notifier.send_weather_alert(alert)
    
    print()
    print("=" * 60)
    print()
    
    # 測試 5：多種警告同時（酷熱 + 暴雨）
    print("測試 5：多種警告同時（34°C + 40mm）")
    print("-" * 40)
    
    current_weather = {
        'temperature': 34.0,
        'rainfall': 40.0,
        'wind_speed': 20.0
    }
    
    alerts = []
    
    if current_weather['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'high',
            'title': '酷熱天氣警告',
            'description': f"香港天文台發出酷熱天氣警告。當前氣溫達 {current_weather['temperature']}°C。",
            'metadata': {
                'temperature': current_weather['temperature'],
                'condition': '酷熱'
            }
        })
    
    if current_weather['rainfall'] >= 30:
        alerts.append({
            'alert_type': 'rainstorm_warning',
            'severity': 'severe',
            'title': '暴雨天氣警告',
            'description': f"香港天文台發出暴雨天氣警告。過去一小時錄得超過 {current_weather['rainfall']}毫米雨量。",
            'metadata': {
                'rainfall': current_weather['rainfall'],
                'condition': '暴雨'
            }
        })
    
    for alert in alerts:
        notifier.send_weather_alert(alert)
    
    print()
    print("=" * 60)
    print()
    
    # 總結
    print("Telegram Bot 通知測試完成")
    print("=" * 60)
    print()
    
    print("測試結果：")
    print("- 正常天氣：無警報")
    print("- 酷熱天氣：已發送警報")
    print("- 暴雨天氣：已發送警報")
    print("- 強風天氣：已發送警報")
    print("- 多種警告：已發送警報")
    print()
    print("注意：以上都是模擬測試，實際應用需要連接真實 Telegram Bot API")


def main():
    """主函數"""
    test_alerts()


if __name__ == "__main__":
    main()
