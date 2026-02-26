#!/usr/bin/env python3
"""
警報通知功能（簡化版本）
"""

import requests
import smtplib
from datetime import datetime, timezone, timedelta
import os

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def send_telegram_alert(title, description, severity='medium'):
    """發送 Telegram 警報"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        
        if not bot_token or not chat_id:
            print("[Alert] Telegram Bot Token 或 Chat ID 未設置")
            return False
        
        # 構建消息
        message = f"""<b>{severity.upper()} - {title}</b>

{description}

<b>時間：</b> {datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 發送
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"[Telegram] 警報已發送：{title}")
            return True
        else:
            print(f"[Telegram] 警報發送失敗：{response.status_code}")
            return False
    except Exception as e:
        print(f"[Telegram] 錯誤：{e}")
        return False


def send_email_alert(title, description, severity='medium'):
    """發送郵件警報"""
    try:
        sender_email = os.environ.get('EMAIL_SENDER', '')
        receiver_email = os.environ.get('EMAIL_RECEIVER', '')
        email_password = os.environ.get('EMAIL_PASSWORD', '')
        
        if not sender_email or not receiver_email:
            print("[Alert] 郵件設置未設置")
            return False
        
        # 構建郵件
        subject = f"[Jarvis Alert] {title} ({severity.upper()})"
        body = f"{description}\n\n"
        body += f"時間：{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}\n"
        body += "建議措施：\n"
        body += "1. 檢查系統日誌\n"
        body += "2. 檢查組件狀態\n"
        body += "3. 嘗試重啟相關服務\n"
        
        # 發送
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, subject, body)
        server.quit()
        
        print(f"[Email] 警報已發送：{title}")
        return True
    except Exception as e:
        print(f"[Email] 錯誤：{e}")
        return False


def main():
    """主函數 - 測試警報功能"""
    print("=" * 60)
    print("警報通知功能測試")
    print("=" * 60)
    print()
    
    # 測試 Telegram 警報
    print("[1/2] 測試 Telegram 警報...")
    print()
    result = send_telegram_alert(
        title="測試警報",
        description="這是一個測試警報消息。系統正在測試警報通知功能。",
        severity="low"
    )
    
    if result:
        print("  ✅ Telegram 警報測試成功")
    else:
        print("  ⚠️  Telegram 警報測試失敗（需要配置 Bot Token 和 Chat ID）")
    
    print()
    
    # 測試郵件警報
    print("[2/2] 測試郵件警報...")
    print()
    result = send_email_alert(
        title="測試警報",
        description="這是一個測試郵件警報。系統正在測試警報通知功能。",
        severity="low"
    )
    
    if result:
        print("  ✅ 郵件警報測試成功")
    else:
        print("  ⚠️  郵件警報測試失敗（需要配置郵件設置）")
    
    print()
    print("=" * 60)
    print("警報通知功能測試完成")
    print("=" * 60)
    print()
    print("警報通知系統已準備就緒！")
    print()
    print("支持的警報類型：")
    print("  1. agent_down - Agent 故障")
    print("  2. agent_slow - Agent 響應緩慢")
    print("  3. database_down - 數據庫故障")
    print("  4. docker_down - Docker 容器故障")
    print()
    print("配置環境變量：")
    print("  Telegram:")
    print("    export TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("    export TELEGRAM_CHAT_ID='your_chat_id'")
    print()
    print("  Email:")
    print("    export EMAIL_SENDER='your_email@gmail.com'")
    print("    export EMAIL_RECEIVER='receiver@gmail.com'")
    print("    export EMAIL_PASSWORD='your_password'")


if __name__ == "__main__":
    main()
