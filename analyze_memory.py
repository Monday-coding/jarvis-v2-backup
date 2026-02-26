#!/usr/bin/env python3
"""
分析記憶體使用情況
"""

import psutil
from datetime import datetime, timezone, timedelta

# 香港時區
HK_TZ = timezone(timedelta(hours=8))


def analyze_memory():
    """分析記憶體使用情況"""
    print("=" * 60)
    print("記憶體使用情況分析")
    print("=" * 60)
    print()
    
    # 1. 系統記憶體使用情況
    print("[1/5] 系統記憶體使用情況...")
    print()
    
    system_memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"總記憶體：{system_memory.total / (1024**3):.2f} GB")
    print(f"可用記憶體：{system_memory.available / (1024**3):.2f} GB")
    print(f"已使用：{system_memory.used / (1024**3):.2f} GB ({system_memory.percent:.1f}%)")
    print(f"記憶體使用率：{system_memory.percent:.1f}%")
    print()
    print(f"Swap：{swap.used / (1024**3):.2f} GB / {swap.total / (1024**3):.2f} GB ({swap.percent:.1f}%)")
    print()
    
    if system_memory.percent > 80:
        print(f"⚠️  系統記憶體使用率過高（{system_memory.percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 關閉不必要的程序")
        print(f"   2. 重啟高記憶體使用的程序")
        print(f"   3. 增加系統記憶體")
        print(f"   4. 使用量化模型（int8、8-bit）")
        print(f"   5. 減少批大小")
    elif system_memory.percent > 60:
        print(f"⚠️  系統記憶體使用率偏高（{system_memory.percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 監控高記憶體使用的程序")
        print(f"   2. 使用量化模型（int8、8-bit）")
        print(f"   3. 減少並發請求數量")
    else:
        print(f"✅ 系統記憶體使用率正常（{system_memory.percent:.1f}%）")
    
    print()
    
    # 2. 磁盤 I/O 使用情況
    print("[2/5] 磁盤 I/O 使用情況...")
    print()
    
    disk = psutil.disk_usage('/')
    io_counters = psutil.disk_io_counters()
    
    print(f"磁盤容量：{disk.total / (1024**3):.2f} GB")
    print(f"已使用：{disk.used / (1024**3):.2f} GB ({disk.percent:.1f}%)")
    print(f"可用：{disk.free / (1024**3):.2f} GB")
    print(f"磁盤使用率：{disk.percent:.1f}%")
    print()
    print(f"讀寫次數：{io_counters.read_count} 次")
    print(f"讀寫時間：{io_counters.read_time_ms} ms")
    print(f"寫入次數：{io_counters.write_count} 次")
    print(f"寫入時間：{io_counters.write_time_ms} ms")
    print()
    
    if disk.percent > 90:
        print(f"⚠️  磁盤使用率過高（{disk.percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 清理磁盤空間")
        print(f"   2. 刪除不必要的文件")
        print(f"   3. 優化數據存儲")
    elif disk.percent > 70:
        print(f"⚠️  磁盤使用率偏高（{disk.percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 定期清理磁盤空間")
        print(f"   2. 優化數據存儲")
    else:
        print(f"✅ 磁盤使用率正常（{disk.percent:.1f}%）")
    
    print()
    
    # 3. CPU 使用情況
    print("[3/5] CPU 使用情況...")
    print()
    
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    print(f"CPU 使用率：{cpu_percent:.1f}%")
    print(f"CPU 核心數：{cpu_count}")
    print()
    
    # 顯示前 5 個 CPU 使用率最高的進程
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_percent'],
                'memory_info': proc.info['memory_info']
            })
        except Exception:
            pass
    
    # 排序並顯示前 5 個
    sorted_processes = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
    
    print("前 5 個 CPU 使用率最高的進程：")
    for i, proc in enumerate(sorted_processes, 1):
        memory_mb = proc['memory_info'].rss / (1024**2)
        print(f"  {i}. {proc['name']} (CPU: {proc['cpu']:.1f}%, 記憶體: {memory_mb:.1f} MB)")
    
    print()
    
    if cpu_percent > 80:
        print(f"⚠️  CPU 使用率過高（{cpu_percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 關閉不必要的程序")
        print(f"   2. 減少並發任務")
        print(f"   3. 使用 GPU 加速")
    elif cpu_percent > 60:
        print(f"⚠️  CPU 使用率偏高（{cpu_percent:.1f}%）")
        print(f"   建議：")
        print(f"   1. 監控高 CPU 使用的程序")
        print(f"   2. 使用 GPU 加速")
    else:
        print(f"✅ CPU 使用率正常（{cpu_percent:.1f}%）")
    
    print()
    
    # 4. 進程列表（所有 Python 進程）
    print("[4/5] 所有 Python 進程...")
    print()
    
    python_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
        try:
            name = proc.info['name']
            if 'python' in name.lower():
                python_processes.append({
                    'pid': proc.info['pid'],
                    'name': name,
                    'memory': proc.info['memory_percent'],
                    'memory_info': proc.info['memory_info']
                })
        except Exception:
            pass
    
    print(f"找到 {len(python_processes)} 個 Python 進程")
    print()
    
    for i, proc in enumerate(python_processes[:10], 1):
        memory_mb = proc['memory_info'].rss / (1024**2)
        print(f"  {i}. {proc['name']} (PID: {proc['pid']}, 記憶體: {memory_mb:.1f} MB, {proc['memory']:.1f}%)")
    
    if len(python_processes) > 10:
        print(f"  ... 還有 {len(python_processes) - 10} 個進程")
    
    print()
    
    # 5. 總結
    print("[5/5] 分析總結...")
    print()
    
    # 系統資源總結
    print("系統資源總結：")
    print(f"  CPU：{cpu_percent:.1f}% ({'高' if cpu_percent > 80 else '正常' if cpu_percent < 60 else '偏高'})")
    print(f"  記憶體：{system_memory.percent:.1f}% ({'高' if system_memory.percent > 80 else '正常' if system_memory.percent < 60 else '偏高'})")
    print(f"  磁盤：{disk.percent:.1f}% ({'高' if disk.percent > 90 else '正常' if disk.percent < 70 else '偏高'})")
    print()
    
    # 問題診斷
    issues = []
    
    if system_memory.percent > 80:
        issues.append("系統記憶體使用率過高")
    
    if disk.percent > 90:
        issues.append("磁盤使用率過高")
    
    if cpu_percent > 80:
        issues.append("CPU 使用率過高")
    
    if issues:
        print("發現以下問題：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("優化建議：")
        print("  1. 關閉不必要的程序")
        print("  2. 使用量化模型（int8、8-bit）")
        print("  3. 減少並發請求數量")
        print("  4. 使用 GPU 加速")
        print("  5. 清理磁盤空間")
    else:
        print("✅ 系統資源使用正常，無明顯問題")
        print()
        print("回應速度慢可能的原因：")
        print("  1. 模型載入時間長（優化：預載入到內存）")
        print("  2. 網絡延遲（優化：使用更快的 API）")
        print("  3. 數據庫查詢慢（優化：添加索引、查詢緩存）")
    
    print()
    print("=" * 60)
    print("分析完成")
    print("=" * 60)
    print()
    print(f"分析時間：{datetime.now(HK_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def main():
    """主函數"""
    print("記憶體使用情況分析")
    print("=" * 60)
    print()
    print("這個腳本會分析：")
    print("  1. 系統記憶體使用情況")
    print("  2. 磁盤 I/O 使用情況")
    print("  3. CPU 使用情況")
    print("  4. 所有 Python 進程")
    print("  5. 分析總結")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    analyze_memory()


if __name__ == "__main__":
    main()
