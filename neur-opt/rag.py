#!/usr/bin/env python3
"""
RAG（檢索增強生成）索引腳本
功能：
1. 加載知識庫
2. 建立索引
3. 支持關鍵詞搜索
4. 支持語義搜索（待實現）
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class RAGIndex:
    """RAG 索引類"""
    
    def __init__(self, kb_file: Path):
        self.kb_file = kb_file
        self.index = {}
        self.embeddings = {}
        
    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """加載知識庫"""
        with open(self.kb_file, 'r', encoding='utf-8') as f:
            kb_content = f.read()
        
        # 解析知識庫（按類別分組）
        entries = []
        current_category = None
        current_heading = None
        current_content = []
        current_tags = []
        
        for line in kb_content.split('\n'):
            # 類別標題
            if line.strip().startswith('###'):
                if current_category and current_heading:
                    entries.append({
                        'category': current_category,
                        'heading': current_heading,
                        'content': '\n'.join(current_content),
                        'tags': current_tags,
                        'id': self._generate_id(current_category, current_heading)
                    })
                current_category = line.replace('###', '').strip()
                current_heading = None
                current_content = []
                current_tags = []
            
            # 條目標題
            elif line.strip().startswith('####'):
                current_heading = line.replace('####', '').strip()
                current_content = []
                current_tags = []
            
            # 內容
            elif current_heading:
                # 提取摘要和標籤
                if '**摘要：**' in line:
                    current_content.append(line.split('**摘要：**')[1])
                elif '**標籤：**' in line:
                    current_tags = [tag.strip() for tag in line.split('**標籤：**')[1].split(',')]
                elif line.strip():
                    current_content.append(line)
        
        # 添加最後一個條目
        if current_category and current_heading:
            entries.append({
                'category': current_category,
                'heading': current_heading,
                'content': '\n'.join(current_content),
                'tags': current_tags,
                'id': self._generate_id(current_category, current_heading)
            })
        
        return entries
    
    def _generate_id(self, category: str, heading: str) -> str:
        """生成唯一 ID"""
        return f"{category.lower()}::{heading.lower().replace(' ', '-')}"
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索知識庫（簡單關鍵詞匹配）"""
        query_lower = query.lower()
        
        results = []
        for entry in self.index.values():
            # 搜索標題、內容、標籤
            score = 0
            if query_lower in entry['heading'].lower():
                score += 10
            if query_lower in entry['content'].lower():
                score += 5
            for tag in entry['tags']:
                if query_lower in tag.lower():
                    score += 3
            
            if score > 0:
                results.append({
                    **entry,
                    'score': score
                })
        
        # 按分數排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def search_by_category(self, query: str, category: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """按類別搜索"""
        query_lower = query.lower()
        
        results = []
        for entry in self.index.values():
            if entry['category'].lower() != category.lower():
                continue
            
            score = 0
            if query_lower in entry['heading'].lower():
                score += 10
            if query_lower in entry['content'].lower():
                score += 5
            for tag in entry['tags']:
                if query_lower in tag.lower():
                    score += 3
            
            if score > 0:
                results.append({
                    **entry,
                    'score': score
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def build_index(self) -> None:
        """建立索引"""
        entries = self.load_knowledge_base()
        
        for entry in entries:
            entry_id = entry['id']
            self.index[entry_id] = entry
        
        print(f"✓ 索引已建立: {len(entries)} 個條目")
        
        # 按類別統計
        category_stats = {}
        for entry in entries:
            cat = entry['category']
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        print(f"  類別統計: {category_stats}")


def save_index(kb_file: Path, index_data: Dict[str, Any]) -> None:
    """保存索引到文件"""
    index_file = kb_file.parent / "index.json"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 索引已保存: {index_file}")


def main():
    """主函數"""
    
    # 路徑配置
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    KB_FILE = WORKSPACE / "knowledge-base.md"
    INDEX_FILE = WORKSPACE / "neur-opt" / "index.json"
    
    # 檢查知識庫
    if not KB_FILE.exists():
        print(f"❌ 知識庫不存在: {KB_FILE}")
        print("   請先運行神經元優化腳本來構建知識庫。")
        sys.exit(1)
    
    print("🔍 RAG 索引構建")
    print("")
    
    # 建立索引
    rag = RAGIndex(KB_FILE)
    rag.build_index()
    
    # 保存索引
    index_data = {
        'entries': list(rag.index.values()),
        'metadata': {
            'total': len(rag.index),
            'kb_file': str(KB_FILE),
            'last_updated': str(datetime.now())
        }
    }
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_index(KB_FILE, index_data)
    
    print("")
    
    # 測試搜索
    print("🎎 測試搜索")
    print("  查詢: 'Python'")
    results = rag.search("Python")
    print(f"  找到 {len(results)} 個結果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. [{result['category']}] {result['heading']} (分數: {result['score']})")
    
    print("")
    print("✅ RAG 索引構建完成！")
    print(f"📁 索引文件: {INDEX_FILE}")


if __name__ == "__main__":
    main()
