#!/usr/bin/env python3
"""
測試 Ollama API 並修復問題
"""

import subprocess
import json


def test_ollama():
    """測試 Ollama API"""
    
    OLLAMA_URL = "http://localhost:11434"
    MODEL = "qwen2.5:1.5b"
    
    # 測試 1：簡單測試
    print("🧪 測試 1：簡單生成")
    result = call_ollama("你好")
    print(f"結果：{result}")
    print("")
    
    # 測試 2：JSON 輸出
    print("🧪 測試 2：JSON 分類")
    prompt = """
你是個分類器。請將 "你好" 分類為 "chat" 或 "task"。
只返回類別詞彙，不要任何其他內容。
"""
    result = call_ollama(prompt)
    print(f"結果：{result}")
    print("")
    
    # 測試 3：結構化 JSON
    print("🧪 測試 3：結構化 JSON")
    prompt = """
你是個分類器。請將 "你好" 分類。
返回 JSON 格式：{"category": "chat"}
只返回 JSON，不要任何其他內容。
"""
    result = call_ollama(prompt)
    print(f"結果：{result}")
    print("")
    
    # 測試 4：直接 JSON 模式
    print("🧪 測試 4：使用格式化參數")
    payload = {
        "model": MODEL.replace('ollama/', ''),
        "prompt": "你好",
        "stream": False,
        "format": "json"  # 使用格式化參數
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
        print(f"結果：{response}")
        print("")
    except:
        print(f"原始輸出：{result.stdout}")


def call_ollama(prompt):
    """調用 Ollama"""
    import subprocess
    import json
    
    OLLAMA_URL = "http://localhost:11434"
    MODEL = "qwen2.5:1.5b"
    
    payload = {
        "model": MODEL.replace('ollama/', ''),
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 100
        }
    }
    
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', f'{OLLAMA_URL}/api/generate',
         '-H', 'Content-Type: application/json',
         "-d", json.dumps(payload)],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    try:
        response = json.loads(result.stdout)
        return response.get('response', '')
    except:
        return result.stdout


if __name__ == "__main__":
    test_ollama()
