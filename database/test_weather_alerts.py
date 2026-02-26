# HKO 天氣監控系統 - 調試版本

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase


def test_weather_query():
    """測試天氣查詢和警告檢測"""
    print("=" * 60)
    print("🌤 天氣查詢和警告測試")
    print("=" * 60)
    print()
    
    # 模擬天氣數據（用於測試）
    # 實際使用中應該從 API 獲取
    
    # 測試 1：正常天氣（無警告）
    print("測試 1：正常天氣（氣溫 28°C）")
    print("-" * 40)
    
    weather_data = {
        'temperature': 28.0,
        'humidity': 75.0,
        'rainfall': 5.0,
        'wind_speed': 15.0,
        'observation_time': '2026-02-26T10:00:00+08:00',
        'source': 'weather.gov.hk'
    }
    
    alerts = []
    
    # 檢查酷熱（< 33°C）
    if weather_data['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'high' if weather_data['temperature'] > 35 else 'moderate',
            'title': '酷熱天氣警告',
            'description': f"當前氣溫達 {weather_data['temperature']}°C。",
            'metadata': {'temperature': weather_data['temperature']}
        })
    
    # 檢查暴雨（< 30mm/h）
    if weather_data['rainfall'] >= 30:
        alerts.append({
            'alert_type': 'rainstorm_warning',
            'severity': 'severe' if weather_data['rainfall'] > 50 else 'high',
            'title': '暴雨天氣警告',
            'description': f"過去一小時錄得超過 {weather_data['rainfall']} 毫米雨量。",
            'metadata': {'rainfall': weather_data['rainfall']}
        })
    
    # 檢查強風（< 40km/h）
    if weather_data['wind_speed'] >= 40:
        alerts.append({
            'alert_type': 'strong_wind_warning',
            'severity': 'high',
            'title': '強風警告',
            'description': f"香港風力正在增強，平均風速達 {weather_data['wind_speed']} 公里/小時。",
            'metadata': {'wind_speed': weather_data['wind_speed']}
        })
    
    if alerts:
        print(f"⚠️  檢測到 {len(alerts)} 個警告：")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['title']} ({alert['severity']})")
            print(f"      描述：{alert['description']}")
    else:
        print("✅ 無警告")
    
    print()
    print(f"📊 天氣數據：")
    print(f"   溫度：{weather_data['temperature']}°C")
    print(f"   濕度：{weather_data['humidity']}%")
    print(f"   雨量：{weather_data['rainfall']}mm")
    print(f"   風速：{weather_data['wind_speed']}km/h")
    print()
    
    # 測試 2：酷熱天氣（33.5°C）
    print("測試 2：酷熱天氣（氣溫 33.5°C）")
    print("-" * 40)
    
    weather_data = {
        'temperature': 33.5,
        'humidity': 85.0,
        'rainfall': 0.0,
        'wind_speed': 10.0,
        'observation_time': '2026-02-26T11:00:00+08:00',
        'source': 'weather.gov.hk'
    }
    
    alerts = []
    
    if weather_data['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'moderate',
            'title': '酷熱天氣警告',
            'description': (
                f"香港天文台發出酷熱天氣警告。"
                f"當前氣溫達 {weather_data['temperature']}°C。"
                f"市民應採取防暑措施，避免長時間在戶外暴曬。"
            ),
            'metadata': {'temperature': weather_data['temperature'], 'condition': '酷熱'}
        })
    
    if alerts:
        print(f"⚠️  檢測到 {len(alerts)} 個警告：")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['title']} ({alert['severity']})")
            print(f"      描述：{alert['description']}")
            print(f"      時間：{weather_data['observation_time']}")
    else:
        print("✅ 無警告")
    
    print()
    print(f"📊 天氣數據：")
    print(f"   溫度：{weather_data['temperature']}°C")
    print(f"   濕度：{weather_data['humidity']}%")
    print(f"   雨量：{weather_data['rainfall']}mm")
    print(f"   風速：{weather_data['wind_speed']}km/h")
    print()
    
    # 測試 3：暴雨天氣（35mm/h）
    print("測試 3：暴雨天氣（降雨量 35mm/h）")
    print("-" * 40)
    
    weather_data = {
        'temperature': 25.0,
        'humidity': 95.0,
        'rainfall': 35.0,
        'wind_speed': 20.0,
        'observation_time': '2026-02-26T12:00:00+08:00',
        "source": "weather.gov.hk"
    }
    
    alerts = []
    
    if weather_data['rainfall'] >= 30:
        alerts.append({
            'alert_type': 'rainstorm_warning',
            'severity': 'severe' if weather_data['rainfall'] > 50 else 'high',
            'title': '暴雨天氣警告',
            'description': (
                f"香港天文台發出暴雨天氣警告。"
                f"過去一小時錄得超過 {weather_data['rainfall']} 毫米雨量。"
                f"市民應提防水浸及山泥傾瀉。"
            ),
            'metadata': {'rainfall': weather_data['rainfall'], 'condition': '暴雨'}
        })
    
    if alerts:
        print(f"⚠️  檢測到 {len(alerts)} 個警告：")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['title']} ({alert['severity']})")
            print(f"      描述：{alert['description']}")
            print(f"      時間：{weather_data['observation_time']}")
    else:
        print("✅ 無警告")
    
    print()
    print(f"📊 天氣數據：")
    print(f"   溫度：{weather_data['temperature']}°C")
    print(f"   濕度：{weather_data['humidity']}%")
    print(f"   雨量：{weather_data['rainfall']}mm")
    print(f"   風速：{weather_data['wind_speed']}km/h")
    print()
    
    # 測試 4：強風天氣（45km/h）
    print("測試 4：強風天氣（風速 45km/h）")
    print("-" * 40)
    
    weather_data = {
        'temperature': 22.0,
        'humidity': 80.0,
        'rainfall': 15.0,
        'wind_speed': 45.0,
        'observation_time': '2026-02-26T13:00:00+08:00',
        "source": "weather.gov.hk"
    }
    
    alerts = []
    
    if weather_data['wind_speed'] >= 40:
        alerts.append({
            'alert_type': 'strong_wind_warning',
            'severity': 'high',
            'title': '強風警告',
            'description': (
                f"香港風力正在增強，平均風速達 {weather_data['wind_speed']} 公里/小時。"
                f"市民應避免在風力強勁的地方逗留。"
            ),
            'metadata': {'wind_speed': weather_data['wind_speed'], 'condition': '強風'}
        })
    
    if alerts:
        print(f"⚠️  檢測到 {len(alerts)} 個警告：")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['title']} ({alert['severity']})")
            print(f"      描述：{alert['description']}")
            print(f"      時間：{weather_data['observation_time']}")
    else:
        print("✅ 無警告")
    
    print()
    print(f"📊 天氣數據：")
    print(f"   溫度：{weather_data['temperature']}°C")
    print(f"   濕度：{weather_data['humidity']}%")
    print(f"   雨量：{weather_data['rainfall']}mm")
    print(f"   風速：{weather_data['wind_speed']}km/h")
    print()
    
    # 測試 5：多種警告同時（酷熱 + 暴雨）
    print("測試 5：多種警告同時（氣溫 34°C + 降雨 40mm/h）")
    print("-" * 40)
    
    weather_data = {
        'temperature': 34.0,
        'humidity': 90.0,
        'rainfall': 40.0,
        'wind_speed': 25.0,
        'observation_time': '2026-02-26T14:00:00+08:00',
        "source": "weather.gov.hk"
    }
    
    alerts = []
    
    if weather_data['temperature'] >= 33:
        alerts.append({
            'alert_type': 'heat_warning',
            'severity': 'high',
            'title': '酷熱天氣警告',
            'description': f"當前氣溫達 {weather_data['temperature']}°C。",
            'metadata': {'temperature': weather_data['temperature']}
        })
    
    if weather_data['rainfall'] >= 30:
        alerts.append({
            'alert_type': 'rainstorm_warning',
            'severity': 'severe',
            'title': '暴雨天氣警告',
            'description': f"過去一小時錄得超過 {weather_data['rainfall']} 毫米雨量。",
            'metadata': {'rainfall': weather_data['rainfall']}
        })
    
    if alerts:
        print(f"⚠️  檢測到 {len(alerts)} 個警告：")
        for i, alert in enumerate(alerts, 1):
            print(f"   {i}. {alert['title']} ({alert['severity']})")
            print(f"      描述：{alert['description']}")
            print(f"      時間：{weather_data['observation_time']}")
    else:
        print("✅ 無警告")
    
    print()
    print(f"📊 天氣數據：")
    print(f"   溫度：{weather_data['temperature']}°C")
    print(f"   濕度：{weather_data['humidity']}%")
    print(f"   雨量：{weather_data['rainfall']}mm")
    print(f"   風速：{weather_data['wind_speed']}km/h")
    print()


def main():
    """主函數"""
    test_weather_query()
    
    print("=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)
    print()
    print("📝 下一步：")
    print("  1. 集成到 Main Agent")
    print("  2. 實現通知發送（Telegram/WhatsApp）")
    print("  3. 實現持續監控")
    print()


if __name__ == "__main__":
    main()
