#!/usr/bin/env python3
"""
配置所有 Agents 自己順序執行
確保服務失敗時可以自己重啟
"""

import os
import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def configure_systemd_services():
    """配置 systemd 服務"""
    print("=" * 60)
    print("配置 Agents 自動重啟")
    print("=" * 60)
    print()
    
    # 要配置的 Agents
    agents = [
        {
            'name': 'Main Agent',
            'service': 'jarvis-main',
            'port': 8000,
            'working_dir': '/home/jarvis/.openclaw/workspace',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000'
        },
        {
            'name': 'Chat Assistant',
            'service': 'jarvis-chat',
            'port': 8001,
            'working_dir': '/home/jarvis/.openclaw/workspace',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001'
        },
        {
            'name': 'Coding Agent',
            'service': 'jarvis-coding',
            'port': 8002,
            'working_dir': '/home/jarvis/.openclaw/workspace',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8002'
        },
        {
            'name': 'System Admin',
            'service': 'jarvis-system',
            'port': 8003,
            'working_dir': '/home/jarvis/.openclaw/workspace',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8003'
        },
        {
            'name': 'Weather Agent',
            'service': 'jarvis-weather',
            'port': 8004,
            'working_dir': '/home/jarvis/.openclaw/workspace',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8004'
        }
    ]
    
    for i, agent in enumerate(agents, 1):
        print(f"[{i}/{len(agents)}] 配置 {agent['name']}...")
        
        try:
            # 創建 systemd 服務文件
            service_file = f"/etc/systemd/system/{agent['service']}.service"
            
            service_content = f"""[Unit]
Description={agent['name']}
After=network.target

[Service]
Type=simple
User=jarvis
WorkingDirectory={agent['working_dir']}
ExecStart={agent['command']}
Restart=always
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
            
            # 保存服務文件
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            print(f"  服務文件已創建：{agent['service']}.service")
            
            # 重新加載 systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], capture_output=True, timeout=10)
            print(f"  systemd 已重新加載")
            
            # 啟用服務
            subprocess.run(['sudo', 'systemctl', 'enable', agent['service']], capture_output=True, timeout=10)
            print(f"  服務已啟用開機自啟")
            
            # 啟動服務
            subprocess.run(['sudo', 'systemctl', 'start', agent['service']], capture_output=True, timeout=30)
            print(f"  服務已啟動")
            
            print()
        except Exception as e:
            print(f"  ❌ 配置失敗：{e}")
            print()
    
    print("=" * 60)
    print("所有 Agents 已配置為自動重啟！")
    print("=" * 60)
    print()
    print("配置總結：")
    print("  服務類型：simple")
    print("  重啟策略：always (總是重啟）")
    print("  重啟間隔：10s")
    print("  開機自啟：enabled")
    print("  服務文件位置：/etc/systemd/system/")
    print()
    print("服務列表：")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['service']}) - 端口 {agent['port']}")
    print()
    print("現在所有 Agents 會：")
    print("  1. 開機時自動啟動")
    print("  2. 故障時自動重啟（10 秒後）")
    print("  3. 連續故障時不斷重啟")
    print()


def main():
    """主函數"""
    print("Agents 自動重啟配置")
    print("=" * 60)
    print()
    print("這個腳本會配置所有 Agents：")
    print("  1. 創建 systemd 服務文件")
    print("  2. 配置開機自啟")
    print("  3. 配置自動重啟")
    print()
    print("需要 root 權限或 sudo")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    success = configure_systemd_services()
    
    if success:
        print()
        print("✅ 所有 Agents 已配置為自動重啟！")
        print()
        print("下一步：")
        print("  1. 重啟系統測試開機自啟")
        print("  2. 測試 Agents 功能")
        print("  3. 運行 Heartbeat 檢查")
    else:
        print()
        print("⚠️  自動重啟配置完成，但可能部分服務失敗")
        print("建議：")
        print("  1. 檢查服務狀態")
        print("  2. 手動啟動失敗的服務")
        print("  3. 檢查日誌文件")


if __name__ == "__main__":
    main()
