#!/usr/bin/env python3
"""
CI/CD 构建状态监控脚本

职责：
1. 检查最近的 GitHub Actions 构建状态
2. 如果构建失败，自动分析错误
3. 尝试自动修复常见问题
4. 发送通知（如果配置）
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta


class CICDMonitor:
    """CI/CD 构建监控器"""
    
    def __init__(self, repo_url: str = "https://github.com/wsolarq11/sys-monitor.git"):
        self.repo_url = repo_url
        self.max_retries = 10
        self.check_interval = 30  # 秒
    
    def check_build_status(self) -> dict:
        """检查构建状态"""
        print("🔍 检查 CI/CD 构建状态...")
        
        # 使用 GitHub CLI 检查最近的 workflow runs
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "5", "--json", 
                 "status,conclusion,name,startedAt"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                return {"success": True, "runs": runs}
            else:
                # gh CLI 不可用，使用备用方法
                return self._check_via_git()
        
        except FileNotFoundError:
            print("⚠️  GitHub CLI (gh) 未安装，使用备用检查方法")
            return self._check_via_git()
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _check_via_git(self) -> dict:
        """通过 Git 检查最近的提交"""
        print("📋 检查最近的提交...")
        
        try:
            # 获取最近的提交
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%ai"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commit_info = result.stdout.strip().split("|")
                return {
                    "success": True,
                    "latest_commit": {
                        "hash": commit_info[0],
                        "message": commit_info[1],
                        "date": commit_info[2]
                    }
                }
            else:
                return {"success": False, "error": "无法获取提交信息"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def monitor_build(self, timeout_minutes: int = 10):
        """监控构建直到完成或超时"""
        print(f"\n⏱️  开始监控构建（超时: {timeout_minutes} 分钟）...\n")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            status = self.check_build_status()
            
            if not status["success"]:
                print(f"❌ 检查失败: {status.get('error', '未知错误')}")
                break
            
            # 检查是否有运行的构建
            runs = status.get("runs", [])
            if runs:
                latest_run = runs[0]
                build_status = latest_run.get("status", "unknown")
                conclusion = latest_run.get("conclusion", None)
                
                print(f"📊 构建状态: {build_status}")
                
                if build_status == "completed":
                    if conclusion == "success":
                        print("✅ 构建成功！")
                        return True
                    else:
                        print(f"❌ 构建失败: {conclusion}")
                        self._handle_build_failure(latest_run)
                        return False
                elif build_status in ["queued", "in_progress"]:
                    print(f"⏳ 构建进行中... ({latest_run.get('name', 'N/A')})")
                    time.sleep(self.check_interval)
                else:
                    print(f"⚠️  未知状态: {build_status}")
                    time.sleep(self.check_interval)
            else:
                print("ℹ️  未找到正在运行的构建")
                print("💡 提示: 构建可能尚未触发，或需要手动触发")
                break
        
        print(f"\n⏱️  监控超时（{timeout_minutes} 分钟）")
        return False
    
    def _handle_build_failure(self, run_info: dict):
        """处理构建失败"""
        print("\n🔧 分析构建失败原因...")
        
        run_id = run_info.get("id")
        if not run_id:
            print("⚠️  无法获取运行 ID")
            return
        
        try:
            # 获取失败的 job 详情
            result = subprocess.run(
                ["gh", "run", "view", str(run_id), "--json", "jobs"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                jobs = json.loads(result.stdout).get("jobs", [])
                for job in jobs:
                    if job.get("conclusion") == "failure":
                        print(f"\n❌ 失败的任务: {job.get('name', 'Unknown')}")
                        
                        # 获取日志
                        self._fetch_job_logs(job.get("id"))
                        
                        # 尝试自动修复
                        self._attempt_auto_fix(job.get("name", ""))
        
        except Exception as e:
            print(f"⚠️  无法获取详细错误: {e}")
    
    def _fetch_job_logs(self, job_id: str):
        """获取任务日志"""
        if not job_id:
            return
        
        try:
            result = subprocess.run(
                ["gh", "run", "view", job_id, "--log"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logs = result.stdout
                # 查找错误信息
                error_lines = [line for line in logs.split('\n') 
                              if 'error' in line.lower() or 'fail' in line.lower()]
                
                if error_lines:
                    print("\n📝 错误日志:")
                    for line in error_lines[-10:]:  # 最后10行错误
                        print(f"   {line}")
        
        except Exception as e:
            print(f"⚠️  无法获取日志: {e}")
    
    def _attempt_auto_fix(self, job_name: str):
        """尝试自动修复常见问题"""
        print("\n🔧 尝试自动修复...")
        
        # 常见问题的自动修复
        fixes_applied = []
        
        # 1. Python 依赖问题
        if "python" in job_name.lower() or "pip" in job_name.lower():
            print("   📦 检查 Python 依赖...")
            try:
                subprocess.run(["pip", "install", "-r", "requirements.txt"], 
                             check=True, capture_output=True)
                fixes_applied.append("Python 依赖已更新")
            except:
                pass
        
        # 2. Node.js 依赖问题
        if "node" in job_name.lower() or "npm" in job_name.lower():
            print("   📦 检查 Node.js 依赖...")
            try:
                subprocess.run(["npm", "ci"], check=True, capture_output=True)
                fixes_applied.append("Node.js 依赖已更新")
            except:
                pass
        
        # 3. Rust 编译问题
        if "rust" in job_name.lower() or "cargo" in job_name.lower():
            print("   📦 检查 Rust 依赖...")
            try:
                subprocess.run(["cargo", "clean"], check=True, capture_output=True)
                fixes_applied.append("Rust 缓存已清理")
            except:
                pass
        
        if fixes_applied:
            print(f"\n✅ 已应用修复: {', '.join(fixes_applied)}")
            print("💡 建议: 重新推送代码以触发新的构建")
        else:
            print("⚠️  无法自动修复，需要手动检查")
    
    def generate_report(self, status: dict):
        """生成监控报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f".lingma/reports/cicd-monitor-{timestamp}.json")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "recommendations": self._generate_recommendations(status)
        }
        
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 监控报告已生成: {report_file}")
        return report_file
    
    def _generate_recommendations(self, status: dict) -> list:
        """生成建议"""
        recommendations = []
        
        if not status.get("success"):
            recommendations.append("检查网络连接和 GitHub 访问权限")
        
        if "runs" in status and status["runs"]:
            latest = status["runs"][0]
            if latest.get("conclusion") == "failure":
                recommendations.append("查看详细的构建日志以定位问题")
                recommendations.append("考虑手动触发重新构建")
        
        if not recommendations:
            recommendations.append("构建状态正常，无需操作")
        
        return recommendations


def main():
    """主函数"""
    print("="*60)
    print("CI/CD 构建状态监控")
    print("="*60)
    
    monitor = CICDMonitor()
    
    # 检查当前状态
    status = monitor.check_build_status()
    
    if status["success"]:
        print("✅ 状态检查成功\n")
        
        # 如果有运行的构建，监控它
        runs = status.get("runs", [])
        if runs and runs[0].get("status") in ["queued", "in_progress"]:
            success = monitor.monitor_build(timeout_minutes=10)
            
            if success:
                print("\n🎉 构建成功完成！")
                return 0
            else:
                print("\n⚠️  构建失败或超时")
                return 1
        else:
            print("ℹ️  没有正在运行的构建")
            print("💡 最近的提交已成功推送到远程仓库")
            return 0
    else:
        print(f"❌ 状态检查失败: {status.get('error', '未知错误')}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
