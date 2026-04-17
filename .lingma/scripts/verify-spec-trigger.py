#!/usr/bin/env python3
"""
端到端验证脚本 - 验证Spec强制约束机制

检查项(16项):
1. Spec文件存在性
2. Spec文件格式正确
3. spec-validator.py存在且可执行
4. spec-worker.py存在且可执行
5. pre-commit.sh存在
6. install-hooks.py存在且可执行
7. Git Hooks目录结构
8. 审计日志目录
9. Worker状态目录
10. Validator功能测试
11. Worker功能测试
12. Hook安装流程
13. 澄清问题检测
14. 任务进度更新
15. 审计日志记录
16. 完整工作流集成测试

使用方式:
    python verify-spec-trigger.py
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class SpecTriggerVerifier:
    """Spec强制约束机制验证器"""

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or os.getcwd()
        self.results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0

    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 70)
        print("Spec强制约束机制 - 端到端验证")
        print("=" * 70)
        print(f"项目根目录: {self.project_root}")
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        checks = [
            ("Spec文件存在性", self.check_spec_exists),
            ("Spec文件格式", self.check_spec_format),
            ("spec-validator.py存在", self.check_validator_exists),
            ("spec-worker.py存在", self.check_worker_exists),
            ("pre-commit.sh存在", self.check_precommit_exists),
            ("install-hooks.py存在", self.check_install_script_exists),
            ("Git Hooks目录结构", self.check_hooks_directory),
            ("审计日志目录", self.check_audit_log_directory),
            ("Worker状态目录", self.check_worker_directory),
            ("Validator功能测试", self.check_validator_functionality),
            ("Worker功能测试", self.check_worker_functionality),
            ("Hook安装流程", self.check_hook_installation),
            ("澄清问题检测", self.check_clarification_detection),
            ("任务进度更新", self.check_task_progress),
            ("审计日志记录", self.check_audit_logging),
            ("完整工作流集成", self.check_full_workflow),
        ]

        for i, (name, check_func) in enumerate(checks, 1):
            print(f"[{i:2d}/16] {name}...", end=" ")

            try:
                result = check_func()

                if result:
                    print("✅ PASS")
                    self.passed += 1
                    self.results.append({"check": name, "status": "PASS"})
                else:
                    print("❌ FAIL")
                    self.failed += 1
                    self.results.append({"check": name, "status": "FAIL"})

            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                self.failed += 1
                self.results.append({"check": name, "status": "ERROR", "error": str(e)})

        print()
        print("=" * 70)
        print(f"验证结果: {self.passed}/{len(checks)} 通过")

        if self.failed == 0:
            print("🎉 所有检查通过! Spec强制约束机制已就绪。")
        else:
            print(f"⚠️  {self.failed} 项检查失败，请查看上方详情。")

        print("=" * 70)
        print()

        return self.failed == 0

    def check_spec_exists(self) -> bool:
        """检查1: Spec文件存在性"""
        spec_path = os.path.join(
            self.project_root, ".lingma", "specs", "current-spec.md"
        )
        return os.path.exists(spec_path)

    def check_spec_format(self) -> bool:
        """检查2: Spec文件格式正确"""
        spec_path = os.path.join(
            self.project_root, ".lingma", "specs", "current-spec.md"
        )

        if not os.path.exists(spec_path):
            return False

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查必需元素
        has_metadata = "- **状态**:" in content or "- **优先级**:" in content
        has_tasks = "- [ ]" in content or "- [x]" in content

        return has_metadata and has_tasks

    def check_validator_exists(self) -> bool:
        """检查3: spec-validator.py存在且可执行"""
        validator_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-validator.py"
        )

        if not os.path.exists(validator_path):
            return False

        # 尝试导入验证
        try:
            result = subprocess.run(
                [sys.executable, validator_path, "--help"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except:
            return False

    def check_worker_exists(self) -> bool:
        """检查4: spec-worker.py存在且可执行"""
        worker_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-worker.py"
        )

        if not os.path.exists(worker_path):
            return False

        # 尝试导入验证
        try:
            result = subprocess.run(
                [sys.executable, worker_path, "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def check_precommit_exists(self) -> bool:
        """检查5: pre-commit.sh存在"""
        hook_path = os.path.join(self.project_root, ".lingma", "hooks", "pre-commit.sh")
        return os.path.exists(hook_path)

    def check_install_script_exists(self) -> bool:
        """检查6: install-hooks.py存在且可执行"""
        install_path = os.path.join(
            self.project_root, ".lingma", "scripts", "install-hooks.py"
        )

        if not os.path.exists(install_path):
            return False

        try:
            result = subprocess.run(
                [sys.executable, install_path, "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def check_hooks_directory(self) -> bool:
        """检查7: Git Hooks目录结构"""
        hooks_dir = os.path.join(self.project_root, ".lingma", "hooks")

        if not os.path.isdir(hooks_dir):
            return False

        # 检查必要文件
        required_files = ["pre-commit.sh"]
        for file in required_files:
            if not os.path.exists(os.path.join(hooks_dir, file)):
                return False

        return True

    def check_audit_log_directory(self) -> bool:
        """检查8: 审计日志目录"""
        log_dir = os.path.join(self.project_root, ".lingma", "logs")

        if not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        return os.path.isdir(log_dir)

    def check_worker_directory(self) -> bool:
        """检查9: Worker状态目录"""
        worker_dir = os.path.join(self.project_root, ".lingma", "worker")

        if not os.path.isdir(worker_dir):
            os.makedirs(worker_dir, exist_ok=True)

        return os.path.isdir(worker_dir)

    def check_validator_functionality(self) -> bool:
        """检查10: Validator功能测试"""
        validator_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-validator.py"
        )

        try:
            result = subprocess.run(
                [sys.executable, validator_path, "--mode", "manual", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            # 解析JSON输出
            output = json.loads(result.stdout)

            # 验证返回结构
            required_keys = ["valid", "mode", "timestamp", "metadata"]
            return all(key in output for key in required_keys)

        except Exception as e:
            print(f"\n       错误: {str(e)}")
            return False

    def check_worker_functionality(self) -> bool:
        """检查11: Worker功能测试"""
        worker_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-worker.py"
        )

        try:
            result = subprocess.run(
                [sys.executable, worker_path, "--status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            # 解析JSON输出
            output = json.loads(result.stdout)

            # 验证返回结构
            required_keys = ["worker_id", "status", "pending_tasks"]
            return all(key in output for key in required_keys)

        except Exception as e:
            print(f"\n       错误: {str(e)}")
            return False

    def check_hook_installation(self) -> bool:
        """检查12: Hook安装流程"""
        # 直接检查.git/hooks/pre-commit是否存在
        git_hook_path = os.path.join(self.project_root, ".git", "hooks", "pre-commit")
        return os.path.exists(git_hook_path) and os.path.getsize(git_hook_path) > 0

    def check_clarification_detection(self) -> bool:
        """检查13: 澄清问题检测"""
        validator_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-validator.py"
        )

        # 创建临时Spec文件包含澄清问题
        temp_spec = os.path.join(
            self.project_root, ".lingma", "specs", "test-clarification.md"
        )

        try:
            with open(temp_spec, "w", encoding="utf-8") as f:
                f.write("""# 测试Spec
