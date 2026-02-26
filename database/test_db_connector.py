#!/usr/bin/env python3
"""
測試腳本：驗證數據庫連接器功能
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase


def main():
    print("=== PostgreSQL 數據庫連接器測試 ===\n")
    
    # 創建數據庫實例
    agent_db = AgentDatabase()
    
    # 測試 1：連接數據庫
    print("測試 1：連接數據庫...")
    with agent_db.db:
        print("✅ 數據庫連接成功！\n")
    
    # 測試 2：獲取所有 Agents
    print("測試 2：獲取所有 Agents...")
    agents = agent_db.get_all_agents()
    print(f"✅ 找到 {len(agents)} 個 Agents：")
    for agent in agents:
        print(f"  - {agent['agent_id']}: {agent['name']} ({agent['model']})")
    print()
    
    # 測試 3：獲取所有表
    print("測試 3：獲取所有表...")
    tables = agent_db.get_tables()
    print(f"✅ 找到 {len(tables)} 個表：")
    for table in tables:
        print(f"  - {table['table_name']}")
    print()
    
    # 測試 4：創建測試對話
    print("測試 4：創建測試對話...")
    agent_db.create_conversation(
        conversation_id="test_conv_001",
        channel="telegram",
        user_id="test_user",
        title="測試對話"
    )
    conv = agent_db.get_conversation("test_conv_001")
    print(f"✅ 對話已創建：{conv['title']}\n")
    
    # 測試 5：保存測試消息
    print("測試 5：保存測試消息...")
    agent_db.save_message(
        message_id="test_msg_001",
        conversation_id="test_conv_001",
        role="user",
        content="這是測試消息",
        agent_id="chat",
        token_count=50
    )
    messages = agent_db.get_conversation_messages("test_conv_001", limit=5)
    print(f"✅ 消息已保存，找到 {len(messages)} 條消息\n")
    
    # 測試 6：保存測試知識
    print("測試 6：保存測試知識...")
    agent_db.save_knowledge(
        entry_id="test_kb_001",
        category="CODE",
        title="測試知識",
        content="這是測試知識內容",
        summary="測試摘要",
        tags=["python", "test"]
    )
    knowledge = agent_db.search_knowledge("測試", limit=5)
    print(f"✅ 知識已保存，找到 {len(knowledge)} 條相關知識\n")
    
    # 測試 7：保存測試記憶
    print("測試 7：保存測試記憶...")
    agent_db.save_memory(
        memory_id="test_mem_001",
        title="測試記憶",
        content="這是測試記憶內容",
        category="preference",
        importance=5
    )
    memories = agent_db.get_memory(category="preference")
    print(f"✅ 記憶已保存，找到 {len(memories)} 條記憶\n")
    
    # 測試 8：保存測試日誌
    print("測試 8：保存測試日誌...")
    import time
    agent_db.save_log(
        log_id=f"test_log_{int(time.time())}",
        level="INFO",
        category="database",
        message="測試日誌消息",
        agent_id="main"
    )
    logs = agent_db.get_logs(level="INFO", limit=5)
    print(f"✅ 日誌已保存，找到 {len(logs)} 條日誌\n")
    
    # 測試 9：創建測試任務
    print("測試 9：創建測試任務...")
    agent_db.create_task(
        task_id="test_task_001",
        title="測試任務",
        description="這是測試任務描述",
        priority=1,
        assigned_agent_id="coding"
    )
    tasks = agent_db.get_tasks(assigned_agent_id="coding")
    print(f"✅ 任務已創建，找到 {len(tasks)} 個任務\n")
    
    # 測試 10：保存測試指標
    print("測試 10：保存測試指標...")
    agent_db.save_metric(
        metric_id=f"test_metric_{int(time.time())}",
        metric_name="response_time",
        metric_value=1.234,
        metric_type="performance",
        agent_id="chat"
    )
    metrics = agent_db.get_metrics(metric_name="response_time", limit=5)
    print(f"✅ 指標已保存，找到 {len(metrics)} 條指標\n")
    
    print("=== 測試完成！數據庫連接器所有功能正常工作。===")


if __name__ == "__main__":
    main()
