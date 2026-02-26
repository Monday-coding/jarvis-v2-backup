#!/usr/bin/env python3
"""
測試 Heartbeat Manager
"""

import sys
sys.path.insert(0, '/home/jarvis/.openclaw/workspace/heartbeat')

from heartbeat_manager import HeartbeatManager


def main():
    """主函數"""
    print("=" * 60)
    print("Heartbeat Manager 測試")
    print("=" * 60)
    print()
    print("這個腳本會測試 Heartbeat 管理器的功能：")
    print("  1. 檢查所有 Agents 健康狀態")
    print("  2. 計算響應時間")
    print("  3. 計算故障次數")
    print("  4. 顯示詳細結果")
    print()
    print("=" * 60)
    print()
    
    # 創建管理器
    manager = HeartbeatManager()
    
    # 運行 Heartbeat 檢查
    results = manager.run_heartbeat_check()
    
    # 顯示總結
    print()
    print("=" * 60)
    print("測試完成！")
    print("=" * 60)
    print()
    print("測試結果：")
    print(f"  總檢查的 Agents：{len(results)}")
    
    healthy_count = len([r for r in results if r['status'] == 'healthy'])
    unhealthy_count = len([r for r in results if r['status'] != 'healthy'])
    
    print(f"  健康的 Agents：{healthy_count}")
    print(f"  不健康的 Agents：{unhealthy_count}")
    print()
    print("Heartbeat Manager 已準備就緒！")
    print()
    print("下一步：")
    print("  1. 實現定時 Heartbeat 檢查（每 30-60 秒）")
    print("  2. 實現自動重啟功能")
    print("  3. 實現警報通知功能")
    print("  4. 實現監控儀表板")


if __name__ == "__main__":
    main()
