#!/usr/bin/env python3
"""
HKO API 實時數據獲取
模擬從香港天文台 API 獲取實時天氣數據
"""

from datetime import datetime, timezone, timedelta
import time
import random

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class HKOAPIClient:
    """香港天文台 API 客戶端（模擬版本）"""
    
    def __init__(self):
        self.base_url = "https://www.hko.gov.hk"
        self.session = None
        
        # 模擬實時天氣變化
        self.weather_trends = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0
        }
    
    def fetch_current_weather(self) -> dict:
        """獲取當前天氣（模擬）"""
        
        # 模擬天氣趨勢（逐步變化）
        trend = random.choice(['rising', 'stable', 'falling'])
        
        if trend == 'rising':
            self.weather_trends['temperature'] += random.uniform(0.5, 1.5)
            self.weather_trends['humidity'] += random.uniform(-2, 2)
            self.weather_trends['rainfall'] += random.uniform(-1, 1)
            self.weather_trends['wind_speed'] += random.uniform(-2, 2)
        elif trend == 'falling':
            self.weather_trends['temperature'] -= random.uniform(0.5, 1.5)
            self.weather_trends['humidity'] += random.uniform(-2, 2)
            self.weather_trends['rainfall'] += random.uniform(-1, 1)
            self.weather_trends['wind_speed'] += random.uniform(-2, 2)
        # stable: no change
        
        # 限制範圍
        self.weather_trends['temperature'] = max(15, min(38, self.weather_trends['temperature']))
        self.weather_trends['humidity'] = max(30, min(95, self.weather_trends['humidity']))
        self.weather_trends['rainfall'] = max(0, min(100, self.weather_trends['rainfall']))
        self.weather_trends['wind_speed'] = max(0, min(80, self.weather_trends['wind_speed']))
        
        # 偶設一些隨機的特殊天氣
        if random.random() < 0.1:  # 10% 概率
            self.weather_trends['temperature'] = random.uniform(33, 36)
        elif random.random() < 0.1:
            self.weather_trends['rainfall'] = random.uniform(30, 50)
        elif random.random() < 0.05:
            self.weather_trends['wind_speed'] = random.uniform(40, 50)
        
        weather_data = {
            'temperature': round(self.weather_trends['temperature'], 1),
            'humidity': int(self.weather_trends['humidity']),
            'rainfall': round(self.weather_trends['rainfall'], 1),
            'wind_speed': round(self.weather_trends['wind_speed'], 1),
            'wind_direction': random.choice(['E', 'NE', 'SE', 'N', 'NW', 'SW', 'ESE']),
            'weather_condition': self.get_weather_condition(),
            'observation_time': datetime.now(HK_TZ),
            'source': 'HKO'
        }
        
        return weather_data
    
    def fetch_weather_warnings(self) -> list:
        """獲取天氣警告（模擬）"""
        
        warnings = []
        
        # 模擬警告消息
        if random.random() < 0.2:  # 20% 概率有警告
            warning_messages = [
                "香港天文台發出強烈季風信號，預料本港風力會增強。",
                "香港天文台發出雷暴警告，預料本港有狂風雷暴。",
                "香港天文台發出酷熱天氣警告，預料本港天氣非常酷熱。",
                "香港天文台發出暴雨警告，預料本港有大雨及狂風雷暴。"
            ]
            
            warnings.append({
                'warning_type': 'special_weather',
                'severity': 'severe',
                'message': random.choice(warning_messages),
                'source': 'HKO'
            })
        
        return warnings
    
    def get_weather_condition(self) -> str:
        """根據數據生成天氣條件"""
        
        temp = self.weather_trends['temperature']
        rainfall = self.weather_trends['rainfall']
        
        if rainfall >= 30:
            if temp > 25:
                return "大雨"
            else:
                return "雨天"
        elif rainfall >= 10:
            return "驟雨"
        elif temp >= 33:
            return "酷熱"
        elif temp >= 30:
            return "炎熱"
        elif temp >= 25:
            return "溫暖"
        elif temp >= 20:
            return "涼爽"
        elif temp >= 15:
            return "微涼"
        else:
            return "寒冷"
    
    def fetch_forecast(self, hours: int = 24) -> list:
        """獲取天氣預報（模擬）"""
        
        forecast = []
        base_temp = self.weather_trends['temperature']
        
        for i in range(hours // 3):  # 每 3 小時一次預報
            future_time = datetime.now(HK_TZ) + timedelta(hours=3 * (i + 1))
            
            # 模擬溫度變化
            temp_change = random.uniform(-2, 2)
            forecast_temp = max(20, min(38, base_temp + temp_change))
            
            # 模擬降雨概率
            rain_probability = random.uniform(0, 100)
            if rain_probability > 60:
                weather = "有驟雨"
            elif rain_probability > 30:
                weather = "多云"
            else:
                weather = "大致多云"
            
            forecast.append({
                'time': future_time,
                'temperature': round(forecast_temp, 1),
                'weather': weather,
                'humidity': random.randint(60, 90),
                'rainfall': round(random.uniform(0, 20), 1) if rain_probability > 40 else 0
            })
        
        return forecast


def main():
    """主函數 - 快速測試"""
    print("=" * 60)
    print("HKO API 實時數據獲取")
    print("=" * 60)
    print()
    
    # 創建 API 客戶端
    api_client = HKOAPIClient()
    
    # 獲取當前天氣
    print("1. 獲取當前天氣...")
    current_weather = api_client.fetch_current_weather()
    
    print(f"   溫度：{current_weather['temperature']}度")
    print(f"   濕度：{current_weather['humidity']}%")
    print(f"   降雨：{current_weather['rainfall']}mm")
    print(f"   風速：{current_weather['wind_speed']}km/h")
    print(f"   風向：{current_weather['wind_direction']}")
    print(f"   天氣：{current_weather['weather_condition']}")
    print(f"   時間：{current_weather['observation_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 檢查警告
    print("2. 檢查天氣警告...")
    warnings = api_client.fetch_weather_warnings()
    
    if warnings:
        print(f"   檢測到 {len(warnings)} 個警告：")
        for i, warning in enumerate(warnings, 1):
            print(f"     {i}. {warning['message']}")
    else:
        print("   無警告")
    print()
    
    # 獲取預報
    print("3. 獲取天氣預報（未來 9 小時）...")
    forecast = api_client.fetch_forecast(9)
    
    print("   未來 9 小時預報：")
    for i, item in enumerate(forecast, 1):
        time_str = item['time'].strftime('%H:%M')
        print(f"     {time_str} - {item['weather']}, {item['temperature']}度")
    
    print()
    print("=" * 60)
    print("API 數據獲取完成！")
    print("=" * 60)
    print()
    print("注意：這是模擬版本，實際使用需要連接真實 HKO API")
    print("      需要申請 API Key，並替換 mock 實現")


if __name__ == "__main__":
    main()
