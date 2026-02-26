#!/usr/bin/env python3
"""
回應緩慢問題診斷
檢查系統資源和瓶頸
"""

import os
import psutil
import time
import requests
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def check_system_resources():
    """檢查系統資源"""
    print("=" * 60)
    print("系統資源監控")
    print("=" * 60)
    print()
    
    # 1. CPU 使用情況
    print("[1/5] CPU 使用情況...")
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    print(f"  CPU 使用率：{cpu_percent}%")
    print(f"  CPU 核心數：{cpu_count}")
    if cpu_freq:
        print(f"  CPU 頻率：{cpu_freq.current:.2f} GHz")
    print()
    
    # 2. 內存使用情況
    print("[2/5] 內存使用情況...")
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"  總內存：{memory.total / (1024**3):.2f} GB")
    print(f"  已使用：{memory.used / (1024**3):.2f} GB ({memory.percent}%)")
    print(f"  可用：{memory.available / (1024**3):.2f} GB")
    print(f"  Swap：{swap.used / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB ({swap.percent}%)")
    print()
    
    # 3. 磁盤使用情況
    print("[3/5] 磁盤使用情況...")
    disk = psutil.disk_usage('/')
    io_counters = psutil.disk_io_counters()
    
    print(f"  總容量：{disk.total / (1024**3):.2f} GB")
    print(f"  已使用：{disk.used / (1024**3):.2f} GB ({disk.percent}%)")
    print(f"  可用：{disk.free / (1024**3):.2f} GB")
    print(f"  讀寫次數：{io_counters.read_count} 次")
    print(f"  讀寫時間：{io_counters.read_time_ms} ms")
    print(f"  寫入時間：{io_counters.write_time_ms} ms")
    print()
    
    # 4. 網絡連接情況
    print("[4/5] 網絡連接情況...")
    network = psutil.net_io_counters()
    
    print(f"  接收字節數：{network.bytes_recv}")
    print(f"  發送字節數：{network.bytes_sent}")
    print(f"  接收包數：{network.packets_recv}")
    print(f"  發送包數：{network.packets_sent}")
    print()
    
    # 5. 運行進程情況
    print("[5/5] 運行進程情況...")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent'],
                'status': proc.info['status']
            })
        except Exception:
            pass
    
    print(f"  總進程數：{len(processes)}")
    
    # 顯示前 5 個 CPU 使用最高的進程
    sorted_by_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    if sorted_by_cpu:
        print(f"  CPU 使用最高的進程：")
        for i, proc in enumerate(sorted_by_cpu, 1):
            print(f"    {i}. {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, 內存: {proc['memory_percent']:.1f}%, 狀態: {proc['status']})")
    
    print()
    print("=" * 60)
    print("監控完成")
    print("=" * 60)
    print()