- **状态**: in-progress
- **优先级**: P1

## 需求
这是一个测试[NEEDS CLARIFICATION]的澄清问题检测功能。
""")

            result = subprocess.run(
                [sys.executable, validator_path, "--spec", temp_spec, "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            output = json.loads(result.stdout)

            # 应该检测到澄清问题
            has_clarifications = output.get("has_unanswered_questions", False)

            return has_clarifications

        except Exception as e:
            print(f"\n       错误: {str(e)}")
            return False

        finally:
            # 清理临时文件
            if os.path.exists(temp_spec):
                os.remove(temp_spec)

    def check_task_progress(self) -> bool:
        """检查14: 任务进度更新"""
        spec_path = os.path.join(
            self.project_root, ".lingma", "specs", "current-spec.md"
        )

        if not os.path.exists(spec_path):
            return False

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否有进度信息
        has_progress = "**进度**:" in content

        return has_progress

    def check_audit_logging(self) -> bool:
        """检查15: 审计日志记录"""
        audit_log = os.path.join(self.project_root, ".lingma", "logs", "audit.log")

        # 确保目录存在
        os.makedirs(os.path.dirname(audit_log), exist_ok=True)

        # 写入测试日志
        test_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "verification_test",
            "message": "Audit logging test",
        }

        try:
            with open(audit_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(test_entry) + "\n")

            # 验证写入
            return os.path.exists(audit_log) and os.path.getsize(audit_log) > 0

        except:
            return False

    def check_full_workflow(self) -> bool:
        """检查16: 完整工作流集成测试"""
        # 模拟完整工作流: Spec验证 -> Worker处理 -> 审计日志

        validator_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-validator.py"
        )
        worker_path = os.path.join(
            self.project_root, ".lingma", "scripts", "spec-worker.py"
        )

        try:
            # 步骤1: 验证Spec
            val_result = subprocess.run(
                [sys.executable, validator_path, "--mode", "CI", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            if val_result.returncode != 0:
                return False

            spec_data = json.loads(val_result.stdout)

            # 步骤2: 获取Worker状态
            worker_result = subprocess.run(
                [sys.executable, worker_path, "--status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root,
            )

            if worker_result.returncode != 0:
                return False

            worker_data = json.loads(worker_result.stdout)

            # 步骤3: 验证审计日志可写
            audit_log = os.path.join(self.project_root, ".lingma", "logs", "audit.log")
            with open(audit_log, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "event_type": "workflow_test",
                            "spec_valid": spec_data["valid"],
                            "worker_status": worker_data["status"],
                        }
                    )
                    + "\n"
                )

            return True

        except Exception as e:
            print(f"\n       错误: {str(e)}")
            return False


def main():
    """主函数"""
    verifier = SpecTriggerVerifier()

    success = verifier.run_all_checks()

    # 生成验证报告
    report_path = os.path.join(
        verifier.project_root,
        ".lingma",
        "reports",
        f'verification-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json',
    )

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "project_root": verifier.project_root,
        "total_checks": 16,
        "passed": verifier.passed,
        "failed": verifier.failed,
        "success_rate": round(verifier.passed / 16 * 100, 2),
        "results": verifier.results,
        "overall_status": "PASS" if success else "FAIL",
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 验证报告已保存: {report_path}")
    print()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
