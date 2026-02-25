#!/usr/bin/env python3
"""
免費天氣查詢腳本 - 使用 wttr.in（無需 API Key）
"""

import subprocess
import sys

def get_weather(city="Hong Kong"):
    """獲取指定城市的天氣"""
    # 使用 wttr.in 免費 API
    url = f"https://wttr.in/{city}?lang=zh&format=j1"
    
    result = subprocess.run(
        ['curl', '-s', url],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            
            # 提取天氣信息
            temp = data['current_condition']['temp']
            condition = data['current_condition']['temp']  # wttr 的返回結構
            weather_desc = {
                "Sunny": "晴天",
                "Cloudy": "多雲",
                "Rain": "下雨",
                "Clear": "晴朗",
                "Partly Cloudy": "多雲"
            }.get(condition, condition)
            
            response = f"""
🌤 **{city} 天氣**

**溫度**：{temp}°C
**天氣**：{weather_desc}
**更新時間**：{data['current_condition'][0]}  # 簡在的時間戳（如果有）
"""
            return response
        except (json.JSONDecodeError, KeyError) as e:
            return f"⚠️ 解析天氣數據失敗: {e}"
    else:
        return f"⚠️ 無法連接到天氣服務"

def main():
    # 支持命令行參數
    city = sys.argv[1] if len(sys.argv) > 1 else "Hong Kong"
    
    print(get_weather(city))

if __name__ == "__main__":
    main()
