#!/usr/bin/env python3
"""
免費天氣查詢腳本 - 使用 wttr.in
無需 API Key，免費使用
"""

import subprocess
import sys
import re

def get_weather_wttr(city="Hong Kong"):
    """
    使用 wttr.in 查詢天氣
    """
    url = f"https://wttr.in/{city}?lang=zh&format=j1"
    
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        try:
            data = result.stdout
            
            # wttr.in 的返回格式是直接的天氣信息
            # 示例：{"temp_c":"27","temp_f":"80","cond":"晴朗"} 或直接字符串
            
            # 嘗試解析 JSON
            if data.startswith('{'):
                weather_data = eval(data)  # wttr.in 的輸出是 Python 字典格式
                
                temp = weather_data.get('temp_c', '未知')
                condition = weather_data.get('cond', '未知')
                humidity = weather_data.get('humidity', '未知')
                
                response = f"""
🌤 **{city} 天氣**

**温度**：{temp}°C
**天气**：{condition}
**湿度**：{humidity}
"""
                return response
            else:
                # 可能是純文本格式
                temp_match = re.search(r'(\d+)\s*°?[CF]', data)
                condition_match = re.search(r'(晴|多云|雨|雪|陰|晴朗)', data)
                
                if temp_match and condition_match:
                    return f"""
🌤 **{city} 天氣**

**温度**：{temp_match.group(1)}°C
**天气**：{condition_match.group(1)}
"""
                
                return f"""
🌤 **{city} 天氣**

{data}
"""
        except:
            return f"⚠️  解析天氣數據失敗"
            return f"""
⚠️  無法獲取天氣數據

你可以：
1. 直接訪問：https://wttr.in/{city}
2. 查看天氣網站：https://www.weather.com.cn/weather/hong-kong
3. 使用手機天氣 APP 查詢
"""

if __name__ == "__main__":
    # 支持命令行參數
    city = sys.argv[1] if len(sys.argv) > 1 else "Hong Kong"
    
    print(get_weather_wttr(city))
