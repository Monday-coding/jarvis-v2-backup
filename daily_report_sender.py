#!/usr/bin/env python3
"""
實現每日簡報發送功能
"""

import os
import requests
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class DailyReportSender:
    """每日簡報發送器"""
    
    def __init__(self):
        self.telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        self.email_sender = os.environ.get('EMAIL_SENDER', '')
        self.email_receiver = os.environ.get('EMAIL_RECEIVER', '')
        self.email_password = os.environ.get('EMAIL_PASSWORD', '')
    
    def send_telegram_report(self, report: str) -> bool:
        """發送 Telegram 簽報"""
        try:
            if not self.telegram_bot_token or not self.telegram_chat_id:
                print("[Telegram] Bot Token 或 Chat ID 未設置")
                return False
            
            # 構建消息
            message = f"""
<b>📅 每日簡報</b>

{report}

<b>時間：</b> {datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}

---
<b>系統助手 - 技術支援系統</b>
"""
            
            # 發送
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"[Telegram] 每日簡報已發送")
                return True
            else:
                print(f"[Telegram] 發送失敗：{response.status_code}")
                return False
        
        except Exception as e:
            print(f"[Telegram] 錯誤：{e}")
            return False
    
    def send_email_report(self, report: str) -> bool:
        """發送郵件簡報"""
        try:
            if not self.email_sender or not self.email_receiver or not self.email_password:
                print("[Email] 郵件設置未設置")
                return False
            
            # 構建郵件
            subject = "[系統助手] 每日簡報"
            body = f"""{report}

---
系統助手 - 技術支援系統
時間：{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 發送
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.sendmail(self.email_sender, self.email_receiver, subject, body)
            server.quit()
            
            print(f"[Email] 每日簡報已發送")
            return True
        
        except Exception as e:
            print(f"[Email] 錯誤：{e}")
            return False
    
    def send_daily_report(self, report: str):
        """發送每日簡報（所有渠道）"""
        print("=" * 60)
        print("發送每日簡報")
        print("=" * 60)
        print()
        print(f"[{datetime.now(HK_TZ).strftime('%H:%M:%S')}] 開始發送每日簡報...")
        print()
        
        results = []
        
        # 1. 發送 Telegram 簽報
        print("[1/2] 發送 Telegram 簽報...")
        telegram_result = self.send_telegram_report(report)
        results.append(telegram_result)
        
        if telegram_result:
            print(f"  ✅ Telegram 簽報已發送")
        else:
            print(f"  ⚠️  Telegram 簽報發送失敗")
        
        print()
        
        # 2. 發送郵件簡報
        print("[2/2] 發送郵件簡報...")
        email_result = self.send_email_report(report)
        results.append(email_result)
        
        if email_result:
            print(f"  ✅ 郵件簡報已發送")
        else:
            print(f"  ⚠️  郵件簡報發送失敗")
        
        print()
        print("=" * 60)
        print("發送完成")
        print("=" * 60)
        print()
        print("發送結果：")
        
        for i, result in enumerate(results, 1):
            status_emoji = "✅" if result else "❌"
            print(f"  {status_emoji} {i}. {'Telegram' if i == 1 else 'Email'}")
        
        print()
        
        # 統計
        success_count = sum(1 for r in results if r)
        total_count = len(results)
        
        print(f"  成功：{success_count}/{total_count}")
        print()
        
        if success_count > 0:
            print("✅ 至少一個簡報已發送成功！")
        else:
            print("⚠️  所有簡報發送失敗")
        
        print()
        print("準備就緒！")
        print()


def main():
    """主函數 - 發送每日簡報"""
    print("=" * 60)
    print("發送每日簡報")
    print("=" * 60)
    print()
    
    # 創建簡報發送器
    sender = DailyReportSender()
    
    # 生成每日簡報
    from daily_report_generator import DailyReportGenerator
    
    generator = DailyReportGenerator()
    daily_report = generator.generate_daily_report()
    
    # 發送簡報
    sender.send_daily_report(daily_report)


if __name__ == "__main__":
    main()
