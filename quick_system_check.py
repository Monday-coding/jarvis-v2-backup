#!/usr/bin/env python3
"""
快速檢查系統資源
"""

import psutil
import time
import requests
from datetime import datetime, timezone, timedelta
import subprocess
import socket

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def quick_check():
    """快速檢查系統資源"""
    print("=" * 60)
    print("系統資源快速檢查")
    print("=" * 60)
    print()
    
    # 1. CPU 使用率
    print("[1/6] CPU 使用率...")
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    if cpu_percent > 80:
        print(f"  CPU 使用率高：{cpu_percent}%")
        print("  原因：可能有高 CPU 程序在運行")
    else:
        print(f"  CPU 使用率正常：{cpu_percent}%")
    
    print(f"  CPU 核心數：{cpu_count}")
    print()
    
    # 2. 內存使用率
    print("[2/6] 內存使用率...")
    memory = psutil.virtual_memory()
    
    if memory.percent > 80:
        print(f"  內存使用率高：{memory.percent}%")
        print(f"  已使用：{memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB")
        print("  原因：可能有內存泄漏或大程序在運行")
    else:
        print(f"  內存使用率正常：{memory.percent}%")
        print(f"  已使用：{memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB")
    
    print(f"  可用：{memory.available / (1024**3):.1f} GB")
    print()
    
    # 3. 磁盤使用率
    print("[3/6] 磁盤使用率...")
    disk = psutil.disk_usage('/')
    
    if disk.percent > 90:
        print(f"  磁盤使用率過高：{disk.percent}%")
        print(f"  已使用：{disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB")
        print("  原因：可能有磁盤空間不足")
    else:
        print(f"  磁盤使用率正常：{disk.percent}%")
        print(f"  已使用：{disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB")
    
    print()
    
    # 4. 網絡延遲
    print("[4/6] 網絡延遲...")
    
    # 測試 DNS
    try:
        start_time = time.time()
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        dns_time = (time.time() - start_time) * 1000
        
        if dns_time > 500:
            print(f"  DNS 延遲較高：{dns_time:.2f}ms")
            print("  原因：可能有網絡問題")
        else:
            print(f"  DNS 延遲正常：{dns_time:.2f}ms")
    except Exception as e:
        print(f"  DNS 連接失敗：{e}")
        print("  原因：可能有網絡連接問題")
    
    # 測試 HTTP
    try:
        start_time = time.time()
        requests.get("https://www.google.com", timeout=10)
        http_time = (time.time() - start_time) * 1000
        
        if http_time > 1000:
            print(f"  HTTP 延遲較高：{http_time:.2f}ms")
            print("  原因：可能有網絡問題或 API 響應慢")
        else:
            print(f"  HTTP 延遲正常：{http_time:.2f}ms")
    except Exception as e:
        print(f"  HTTP 連接失敗：{e}")
        print("  原因：可能有網絡連接問題")
    
    print()
    
    # 5. 進程列表
    print("[5/6] 前 5 個 CPU 使用率最高的進程...")
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_percent']
            })
        except Exception:
            pass
    
    # 排序並顯示前 5 個
    sorted_processes = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
    
    if sorted_processes:
        for i, proc in enumerate(sorted_processes, 1):
            print(f"  {i}. {proc['name']} (CPU: {proc['cpu']:.1f}%, 內存: {proc['memory']:.1f}%)")
    else:
        print("  無法獲取進程列表")
    
    print()
    
    # 6. 總結
    print("[6/6] 總結...")
    print()
    print("系統資源狀態：")
    print(f"  CPU：{cpu_percent}% ({'高' if cpu_percent > 80 else '正常'})")
    print(f"  內存：{memory.percent}% ({'高' if memory.percent > 80 else '正常'})")
    print(f"  磁盤：{disk.percent}% ({'高' if disk.percent > 90 else '正常'})")
    print()
    
    # 診斷問題
    issues = []
    
    if cpu_percent > 80:
        issues.append("CPU 使用率高")
    
    if memory.percent > 80:
        issues.append("內存使用率高")
    
    if disk.percent > 90:
        issues.append("磁盤使用率過高")
    
    if issues:
        print("發現以下問題：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        
        print("建議的解決方案：")
        print("  1. 關閉不必要的程序")
        print("  2. 釋放內存")
        print("  3. 清理磁盤空間")
        print("  4. 重啟系統或服務")
    else:
        print("系統資源正常，無明顯問題")
        print()
        print("回應速度慢可能的原因：")
        print("  1. 模型載入時間長（優化：預載入到內存）")
        print("  2. 網絡延遲（優化：使用更快的 API）")
        print("  3. 數據庫查詢慢（優化：添加索引）")
        print("  4. 隊列順序（優化：減少隊列長度）")
        print("  5. 並行處理不足（優化：增加並發處理能力）")
    
    print()
    print("=" * 60)
    print("檢查完成")
    print("=" * 60)
    print()
    print("詳細的診斷建議：")
    print("  1. 如果 CPU 高：檢查哪些程序占用 CPU")
    print("  2. 如果內存高：檢查哪些程序占用內存")
    print("  3. 如果磁盤高：清理磁盤空間")
    print("  4. 如果網絡慢：優化網絡連接或使用更快的 API")
    print()


def main():
    """主函數"""
    print("快速系統檢查")
    print("=" * 60)
    print()
    
    quick_check()


if __name__ == "__main__":
    main()
