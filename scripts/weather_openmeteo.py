#!/usr/bin/env python3
"""
免費天氣查詢腳本 - 使用 Open-Meteo（無需 API Key）
"""

import subprocess
import json

def get_weather_opnmeteo(city="Hong Kong"):
    """
    使用 Open-Meteo 免費天氣 API
    無需 API Key
    """
    # Hong Kong 的坐標
    url = f"https://api.open-meteo.com/v1/forecast?latitude=22.3193&longitude=114.1694&current=weather&timezone=Asia%2FHong_Kong"
    
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            
            # 提取當前天氣
            current = data['current_weather']
            
            # 轉換天氣代碼
            weather_codes = {
                0: "晴朗",
                1: "多云",
                2: "阴天",
                3: "雷阵雨",
                45: "雾",
                48: "毛毛雨",
                51: "毛毛雨",
                53: "阵雨",
                55: "雷阵雨",
                61: "大雨",
                63: "暴雨",
                65: "大雪",
                66: "雨夹雪",
                67: "雨夹雪",
                71: "小雪",
                73: "中雪",
                75: "大雪",
                77: "阵雨夹雪",
                80: "雷阵雨",
                81: "雷雨",
                82: "雷阵雨",
                85: "暴雪",
                95: "雷暴",
                96: "雷暴",
                99: "雷暴"
            }
            
            code = current['weathercode']
            description = weather_codes.get(code, "未知")
            
            # 简化温度显示
            temp = current['temperature']
            
            # 风速转换（km/h -> m/s）
            wind_speed = round(current['windspeed'] * 1000 / 3600, 1)
            
            response = f"""
🌤 **{city} 天氣**

**温度**：{temp}°C
**天气**：{description}
**风速**：{wind_speed} m/s ({current['windspeed']} km/h)
**湿度**：{current['humidity']}%
"""
            return response
        except Exception as e:
            return f"⚠️  解析天气数据失败: {e}"
    else:
        return "⚠️  获取天气失败"

def main():
    # 支持命令行参数
    city = "Hong Kong"
    
    print(get_weather_opnmeteo(city))

if __name__ == "__main__":
    main()
