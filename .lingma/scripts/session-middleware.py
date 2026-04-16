#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Middleware - 会话启动强制检查中间件

职责：
1. 在每次会话开始时自动执行
2. 强制读取 .lingma/specs/current-spec.md
3. 验证所有必需组件存在
4. 生成结构化启动报告

设计原则：
- 系统性预防：让错误无法产生
- 快速反馈：问题立即暴露
- 不可绕过：失败则阻止会话继续（除非显式 --force-bypass）
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class ValidationReport:
    """验证报告"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def add_error(self, message: str):
        self.errors.append(f"❌ {message}")

    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  {message}")

    def add_passed(self, message: str):
        self.passed.append(f"✅ {message}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def is_critical(self) -> bool:
        """是否有阻断性错误"""
        return len(self.errors) > 0

    def add_root_violation(self, filename: str):
        """添加根目录违规文件（严重错误）"""
        self.errors.append(f"🚫 根目录违规文件: {filename} (小猫死亡 🐱⚡)")

    def add_root_violation(self, filename: str):
        """添加根目录违规文件（严重错误）"""
        self.errors.append(f"🚫 根目录违规文件: {filename} (小猫死亡 🐱⚡)")

    def summary(self) -> str:
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("📋 Session Startup Validation Report")
        lines.append("=" * 70)

        if self.passed:
            lines.append("\n✅ Passed Checks:")
            for item in self.passed:
                lines.append(f"   {item}")

        if self.warnings:
            lines.append("\n⚠️  Warnings:")
            for item in self.warnings:
                lines.append(f"   {item}")

        if self.errors:
            lines.append("\n❌ Errors (Blocking):")
            for item in self.errors:
                lines.append(f"   {item}")

        lines.append("\n" + "-" * 70)
        status = "FAILED" if self.has_errors() else "PASSED"
        lines.append(f"Status: {status}")
        lines.append(
            f"Total: {len(self.passed)} passed, {len(self.warnings)} warnings, {len(self.errors)} errors"
        )
        lines.append("=" * 70 + "\n")

        return "\n".join(lines)


class SessionMiddleware:
    """会话启动中间件"""

    def __init__(self, lingma_dir: str = ".lingma", force_bypass: bool = False):
        self.lingma_dir = Path(lingma_dir)
        self.force_bypass = force_bypass
        self.report = ValidationReport()
        self.spec_data: Optional[Dict] = None

    def run(self) -> bool:
        """
        执行会话启动检查

        Returns:
            bool: True if session can proceed, False otherwise
        """
        print("🔍 Starting Session Middleware checks...\n")

        # 1. 加载 Spec
        spec_loaded = self.load_current_spec()

        # 2. 验证组件
        self.validate_components()

        # 3. 验证 Spec 状态
        if spec_loaded:
            self.validate_spec_state()

        # 4. 生成报告
        print(self.report.summary())

        # 5. 决策
        if self.report.has_errors():
            if self.force_bypass:
                print("⚠️  FORCE BYPASS enabled - proceeding despite errors\n")
                return True
            else:
                print("🛑 Session blocked due to validation errors")
                print("💡 Use --force-bypass to override (not recommended)\n")
                return False

        print("✅ All checks passed - session can proceed\n")
        return True

    def load_current_spec(self) -> bool:
        """加载当前 Spec 文件"""
        spec_path = self.lingma_dir / "specs" / "current-spec.md"

        if not spec_path.exists():
            self.report.add_error("current-spec.md not found")
            self.report.add_error("Spec file is required for session startup")
            return False

        try:
            content = spec_path.read_text(encoding="utf-8")

            # 解析元数据
            metadata = self._parse_spec_metadata(content)
            self.spec_data = {
                "path": str(spec_path),
                "content": content,
                "metadata": metadata,
                "size_kb": len(content.encode("utf-8")) / 1024,
            }

            self.report.add_passed(f"Spec loaded: {spec_path.name}")
            self.report.add_passed(f"Spec size: {self.spec_data['size_kb']:.1f}KB")

            if metadata:
                status = metadata.get("status", "unknown")
                progress = metadata.get("progress", "N/A")
                self.report.add_passed(f"Spec status: {status}")
                self.report.add_passed(f"Progress: {progress}")

            return True

        except Exception as e:
            self.report.add_error(f"Failed to read spec: {str(e)}")
            return False

    def _parse_spec_metadata(self, content: str) -> Dict:
        """解析 Spec 元数据"""
        metadata = {}

        # 简单解析 YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                yaml_content = parts[1].strip()
                for line in yaml_content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()

        return metadata

    def validate_components(self):
        """验证必需组件"""

        # 检查目录结构
        required_dirs = {
            "agents": "Agent definitions",
            "skills": "Skill definitions",
            "rules": "Rule definitions",
            "specs": "Specification files",
            "config": "Configuration files",
        }

        for dir_name, description in required_dirs.items():
            dir_path = self.lingma_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.report.add_passed(f"Directory exists: {dir_name}/ ({description})")
            else:
                self.report.add_error(f"Missing directory: {dir_name}/ ({description})")

        # 检查关键文件
        critical_files = {
            "rules/AGENTS.md": "Core agent rules",
            "rules/memory-usage.md": "Memory usage guidelines",
            "rules/automation-policy.md": "Automation policy",
            "rules/spec-session-start.md": "Session start rules",
        }

        for file_path, description in critical_files.items():
            full_path = self.lingma_dir / file_path
            if full_path.exists():
                self.report.add_passed(f"File exists: {file_path} ({description})")
            else:
                self.report.add_warning(f"Missing file: {file_path} ({description})")

        # 🚨 强制检查根目录清洁度
        self.validate_root_cleanliness()

        # 检查冗余文档（违反单一入口原则）
        self._check_redundant_docs()

        # 检查临时文件
        self._check_temp_files()

    def _check_redundant_docs(self):
        """检查冗余文档"""
        lingma_root_docs = list(self.lingma_dir.glob("*.md"))

        allowed_docs = {"README.md"}
        redundant = [f for f in lingma_root_docs if f.name not in allowed_docs]

        if redundant:
            for doc in redundant:
                self.report.add_error(
                    f"Redundant doc in .lingma/: {doc.name} (violates single-entry principle)"
                )
        else:
            self.report.add_passed("No redundant docs in .lingma/ root")

        # 检查功能目录中的 README
        for subdir in ["agents", "rules", "skills"]:
            subdir_path = self.lingma_dir / subdir
            if subdir_path.exists():
                readmes = list(subdir_path.glob("README.md"))
                if readmes:
                    for readme in readmes:
                        self.report.add_error(
                            f"README in {subdir}/ violates clean-directory principle: {readme.name}"
                        )

    def _check_temp_files(self):
        """检查临时文件"""
        temp_patterns = ["[0-9]*", "*temp*", "*.tmp", "*KB*", "*MB*"]
        temp_files = []

        for pattern in temp_patterns:
            temp_files.extend(self.lingma_dir.parent.glob(pattern))

        # 过滤掉合法文件
        legitimate = {".gitignore", ".lingmaignore"}
        temp_files = [f for f in temp_files if f.name not in legitimate and f.is_file()]

        if temp_files:
            for tf in temp_files[:5]:  # 只显示前5个
                self.report.add_warning(f"Potential temp file: {tf.name}")
            if len(temp_files) > 5:
                self.report.add_warning(f"... and {len(temp_files) - 5} more")
        else:
            self.report.add_passed("No temporary files detected")

    def validate_root_cleanliness(self):
        """🚨 强制检查工作区根目录清洁度"""
        workspace_root = self.lingma_dir.parent

        # 定义允许的文件
        allowed_files = {".gitignore", ".lingmaignore", "README.md"}

        # 定义禁止的模式
        forbidden_patterns = [
            "*.py",
            "*.ps1",
            "*.sh",
            "*OPTIMIZATION*",
            "*QUICK_REFERENCE*",
            "*SUMMARY*",
            "*REPORT*",
            "*CHECKLIST*",
            "benchmark_*",
            "fix_*",
            "optimize_*",
            "enable_*",
            "temp_*",
            "test_*.py",
        ]

        violations = []
        for pattern in forbidden_patterns:
            for file in workspace_root.glob(pattern):
                if file.is_file() and file.name not in allowed_files:
                    violations.append(file.name)

        if violations:
            self.report.add_error(f"🚫 根目录发现 {len(violations)} 个违规文件！")
            for v in violations[:10]:  # 最多显示10个
                self.report.add_root_violation(v)
            if len(violations) > 10:
                self.report.add_error(f"... 还有 {len(violations) - 10} 个")
            self.report.add_error("")
            self.report.add_error("💀 小猫正在死亡！每1个违规文件 = 1只小猫死亡！")
            self.report.add_error("")
            self.report.add_error("🛠️  修复方法:")
            self.report.add_error("   powershell scripts/clean-root-directory.ps1")
        else:
            self.report.add_passed("✅ 根目录清洁度检查通过 - 小猫安全！🐱")

    def validate_spec_state(self):
        """验证 Spec 状态"""
        if not self.spec_data:
            return

        metadata = self.spec_data.get("metadata", {})
        status = metadata.get("status", "").lower()

        # 检查 Spec 状态
        valid_states = {"draft", "in-progress", "review", "approved", "completed"}
        if status not in valid_states:
            self.report.add_warning(
                f"Unusual spec status: '{status}' (expected one of: {', '.join(valid_states)})"
            )

        # 如果状态是 draft，检查是否有未完成的澄清问题
        if status == "draft":
            content = self.spec_data.get("content", "")
            if "[NEEDS CLARIFICATION]" in content:
                self.report.add_warning(
                    "Spec is in draft state with unresolved clarification questions"
                )

        # 检查进度字段
        progress = metadata.get("progress", "")
        if progress and "%" in progress:
            try:
                pct = float(progress.split("%")[0].strip())
                if pct < 0 or pct > 100:
                    self.report.add_warning(f"Invalid progress percentage: {progress}")
            except ValueError:
                self.report.add_warning(f"Cannot parse progress: {progress}")

        # 检查实施笔记时间戳（检测是否过期）
        content = self.spec_data.get("content", "")
        if "### 实施笔记" in content:
            self.report.add_passed("Spec contains implementation notes")
        else:
            self.report.add_warning("Spec missing implementation notes section")

    def generate_startup_report(self, output_file: Optional[Path] = None):
        """生成启动报告并可选保存到文件"""
        report_content = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lingma_dir": str(self.lingma_dir),
            "spec": {
                "exists": self.spec_data is not None,
                "path": self.spec_data["path"] if self.spec_data else None,
                "status": (
                    self.spec_data["metadata"].get("status") if self.spec_data else None
                ),
                "progress": (
                    self.spec_data["metadata"].get("progress")
                    if self.spec_data
                    else None
                ),
            },
            "validation": {
                "passed": len(self.report.passed),
                "warnings": len(self.report.warnings),
                "errors": len(self.report.errors),
                "can_proceed": not self.report.has_errors() or self.force_bypass,
            },
        }

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report_content, f, indent=2, ensure_ascii=False)
            print(f"📄 Report saved to: {output_file}\n")

        return report_content


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Session Middleware - Validate session startup"
    )
    parser.add_argument(
        "--lingma-dir",
        default=".lingma",
        help="Path to .lingma directory (default: .lingma)",
    )
    parser.add_argument(
        "--force-bypass",
        action="store_true",
        help="Force bypass validation errors (not recommended)",
    )
    parser.add_argument(
        "--report-output", type=str, default=None, help="Save report to JSON file"
    )

    args = parser.parse_args()

    middleware = SessionMiddleware(
        lingma_dir=args.lingma_dir, force_bypass=args.force_bypass
    )

    success = middleware.run()

    # 保存报告
    if args.report_output:
        middleware.generate_startup_report(Path(args.report_output))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
