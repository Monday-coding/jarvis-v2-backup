# Heartbeat 功能優化方案

## 📋 概述

**Heartbeat 功能**是一個定期發送信號的機制，用於：
- 監控系統健康狀態
- 檢測組件是否正常運行
- 提早發現潛在故障
- 確保服務可用性

## 🎯 目標

### 核心目標
1. **系統健康監控** - 實時監控所有組件
2. **故障檢測** - 快速發現和定位問題
3. **自動恢復** - 自動重啟故障組件
4. **性能優化** - 減少 heartbeat 本身對系統的影響
5. **可觀測性** - 提供清晰的監控界面和警報

---

## 🏗 系統架構

### 架構設計

```
┌─────────────────────────────────────────┐
│           Heartbeat Manager               │
│           (核心協調器）                      │
├─────────────────────────────────────────┤
│                                           │
│  ┌────────────────────────────────┐   │
│  │   組件監控器              │   │
│  │   - Agents                 │   │
│  │   - PostgreSQL               │   │
│  │   - Docker                  │   │
│  │   - 系統服務                │   │
│  └────────────────────────────────┘   │
│                                           │
│  ┌────────────────────────────────┐   │
│  │   策略管理器              │   │
│  │   - 發送頻率                │   │
│  │   - 检測策略                │   │
│  │   - 重試機制                │   │
│  └────────────────────────────────┘   │
│                                           │
│  ┌────────────────────────────────┐   │
│  │   警報處理器              │   │
│  │   - 警報生成                │   │
│  │   - 通知發送                │   │
│  │   - 降級處理                │   │
│  └────────────────────────────────┘   │
│                                           │
│  ┌────────────────────────────────┐   │
│  │   數據收集器              │   │
│  │   - 指標收集                │   │
│  │   - 趨勢分析                │   │
│  │   - 報告生成                │   │
│  └────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 💓 核心功能設計

### 1. 組件監控

#### 1.1 Agents 監控
```python
class AgentHeartbeat:
    """Agent 心跳監控"""
    
    def __init__(self):
        self.agents = {
            'main': {'name': 'Main Agent', 'url': 'http://localhost:8000/health'},
            'chat': {'name': 'Chat Assistant', 'url': 'http://localhost:8001/health'},
            'coding': {'name': 'Worker', 'url': 'http://localhost:8002/health'},
            'system-admin': {'name': 'System Admin', 'url': 'http://localhost:8003/health'},
            'weather': {'name': 'Weather Agent', 'url': 'http://localhost:8004/health'}
        }
        self.heartbeat_interval = 60  # 秒
        self.timeout = 10  # 秒
        self.fail_threshold = 3  # 連續失敗閾值
    
    def check_agent_health(self, agent_id: str) -> dict:
        """檢查 Agent 健康狀態"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {
                'agent_id': agent_id,
                'status': 'unknown',
                'response_time': None,
                'error': 'Unknown agent'
            }
        
        start_time = time.time()
        try:
            response = requests.get(
                agent['url'],
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'status': 'healthy',
                    'response_time': response_time,
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 0
                }
            else:
                return {
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'status': 'unhealthy',
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}",
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 1
                }
        except Exception as e:
            return {
                'agent_id': agent_id,
                'agent_name': agent['name'],
                'status': 'error',
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.now(HK_TZ),
                'fail_count': 1
            }
    
    def check_all_agents(self) -> list:
        """檢查所有 Agents"""
        results = []
        
        for agent_id in self.agents:
            result = self.check_agent_health(agent_id)
            results.append(result)
        
        return results
```

#### 1.2 PostgreSQL 監控
```python
class DatabaseHeartbeat:
    """數據庫心跳監控"""
    
    def __init__(self):
        self.db = PostgreSQLConnector()
        self.heartbeat_interval = 60  # 秒
        self.timeout = 10  # 秒
        self.fail_threshold = 3  # 連續失敗閾值
    
    def check_database_health(self) -> dict:
        """檢查數據庫健康狀態"""
        start_time = time.time()
        try:
            # 嘗試連接
            if not self.db.connect():
                return {
                    'component': 'database',
                    'status': 'unhealthy',
                    'response_time': None,
                    'error': 'Connection failed',
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 1
                }
            
            # 嘗試查詢
            start_time = time.time()
            result = self.db.execute_query("SELECT 1", ())
            query_time = time.time() - start_time
            
            # 檢查連接池
            self.db.disconnect()
            
            response_time = time.time() - start_time
            
            return {
                'component': 'database',
                'status': 'healthy',
                'response_time': response_time,
                'query_time': query_time,
                'timestamp': datetime.now(HK_TZ),
                'fail_count': 0,
                'metrics': {
                    'active_connections': result[0]['count'] if result else 0
                }
            }
        except Exception as e:
            return {
                'component': 'database',
                'status': 'error',
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.now(HK_TZ),
                'fail_count': 1
            }
```

#### 1.3 Docker 容器監控
```python
class DockerHeartbeat:
    """Docker 容器心跳監控"""
    
    def __init__(self):
        self.containers = [
            {'name': 'openclaw-postgres', 'container': 'openclaw-postgres'},
            {'name': 'gateway', 'container': 'openclaw-gateway'}
        ]
        self.heartbeat_interval = 30  # 秒
        self.timeout = 5  # 秒
        self.fail_threshold = 3  # 連續失敗閾值
    
    def check_container_health(self, container_name: str) -> dict:
        """檢查容器健康狀態"""
        start_time = time.time()
        try:
            # 檢查容器狀態
            client = docker.from_env()
            container = client.containers.get(container_name)
            
            if not container:
                return {
                    'container': container_name,
                    'status': 'unhealthy',
                    'response_time': None,
                    'error': 'Container not found',
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 1
                }
            
            status = container.status
            
            if status == 'running':
                return {
                    'container': container_name,
                    'status': 'healthy',
                    'response_time': time.time() - start_time,
                    'metrics': {
                        'status': status,
                        'restart_count': container.attrs.get('RestartCount', 0)
                    },
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 0
                }
            else:
                return {
                    'container': container_name,
                    'status': 'unhealthy',
                    'response_time': None,
                    'metrics': {
                        'status': status
                    },
                    'timestamp': datetime.now(HK_TZ),
                    'fail_count': 1
                }
        except Exception as e:
            return {
                'container': container_name,
                'status': 'error',
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.now(HK_TZ),
                'fail_count': 1
            }
```

---

### 2. 策略管理

#### 2.1 發送頻率
```python
class HeartbeatStrategy:
    """Heartbeat 策略"""
    
    def __init__(self):
        self.strategies = {
            'aggressive': {
                'interval': 15,  # 秒
                'timeout': 3,
                'description': '快速檢測，適用於生產環境'
            },
            'normal': {
                'interval': 30,  # 秒
                'timeout': 5,
                'description': '平衡檢測，適用於一般環境'
            },
            'conservative': {
                'interval': 60,  # 秒
                'timeout': 10,
                'description': '保守檢測，適用於開發環境'
            }
        }
        self.current_strategy = 'normal'
    
    def set_strategy(self, strategy: str):
        """設置策略"""
        if strategy in self.strategies:
            self.current_strategy = strategy
            return True
        return False
    
    def get_strategy(self) -> dict:
        """獲取當前策略"""
        return {
            'strategy': self.current_strategy,
            **self.strategies[self.current_strategy]
        }
```

#### 2.2 故障檢測策略
```python
class FaultDetection:
    """故障檢測"""
    
    def __init__(self):
        self.fail_counts = {}
        self.fail_threshold = 3  # 連續失敗閾值
        self.recovery_threshold = 2  # 連續成功恢復閾值
    
    def detect_fault(self, component_id: str, result: dict) -> dict:
        """檢測故障"""
        if result['status'] == 'healthy':
            # 檢查是否恢復
            self.fail_counts[component_id] = max(0, self.fail_counts.get(component_id, 0) - 1)
            
            if self.fail_counts[component_id] == 0:
                return {
                    'component': component_id,
                    'status': 'recovered',
                    'fail_count': self.fail_counts[component_id],
                    'action': 'monitor'
                }
        else:
            # 檢查是否故障
            self.fail_counts[component_id] = self.fail_counts.get(component_id, 0) + 1
            
            if self.fail_counts[component_id] >= self.fail_threshold:
                return {
                    'component': component_id,
                    'status': 'fault',
                    'fail_count': self.fail_counts[component_id],
                    'action': 'restart'
                }
        
        return {
            'component': component_id,
            'status': 'healthy',
            'fail_count': self.fail_counts.get(component_id, 0),
            'action': 'monitor'
        }
```

#### 2.3 自動恢復策略
```python
class AutoRecovery:
    """自動恢復"""
    
    def __init__(self, db):
        self.db = db
        self.recovery_actions = {
            'agent': {
                'command': 'systemctl restart openclaw-{agent}',
                'script': '/home/jarvis/.openclaw/workspace/scripts/restart_{agent}.sh'
            },
            'database': {
                'command': 'docker exec openclaw-postgres pg_ctl reload',
                'script': '/home/jarvis/.openclaw/workspace/scripts/restart_db.sh'
            },
            'docker': {
                'command': 'docker restart {container}',
                'script': '/home/jarvis/.openclaw/workspace/scripts/restart_{container}.sh'
            }
        }
    
    def recover_component(self, component_type: str, component_id: str) -> bool:
        """恢復組件"""
        action = self.recovery_actions.get(component_type)
        if not action:
            return False
        
        command = action['command'].format(**{component_type: component_id})
        
        try:
            # 執行恢復命令
            result = subprocess.run(command, shell=True, capture_output=True, timeout=30)
            
            if result.returncode == 0:
                # 記錄恢復操作
                self.db.save_log(
                    log_id=f"recovery_{int(time.time())}",
                    level="WARNING",
                    category="heartbeat",
                    message=f"組件 {component_id} 已恢復",
                    agent_id="heartbeat",
                    metadata={
                        'component_type': component_type,
                        'component_id': component_id,
                        'command': command,
                        'timestamp': datetime.now(HK_TZ).isoformat()
                    }
                )
                return True
            else:
                return False
        except Exception as e:
            print(f"[ERROR] 恢復失敗: {e}")
            return False
```

---

### 3. 警報處理

#### 3.1 警報生成
```python
class AlertGenerator:
    """警報生成器"""
    
    def __init__(self):
        self.alert_templates = {
            'agent_down': {
                'title': 'Agent 故障',
                'severity': 'high',
                'description': "Agent {agent_name} 檢測到故障，無法響應心跳請求。",
                'recommendations': [
                    "檢查 Agent 進程狀態",
                    "檢查 Agent 日誌文件",
                    "嘗試重啟 Agent",
                    "檢查網絡連接"
                ]
            },
            'database_down': {
                "title": "數據庫故障",
                "severity": "severe",
                "description": "數據庫檢測到故障，無法響應心跳請求。",
                "recommendations": [
                    "檢查 PostgreSQL 進程狀態",
                    "檢查 PostgreSQL 日誌文件",
                    "檢查 Docker 容器狀態",
                    "檢查數據庫磁盤空間",
                    "嘗試重啟數據庫"
                ]
            },
            'docker_down': {
                "title": "Docker 容器故障",
                "severity": "high",
                "description": "Docker 容器 {container_name} 檢測到故障，無法運行。",
                "recommendations": [
                    "檢查容器狀態",
                    "檢查容器日誌",
                    "檢查容器資源使用",
                    "嘗試重啟容器"
                ]
            },
            'agent_slow': {
                "title": "Agent 響應緩慢",
                "severity": "low",
                "description": "Agent {agent_name} 響應時間超過閾值：{response_time}秒。",
                "recommendations": [
                    "檢查 Agent 進程資源使用",
                    "優化 Agent 模型大小",
                    "檢查系統負載"
                ]
            }
        }
    
    def generate_alert(self, alert_type: str, **kwargs) -> dict:
        """生成警報"""
        template = self.alert_templates.get(alert_type)
        if not template:
            return None
        
        alert = {
            'alert_id': f"alert_{int(time.time())}",
            'alert_type': alert_type,
            'severity': template['severity'],
            'title': template['title'].format(**kwargs),
            'description': template['description'].format(**kwargs),
            'recommendations': template['recommendations'],
            'timestamp': datetime.now(HK_TZ),
            'metadata': kwargs
        }
        
        return alert
```

#### 3.2 通知發送
```python
class NotificationSender:
    """通知發送器"""
    
    def __init__(self, db):
        self.db = db
        self.channels = ['telegram', 'email']
        self.notification_queue = []
    
    def send_alert(self, alert: dict, channels: list = None):
        """發送警報通知"""
        if channels is None:
            channels = self.channels
        
        results = []
        
        for channel in channels:
            if channel == 'telegram':
                result = self.send_telegram_alert(alert)
                results.append(result)
            elif channel == 'email':
                result = self.send_email_alert(alert)
                results.append(result)
        
        # 記錄通知發送
        for result in results:
            self.db.save_log(
                log_id=f"notification_{int(time.time())}",
                level="WARNING" if alert['severity'] in ['high', 'severe'] else "INFO",
                category="heartbeat",
                message=f"發送 {result['channel']} 警報：{alert['title']}",
                agent_id="heartbeat",
                metadata={
                    'alert_id': alert['alert_id'],
                    'channel': result['channel'],
                    'status': result['status'],
                    'timestamp': datetime.now(HK_TZ).isoformat()
                }
            )
        
        return results
    
    def send_telegram_alert(self, alert: dict) -> dict:
        """發送 Telegram 警報"""
        try:
            # 發送 Telegram 消息
            message = f"""
