#!/usr/bin/env python3
"""
配置所有 Agents 自動啟動
設置 systemd 服務，開機自動啟動
"""

import os
import subprocess


def setup_systemd_services():
    """設置 systemd 服務"""
    print("=" * 60)
    print("設置 Agents 自動啟動")
    print("=" * 60)
    print()
    
    # Agents 配置
    agents = [
        {
            'name': 'Main Agent',
            'service': 'openclaw-main',
            'port': 8000,
            'working_dir': '/home/jarvis/.openclaw/workspace/main-agent',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000',
            'description': 'Main Agent (Orchestrator)'
        },
        {
            'name': 'Chat Assistant',
            'service': 'openclaw-chat',
            'port': 8001,
            'working_dir': '/home/jarvis/.openclaw/workspace/chat-agent',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8001',
            'description': 'Chat Assistant (Information Helper)'
        },
        {
            'name': 'Worker',
            'service': 'openclaw-coding',
            'port': 8002,
            'working_dir': '/home/jarvis/.openclaw/workspace/coding-agent',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8002',
            'description': 'Worker (Coding Assistant)'
        },
        {
            'name': 'System Admin',
            'service': 'openclaw-system',
            'port': 8003,
            'working_dir': '/home/jarvis/.openclaw/workspace/system-admin-agent',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8003',
            'description': 'System Admin (System Management)'
        },
        {
            'name': 'Weather Agent',
            'service': 'openclaw-weather',
            'port': 8004,
            'working_dir': '/home/jarvis/.openclaw/workspace/weather-agent',
            'command': '/home/jarvis/.openclaw/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8004',
            'description': 'Weather Agent (Weather Helper)'
        }
    ]
    
    for i, agent in enumerate(agents, 1):
        print(f"[{i}/{len(agents)}] 創建 {agent['name']} 服務...")
        
        # 創建 systemd 服務文件
        service_content = f"""[Unit]
Description={agent['description']}
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
        service_file = f"/etc/systemd/system/{agent['service']}.service"
        
        try:
            # 使用 sudo 創建服務文件
            result = subprocess.run(
                ['sudo', 'tee', service_file],
                input=service_content,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"  ✅ 服務文件已創建：{agent['service']}.service")
            else:
                print(f"  ❌ 服務文件創建失敗")
                print(f"  錯誤：{result.stderr}")
                continue
            
            # 重新加載 systemd
            print(f"  重新加載 systemd...")
            result = subprocess.run(['sudo', 'systemctl', 'daemon-reload'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"  ✅ systemd 已重新加載")
            else:
                print(f"  ⚠️  systemd 重新加載失敗（可能已是最新的）")
            
            # 啟動服務
            print(f"  啟動 {agent['name']}...")
            result = subprocess.run(['sudo', 'systemctl', 'enable', agent['service']], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"  ✅ {agent['name']} 已啟用開機自啟")
            else:
                print(f"  ❌ {agent['name']} 啟用開機自啟失敗")
                continue
            
            # 開始服務
            print(f"  啟動服務...")
            result = subprocess.run(['sudo', 'systemctl', 'start', agent['service']], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  ✅ {agent['name']} 已啟動")
            else:
                print(f"  ❌ {agent['name']} 啟動失敗")
                print(f"  錯誤：{result.stderr}")
            
            print()
        except Exception as e:
            print(f"  ❌ 設置失敗：{e}")
            print()
    
    print("=" * 60)
    print("所有服務已配置")
    print("=" * 60)
    print()
    print("服務列表：")
    for agent in agents:
        print(f"  - {agent['name']} ({agent['service']})")
    print()
    print("狀態：")
    print("  - 開機自啟：✅ 已啟用")
    print("  - 自動重啟：✅ 已啟用")
    print("  - 服務狀態：需檢查")
    print()
    print("檢查服務狀態：")
    print("  sudo systemctl status openclaw-main")
    print("  sudo systemctl status openclaw-chat")
    print("  sudo systemctl status openclaw-coding")
    print("  sudo systemctl status openclaw-system")
    print("  sudo systemctl status openclaw-weather")
    print()
    print("重啟服務：")
    print("  sudo systemctl restart openclaw-main")
    print("  sudo systemctl restart openclaw-chat")
    print("  sudo systemctl restart openclaw-coding")
    print("  sudo systemctl restart openclaw-system")
    print("  sudo systemctl restart openclaw-weather")


def main():
    """主函數"""
    print("Agents 自動啟動配置")
    print("=" * 60)
    print()
    print("這個腳本會：")
    print("  1. 為所有 Agents 創建 systemd 服務")
    print("  2. 配置開機自啟")
    print("  3. 配置自動重啟")
    print("  4. 啟動所有服務")
    print()
    print("需要 root 權限或 sudo")
    print()
    print("=" * 60)
    print()
    
    success = setup_systemd_services()
    
    if success:
        print()
        print("✅ 所有 Agents 已配置為自動啟動！")
        print()
        print("下一步：")
        print("  1. 檢查服務狀態")
        print("  2. 測試 Agents 功能")
        print("  3. 配置 Heartbeat 監控")
    else:
        print()
        print("⚠️  自動啟動配置完成，但部分服務可能啟動失敗")
        print()
        print("建議：")
        print("  1. 手動檢查服務狀態")
        print("  2. 手動啟動失敗的服務")
        print("  3. 檢查日誌文件")


if __name__ == "__main__":
    main()
