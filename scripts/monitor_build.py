#!/usr/bin/env python3
"""Monitor GitHub Actions Build Status"""
import subprocess
import json
import sys

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    print("🔍 检查GitHub Actions构建状态...")
    
    # Get latest workflow runs
    cmd = 'gh run list --workflow ci.yml --limit 5 --json status,conclusion,name,createdAt'
    output = run_command(cmd)
    
    if not output:
        print("❌ 未找到任何workflow运行记录")
        sys.exit(1)
    
    try:
        runs = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        sys.exit(1)
    
    print("\n📊 最近5次构建状态:")
    print("━" * 60)
    
    for run in runs:
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', '')
        name = run.get('name', 'Unknown')
        created = run.get('createdAt', '')
        
        # Determine status icon
        if status == "completed":
            if conclusion == "success":
                icon = "✅"
                color_code = "\033[92m"  # Green
            else:
                icon = "❌"
                color_code = "\033[91m"  # Red
        elif status == "in_progress":
            icon = "🔄"
            color_code = "\033[93m"  # Yellow
        else:
            icon = "⏳"
            color_code = "\033[90m"  # Gray
        
        reset_code = "\033[0m"
        print(f"{color_code}{icon} [{status}] {name}{reset_code}")
        print(f"   创建时间: {created}")
        print()
    
    # Check for in-progress builds
    in_progress = [r for r in runs if r.get('status') == 'in_progress']
    if in_progress:
        print("\n🔄 检测到正在运行的构建，等待完成...")
        print("提示: 可以使用 'gh run watch' 实时监控")
    else:
        latest = runs[0] if runs else None
        if latest and latest.get('conclusion') == 'success':
            print("\n✅ 最新构建成功！")
        else:
            print("\n❌ 最新构建失败！查看详细日志:")
            print("   gh run view --log")

if __name__ == "__main__":
    main()
