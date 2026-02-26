#!/usr/bin/env python3
"""
檢查 Agent 記憶體使用情況
"""

import psutil
import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def check_agent_memory():
    """檢查 Agent 記憶體使用"""
    print("=" * 60)
    print("Agent 記憶體使用檢查")
    print("=" * 60)
    print()
    
    # 1. 獲取所有 Agents 進程
    print("[1/5] 獲取所有 Agents 進程...")
    agents = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent']):
        try:
            name = proc.info['name']
            if any(agent in name.lower() for agent in ['jarvis', 'openclaw', 'main', 'chat', 'coding', 'system', 'weather']):
                agents.append({
                    'pid': proc.info['pid'],
                    'name': name,
                    'memory_percent': proc.info['memory_percent'],
                    'memory_info': proc.info['memory_info'],
                    'cpu_percent': proc.info['cpu_percent']
                })
        except Exception:
            pass
    
    print(f"  找到 {len(agents)} 個 Agents 進程")
    print()
    
    # 2. 按記憶體使用排序
    print("[2/5] 按記憶體使用排序...")
    sorted_agents = sorted(agents, key=lambda x: x['memory_percent'], reverse=True)
    
    print(f"  前 10 個記憶體使用最高的 Agents：")
    print()
    
    for i, agent in enumerate(sorted_agents[:10], 1):
        memory_mb = agent['memory_info'].rss / (1024 * 1024)
        print(f"    {i}. {agent['name']} (PID: {agent['pid']})")
        print(f"       記憶體：{memory_mb:.1f} MB ({agent['memory_percent']:.1f}%)")
        print(f"       CPU：{agent['cpu_percent']:.1f}%")
        print()
    
    # 3. 檢查總記憶體使用
    print("[3/5] 檢查總記憶體使用...")
    total_memory = sum(agent['memory_info'].rss for agent in agents)
    total_memory_mb = total_memory / (1024 * 1024)
    
    print(f"  總記憶體使用：{total_memory_mb:.1f} MB ({total_memory / (1024 * 1024 * 1024):.2f} GB)")
    print()
    
    # 4. 檢查系統總記憶體
    print("[4/5] 檢查系統總記憶體...")
    system_memory = psutil.virtual_memory()
    
    print(f"  系統總記憶體：{system_memory.total / (1024 * 1024 * 1024):.2f} GB")
    print(f"  系統可用記憶體：{system_memory.available / (1024 * 1024 * 1024):.2f} GB")
    print(f"  系統記憶體使用率：{system_memory.percent:.1f}%")
    print()
    
    # 5. 統論
    print("[5/5] 分析和建議...")
    print()
    
    # 計憶體使用率
    agent_memory_percent = (total_memory / system_memory.total) * 100
    
    print("分析：")
    print(f"  Agents 記憶體使用率：{agent_memory_percent:.1f}%")
    
    if agent_memory_percent > 80:
        print(f"  ⚠️  記憶體使用率過高（{agent_memory_percent:.1f}%）")
        print(f"  建議：")
        print(f"    1. 重啟高記憶體使用的 Agents")
        print(f"    2. 使用量化模型（int8、8-bit）")
        print(f"    3. 減少並發請求數量")
        print(f"    4. 使用模型分片（按需載入）")
        print(f"    5. 增加系統記憶體")
    elif agent_memory_percent > 60:
        print(f"  ⚠️  記憶體使用率偏高（{agent_memory_percent:.1f}%）")
        print(f"  建議：")
        print(f"    1. 監控高記憶體使用的 Agents")
        print(f"    2. 考慮使用量化模型")
        print(f"    3. 減少並發請求數量")
    else:
        print(f"  ✅  記憶體使用率正常（{agent_memory_percent:.1f}%）")
    
    print()
    print("高記憶體使用的 Agents：")
    for agent in sorted_agents[:5]:
        print(f"  - {agent['name']} ({agent['memory_percent']:.1f}%)")
    
    print()
    print("=" * 60)
    print("檢查完成")
    print("=" * 60)
    print()
    print("總結：")
    print(f"  找到的 Agents：{len(agents)}")
    print(f"  總記憶體使用：{total_memory_mb:.1f} MB")
    print(f"  記憶體使用率：{agent_memory_percent:.1f}%")
    print()


def main():
    """主函數"""
    print("Agent 記憶體使用檢查")
    print("=" * 60)
    print()
    print("這個腳本會：")
    print("  1. 獲取所有 Agents 進程")
    print("  2. 按記憶體使用排序")
    print("  3. 檢查總記憶體使用")
    print("  4. 檢查系統總記憶體")
    print("  5. 分析和建議")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    check_agent_memory()


if __name__ == "__main__":
    main()
