#!/usr/bin/env python3
"""
RAG 緩存系統 - 快速檢索和緩存常見問題
功能：
1. 從 knowledge-base.md 構建索引
2. 向量化知識（使用 Ollama）
3. 緩存常見問答
4. 支持快速檢索
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import subprocess
from datetime import datetime


class RAGCache:
    """RAG 緩存類"""

    def __init__(self, workspace: Path = None):
        if workspace is None:
            workspace = Path.home() / ".openclaw" / "workspace"

        self.workspace = workspace
        self.kb_file = workspace / "knowledge-base.md"
        self.cache_file = workspace / "rag" / "cache.json"
        self.index_file = workspace / "rag" / "index.json"
        self.log_file = workspace / "rag" / "log.txt"

        # 創建目錄
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

        # 加載現有緩存
        self.cache = self._load_cache()
        self.index = self._load_index()

        self._log("RAG Cache 初始化完成")

    def _load_cache(self) -> Dict[str, Any]:
        """加載緩存"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self) -> None:
        """保存緩存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)

    def _load_index(self) -> List[Dict[str, Any]]:
        """加載索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_index(self) -> None:
        """保存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def _log(self, message: str) -> None:
        """記錄日誌"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)

        print(message)

    def _get_embedding(self, text: str, model: str = "qwen2.5:0.5b") -> Optional[List[float]]:
        """
        使用 Ollama 獲取文本嵌入（簡化版）
        由於 Ollama 嵌入 API 可能不可用，使用哈希作為替代
        """
        # 使用簡單的哈希作為嵌入（實際應該使用真實的向量嵌入）
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        # 將哈希轉換為一個偽向量（用於演示）
        pseudo_embedding = [float(int(c, 16) / 15.0) for c in text_hash[:128]]
        return pseudo_embedding

    def _calculate_similarity(self, query: str, entry: Dict[str, Any]) -> float:
        """
        計算查詢和條目之間的相似度（簡化版）
        使用關鍵詞匹配 + 標籤匹配
        """
        score = 0.0
        query_lower = query.lower()

        # 1. 標題匹配（權重 10）
        if entry.get('heading'):
            heading_lower = entry['heading'].lower()
            if query_lower in heading_lower:
                score += 10
            # 精確匹配
            if query_lower == heading_lower:
                score += 15

        # 2. 內容匹配（權重 5）
        if entry.get('content'):
            content_lower = entry['content'].lower()
            if query_lower in content_lower:
                score += 5

        # 3. 標籤匹配（權重 3）
        if entry.get('tags'):
            for tag in entry['tags']:
                if query_lower in tag.lower():
                    score += 3

        # 4. 摘要匹配（權重 2）
        if entry.get('summary'):
            summary_lower = entry['summary'].lower()
            if query_lower in summary_lower:
                score += 2

        return score

    def query_cache(self, question: str) -> Optional[str]:
        """
        查詢緩存
        返回緩存的答案（如果存在）
        """
        # 檢查精確匹配
        question_hash = hashlib.md5(question.encode('utf-8')).hexdigest()

        if question_hash in self.cache:
            self._log(f"緩存命中: {question[:50]}...")
            return self.cache[question_hash]['answer']

        return None

    def store_cache(self, question: str, answer: str) -> None:
        """
        存儲到緩存
        """
        question_hash = hashlib.md5(question.encode('utf-8')).hexdigest()

        self.cache[question_hash] = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'count': self.cache.get(question_hash, {}).get('count', 0) + 1
        }

        self._save_cache()
        self._log(f"緩存存儲: {question[:50]}...")

    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        加載知識庫
        解析 knowledge-base.md
        """
        if not self.kb_file.exists():
            self._log(f"警告：知識庫不存在: {self.kb_file}")
            return []

        with open(self.kb_file, 'r', encoding='utf-8') as f:
            kb_content = f.read()

        # 解析知識庫（按類別分組）
        entries = []
        current_category = None
        current_heading = None
        current_content = []
        current_tags = []
        current_summary = ""

        for line in kb_content.split('\n'):
            # 日期標題
            if line.strip().startswith('## ') and re.match(r'## \d{4}-\d{2}-\d{2}', line):
                # 跳過日期標題
                continue

            # 類別標題
            elif line.strip().startswith('###'):
                # 保存前一個條目
                if current_heading:
                    entries.append({
                        'category': current_category,
                        'heading': current_heading,
                        'content': '\n'.join(current_content),
                        'tags': current_tags,
                        'summary': current_summary,
                        'id': self._generate_id(current_category, current_heading)
                    })

                current_category = line.replace('###', '').strip()
                current_heading = None
                current_content = []
                current_tags = []
                current_summary = ""

            # 條目標題
            elif line.strip().startswith('####'):
                # 保存前一個條目
                if current_heading:
                    entries.append({
                        'category': current_category,
                        'heading': current_heading,
                        'content': '\n'.join(current_content),
                        'tags': current_tags,
                        'summary': current_summary,
                        'id': self._generate_id(current_category, current_heading)
                    })

                current_heading = line.replace('####', '').strip()
                current_content = []
                current_tags = []
                current_summary = ""

            # 摘要
            elif '**摘要：**' in line or '**Summary:**' in line:
                current_summary = line.split('**')[2].strip() if '**' in line else line

            # 標籤
            elif '**標籤：**' in line or '**Tags:**' in line:
                tag_str = line.split('**')[2].strip() if '**' in line else line
                current_tags = [tag.strip() for tag in tag_str.split(',')]

            # 內容
            elif current_heading and line.strip():
                current_content.append(line)

        # 添加最後一個條目
        if current_heading:
            entries.append({
                'category': current_category,
                'heading': current_heading,
                'content': '\n'.join(current_content),
                'tags': current_tags,
                'summary': current_summary,
                'id': self._generate_id(current_category, current_heading)
            })

        self._log(f"加載了 {len(entries)} 個知識庫條目")
        return entries

    def _generate_id(self, category: str, heading: str) -> str:
        """生成唯一 ID"""
        category_clean = category.lower().replace(' ', '-')
        heading_clean = heading.lower().replace(' ', '-')[:50]
        return f"{category_clean}::{heading_clean}"

    def build_index(self) -> None:
        """
        構建索引
        從知識庫加載條目並建立索引
        """
        self._log("開始構建 RAG 索引...")

        entries = self.load_knowledge_base()

        # 構建索引
        self.index = []

        for entry in entries:
            # 計算嵌入
            embedding = self._get_embedding(entry['heading'] + " " + entry.get('summary', ''))

            self.index.append({
                'id': entry['id'],
                'category': entry['category'],
                'heading': entry['heading'],
                'content': entry['content'],
                'tags': entry.get('tags', []),
                'summary': entry.get('summary', ''),
                'embedding': embedding
            })

        # 保存索引
        self._save_index()

        # 統計
        category_stats = {}
        for entry in self.index:
            cat = entry['category']
            category_stats[cat] = category_stats.get(cat, 0) + 1

        self._log(f"索引構建完成: {len(self.index)} 個條目")
        self._log(f"分類統計: {category_stats}")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索知識庫
        返回相關條目（按相似度排序）
        """
        self._log(f"搜索查詢: {query}")

        # 計算每個條目的相似度
        results = []
        for entry in self.index:
            score = self._calculate_similarity(query, entry)

            if score > 0:
                results.append({
                    **entry,
                    'score': score
                })

        # 按分數排序
        results.sort(key=lambda x: x['score'], reverse=True)

        top_results = results[:top_k]

        self._log(f"找到 {len(top_results)} 個相關結果")
        return top_results

    def query(self, question: str, use_cache: bool = True) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """
        查詢知識庫
        返回：(緩存答案, 搜索結果)
        """
        # 1. 檢查緩存
        if use_cache:
            cached_answer = self.query_cache(question)
            if cached_answer:
                return cached_answer, []

        # 2. 搜索知識庫
        search_results = self.search(question, top_k=5)

        return None, search_results

    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計"""
        total_queries = sum(entry.get('count', 0) for entry in self.cache.values())

        return {
            'total_entries': len(self.cache),
            'total_queries': total_queries,
            'index_size': len(self.index),
            'kb_file': str(self.kb_file),
            'cache_file': str(self.cache_file),
            'index_file': str(self.index_file)
        }


def main():
    """主函數"""

    # 創建 RAG Cache
    rag = RAGCache()

    print("=" * 60)
    print("RAG 緩存系統")
    print("=" * 60)
    print("")

    # 構建索引
    print("📚 構建索引...")
    rag.build_index()
    print("")

    # 統計信息
    print("📊 統計信息:")
    stats = rag.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print("")

    # 測試搜索
    print("🔍 測試搜索:")
    test_queries = [
        "Python",
        "優化",
        "系統設置",
        "GitHub"
    ]

    for query in test_queries:
        print(f"\n查詢: '{query}'")
        results = rag.search(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['category']}] {result['heading']} (分數: {result['score']})")
                if result.get('summary'):
                    print(f"      摘要: {result['summary']}")
        else:
            print("   沒有找到相關結果")

    print("")
    print("✨ RAG 緩存系統初始化完成！")


if __name__ == "__main__":
    main()
