#!/usr/bin/env python3
"""
警報通知功能
當 Agent 故障時，發送 Telegram/Email 警報
"""

import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class AlertManager:
    """警報管理器"""
    
    def __init__(self):
        self.alert_types = {
            'agent_down': {
                'title': 'Agent 故障',
                'severity': 'high',
                'template': """<b>{severity} - {title}</b>

{description}

<b>組件信息：</b>
  - Agent Name: {agent_name}
  - Agent ID: {agent_id}
  - 故障次數: {fail_count}

<b>建議措施：</b>
"""
            },
            'agent_slow': {
                'title': 'Agent 響應緩慢',
                'severity': 'low',
                'template': """<b>{severity} - {title}</b>

{description}

<b>性能信息：</b>
  - Agent Name: {agent_name}
  - 響應時間: {response_time}秒
  - 響應閾值: {threshold}秒

<b>建議措施：</b>
"""
            },
            'database_down': {
                'title': '數據庫故障',
                'severity': 'severe',
                'template': """<b>{severity} - {title}</b>

{description}

<b>組件信息：</b>
  - Component: {component}
  - 故障次數: {fail_count}

<b>建議措施：</b>
"""
            },
            'docker_down': {
                'title': 'Docker 容器故障',
                'severity': 'high',
                'template': """<b>{severity} - {title}</b>

{description}

<b>容器信息：</b>
  - Container Name: {container_name}
  - 故障次數: {fail_count}

<b>建議措施：</b>
"""
            }
        }
        
        # 通知頻道
        self.channels = ['telegram', 'email']
    
    def generate_alert(self, alert_type: str, **kwargs) -> dict:
        """生成警報"""
        template = self.alert_types.get(alert_type)
        if not template:
            return None
        
        # 生成警報內容
        title = template['title']
        severity = template['severity']
        description = template['description'].format(**kwargs)
        
        # 生成建議措施
        recommendations = self.get_recommendations(alert_type, **kwargs)
        
        # 添加建議措施
        template['template'] += recommendations
        
        # 生成完整消息
        message = template['template'].format(
            severity=severity.upper(),
            title=title,
            description=description,
            **kwargs
        )
        
        alert = {
            'alert_id': f"alert_{int(datetime.now(HK_TZ).timestamp())}",
            'alert_type': alert_type,
            'severity': severity,
            'title': title,
            'description': description,
            'message': message,
            'timestamp': datetime.now(HK_TZ),
            'metadata': kwargs
        }
        
        return alert
    
    def get_recommendations(self, alert_type: str, **kwargs) -> str:
        """獲取建議措施"""
        recommendations = ""
        
        if alert_type == 'agent_down':
            recommendations = """1. 檢查 Agent 進程狀態
2. 檢查 Agent 日誌文件
3. 嘗試重啟 Agent
4. 檢查網絡連接
5. 檢查 Agent 端口是否正常監聽"""
        elif alert_type == 'agent_slow':
            recommendations = """1. 檢查 Agent 進程資源使用（CPU、內存）
2. 優化 Agent 模型大小
3. 檢查系統負載
4. 考慮增加 Agent 實例數量"""
        elif alert_type == 'database_down':
            recommendations = """1. 檢查 PostgreSQL 進程狀態
2. 檢查 PostgreSQL 日誌文件
3. 檢查 Docker 容器狀態
4. 檢查數據庫磁盤空間
5. 嘗試重啟數據庫"""
        elif alert_type == 'docker_down':
            recommendations = """1. 檢查容器狀態
2. 檢查容器日誌
3. 檢查容器資源使用（CPU、內存、磁盤）
4. 嘗試重啟容器"""
        else:
            recommendations = """1. 檢查系統日志
2. 檢查資源使用情況
3. 重啟相關服務"""
        
        return recommendations
    
    def send_telegram_alert(self, alert: dict) -> dict:
        """發送 Telegram 警報（模擬）"""
        try:
            # 獲取 Telegram Bot Token 和 Chat ID
            telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
            
            if not telegram_token or not chat_id:
                print("[Telegram] Bot Token 或 Chat ID 未設置")
                return {
                    'channel': 'telegram',
                    'status': 'error',
                    'error': 'Bot Token or Chat ID not set',
                    'timestamp': datetime.now(HK_TZ)
                }
            
            # 構建消息
            message = f"""<b>{alert['severity'].upper()} - {alert['title']}</b>

{alert['description']}

<b>警報 ID:</b> {alert['alert_id']}
<b>時間:</b> {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 發送（模擬）
            print(f"[Telegram] 發送警報：{alert['title']}")
            print(f"  消息：{message[:100]}...")
            print()
            
            return {
                'channel': 'telegram',
                'status': 'sent',
                'timestamp': datetime.now(HK_TZ),
                'alert_id': alert['alert_id'],
                'title': alert['title']
            }
        except Exception as e:
            return {
                'channel': 'telegram',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(HK_TZ)
            }
    
    def send_email_alert(self, alert: dict) -> dict:
        """發送郵件警報（模擬）"""
        try:
            # 構建郵件內容
            subject = f"[Jarvis Alert] {alert['title']} ({alert['severity'].upper()})"
            body = f"{alert['description']}\n\n"
            body += f"警報 ID: {alert['alert_id']}\n"
            body += f"時間: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            body += "建議措施：\n"
            
            # 添加建議措施
            recommendations = self.get_recommendations(alert['alert_type'], **alert['metadata'])
            for i, rec in enumerate(recommendations.split('\n'), 1):
                body += f"{i}. {rec}\n"
            
            # 發送（模擬）
            print(f"[Email] 發送警報：{alert['title']}")
            print(f"  主題：{subject}")
            print(f"  內容：{body[:100]}...")
            print()
            
            return {
                'channel': 'email',
                'status': 'sent',
                'timestamp': datetime.now(HK_TZ),
                'alert_id': alert['alert_id'],
                'title': alert['title']
            }
        except Exception as e:
            return {
                'channel': 'email',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(HK_TZ)
            }
    
    def send_alert(self, alert_type: str, **kwargs):
        """發送警報"""
        # 生成警報
        alert = self.generate_alert(alert_type, **kwargs)
        if not alert:
            print(f"[ALERT] 無法生成警報：{alert_type}")
            return
        
        print("=" * 60)
        print(f"警報：{alert['title']} ({alert['severity']})")
        print("=" * 60)
        print()
        print(f"描述：{alert['description']}")
        print()
        
        # 發送警報
        results = []
        
        if 'telegram' in self.channels:
            telegram_result = self.send_telegram_alert(alert)
            results.append(telegram_result)
        
        if 'email' in self.channels:
            email_result = self.send_email_alert(alert)
            results.append(email_result)
        
        # 顯示結果
        print("發送結果：")
        for result in results:
            status_emoji = "✅" if result['status'] == 'sent' else "❌"
            print(f"  {status_emoji} {result['channel']}: {result['status']}")
        
        print()
        print("=" * 60)
        print("警報已發送！")
        print("=" * 60)
        print()
        
        return alert


def main():
    """主函數 - 測試警報功能"""
    print("=" * 60)
    print("警報通知功能測試")
    print("=" * 60)
    print()
    
    # 創建警報管理器
    alert_manager = AlertManager()
    
    # 測試警報
    print("測試警報通知...")
    print()
    
    # 測試 1：Agent 故障
    print("測試 1：Agent 故警")
    print("-" * 40)
    
    alert1 = alert_manager.send_alert(
        alert_type='agent_down',
        agent_name='Main Agent',
        agent_id='main',
        fail_count=5
    )
    print()
    
    # 測試 2：Agent 響應緩慢
    print("測試 2：Agent 響應緩慢")
    print("-" * 40)
    
    alert2 = alert_manager.send_alert(
        alert_type='agent_slow',
        agent_name='Chat Assistant',
        agent_id='chat',
        response_time=8.5,
        threshold=5.0
    )
    print()
    
    # 測試 3：數據庫故障
    print("測試 3：數據庫故障")
    print("-" * 40)
    
    alert3 = alert_manager.send_alert(
        alert_type='database_down',
        component='PostgreSQL',
        fail_count=3
    )
    print()
    
    print("=" * 60)
    print("警報功能測試完成")
    print("=" * 60)
    print()
    print("支持的警報類型：")
    print("  1. agent_down - Agent 故障")
    print("  2. agent_slow - Agent 響應緩慢")
    print("  3. database_down - 數據庫故障")
    print("  4. docker_down - Docker 容器故障")
    print()
    print("警報通知系統已準備就緒！")


if __name__ == "__main__":
    main()
