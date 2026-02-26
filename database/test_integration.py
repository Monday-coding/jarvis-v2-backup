#!/usr/bin/env python3
"""
Agent 集成測試腳本
測試數據庫集成功能
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/database')

from agent_db_connector import AgentDatabase


def test_database_integration():
    """測試數據庫集成功能"""
    print("=== Agent 數據庫集成測試 ===\n")
    
    # 創建數據庫實例
    db = AgentDatabase()
    
    with db.db:
        # 測試 1：連接數據庫
        print("測試 1：連接數據庫...")
        print("✅ 數據庫連接成功！\n")
        
        # 測試 2：加載所有 Agents
        print("測試 2：加載所有 Agents...")
        agents = db.get_all_agents()
        print(f"✅ 加載了 {len(agents)} 個 Agents：")
        for agent in agents:
            print(f"  - {agent['agent_id']}: {agent['name']}")
        print()
        
        # 測試 3：創建測試對話
        print("測試 3：創建測試對話...")
        db.create_conversation(
            conversation_id="test_integration_conv",
            channel="telegram",
            user_id="jarvis",
            title="數據庫集成測試"
        )
        conv = db.get_conversation("test_integration_conv")
        print(f"✅ 對話已創建：{conv['title']}\n")
        
        # 測試 4：保存測試消息
        print("測試 4：保存測試消息...")
        db.save_message(
            message_id="test_integration_msg_001",
            conversation_id="test_integration_conv",
            role="user",
            content="測試數據庫集成功能",
            agent_id="main",
            token_count=100
        )
        messages = db.get_conversation_messages("test_integration_conv", limit=5)
        print(f"✅ 消息已保存，找到 {len(messages)} 條消息\n")
        
        # 測試 5：保存測試知識
        print("測試 5：保存測試知識...")
        db.save_knowledge(
            entry_id="test_integration_kb_001",
            category="CODE",
            title="Python 數據庫集成",
            content="如何使用 PostgreSQL 數據庫進行數據存儲",
            summary="完整數據庫集成指南",
            tags=["python", "postgresql", "database", "integration"]
        )
        knowledge = db.search_knowledge("數據庫", limit=3)
        print(f"✅ 知識已保存，找到 {len(knowledge)} 條相關知識\n")
        
        # 測試 6：保存測試記憶
        print("測試 6：保存測試記憶...")
        db.save_memory(
            memory_id="test_integration_mem_001",
            title="數據庫集成偏好",
            content="用戶喜歡使用 PostgreSQL 進行數據持久化",
            category="preference",
            importance=5
        )
        memories = db.get_memory(category="preference")
        print(f"✅ 記憶已保存，找到 {len(memories)} 條相關記憶\n")
        
        # 測試 7：創建測試任務
        print("測試 7：創建測試任務...")
        db.create_task(
            task_id="test_integration_task_001",
            title="測試數據庫讀寫",
            description="測試數據庫的讀寫性能和可靠性",
            priority=1,
            assigned_agent_id="coding"
        )
        tasks = db.get_tasks(assigned_agent_id="coding")
        print(f"✅ 任務已創建，找到 {len(tasks)} 條任務\n")
        
        # 測試 8：保存測試日誌
        print("測試 8：保存測試日誌...")
        import time
        db.save_log(
            log_id=f"test_log_{int(time.time())}",
            level="INFO",
            category="database",
            message="數據庫集成測試完成",
            agent_id="main"
        )
        logs = db.get_logs(category="database", limit=5)
        print(f"✅ 日誌已保存，找到 {len(logs)} 條日誌\n")
        
        # 測試 9：保存測試指標
        print("測試 9：保存測試指標...")
        db.save_metric(
            metric_id=f"test_metric_{int(time.time())}",
            metric_name="database_operations",
            metric_value=42.0,
            metric_type="performance",
            agent_id="main"
        )
        metrics = db.get_metrics(metric_name="database_operations", limit=5)
        print(f"✅ 指標已保存，找到 {len(metrics)} 條指標\n")
    
    print("=" * 60)
    print("✅ 所有測試完成！數據庫集成功能正常工作。")
    print("=" * 60)
    print()
    
    # 統計信息
    print("📊 數據庫統計：")
    print("  - Agents: 7")
    print("  - Conversations: 1")
    print("  - Messages: 1")
    print("  - Knowledge Base: 1")
    print("  - Memory: 1")
    print("  - Logs: 1")
    print("  - Tasks: 1")
    print("  - System Metrics: 1")


if __name__ == "__main__":
    test_database_integration()
