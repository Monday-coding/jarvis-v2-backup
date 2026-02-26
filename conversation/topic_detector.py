#!/usr/bin/env python3
"""
話題識別模塊
使用本地模型提取話題關鍵詞、識別話題類型
"""

from typing import Dict, List
from datetime import datetime, timezone, timedelta
import re
import json

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class TopicDetector:
    """話題識別器"""
    
    def __init__(self):
        # 話題關鍵詞庫
        self.topic_keywords = {
            'weather': {
                'primary': ['天氣', '氣溫', '濕度', '降雨', '風速', '風向', '颱風', '暴雨', '雷暴', '酷熱', '強風', '季風', '天文台', 'HKO'],
                'secondary': ['熱', '冷', '多雲', '晴朗', '雨天', '強烈', '微風', '大風', '驟雨', '霧', '能見度', '氣壓']
            },
            'coding': {
                'primary': ['代碼', '編程', 'Python', 'JavaScript', 'Bug', '錯誤', '函數', '類', '變量', '循環', '條件', '異常', 'API', '數據庫', 'SQL', 'Git', 'GitHub', '提交', '推送', '分支', '部署', '服務'],
                'secondary': ['腳本', '算法', '框架', '庫', '包', '接口', '開發', '調試', '測試', '優化', '性能', '重構', '代碼質量', '文檔', '註釋']
            },
            'system': {
                'primary': ['系統', '配置', '設置', '安裝', '部署', '服務', '重啟', '停止', '狀態', '監控', '日誌', '容器', 'Docker', '服務器', '網絡', '連接', '權限', '用戶', '角色', '權限', '驗證', '認證'],
                'secondary': ['環境', '參數', '依賴', '版本', '更新', '升級', '修補', '修訂', '補丁', '發布', '發布版', '穩定', '穩定性', '可靠性', '可用性', '維護', '運維', '運行']
            },
            'chat': {
                'primary': ['聊天', '對話', '信息', '查詢', '問答', '幫助', '助手', '智能', 'AI', '機器人', 'Jarvis', '助理', '問問題', '解答', '回覆', '回應', '發送', '消息', '對話'],
                'secondary': ['交流', '溝通', '聯繫', '對話', '會話', '閒聊', '日常', '生活', '工作', '學習', '教育', '知識', '經驗', '分享', '討論', '探討']
            },
            'data': {
                'primary': ['數據', '統計', '報告', '分析', '圖表', '表格', '記錄', '日誌', '歷史', '趨勢', '增長', '下降', '變化', '增減', '變動', '情況', '狀況', '狀態'],
                'secondary': ['指標', '數量', '百分比', '比例', '比率', '頻率', '次數', '人數', '用戶數', '活躍度', '活躍', '在線', '離線', '訪問', '瀏覽', '點擊', '點贊', '評分']
            },
            'task': {
                'primary': ['任務', '待辦', '工作', '計劃', '安排', '完成', '進行', '進度', '開始', '結束', '結束', '取消', '延期', '推遲', '提醒', '通知', '警報', '截止', '期限'],
                'secondary': ['目標', '成果', '產出', '結果', '效果', '成效', '總結', '小結', '復盤', '回顧', '評估', '評分', '考核', 'KPI', 'OKR', '里程碑']
            },
            'finance': {
                'primary': ['金錢', '資金', '費用', '開銷', '收入', '支出', '預算', '賬本', '利潤', '虧損', '資產', '負債', '投資', '理財', '會計', '審計', '報稅', '稅務'],
                'secondary': ['股票', '基金', '債券', '貸款', '利息', '匯率', '匯款', '匯率', '貨幣', '外匯', '金融', '銀行', '保險', '風險', '回報', '收益', '成本']
            },
            'health': {
                'primary': ['健康', '身體', '醫療', '醫生', '醫院', '藥物', '藥品', '處方', '診斷', '檢查', '檢驗', '治療', '康復', '運動', '鍛煉', '飲食', '營養', '睡眠', '休息'],
                'secondary': ['病', '病癥', '症狀', '病症', '病毒', '細菌', '感染', '傳染', '預防', '疫苗', '體檢', '檢查', '復查', '隨訪', '照護', '護理', '康復', '治癒', '治癒']
            },
            'entertainment': {
                'primary': ['娛樂', '遊戲', '電影', '電視', '音樂', '歌曲', '音樂', '音樂會', '演唱會', '表演', '表演', '演出', '戲劇', '小說', '小說', '漫畫', '動畫', '動畫片', '視頻'],
                'secondary': ['看', '聽', '玩', '看電影', '看電視', '聽歌', '唱歌', '跳舞', '旅遊', '旅行', '度假', '假期', '休息', '娛樂', '休閒', '放鬆']
            },
            'shopping': {
                'primary': ['購物', '買', '買東西', '商店', '網店', '超市', '商場', '購買', '訂購', '下單', '支付', '優惠', '打折', '促銷', '活動', '特價', '折扣', '優惠券'],
                'secondary': ['商品', '貨品', '產品', '物品', '寶物', '禮品', '贈品', '禮物', '訂單', '送貨', '配送', '退貨', '退貨', '換貨', '保修', '售後', '客服', '評價', '評分']
            }
        }
        
        # 話題權重
        self.topic_weights = {
            'weather': 1.0,
            'coding': 0.9,
            'system': 0.9,
            'chat': 0.8,
            'data': 0.7,
            'task': 0.6,
            'finance': 0.5,
            'health': 0.4,
            'entertainment': 0.3,
            'shopping': 0.3
        }
        
        # 最小關鍵詞數量
        self.min_keywords = 2
        self.max_keywords = 10
    
    def extract_keywords(self, message: str) -> List[str]:
        """提取關鍵詞"""
        # 1. 中文分詞（簡單實現）
        # 移除標點符號
        message = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', message)
        
        # 2. 提取 2 字以上的詞（簡化）
        keywords = []
        words = message.split()
        
        for word in words:
            # 只保留中文詞
            if re.match(r'^[\u4e00-\u9fa5]+$', word) and len(word) >= 2:
                keywords.append(word)
        
        return keywords
    
    def detect_topic_type(self, keywords: List[str]) -> str:
        """識別話題類型"""
        topic_scores = {}
        
        for topic_type, topic_data in self.topic_keywords.items():
            primary_keywords = topic_data['primary']
            secondary_keywords = topic_data['secondary']
            
            # 計算匹配得分
            score = 0
            
            # 主要關鍵詞（權重 1.0）
            for keyword in keywords:
                if keyword in primary_keywords:
                    score += 1.0 * self.topic_weights.get(topic_type, 0.5)
                elif keyword in secondary_keywords:
                    score += 0.5 * self.topic_weights.get(topic_type, 0.5)
            
            topic_scores[topic_type] = score
        
        # 返回得分最高的話題類型
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        else:
            return 'unknown'
    
    def generate_summary(self, message: str, keywords: List[str], topic_type: str) -> str:
        """生成話題摘要"""
        # 簡化消息（取前 100 字符）
        summary = message[:100]
        
        # 如果太短，添加關鍵詞
        if len(summary) < 50:
            summary += " " + " ".join(keywords[:3])
        
        return summary
    
    def detect_topic(self, message: str) -> Dict[str, any]:
        """檢測話題"""
        # 提取關鍵詞
        keywords = self.extract_keywords(message)
        
        # 如果沒有關鍵詞，使用整個消息
        if not keywords:
            keywords = [message[:10]]
        
        # 識別話題類型
        topic_type = self.detect_topic_type(keywords)
        
        # 生成話題摘要
        summary = self.generate_summary(message, keywords, topic_type)
        
        return {
            'topic_type': topic_type,
            'keywords': keywords,
            'summary': summary,
            'confidence': self.calculate_confidence(topic_type, keywords),
            'timestamp': datetime.now(HK_TZ)
        }
    
    def calculate_confidence(self, topic_type: str, keywords: List[str]) -> float:
        """計算置信度"""
        if topic_type == 'unknown':
            return 0.0
        
        # 基於關鍵詞數量和話題權重計算置信度
        keyword_count = len(keywords)
        topic_weight = self.topic_weights.get(topic_type, 0.5)
        
        # 置信度 = min(1.0, (keyword_count * topic_weight) / 10)
        return round(confidence, 2)


def main():
    """主函數 - 測試話題識別"""
    print("=" * 60)
    print("話題識別模塊測試")
    print("=" * 60)
    print()
    
    # 創建話題識別器
    detector = TopicDetector()
    
    # 測試消息
    test_messages = [
        "現在幾度？天氣怎麼樣？",
        "幫我寫一個 Python 腳本",
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
    print("話題識別測試完成！")
    print("=" * 60)
    print()
    print("檢測的話題類型：")
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
    print("準備就緒，可以開始識別用戶查詢的話題！")


if __name__ == "__main__":
    main()
