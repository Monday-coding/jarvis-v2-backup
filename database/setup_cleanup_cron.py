#!/usr/bin/env python3
"""
設置定期清理 Cron Job
每天凌晨 2 點清理舊的天氣數據
"""

import subprocess
import os

def setup_cleanup_cron():
    """設置清理 Cron Job"""
    print("=" * 60)
    print("設置定期清理 Cron Job")
    print("=" * 60)
    print()
    
    # 獲取當前 crontab
    print("[1/4] 獲取當前 crontab...")
    
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            crontab_content = result.stdout
        else:
            print("  無有現有 crontab")
            crontab_content = ""
    except Exception as e:
        print(f"  無法獲取 crontab: {e}")
        crontab_content = ""
    
    print("  完成")
    print()
    
    # 檢查是否已經有清理任務
    print("[2/4] 檢查現有清理任務...")
    
    cleanup_job_exists = 'clean_via_docker.py' in crontab_content
    
    if cleanup_job_exists:
        print("  已有清理任務")
        
        # 詢問是否更新
        print()
        choice = input("  是否更新清理頻率？(y/n): ").strip().lower()
        
        if choice == 'y':
            print()
            print("  清理頻率選項：")
            print("    1. 每天凌晨 2 點（推薦）")
            print("    2. 每天凌晨 4 點")
            print("    3. 每 6 小時")
            print("    4. 每 12 小時")
            print()
            
            freq_choice = input("  請選擇清理頻率 (1-4): ").strip()
            
            if freq_choice == '1':
                cron_time = '0 2 * * *'  # 每天凌晨 2 點
            elif freq_choice == '2':
                cron_time = '0 4 * * *'  # 每天凌晨 4 點
            elif freq_choice == '3':
                cron_time = '0 */6 * * *'  # 每 6 小時
            elif freq_choice == '4':
                cron_time = '0 */12 * * *'  # 每 12 小時
            else:
                print("  無效選擇，保持默認（每天凌晨 2 點）")
                cron_time = '0 2 * * *'
        else:
            print("  不更新，保持現有配置")
            print()
            print("=" * 60)
            print("清理 Cron Job 已存在")
            print("=" * 60)
            print()
            print("當前清理任務：")
            for line in crontab_content.split('\n'):
                if 'clean_via_docker' in line:
                    print(f"  {line}")
            print()
            return True
    else:
        print("  沒有現有清理任務")
        cron_time = '0 2 * * *'  # 默認每天凌晨 2 點
    print()
    
    # 創建清理腳本路徑
    print("[3/4] 創建清理腳本路徑...")
    
    script_path = os.path.expanduser('~/.openclaw/workspace/database/clean_via_docker.py')
    script_command = f"/usr/bin/python3 {script_path}"
    
    print(f"  腳本路徑：{script_path}")
    print(f"  執行命令：{script_command}")
    print("  完成")
    print()
    
    # 創建新的 crontab 內容
    print("[4/4] 創建新的 crontab...")
    
    new_cron_job = f"{cron_time} {script_command} >> /home/jarvis/.openclaw/workspace/database/clean.log 2>&1\n"
    
    # 如果已經有，替換
    if cleanup_job_exists:
        lines = crontab_content.split('\n')
        new_lines = []
        
        for line in lines:
            if 'clean_via_docker' in line:
                continue  # 跳過舊的清理任務
        
            new_lines.append(line)
        
        new_lines.append(new_cron_job)
        new_crontab = '\n'.join(new_lines)
    else:
        # 添加到現有 crontab
        if crontab_content:
            new_crontab = crontab_content + '\n' + new_cron_job
        else:
            new_crontab = new_cron_job
    
    # 保存 crontab
    print("  保存 crontab...")
    
    try:
        process = subprocess.run(
            ['crontab', '-'],
            input=new_crontab,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if process.returncode == 0:
            print("  ✅ Crontab 已更新")
        else:
            print(f"  ❌ Crontab 更新失敗: {process.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 無法保存 crontab: {e}")
        return False
    
    print()
    print("=" * 60)
    print("定期清理 Cron Job 設置完成")
    print("=" * 60)
    print()
    print("清理配置：")
    print(f"  清理腳本：{script_path}")
    print(f"  清理頻率：每天凌晨 2 點")
    print(f"  日誌文件：/home/jarvis/.openclaw/workspace/database/clean.log")
    print()
    print("清理策略：")
    print("  天氣數據：保留最近 7 天")
    print("  天氣警告：保留最近 30 天")
    print("  天氣預報：保留最近 3 天")
    print("  系統日誌：保留最近 30 天")
    print()
    print("Cron Job 運行時間：")
    print(f"  下次清理：今天凌晨 2 點")
    print(f"  每天運行：每天凌晨 2 點自動清理")
    print()
    print("查看 Cron Job：")
    print("  crontab -l")
    print()
    print("查看清理日誌：")
    print(f"  tail -f /home/jarvis/.openclaw/workspace/database/clean.log")
    print()
    print("=" * 60)
    print("設置完成！")
    print("=" * 60)
    
    return True


def main():
    """主函數"""
    print("定期清理 Cron Job 設置")
    print("=" * 60)
    print()
    print("這個腳本會設置每天凌晨 2 點自動清理舊的天氣數據")
    print()
    print("需要 root 權限或 sudo")
    print()
    print("=" * 60)
    print()
    
    success = setup_cleanup_cron()
    
    if success:
        print()
        print("✅ 定期清理已設置完成！")
        print()
        print("下一步：")
        print("  1. 查看數據庫狀態")
        print("  2. 檢查天氣監控系統")
        print("  3. 測試數據庫查詢")
    else:
        print()
        print("❌ 定期清理設置失敗")
        print("請檢查錯誤並重試")


if __name__ == "__main__":
    main()
