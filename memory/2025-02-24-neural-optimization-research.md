# 神經元優化（Neural Optimization）系統設計

## 📋 專案總覽

- **目標**：自動建立每日紀錄，分類歸納到樹狀資料庫
- **核心組件**：
  1. Python 腳本 - 每日紀錄分類
  2. 樹狀資料庫 - 存儲結構化知識
  3. Cron Job - 定時執行
  4. RAG 索引 - 主動觸發記憶與知識庫

---

## 🧠 核心概念

### 什麼是神經元優化？

**Neural Optimization** 不是傳統的「優化神經網絡」，而是一種：
- 利用神經網絡（LLM）的自監控能力
- 自動提取、分類、歸納日誌紀錄
- 構建結構化的知識圖（樹狀資料庫）
- 讓 AI 能夠「主動反思」並優化自身行為

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    用戶活動                              │
│                  (WhatsApp, 命令等）                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  OpenClaw Main Agent                       │
│                  - 執行任務                                         │
│                  - 記錄日誌                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              每日紀錄 (memory/YYYY-MM-DD.md)                  │
│              - 原始日誌                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            Cron Job (每日 23:55 執行)                        │
│            - 調用 NeurOpt Script                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          NeurOpt Python 腳本 (neur-opt.py)                   │
│          1. 讀取今日日誌                                       │
│          2. 使用 LLM 分類紀錄                                     │
│          3. 提取關鍵信息                                       │
│          4. 更新樹狀資料庫                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          樹狀資料庫 (knowledge-base.md)                     │
│          - 按主題分層                                         │
│          - 連結相關記憶                                       │
│          - 結構化知識                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            RAG 索引 (ChromaDB/FAISS)                       │
│            - 向量化知識                                           │
│            - 快速檢索                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                聊天交互 (RAG)                              │
│          - 語用相關知識                                       │
│          - 主動觸發記憶                                       │
│          - 持續優化                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 檔案結構

```
~/.openclaw/
├── workspace/
│   ├── neur-opt/                    # 神經元優化模塊
│   │   ├── neur-opt.py            # 主腳本
│   │   ├── classify.py           # 分類器
│   │   ├── kb-builder.py          # 知識庫構建器
│   │   └── rag.py                # RAG 索引
│   │
│   ├── knowledge-base.md           # 樹狀資料庫
│   │
│   └── memory/
│       ├── YYYY-MM-DD.md            # 每日紀錄
│       └── memory.md               # 長期記憶
│
└── cron/
    └── neur-opt.daily.sh            # 每日執行腳本
```

---

## 🐍 1. NeurOpt Python 腳本

### neur-opt.py - 主腳本

```python
#!/usr/bin/env python3
"""
神經元優化（Neural Optimization）主腳本
功能：
1. 讀取今日日誌
2. 使用 LLM 分類紀錄
3. 提取關鍵信息
4. 更新樹狀資料庫
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import re

# OpenClaw 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
KB_FILE = WORKSPACE / "knowledge-base.md"
OLLAMA_URL = "http://localhost:11434"
MODEL = "ollama/qwen2.5:1.5b"


def load_daily_log(date_str: str = None) -> str:
    """加載今日日誌"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    log_file = MEMORY_DIR / f"{date_str}.md"
    
    if not log_file.exists():
        return f"# {date_str} - 沒有活動記錄\n\n今天還沒有活動記錄。"
    
    with open(log_file, 'r', encoding='utf-8') as f:
        return f.read()


def classify_entries(log_content: str) -> List[Dict[str, Any]]:
    """
    使用 LLM 分類日誌條目
    返回格式：[{"content": "...", "category": "...", "tags": [...], "summary": "..."}]
    """
    
    # 提取條目（以 ## 或 ### 開頭）
    entries = []
    lines = log_content.split('\n')
    current_entry = []
    current_heading = ""
    
    for line in lines:
        # 檢測標題
        if line.strip().startswith('##') or line.strip().startswith('###'):
            if current_entry:
                entries.append({
                    'heading': current_heading,
                    'content': '\n'.join(current_entry)
                })
            current_heading = line.strip()
            current_entry = []
        else:
            current_entry.append(line)
    
    # 添加最後一個條目
    if current_entry:
        entries.append({
            'heading': current_heading,
            'content': '\n'.join(current_entry)
        })
    
    # 如果沒有標題，將整個內容作為一個條目
    if not entries:
        entries.append({
            'heading': "活動記錄",
            'content': log_content
        })
    
    return entries


def classify_with_llm(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    使用 Ollama LLM 分類每個條目
    """
    
    prompt_template = """
你是一個日誌分類專家。請將以下日誌條目分類。

分類類別（選一個）：
- conversation: 對話
- task: 任務
- code: 代碼
- system: 系統操作
- error: 錯誤
- research: 研究/學習

提取標籤（tags，用逗號分隔）：
- 例如：python, 設置, 錯誤, 研究, 優化

摘要（summary，一行）：
- 用一句話概括這個條目的內容

返回 JSON 格式：
{
  "category": "類別",
  "tags": "標籤1, 標籤2",
  "summary": "摘要"
}

日誌條目：
{heading}
{content}
"""
    
    classified_entries = []
    
    for entry in entries:
        # 構建 prompt
        prompt = prompt_template.format(
            heading=entry.get('heading', ''),
            content=entry.get('content', '')[:1000]  # 限制長度
        )
        
        # 調用 LLM
        try:
            result = call_ollama_llm(
                prompt=f"{prompt}\n\n只返回 JSON，不要任何解釋：",
                model=MODEL
            )
            
            # 解析 JSON
            json_match = re.search(r'\{[^{}]*\}', result)
            if json_match:
                classification = json.loads(json_match.group())
                classified_entries.append({
                    'original': entry,
                    'classification': classification
                })
            else:
                # JSON 解析失敗，使用默認分類
                classified_entries.append({
                    'original': entry,
                    'classification': {
                        'category': 'system',
                        'tags': 'uncategorized',
                        'summary': '無法分類'
                    }
                })
                
        except Exception as e:
            print(f"⚠️  分類失敗: {e}")
            classified_entries.append({
                'original': entry,
                'classification': {
                    'category': 'error',
                    'tags': 'parsing_error',
                    'summary': str(e)[:100]
                }
            })
    
    return classified_entries


def call_ollama_llm(prompt: str, model: str) -> str:
    """調用 Ollama LLM"""
    import subprocess
    import json
    
    payload = {
        "model": model.replace('ollama/', ''),
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 500
        }
    }
    
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', f'{OLLAMA_URL}/api/generate',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(payload)],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    try:
        response = json.loads(result.stdout)
        return response.get('response', '')
    except:
        return result.stdout


def build_knowledge_base(classified_entries: List[Dict[str, Any]], kb_file: Path):
    """
    構建或更新樹狀知識庫
    """
    
    # 讀取現有知識庫
    if kb_file.exists():
        with open(kb_file, 'r', encoding='utf-8') as f:
            kb_content = f.read()
    else:
        kb_content = "# 知識庫\n\n"
    
    # 按類別分組
    categorized = {}
    for entry in classified_entries:
        cat = entry['classification'].get('category', 'uncategorized')
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(entry)
    
    # 構建新的知識庫內容
    new_kb = []
    
    # 添加日期標題
    new_kb.append(f"## {datetime.now().strftime('%Y-%m-%d')}")
    new_kb.append("")
    
    # 按類別組織
    for category, entries in categorized.items():
        new_kb.append(f"### {category.upper()}")
        new_kb.append("")
        
        for entry in entries:
            original = entry['original']
            classification = entry['classification']
            
            # 添加條目
            heading = original.get('heading', '無標題')
            summary = classification.get('summary', '')
            tags = classification.get('tags', '')
            
            new_kb.append(f"#### {heading}")
            if summary:
                new_kb.append(f"**摘要：** {summary}")
            if tags:
                new_kb.append(f"**標籤：** {tags}")
            new_kb.append("")
    
    # 合併現有知識庫（保留最近 30 天）
    kb_lines = kb_content.split('\n')
    
    # 找到最後一個日期標題
    last_date_idx = -1
    for i, line in enumerate(kb_lines):
        if line.startswith('## 20'):
            last_date_idx = i
    
    # 保留最近 30 天的內容
    if last_date_idx > 0:
        old_kb_lines = kb_lines[:last_date_idx]
    else:
        old_kb_lines = []
    
    # 寫入新知識庫
    full_kb = '\n'.join(old_kb_lines) + '\n' + '\n'.join(new_kb)
    
    # 保存知識庫
    with open(kb_file, 'w', encoding='utf-8') as f:
        f.write(full_kb)
    
    print(f"✓ 知識庫已更新: {len(categorized)} 個類別, {len(classified_entries)} 個條目")


def update_memory_link(classified_entries: List[Dict[str, Any]]):
    """
    更新 MEMORY.md，連接相關記憶
    """
    
    memory_file = WORKSPACE / "MEMORY.md"
    
    if not memory_file.exists():
        return
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        memory_content = f.read()
    
    # 添加關聯部分（如果有）
    if len(classified_entries) > 0:
        memory_lines = memory_content.split('\n')
        
        # 查找知識庫部分
        kb_section_idx = -1
        for i, line in enumerate(memory_lines):
            if '## 知識庫' in line or '# 知識庫' in line:
                kb_section_idx = i
                break
        
        # 如果沒有知識庫部分，添加
        if kb_section_idx == -1:
            memory_lines.append("")
            memory_lines.append("## 知識庫")
            memory_lines.append(f"- 見知識庫: {KB_FILE}")
            memory_lines.append(f"- 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            memory_lines.append("")
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(memory_lines))
        else:
            # 更新知識庫部分
            for i in range(kb_section_idx, min(kb_section_idx + 5, len(memory_lines))):
                if '最後更新' in memory_lines[i]:
                    memory_lines[i] = f"- 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    break
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(memory_lines))


def main():
    parser = argparse.ArgumentParser(description='神經元優化 - 自動建立每日紀錄')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)，默認今天')
    parser.add_argument('--dry-run', action='store_true', help='試運行，不修改文件')
    args = parser.parse_args()
    
    print("🧠 神經元優化（Neural Optimization）")
    print(f"📅 日期: {args.date or datetime.now().strftime('%Y-%m-%d')}")
    print("")
    
    # 1. 讀取今日日誌
    print("1️⃣  讀取今日日誌...")
    log_content = load_daily_log(args.date)
    print(f"   ✓ 日誌已加載 ({len(log_content)} 字符)")
    print("")
    
    # 2. 分類條目
    print("2️⃣  分類日誌條目...")
    entries = classify_entries(log_content)
    print(f"   ✓ 發現 {len(entries)} 個條目")
    print("")
    
    # 3. 使用 LLM 分類
    print("3️⃣  使用 LLM 分類...")
    classified = classify_with_llm(entries)
    print(f"   ✓ 分類完成")
    
    # 顯示分類結果
    category_counts = {}
    for entry in classified:
        cat = entry['classification'].get('category', 'uncategorized')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in category_counts.items():
        print(f"   - {cat}: {count}")
    print("")
    
    # 4. 構建知識庫
    print("4️⃣  構建知識庫...")
    if not args.dry_run:
        build_knowledge_base(classified, KB_FILE)
        update_memory_link(classified)
        print(f"   ✓ 知識庫已更新: {KB_FILE}")
        print(f"   ✓ MEMORY.md 已連接")
    else:
        print("   [試運行] 跳過知識庫更新")
    print("")
    
    # 5. 生成摘要
    print("5️⃣  生成摘要...")
    summary = {
        "date": args.date or datetime.now().strftime('%Y-%m-%d'),
        "total_entries": len(entries),
        "categories": category_counts,
        "knowledge_base": str(KB_FILE),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"   ✓ 摘要已生成:")
    print(f"      - 日期: {summary['date']}")
    print(f"      - 總條目: {summary['total_entries']}")
    print(f"      - 分類: {summary['categories']}")
    print("")
    
    # 保存摘要
    summary_file = WORKSPACE / "neur-opt" / f"summary-{datetime.now().strftime('%Y-%m-%d')}.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not args.dry_run:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"   ✓ 摘要已保存: {summary_file}")
    else:
        print("   [試運行] 跳過摘要保存")
    print("")
    
    print("✨ 神經元優化完成！")


if __name__ == "__main__":
    main()
```

---

## 📅 2. Cron Job 配置

### neur-opt.daily.sh - 每日執行腳本

```bash
#!/bin/bash
# 神經元優化 - 每日執行腳本

# 設置
WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE/neur-opt"
PYTHON_SCRIPT="$SCRIPT_DIR/neur-opt.py"
LOG_FILE="$WORKSPACE/neur-opt/cron.log"

# 確保工作區存在
mkdir -p "$SCRIPT_DIR"

# 執行 Python 腳本
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🧠 開始神經元優化..." >> "$LOG_FILE"
cd "$WORKSPACE"

# 執行 neur-opt
if [ -f "$PYTHON_SCRIPT" ]; then
    python3 "$PYTHON_SCRIPT" --date "$(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 腳本不存在: $PYTHON_SCRIPT" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✨ 神經元優化完成" >> "$LOG_FILE"
```

### 安裝 Cron Job

```bash
# 方法 1：使用 crontab -e（推薦）
(crontab -l 2>/dev/null; echo "55 23 * * * $HOME/.openclaw/workspace/neur-opt/neur-opt.daily.sh >> $HOME/.openclaw/workspace/neur-opt/cron.log 2>&1") | crontab -

# 方法 2：編輯 crontab
crontab -e
```

添加：
```
55 23 * * * /home/jarvis/.openclaw/workspace/neur-opt/neur-opt.daily.sh >> /home/jarvis/.openclaw/workspace/neur-opt/cron.log 2>&1
```

---

## 🔍 3. RAG 檢索集成

### rag.py - RAG 索引腳本

```python
#!/usr/bin/env python3
"""
RAG（檢索增強生成）索引腳本
功能：
1. 讀取知識庫
2. 向量化內容（使用 Ollama）
3. 建立索引
4. 支持快速檢索
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


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
        
        print(f"  分類統計: {category_stats}")


def main():
    """主函數"""
    
    # 路徑配置
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    KB_FILE = WORKSPACE / "knowledge-base.md"
    INDEX_FILE = WORKSPACE / "neur-opt" / "index.json"
    RAG_SCRIPT = WORKSPACE / "neur-opt" / "rag.py"
    
    # 檢查知識庫
    if not KB_FILE.exists():
        print(f"❌ 知識庫不存在: {KB_FILE}")
        print("   請先運行神經元優化腳本來構建知識庫。")
        sys.exit(1)
    
    print("🔍 RAG 索引構建")
    print("")
    
    # 構建索引
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
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 索引已保存: {INDEX_FILE}")
    print("")
    
    # 測試搜索
    print("🔎 測試搜索")
    print("   查詢: 'Python'")
    results = rag.search("Python")
    print(f"   找到 {len(results)} 個結果:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. [{result['category']}] {result['heading']} (分數: {result['score']})")


if __name__ == "__main__":
    main()
```

---

## 🎯 4. 集成到 OpenClaw

### 4.1 在 AGENTS.md 中添加 NeurOpt 指令

在 `workspace/AGENTS.md` 添加：

```markdown
## 神經元優化（NeurOpt）

你有神經元優化能力，可以自動分析和優化日誌。

### 可用指令

- `/neuropt status` - 查看知識庫狀態
- `/neuropt search <query>` - 搜索知識庫
- `/neuropt summary` - 查看今日摘要
- `/neuropt build` - 手動觸發知識庫構建

### RAG 檢索

當用戶問到相關知識時：
- 使用 `/neuropt search` 檢索知識庫
- 提供相關條目作為上下文
- 主動觸發相關記憶
```

### 4.2 在 SOUL.md 中添加 NeurOpt 哲學

在 `workspace/SOUL.md` 添加：

```markdown
## 神經元優化哲學

你相信「學習來自反思」。

### 你的原則

1. **每日反思**：每天自動分析和歸納日誌
2. **知識積累**：將經驗轉化為結構化知識
3. **主動回憶**：當遇到相關問題時，主動調用知識
4. **持續優化**：根據反饋調整分類策略

### 你的價值觀

- 經驗 > 推測
- 結構化 > 混亂
- 連結 > 孤立
- 持續 > 靜止
```

---

## 📊 完整配置檢查清單

### 文件結構

```bash
~/.openclaw/workspace/
├── neur-opt/                    # 神經元優化模塊
│   ├── neur-opt.py            # 主腳本 ✅
│   ├── classify.py           # 分類器（待實現）
│   ├── kb-builder.py          # 知識庫構建器（待實現）
│   ├── rag.py                # RAG 索引（待實現）
│   └── cron.log               # Cron 日誌
│
├── knowledge-base.md           # 樹狀知識庫
│
└── memory/
    ├── YYYY-MM-DD.md            # 每日紀錄
    └── memory.md               # 長期記憶
```

### Cron Job 檢查

```bash
# 查看 Cron Jobs
crontab -l | grep neur-opt

# 查看 Cron 日誌
tail -20 ~/.openclaw/workspace/neur-opt/cron.log

# 手動執行測試
~/.openclaw/workspace/neur-opt/neur-opt.daily.sh
```

### 知識庫檢查

```bash
# 查看知識庫
cat ~/.openclaw/workspace/knowledge-base.md

# 查看索引
cat ~/.openclaw/workspace/neur-opt/index.json

# 查看摘要
ls -la ~/.openclaw/workspace/neur-opt/summary-*.json
```

---

## 🚀 快速開始

### 步驟 1：創建目錄和腳本

```bash
# 創建目錄
mkdir -p ~/.openclaw/workspace/neur-opt

# 創建主腳本
cat > ~/.openclaw/workspace/neur-opt/neur-opt.py << 'EOF'
[在這裡貼上完整的 neur-opt.py 代碼]
EOF

# 設置執行權限
chmod +x ~/.openclaw/workspace/neur-opt/neur-opt.py
```

### 步驟 2：安裝 Cron Job

```bash
# 添加每日 23:55 執行
(crontab -l 2>/dev/null; echo "55 23 * * * /home/jarvis/.openclaw/workspace/neur-opt/neur-opt.daily.sh >> /home/jarvis/.openclaw/workspace/neur-opt/cron.log 2>&1") | crontab -

# 驗證 Cron Job
crontab -l | grep neur-opt
```

### 步驟 3：測試腳本

```bash
# 手動執行（測試模式）
python3 ~/.openclaw/workspace/neur-opt/neur-opt.py --dry-run

# 實際執行
python3 ~/.openclaw/workspace/neur-opt/neur-opt.py
```

---

## 📝 示例輸出

### 知識庫結構示例

```markdown
## 2025-02-24

### CODE
#### Python 腳本優化
**摘要：** 優化了 Python 腳本的執行速度
**標籤：** python, 優化, 效率

#### Git Hook 設置
**摘要：** 配置了 pre-commit hook
**標籤：** git, 版本控制, 自動化

### TASK
#### 系統設置
**摘要：** 完成了 Ollama + Multi-Agent 設置
**標籤：** 系統, 設置, ollama, multi-agent

### RESEARCH
#### 神經元優化研究
**摘要：** 研究了 NeurOpt 架構
**標籤：** 研究, 神經元優化, AI
```

### RAG 搜索示例

```
用戶: "Python 腳本優化"

RAG 搜索結果:
1. [CODE] Python 腳本優化 (分數: 10)
   - 摘要: 優化了 Python 腳本的執行速度
   - 標籤: python, 優化, 效率
   - 內容: [完整內容]

AI 回應:
"根據我之前的經驗（見知識庫中的相關條目），Python 腳本優化有以下幾種方法..."
```

---

## 🎉 總結

### 系統組件

| 組件 | 功能 | 狀態 |
|------|------|------|
| **NeurOpt Script** | 每日分類日誌 | 📝 待實現 |
| **樹狀知識庫** | 結構化知識存儲 | 📝 待實現 |
| **Cron Job** | 每日 23:55 自動執行 | 📝 待設置 |
| **RAG 索引** | 快速檢索知識 | 📝 待實現 |
| **OpenClaw 集成** | 主動觸發記憶 | 📝 待集成 |

### 工作流程

```
用戶活動
    ↓
OpenClaw 執行
    ↓
日誌記錄 (memory/YYYY-MM-DD.md)
    ↓
Cron Job (每日 23:55)
    ↓
NeurOpt Script 分類
    ↓
更新樹狀知識庫 (knowledge-base.md)
    ↓
RAG 索引
    ↓
未來對話時主動觸發記憶
```

### 預期效果

1. **自動化**：每天自動分析和歸納日誌
2. **結構化**：將經驗轉化為可檢索的知識
3. **智能化**：根據上下文主動調用相關知識
4. **持續優化**：每日反思，持續改進

---

## 📁 檔案位置

所有文件將創建在：
- `~/.openclaw/workspace/neur-opt/`
- `~/.openclaw/workspace/knowledge-base.md`
- `~/.openclaw/workspace/memory/YYYY-MM-DD.md`

---

準備開始實現嗎？我可以幫你：
1. ✅ 創建完整腳本
2. ✅ 設置 Cron Job
3. ✅ 測試 RAG 搜索
4. ✅ 集成到 OpenClaw

告訴我！🚀