<b>{alert['severity'].upper()} - {alert['title']}</b>

{alert['description']}

<b>建議措施：</b>
"""
            
            for i, rec in enumerate(alert['recommendations'], 1):
                message += f"{i}. {rec}\n"
            
            # 發送（模擬）
            print(f"[Telegram] 發送警報：{alert['title']}")
            
            return {
                'channel': 'telegram',
                'status': 'sent',
                'timestamp': datetime.now(HK_TZ)
            }
        except Exception as e:
            return {
                'channel': 'telegram',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(HK_TZ)
            }
    
    def send_email_alert(self, alert: dict) -> dict:
        """發送郵件警報"""
        try:
            # 發送郵件
            subject = f"[Jarvis Heartbeat] {alert['title']} ({alert['severity'].upper()})"
            body = f"{alert['description']}\n\n建議措施：\n"
            
            for i, rec in enumerate(alert['recommendations'], 1):
                body += f"{i}. {rec}\n"
            
            # 發送（模擬）
            print(f"[Email] 發送警報：{alert['title']}")
            
            return {
                'channel': 'email',
                'status': 'sent',
                'timestamp': datetime.now(HK_TZ)
            }
        except Exception as e:
            return {
                'channel': 'email',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(HK_TZ)
            }
```

---

### 4. 數據收集

#### 4.1 指標收集
```python
class MetricsCollector:
    """指標收集器"""
    
    def __init__(self, db):
        self.db = db
    
    def collect_agent_metrics(self, agent_id: str, heartbeat_result: dict) -> dict:
        """收集 Agent 指標"""
        return {
            'agent_id': agent_id,
            'timestamp': heartbeat_result['timestamp'],
            'metrics': {
                'response_time': heartbeat_result['response_time'],
                'status': heartbeat_result['status'],
                'fail_count': heartbeat_result.get('fail_count', 0)
            },
            'metadata': heartbeat_result.get('metadata', {})
        }
    
    def collect_system_metrics(self) -> dict:
        """收集系統指標"""
        # CPU 使用率
        cpu_usage = self.get_cpu_usage()
        
        # 內存使用率
        memory_usage = self.get_memory_usage()
        
        # 磁盤使用率
        disk_usage = self.get_disk_usage()
        
        # 網絡統計
        network_stats = self.get_network_stats()
        
        return {
            'timestamp': datetime.now(HK_TZ),
            'metrics': {
                'cpu': cpu_usage,
                'memory': memory_usage,
                'disk': disk_usage,
                'network': network_stats
            }
        }
    
    def save_metrics(self, metrics: dict) -> bool:
        """保存指標到數據庫"""
        try:
            self.db.execute_update("""
                INSERT INTO system_metrics (metric_name, metric_value, metric_type, component, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
            """, (
                f"heartbeat_{int(time.time())}",
                json.dumps(metrics['metrics']),
                'heartbeat',
                'system',
                metrics['timestamp'],
                json.dumps(metadata)
            ))
            
            return True
        except Exception as e:
            print(f"[ERROR] 保存指標失敗: {e}")
            return False
```

---

### 5. 報告生成

#### 5.1 每日報告
```python
class DailyReportGenerator:
    """每日報告生成器"""
    
    def __init__(self, db):
        self.db = db
    
    def generate_daily_report(self, date: datetime = None) -> dict:
        """生成每日報告"""
        if date is None:
            date = datetime.now(HK_TZ) - timedelta(days=1)
        
        # 收集心跳數據
        heartbeats = self.db.execute_query("""
            SELECT * FROM heartbeat_logs
            WHERE timestamp >= %s AND timestamp < %s
            ORDER BY timestamp ASC
        """, (
            date.replace(hour=0, minute=0, second=0),
            (date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        ))
        
        # 統計總體健康狀況
        total_heartbeats = len(heartbeats)
        healthy_heartbeats = len([h for h in heartbeats if h['status'] == 'healthy'])
        unhealthy_heartbeats = len([h for h in heartbeats if h['status'] != 'healthy'])
        
        # 統計平均響應時間
        if healthy_heartbeats:
            avg_response_time = sum(h['response_time'] for h in healthy_heartbeats) / healthy_heartbeats
        else:
            avg_response_time = 0
        
        # 統計組件健康狀況
        component_stats = self.db.execute_query("""
            SELECT component, status, COUNT(*) as count
            FROM heartbeat_logs
            WHERE timestamp >= %s AND timestamp < %s
            GROUP BY component, status
        """, (
            date.replace(hour=0, minute=0, second=0),
            (date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        ))
        
        # 生成報告
        report = {
            'report_id': f"report_{date.strftime('%Y%m%d')}",
            'report_date': date.strftime('%Y-%m-%d'),
            'overall': {
                'total_heartbeats': total_heartbeats,
                'healthy_percentage': healthy_heartbeats / total_heartbeats * 100 if total_heartbeats > 0 else 0,
                'avg_response_time': avg_response_time
            },
            'components': {},
            'alerts': []
        }
        
        # 添加組件統計
        for stat in component_stats:
            component = stat['component']
            status = stat['status']
            count = stat['count']
            
            if component not in report['components']:
                report['components'][component] = {}
            
            report['components'][component][status] = count
        
        # 添加警告
        alerts = self.db.execute_query("""
            SELECT * FROM heartbeat_alerts
            WHERE alert_time >= %s AND alert_time < %s
            ORDER BY alert_time DESC
        """, (
            date.replace(hour=0, minute=0, second=0),
            (date + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        ))
        
        for alert in alerts:
            report['alerts'].append({
                'alert_id': alert['alert_id'],
                'alert_type': alert['alert_type'],
                'severity': alert['severity'],
                'title': alert['title'],
                'component': alert['component'],
                'alert_time': alert['alert_time']
            })
        
        return report
```

---

## 🚀 實施計劃

### 第 1 階段：基礎研究和設計（2 小時）

#### 1.1 研究現有系統
- 分析當前架構
- 識別需要監控的組件
- 確定監控頻率和策略

#### 1.2 設計監控架構
- 設計 Heartbeat Manager
- 設計組件監控器
- 設計策略管理器
- 設計警報處理器

### 第 2 階段：核心功能實現（3 小時）

#### 2.1 實現監控器
- 實現 Agents 監控
- 實現 PostgreSQL 監控
- 實現 Docker 容器監控

#### 2.2 實現策略管理
- 實現發送頻率控制
- 實現故障檢測策略
- 實現自動恢復策略

### 第 3 階段：警報和通知（2 小時）

#### 3.1 實現警報生成
- 實現警報模板
- 實現警報生成邏輯

#### 3.2 實現通知發送
- 實現 Telegram 通知
- 實現郵件通知

### 第 4 階段：數據收集和報告（2 小時）

#### 4.1 實現數據收集
- 實現指標收集
- 實現指標存儲

#### 4.2 實現報告生成
- 實現每日報告
- 實現實時監控儀表板

---

## 📊 性能指標

### 響應時間
- Heartbeat 檢查：< 2s
- 故障檢測：< 1s
- 自動恢復：< 10s
- 警報發送：< 3s

### 資源使用
- CPU：< 5%
- 內存：< 200MB
- 磁盤：< 100MB/天

---

## 🎯 預期效果

### 可靠性提升
- 故障檢測準確度：>= 95%
- 自動恢復成功率：>= 90%
- 系統可用性：>= 99.9%

### 性能優化
- 響應時間：-50%
- 資源使用：-30%

---

## 📁 文件結構

```
heartbeat/
├── heartbeat_manager.py      # Heartbeat 管理器
├── monitors/
│   ├── agent_monitor.py     # Agent 監控器
│   ├── database_monitor.py   # 數據庫監控器
│   └── docker_monitor.py     # Docker 監控器
├── strategies/
│   ├── heartbeat_strategy.py # 發送頻率策略
│   ├── fault_detection.py    # 故障檢測
│   └── auto_recovery.py      # 自動恢復
├── alerts/
│   ├── alert_generator.py   # 警報生成
│   ├── notification_sender.py # 通知發送
│   └── alert_templates.py      # 警報模板
├── metrics/
│   ├── metrics_collector.py  # 指標收集
│   └── daily_report.py        # 每日報告
├── heartbeat_cron.py           # Heartbeat Cron Job
└── heartbeat_dashboard.py     # 監控儀表板
```

---

## 🚀 總結

**可行性**：⭐⭐⭐⭐⭐ (10/10) - 完全可行

**優點**：
- ✅ 實時監控所有組件
- ✅ 快速故障檢測和定位
- ✅ 自動恢復故障組件
- ✅ 多通道警報通知
- ✅ 完整的監控報告

**挑戰**：
- ⚠️ 實現複雜度較高
- ⚠️ 需要設計合理的閾值
- ⚠️ 可能會有誤報（假故障）

**建議**：
- 🎯 立即開始實現
- 🎯 從基礎功能開始，逐步增加高級功能
- 🎯 先實現監控和警報，再實現自動恢復
- 🎯 持續優化和調整參數

---

**你同意這個方案嗎？**
**同意的話，我會立即開始實現！** 🚀

或者你有其他建議和修改？
