#!/usr/bin/env python3
"""
Heartbeat Manager
核心協調器 - 監控所有 Agents
"""

import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


class HeartbeatManager:
    """Heartbeat 管理器"""
    
    def __init__(self):
        # Agents 配置
        self.agents = {
            'main': {
                'name': 'Main Agent',
                'url': 'http://localhost:8000/health',
                'timeout': 5,
                'interval': 30,
                'fail_threshold': 3,
                'enabled': True
            },
            'chat': {
                'name': 'Chat Assistant',
                'url': 'http://localhost:8001/health',
                'timeout': 10,
                'interval': 60,
                'fail_threshold': 5,
                'enabled': True
            },
            'coding': {
                'name': 'Worker',
                'url': 'http://localhost:8002/health',
                'timeout': 10,
                'interval': 60,
                'fail_threshold': 5,
                'enabled': True
            },
            'system-admin': {
                'name': 'System Admin',
                'url': 'http://localhost:8003/health',
                'timeout': 10,
                'interval': 30,
                'fail_threshold': 3,
                'enabled': True
            },
            'weather': {
                'name': 'Weather Agent',
                'url': 'http://localhost:8004/health',
                'timeout': 10,
                'interval': 60,
                'fail_threshold': 5,
                'enabled': True
            }
        }
        
        # 故障計數
        self.fail_counts = {agent_id: 0 for agent_id in self.agents}
        
        # Heartbeat 狀態
        self.running = False
        self.last_check_time = {}
    
    def check_agent_health(self, agent_id: str) -> dict:
        """檢查 Agent 健康狀態"""
        agent = self.agents.get(agent_id)
        if not agent or not agent['enabled']:
            return {
                'agent_id': agent_id,
                'status': 'disabled',
                'response_time': None,
                'error': 'Agent not enabled'
            }
        
        start_time = time.time()
        
        try:
            response = requests.get(
                agent['url'],
                timeout=agent['timeout']
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # 重置故障計數
                self.fail_counts[agent_id] = 0
                self.last_check_time[agent_id] = datetime.now(HK_TZ)
                
                return {
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'status': 'healthy',
                    'response_time': round(response_time, 2),
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': self.fail_counts[agent_id]
                }
            else:
                # 故障計數
                self.fail_counts[agent_id] = self.fail_counts.get(agent_id, 0) + 1
                self.last_check_time[agent_id] = datetime.now(HK_TZ)
                
                return {
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'status': 'unhealthy',
                    'response_time': round(response_time, 2),
                    'error': f"HTTP {response.status_code}",
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': self.fail_counts[agent_id]
                }
        
        except requests.Timeout:
            # 故障計數
            self.fail_counts[agent_id] = self.fail_counts.get(agent_id, 0) + 1
            self.last_check_time[agent_id] = datetime.now(HK_TZ)
            
            return {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'status': 'timeout',
                'response_time': None,
                'error': 'Request timeout',
                'timestamp': datetime.now(HK_TZ),
                'fail_count': self.fail_counts[agent_id]
            }
        
        except Exception as e:
            # 故障計數
            self.fail_counts[agent_id] = self.fail_counts.get(agent_id, 0) + 1
            self.last_check_time[agent_id] = datetime.now(HK_TZ)
            
            return {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'status': 'error',
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.now(HK_TZ),
                'fail_count': self.fail_counts[agent_id]
            }
    
    def check_all_agents(self) -> List[dict]:
        """檢查所有 Agents"""
        results = []
        
        for agent_id, agent in self.agents.items():
            if agent['enabled']:
                result = self.check_agent_health(agent_id)
                results.append(result)
        
        return results
    
    def run_heartbeat_check(self):
        """運行一次 Heartbeat 檢查"""
        print("=" * 60)
        print("Heartbeat 檢查")
        print("=" * 60)
        print()
        
        check_time = datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{check_time}] 開始檢查...")
        print()
        
        # 檢查所有 Agents
        results = self.check_all_agents()
        
        # 統計結果
        healthy_count = len([r for r in results if r['status'] == 'healthy'])
        unhealthy_count = len([r for r in results if r['status'] != 'healthy'])
        timeout_count = len([r for r in results if r['status'] == 'timeout'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        print(f"檢查結果：")
        print(f"  總數：{len(results)}")
        print(f"  正常：{healthy_count}")
        print(f"  異常：{unhealthy_count}")
        print(f"  超時：{timeout_count}")
        print(f"  錯誤：{error_count}")
        print()
        
        # 顯示詳細結果
        print("詳細結果：")
        for i, result in enumerate(results, 1):
            status_emoji = "✅" if result['status'] == 'healthy' else "❌"
            
            print(f"{i}. {status_emoji} {result['agent_name']} ({result['status']})")
            
            if result['status'] == 'healthy':
                print(f"   響應時間：{result['response_time']}s")
            else:
                print(f"   錯誤：{result['error']}")
                print(f"   故障次數：{result['fail_count']}")
            
            print()
        
        print("=" * 60)
        print("檢查完成")
        print("=" * 60)
        print()
        
        return results


def main():
    """主函數 - 測試 Heartbeat"""
    print("Heartbeat 管理器測試")
    print("=" * 60)
    print()
    
    # 創建管理器
    manager = HeartbeatManager()
    
    # 運行檢查
    results = manager.run_heartbeat_check()
    
    # 顯示總結
    print("總結：")
    print(f"  檢查的 Agents：{len(results)}")
    print()
    print("Heartbeat 管理器已準備就緒！")


if __name__ == "__main__":
    main()
