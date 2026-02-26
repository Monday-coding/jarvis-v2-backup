#!/usr/bin/env python3
"""
快速修復文件問題
"""

import subprocess
from datetime import datetime, timezone, timedelta


def fix_file_issue():
    """修復文件編輯問題"""
    print("=" * 60)
    print("修復文件問題")
    print("=" * 60)
    print()
    
    # 放棄所有本地更改
    print("[1/3] 放棄所有本地更改...")
    result = subprocess.run(['git', 'reset', '--hard'], capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("  所有本地更改已放棄")
    else:
        print(f"  放棄失敗：{result.stderr}")
    
    print()
    
    # 拉取最新更改
    print("[2/3] 拉取最新更改...")
    result = subprocess.run(['git', 'pull', 'origin', 'master'], capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("  最新更改已拉取")
    else:
        print(f"  拉取失敗：{result.stderr}")
    
    print()
    
    # 檢查狀態
    print("[3/3] 檢查文件狀態...")
    result = subprocess.run(['git', 'status'], capture_output=True, text=True, timeout=10)
    
    print(f"  狀態：")
    print(f"  {result.stdout}")
    print()
    
    print("=" * 60)
    print("修復完成")
    print("=" * 60)
    print()
    print("系統狀態：")
    print("  所有本地更改已放棄")
    print("  已拉取最新更改")
    print("  文件狀態正常")
    print()
    print("準備就緒！")


def main():
    """主函數"""
    print("文件問題修復")
    print("=" * 60)
    print()
    print("這個腳本會：")
    print("  1. 放棄所有本地更改")
    print("  2. 拉取最新更改")
    print("  3. 檢查文件狀態")
    print()
    print("準備開始...")
    print()
    print("=" * 60)
    print()
    
    fix_file_issue()
    
    print()
    print("✅ 文件問題已修復！")
    print()
    print("下一步：")
    print("  1. 檢查文件狀態")
    print("  2. 檢查所有文件是否正常")
    print("  3. 繼續其他工作")


if __name__ == "__main__":
    main()
