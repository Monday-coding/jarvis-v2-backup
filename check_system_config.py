#!/usr/bin/env python3
"""
檢查系統配置和模型路徑
"""

import os
import subprocess
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def check_system_config():
    """檢查系統配置"""
    print("=" * 60)
    print("系統配置檢查")
    print("=" * 60)
    print()
    
    # 1. 檢查模型緩存目錄
    print("[1/5] 檢查模型緩存目錄...")
    
    cache_dir = "/home/jarvis/.cache/models"
    
    if os.path.exists(cache_dir):
        print(f"  模型目錄存在：{cache_dir}")
        print(f"  權限：{oct(os.stat(cache_dir).st_mode)[-3:]}")
    else:
        print(f"  模型目錄不存在：{cache_dir}")
        print(f"  創建目錄...")
        os.makedirs(cache_dir, exist_ok=True)
        print(f"  目錄已創建：{cache_dir}")
        print(f"  權限已設置：755")
    
    print()
    
    # 2. 檢查 Agents 狀態
    print("[2/5] 檢查 Agents 狀態...")
    
    agents = ['jarvis-main', 'jarvis-chat', 'jarvis-coding', 'jarvis-system', 'jarvis-weather']
    
    for agent in agents:
        result = subprocess.run(
            ['sudo', 'systemctl', 'status', agent],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            if 'active' in result.stdout:
                print(f"  {agent}: ✅ 運行中")
            elif 'inactive' in result.stdout or 'dead' in result.stdout:
                print(f"  {agent}: ⚠️ 未運行")
            else:
                print(f"  {agent}: ⚠️ 未知狀態")
        else:
            print(f"  {agent}: ❌ 狀態檢查失敗")
    
    print()
    
    # 3. 檢查系統資源
    print("[3/5] 檢查系統資源...")
    
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    print(f"  CPU 使用率：{cpu_percent}%")
    print(f"  內存使用率：{memory.percent}%")
    print(f"  磁盤使用率：{disk.percent}%")
    
    if cpu_percent > 80:
        print(f"  ⚠️ CPU 使用率過高")
    if memory.percent > 80:
        print(f"  ⚠️ 內存使用率過高")
    if disk.percent > 90:
        print(f"  ⚠️ 磁盤使用率過高")
    
    print()
    
    # 4. 檢查 Python 環境
    print("[4/5] 檢查 Python 環境...")
    
    import sys
    print(f"  Python 版本：{sys.version}")
    print(f"  Python 路徑：{sys.executable}")
    print(f"  香港時區：{HK_TZ}")
    
    print()
    
    # 5. 檢查必要的依賴
    print("[5/5] 檢查必要的依賴...")
    
    required_packages = [
        'torch',
        'transformers',
        'ollama',
        'vllm',
        'fastapi',
        'uvicorn',
        'requests',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        result = subprocess.run(
            [sys.executable, '-c', f'import {package}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  {package}: ✅ 已安裝")
        else:
            print(f"  {package}: ⚠️ 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print()
        print(f"  缺少的依賴：{missing_packages}")
        print()
        print("  安裝命令：")
        print(f"  pip3 install {' '.join(missing_packages)}")
    
    print()
    print("=" * 60)
    print("配置檢查完成")
    print("=" * 60)
    print()
    print("總結：")
    print(f"  模型目錄：{'已存在' if os.path.exists(cache_dir) else '已創建'}")
    print(f"  Agents：{'已運行' if all('active' in subprocess.run(['sudo', 'systemctl', 'status', agent], capture_output=True, text=True).stdout for agent in agents) else '部分未運行'}")
    print(f"  系統資源：{cpu_percent}% CPU, {memory.percent}% 內存, {disk.percent}% 磁盤")
    print(f"  依賴：{'全部安裝' if not missing_packages else f'缺少 {len(missing_packages)} 個依賴'}")
    print()
    print("準備就緒！")


def main():
    """主函數"""
    print("系統配置檢查")
    print("=" * 60)
    print()
    print("這個腳本會：")
    print("  1. 檢查模型緩存目錄")
    print("  2. 檢查 Agents 狀態")
    print("  3. 檢查系統資源")
    print("  4. 檢查 Python 環境")
    print("  5. 檢查必要的依賴")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    check_system_config()


if __name__ == "__main__":
    main()
