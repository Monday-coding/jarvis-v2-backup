#!/usr/bin/env python3
"""
超簡化的神經元優化腳本 - 使用簡化的 JSON 提取方法
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import re


WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
KB_FILE = WORKSPACE / "knowledge-base.md"
OLLAMA_URL = "http://localhost:11434"
MODEL = "ollama/qwen2.5:1.5b"


def load_daily_log(date_str: str = None) -> str:
    """讀取今日日誌"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    log_file = MEMORY_DIR / f"{date_str}.md"
    
    if not log_file.exists():
        return f"# {date_str} - 沒有活動記錄\n\n今天還沒有活動記錄。"
    
    with open(log_file, 'r', encoding='utf-8') as f:
        return f.read()


def classify_entries(log_content: str) -> List[Dict[str, Any]]:
    """提取日誌條目"""
    entries = []
    lines = log_content.split('\n')
    current_entry = []
    current_heading = ""
    
    for line in lines:
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
    
    if current_entry:
        entries.append({
            'heading': current_heading,
            'content': '\n'.join(current_entry)
        })
    
    if not entries:
        entries.append({
            'heading': "活動記錄",
            'content': log_content
        })
    
    return entries


def classify_with_llm(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """使用 LLM 分類每個條目 - 使用簡化的 prompt"""
    
    classified_entries = []
    
    for i, entry in enumerate(entries):
        heading = entry.get('heading', '')
        content = entry.get('content', '')
        
        # 簡化的 prompt - 直接要求 JSON，不要其他解釋
        prompt = f"""請分析以下日誌條目並返回 JSON。

分類選項（選一個）：
- conversation
- task
- code
- system
- error
- research

日誌標題：{heading}
日誌內容：{content[:300]}

只返回 JSON，格式如下：
{{"category":"分類選項"}}

只返回 JSON，不要任何其他內容、解釋或標點符號。"""
        
        try:
            result = call_ollama_llm_simple(prompt)
            
            # 嘗試提取 JSON
            classification = extract_simple_json(result)
            
            if classification:
                classified_entries.append({
                    'original': entry,
                    'classification': classification
                })
            else:
                # 使用默認分類
                classified_entries.append({
                    'original': entry,
                    'classification': {
                        'category': 'system',
                        'tags': 'uncategorized',
                        'summary': heading[:50]
                    }
                })
            
            # 顯示進度
            if (i + 1) % 5 == 0:
                print(f"   已處理 {i + 1}/{len(entries)} 個條目...")
                
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


def extract_simple_json(text: str) -> Dict[str, Any]:
    """提取簡單的 JSON"""
    # 查找 {...} 模式
    json_match = re.search(r'\{[^{}]*(?:"[^"]*"[^{}]*[^}]*)*[^{}]*\}', text)
    
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    # 如果找不到 JSON，查找 "category":"xxx"
    category_match = re.search(r'"category"\s*:\s*"([^"]+)"', text)
    if category_match:
        return {'category': category_match.group(1).strip('"')}
    
    return {}


def call_ollama_llm_simple(prompt: str) -> str:
    """調用 Ollama LLM - 簡化版本"""
    import subprocess
    
    payload = {
        "model": MODEL.replace('ollama/', ''),
        "prompt": prompt,
        "stream": False,
        "raw": True,  # 只返回文本，不包含標記
        "options": {
            "temperature": 0.1,  # 更低的溫度，使輸出更確定
            "max_tokens": 50,   # 更少的 tokens
            "num_predict": 50
        }
    }
    
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', f'{OLLAMA_URL}/api/generate',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(payload)],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return result.stdout.strip()


def build_knowledge_base(classified_entries: List[Dict[str, Any]], kb_file: Path):
    """構建知識庫"""
    
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
    
    # 構建新內容
    new_kb = []
    new_kb.append(f"## {datetime.now().strftime('%Y-%m-%d')}")
    new_kb.append("")
    
    for category, entries in categorized.items():
        new_kb.append(f"### {category.upper()}")
        new_kb.append("")
        
        for entry in entries:
            original = entry['original']
            classification = entry['classification']
            
            heading = original.get('heading', '無標題')
            category_val = classification.get('category', '')
            summary = classification.get('summary', heading[:50])
            
            new_kb.append(f"#### {heading}")
            new_kb.append(f"**摘要：** {summary}")
            new_kb.append(f"**分類：** {category_val}")
            new_kb.append("")
    
    # 合併
    kb_lines = kb_content.split('\n')
    
    # 保留最近 30 天
    last_date_idx = -1
    for i, line in enumerate(kb_lines):
        if line.startswith('## 20'):
            last_date_idx = i
    
    if last_date_idx > 0:
        old_kb_lines = kb_lines[:last_date_idx]
    else:
        old_kb_lines = []
    
    full_kb = '\n'.join(old_kb_lines) + '\n' + '\n'.join(new_kb)
    
    # 保存
    with open(kb_file, 'w', encoding='utf-8') as f:
        f.write(full_kb)
    
    print(f"✓ 知識庫已更新: {len(categorized)} 個類別, {len(classified_entries)} 個條目")


def update_memory_link(classified_entries: List[Dict[str, Any]]):
    """更新 MEMORY.md"""
    
    memory_file = WORKSPACE / "MEMORY.md"
    
    if not memory_file.exists():
        return
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        memory_content = f.read()
    
    memory_lines = memory_content.split('\n')
    
    # 查找知識庫部分
    kb_section_idx = -1
    for i, line in enumerate(memory_lines):
        if '## 知識庫' in line or '# 知識庫' in line:
            kb_section_idx = i
            break
    
    if kb_section_idx == -1:
        memory_lines.append("")
        memory_lines.append("## 知識庫")
        memory_lines.append(f"- 連結知識庫: {KB_FILE}")
        memory_lines.append(f"- 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        memory_lines.append("")
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(memory_lines))


def main():
    parser = argparse.ArgumentParser(description='神經元優化 - 簡化版')
    parser.add_argument('--dry-run', action='store_true', help='試運行，不修改文件')
    args = parser.parse_args()
    
    print("🧠 神經元優化（Neural Optimization）- 簡化版")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print("")
    
    # 1. 讀取今日日誌
    print("1️⃣  讀取今日日誌...")
    log_content = load_daily_log()
    print(f"   ✓ 日誌已加載 ({len(log_content)} 字符)")
    print("")
    
    # 2. 分類條目
    print("2️⃣  分類日誌條目...")
    entries = classify_entries(log_content)
    print(f"   ✓ 發現 {len(entries)} 個條目")
    print("")
    
    # 3. 使用 LLM 分類
    print("3️⃣  使用 LLM 分類（使用簡化方法）...")
    classified = classify_with_llm(entries)
    
    # 顯示分類結果
    category_counts = {}
    for entry in classified:
        cat = entry['classification'].get('category', 'uncategorized')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in category_counts.items():
        print(f"   - {cat}: {count}")
    print(f"   ✓ 分類完成")
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
        "date": datetime.now().strftime('%Y-%m-%d'),
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
    summary_dir = WORKSPACE / "neur-opt"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_file = summary_dir / f"summary-{datetime.now().strftime('%Y-%m-%d')}.json"
    
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
