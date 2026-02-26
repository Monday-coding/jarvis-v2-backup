#!/usr/bin/env python3
"""
香港天文台天氣 Agent v2.1
Main Agent 的子 Agent
"""

from datetime import datetime, timezone, timedelta
import sys

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class WeatherAgent:
    """天氣 Agent - 處理天氣查詢和警告"""

    def __init__(self):
        self.name = "Weather Agent"
        self.description = "處理天氣查詢和警告"
        
        # 模擬天氣數據（用於測試）
        self.current_weather = {
            'temperature': 28.0,
            'humidity': 75,
            'rainfall': 5.0,
            'wind_speed': 15.0,
            'wind_direction': 'ESE',
            'weather_condition': '多云局部地區有驟雨',
            'observation_time': datetime.now(HK_TZ)
        }

    def check_alerts(self) -> list:
        """檢查天氣警告"""
        alerts = []
        
        # 1. 酷熱警告（> 33°C）
        if self.current_weather['temperature'] >= 33:
            severity = 'high' if self.current_weather['temperature'] > 35 else 'moderate'
            alerts.append({
                'alert_type': 'heat_warning',
                'severity': severity,
                'title': '酷熱天氣警告',
                'description': (
                    f"香港天文台發出酷熱天氣警告。"
                    f"當前氣溫達 {self.current_weather['temperature']}°C。"
                    f"市民應採取防暑措施，避免長時間在戶外暴曬。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'temperature': self.current_weather['temperature'],
                    'condition': '酷熱'
                }
            })
        
        # 2. 暴雨警告（> 30mm/h）
        if self.current_weather['rainfall'] >= 30:
            severity = 'severe' if self.current_weather['rainfall'] > 50 else 'high'
            alerts.append({
                'alert_type': 'rainstorm_warning',
                'severity': severity,
                'title': '暴雨天氣警告',
                'description': (
                    f"香港天文台發出暴雨天氣警告。"
                    f"過去一小時錄得超過 {self.current_weather['rainfall']} 毫米雨量。"
                    f"市民應提防水浸及山泥傾瀉。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'rainfall': self.current_weather['rainfall'],
                    'condition': '暴雨'
                }
            })
        
        # 3. 強風警告（> 40km/h）
        if self.current_weather['wind_speed'] >= 40:
            severity = 'high' if self.current_weather['wind_speed'] > 60 else 'moderate'
            alerts.append({
                'alert_type': 'strong_wind_warning',
                'severity': severity,
                'title': '強風警告',
                'description': (
                    f"香港風力正在增強，平均風速達 {self.current_weather['wind_speed']} 公里/小時。"
                    f"市民應避免在風力強勁的地方逗留。"
                ),
                'effect_start_time': datetime.now(HK_TZ),
                'metadata': {
                    'wind_speed': self.current_weather['wind_speed'],
                    'condition': '強風'
                }
            })
        
        return alerts

    def get_weather_report(self) -> str:
        """生成天氣報告"""
        report = []
        report.append("🌤 香港天文台天氣報告")
        report.append("")
        report.append("📊 當前天氣：")
        report.append(f"   溫度：{self.current_weather['temperature']}°C")
        report.append(f"   濕度：{self.current_weather['humidity']}%")
        report.append(f"   降雨量：{self.current_weather['rainfall']}mm")
        report.append(f"   風速：{self.current_weather['wind_speed']}km/h")
        report.append(f"   風向：{self.current_weather['wind_direction']}")
        report.append(f"   天氣：{self.current_weather['weather_condition']}")
        report.append("")
        report.append(f"⏰ 更新時間：{self.current_weather['observation_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 檢查警告
        alerts = self.check_alerts()
        
        if alerts:
            report.append("")
            report.append(f"⚠️  注意：發現 {len(alerts)} 個警告")
            
            for i, alert in enumerate(alerts, 1):
                report.append("")
                report.append(f"{i}. {alert['title']} ({alert['severity']})")
                report.append(f"   {alert['description']}")
                report.append(f"   時間：{alert['effect_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            report.append("")
            report.append("✅ 無警告")
        
        return "\n".join(report)


def handle_weather_query(query: str) -> str:
    """處理天氣查詢"""
    agent = WeatherAgent()
    
    # 模擬不同查詢結果
    if '溫度' in query or '熱' in query or '幾度' in query:
        return agent.get_weather_report()
    elif '預報' in query or '未來' in query:
        return generate_forecast_report(agent.current_weather)
    elif '警報' in query or '警告' in query or '特別' in query:
        alerts = agent.check_alerts()
        if alerts:
            report = []
            report.append("⚠️  注意：發現警告")
            for alert in alerts:
                report.append("")
                report.append(f"🚨 {alert['title']} ({alert['severity']})")
                report.append(f"{alert['description']}")
            return "\n".join(report)
        else:
            return "✅ 目前無警告"
    elif '雨' in query or '降雨' in query:
        return generate_rainfall_report(agent.current_weather)
    elif '風' in query or '風速' in query:
        return generate_wind_report(agent.current_weather)
    else:
        return agent.get_weather_report()


def generate_forecast_report(weather: dict) -> str:
    """生成天氣預報報告"""
    report = []
    report.append("🌤 香港天文台天氣預報")
    report.append("")
    report.append("📊 未來 24 小時預報：")
    report.append("")
    report.append("今天：")
    report.append("  最高溫度：32°C")
    report.append("  最低溫度：26°C")
    report.append("  天氣：多云，局部地區有驟雨")
    report.append("")
    report.append("明天：")
    report.append("  最高溫度：34°C")
    report.append("  最低溫度：27°C")
    report.append("  天氣：多云，局部地區有雷暴")
    report.append("")
    report.append("後天：")
    report.append("  最高溫度：31°C")
    report.append("  最低溫度：26°C")
    report.append("  天氣：大致多云")
    report.append("")
    report.append("⚠️  注意：明天預計氣溫較高，請注意防暑。")
    
    return "\n".join(report)


def generate_rainfall_report(weather: dict) -> str:
    """生成降雨報告"""
    report = []
    report.append("🌧 香港天文台降雨報告")
    report.append("")
    report.append(f"📊 當前降雨：{weather['rainfall']}mm")
    report.append("")
    
    if weather['rainfall'] >= 30:
        report.append("⚠️  暴雨警告")
        report.append("")
        report.append("市民應提防水浸及山泥傾瀉：")
        report.append("  • 避免在低窪地區逗留")
        report.append("  • 不要在河邊或山區行走")
        report.append("  • 如需外出，應攜帶雨具")
        report.append("  • 遠離排水渠")
        report.append("  • 注意道路情況，駕駛人士應小心")
    elif weather['rainfall'] >= 10:
        report.append("💧 有降雨，注意防滑")
        report.append("")
        report.append("建議措施：")
        report.append("  • 穿著防水鞋")
        report.append("  • 遠離排水渠")
        report.append("  • 小心行走")
    else:
        report.append("✅ 無降雨或降雨量很小")
    
    return "\n".join(report)


def generate_wind_report(weather: dict) -> str:
    """生成風速報告"""
    report = []
    report.append("💨 香港天文台風速報告")
    report.append("")
    report.append(f"📊 當前風速：{weather['wind_speed']}km/h")
    report.append(f"📊 風向：{weather['wind_direction']}")
    report.append("")
    
    if weather['wind_speed'] >= 40:
        report.append("⚠️  強風警告")
        report.append("")
        report.append("市民應避免在風力強勁的地方逗留：")
        report.append("  • 遠離建築工地")
        report.append("  • 避免在海邊活動")
        report.append("  • 固定鬆散物品")
        report.append("  • 如需外出，應穿著合適的衣物")
        report.append("  • 避免騎自行車")
    elif weather['wind_speed'] >= 20:
        report.append("💨 有風，注意防風")
        report.append("")
        report.append("建議措施：")
        report.append("  • 注意高空墜物")
        report.append("  • 遠離建築工地")
    else:
        report.append("✅ 風速正常，適合戶外活動")
    
    return "\n".join(report)


def main():
    """主函數"""
    print("🌤 香港天文台天氣 Agent 測試")
    print("=" * 60)
    print()
    
    # 測試查詢
    test_queries = [
        "現在幾度",
        "今天天氣預報",
        "有沒有警報",
        "下雨嗎",
        "現在風速多少"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 測試查詢 {i}: {query}")
        print("-" * 40)
        print(handle_weather_query(query))
        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
