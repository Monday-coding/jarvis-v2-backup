#!/usr/bin/env python3
"""
修復 AgentDatabase 上下文管理器
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

# 重新導入整個文件
with open('/home/jarvis/.openclaw/workspace/database/agent_db_connector.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加 __enter__ 和 __exit__ 方法
agent_class_start = content.find('class AgentDatabase:')
if agent_class_start != -1:
    # 找到 __init__ 方法
    init_start = content.find('def __init__(self):', agent_class_start)
    
    # 在 __init__ 方法之後添加上下文管理器
    if init_start != -1:
        # 找到 self.db = PostgreSQLConnector()
        init_end = content.find('\n\n    # ==================== AGENTS', init_start)
        
        # 替換該部分
        new_init = '''    def __init__(self):
        self.db = PostgreSQLConnector()

    def __enter__(self):
        """上下文管理器入口"""
        self.db.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.db.disconnect()

    # ==================== AGENTS'''

'''
        content = content[:init_start] + new_init + content[init_end:]
        
        # 保存修改後的文件
        with open('/home/jarvis/.openclaw/workspace/database/agent_db_connector_fixed.py', 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("文件已修復並保存為 agent_db_connector_fixed.py")
    print("請備份原文件，然後用修復版本替換")
