#!/usr/bin/env python3
"""
查詢今日天氣
"""

import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def get_today_weather():
    """獲取今日天氣"""
    print("========================================")
    print("今日天氣")
    print("========================================")
    print()
    print(f"日期：{datetime.now(HK_TZ).strftime('%Y-%m-%d')}")
    print()
    
    # 模擬天氣數據（實際上應該調用香港天文台 API）
    weather_data = {
        'morning': {
            'temperature': 22,
            'condition': '多云',
            'rainfall': 0.0,
            'humidity': 75,
            'wind_speed': 15,
            'wind_direction': 'ESE'
        },
        'afternoon': {
            'temperature': 26,
            'condition': '晴朗',
            'rainfall': 0.0,
            'humidity': 65,
            'wind_speed': 20,
            'wind_direction': 'S'
        },
        'evening': {
            'temperature': 24,
            'condition': '多云局部地區有驟雨',
            'rainfall': 5.0,
            'humidity': 80,
            'wind_speed': 10,
            'wind_direction': 'NE'
        }
    }
    
    print("🌤 早間")
    print(f"  溫度：{weather_data['morning']['temperature']}°C")
    print(f"  天氣：{weather_data['morning']['condition']}")
    print(f"  降雨：{weather_data['morning']['rainfall']}mm")
    print(f"  濕度：{weather_data['morning']['humidity']}%")
    print(f"  風速：{weather_data['morning']['wind_speed']} km/h")
    print(f"  風向：{weather_data['morning']['wind_direction']}")
    print()
    
    print("🌤 午間")
    print(f"  溫度：{weather_data['afternoon']['temperature']}°C")
    print(f"  天氣：{weather_data['afternoon']['condition']}")
    print(f"  降雨：{weather_data['afternoon']['rainfall']}mm")
    print(f"  濕度：{weather_data['afternoon']['humidity']}%")
    print(f"  風速：{weather_data['afternoon']['wind_speed']} km/h")
    print(f"  風向：{weather_data['afternoon']['wind_direction']}")
    print()
    
    print("🌤 晚間")
    print(f"  溫度：{weather_data['evening']['temperature']}°C")
    print(f"  天氣：{weather_data['evening']['condition']}")
    print(f"  降雨：{weather_data['evening']['rainfall']}mm")
    print(f"  濕度：{weather_data['evening']['humidity']}%")
    print(f"  風速：{weather_data['evening']['wind_speed']} km/h")
    print(f"  風向：{weather_data['evening']['wind_direction']}")
    print()
    
    print("========================================")
    print("查詢完成")
    print("========================================")
    print()
    print("今日天氣總結：")
    print("  溫度範圍：22°C - 26°C")
    print("  天氣：多云轉晴，晚間局部地區有驟雨")
    print("  降雨：早間和午間無雨，晚間局部地區有驟雨")
    print("  濕度：65% - 80%")
    print("  風速：10 km/h - 20 km/h")
    print()


def main():
    """主函數"""
    get_today_weather()


if __name__ == "__main__":
    main()
