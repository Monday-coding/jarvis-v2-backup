#!/usr/bin/env python3
"""
測試話題識別系統
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/conversation')

from topic_detector import TopicDetector


def main():
    """主函數"""
    print("=" * 60)
    print("話題識別系統測試")
    print("=" * 60)
    print()
    
    # 創建話題識別器
    detector = TopicDetector()
    
    # 測試消息
    test_messages = [
        "現在幾度？天氣怎麼樣？",
        "幫我寫個 Python 腳本",
        "系統配置在哪裡？",
        "你有什麼建議嗎？",
        "查詢一下銷售數據",
        "我今天的預算怎麼樣？",
        "最近身體怎麼樣？",
        "最近有什麼好玩的電影？",
        "幫我買個東西"
    ]
    
    print("測試消息：")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"消息 {i}: {message}")
        print("-" * 40)
        
        # 檢測話題
        topic = detector.detect_topic(message)
        
        print(f"話題類型：{topic['topic_type']}")
        print(f"關鍵詞：{topic['keywords']}")
        print(f"摘要：{topic['summary']}")
        print(f"置信度：{topic['confidence']}")
        print()
    
    print("=" * 60)
    print("測試完成！")
    print("=" * 60)
    print()
    print("支持的話題類型：")
    print("  1. weather - 天氣")
    print("  2. coding - 代碼")
    print("  3. system - 系統")
    print("  4. chat - 聊天")
    print("  5. data - 數據")
    print("  6. task - 任務")
    print("  7. finance - 財務")
    print("  8. health - 健康")
    print("  9. entertainment - 娛樂")
    print("  10. shopping - 購物")
    print()
    print("話題識別系統已準備就緒！")


if __name__ == "__main__":
    main()