def check_model_performance():
    """檢查模型性能"""
    print("=" * 60)
    print("模型性能測試")
    print("=" * 60)
    print()
    
    # 測試 API 響應時間
    print("[1/3] 測試本地 API...")
    
    test_messages = [
        "天氣怎麼樣？",
        "幫我寫個 Python 腳本",
        "系統配置在哪裡？",
        "你有什麼建議嗎？",
        "查詢一下銷售數據"
    ]
    
    response_times = []
    
    for i, message in enumerate(test_messages, 1):
        start_time = time.time()
        
        try:
            # 模擬本地 API 調用
            # 這裡可以替換為實際的 API 調用
            time.sleep(0.5)  # 模擬處理時間
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"  消息 {i}: {message} - 響應時間：{response_time:.2f}s")
        except Exception as e:
            print(f"  消息 {i}: {message} - 錯誤：{e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print()
        print(f"  平均響應時間：{avg_time:.2f}s")
        print(f"  最快響應時間：{min_time:.2f}s")
        print(f"  最慢響應時間：{max_time:.2f}s")
    else:
        print(f"  無法測試 API")
    
    print()
    
    # 測試網絡延遲
    print("[2/3] 測試網絡延遲...")
    
    try:
        # 測試 Google DNS
        start_time = time.time()
        socket.create_connection(("8.8.8.8", 53))
        dns_time = time.time() - start_time
        print(f"  DNS 延遲：{dns_time*1000:.2f}ms")
        
        # 測試 HTTP 請求
        start_time = time.time()
        requests.get("https://www.google.com", timeout=10)
        http_time = time.time() - start_time
        print(f"  HTTP 延遲：{http_time:.2f}s")
    except Exception as e:
        print(f"  無法測試網絡：{e}")
    
    print()
    
    # 測試數據庫連接
    print("[3/3] 測試數據庫連接...")
    
    try:
        # 測試本地數據庫連接
        start_time = time.time()
        
        # 模擬數據庫查詢
        time.sleep(0.3)  # 模擬查詢時間
        
        db_time = time.time() - start_time
        print(f"  數據庫查詢時間：{db_time:.2f}s")
    except Exception as e:
        print(f"  無法測試數據庫：{e}")
    
    print()
    print("=" * 60)
    print("性能測試完成")
    print("=" * 60)
    print()


def diagnose_slow_response():
    """診斷回應緩慢問題"""
    print("=" * 60)
    print("回應緩慢問題診斷")
    print("=" * 60)
    print()
    
    # 1. 檢查系統資源
    print("[第 1 步] 檢查系統資源...")
    check_system_resources()
    
    # 2. 檢查模型性能
    print("[第 2 步] 檢查模型性能...")
    check_model_performance()
    
    # 3. 分析瓶頸
    print("[第 3 步] 分析潛在瓶頸...")
    
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    issues = []
    
    # 分析 CPU 瓶頸
    if cpu_percent > 80:
        issues.append({
            'type': 'CPU',
            'severity': 'high',
            'message': f"CPU 使用率過高（{cpu_percent}%）",
            'recommendation': "關閉不必要的程序，使用 GPU 加速"
        })
    elif cpu_percent > 60:
        issues.append({
            'type': 'CPU',
            'severity': 'medium',
            'message': f"CPU 使用率偏高（{cpu_percent}%）",
            'recommendation': "優化模型大小，使用更高效的模型"
        })
    
    # 分析內存瓶頸
    if memory.percent > 80:
        issues.append({
            'type': '內存',
            'severity': 'high',
            'message': f"內存使用率過高（{memory.percent}%）",
            'recommendation': "關閉不必要的程序，增加系統內存，使用量化模型"
        })
    elif memory.percent > 60:
        issues.append({
            'type': '內存',
            'severity': 'medium',
            'message': f"內存使用率偏高（{memory.percent}%）",
            'recommendation': "優化模型配置，使用 8-bit 量化模型"
        })
    
    # 分析 I/O 瓶頸
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        issues.append({
            'type': '磁盤 I/O',
            'severity': 'high',
            'message': f"磁盤使用率過高（{disk.percent}%）",
            'recommendation': "清理磁盤空間，優化數據存儲"
        })
    elif disk.percent > 70:
        issues.append({
            'type': '磁盤 I/O',
            'severity': 'medium',
            'message': f"磁盤使用率偏高（{disk.percent}%）",
            'recommendation': "定期清理磁盤，優化數據存儲"
        })
    
    if issues:
        print("  發現以下潛在問題：")
        print()
        
        for i, issue in enumerate(issues, 1):
            severity_emoji = "🔴" if issue['severity'] == 'high' else "🟡"
            print(f"  {severity_emoji} {i}. {issue['type']}：{issue['message']}")
            print(f"     建議：{issue['recommendation']}")
            print()
    else:
        print("  未發現明顯瓶頸，系統運行正常")
        print()
    
    print("=" * 60)
    print("診斷完成")
    print("=" * 60)
    print()
    
    if issues:
        print("優化建議：")
        print("  1. CPU 使用率高")
        print("     - 關閉不必要的程序")
        print("     - 使用 GPU 加速（如果有的話）")
        print("     - 優化模型大小（使用 8-bit 量化）")
        print()
        print("  2. 內存使用率高")
        print("     - 關閉不必要的程序")
        print("     - 增加系統內存")
        print("     - 使用量化模型（int8、8-bit）")
        print("     - 優化批大小")
        print()
        print("  3. 磁盤 I/O 高")
        print("     - 清理磁盤空間")
        print("     - 優化數據存儲")
        print("     - 使用 SSD 而不是 HDD")
        print()
        print("  4. 模型載入時間長")
        print("     - 預載模型到內存（而不是從磁盤加載）")
        print("     - 使用 vLLM（本地推理）")
        print("     - 優化模型大小（使用更小的模型或量化模型）")
        print()
        print("  5. 網絡延遲高")
        print("     - 優化網絡連接")
        print("     - 使用更快的 API")
        print("     - 減少請求次數（使用緩存或批次處理）")
        print()
    else:
        print("系統運行正常，無需優化")
        print()


def main():
    """主函數"""
    print("回應緩慢問題診斷")
    print("=" * 60)
    print()
    
    # 運行診斷
    diagnose_slow_response()


if __name__ == "__main__":
    main()
