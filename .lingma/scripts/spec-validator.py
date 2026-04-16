#!/usr/bin/env python3
"""
Spec验证中间件 - 硬约束自动化核心组件

功能:
1. 解析current-spec.md元数据
2. 验证必填字段(status/priority/tasks)
3. 检测澄清问题标记[NEEDS CLARIFICATION]
4. 支持4种模式: pre-commit/post-checkout/CI/manual
5. 返回结构化验证结果

使用方式:
    python spec-validator.py --mode pre-commit
    python spec-validator.py --mode manual --spec path/to/spec.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SpecValidator:
    """Spec验证器 - 强制执行Spec驱动开发规范"""

    REQUIRED_FIELDS = ["status", "priority"]
    VALID_STATUSES = ["draft", "in-progress", "review", "completed", "archived"]
    VALID_PRIORITIES = ["P0", "P1", "P2", "P3", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    CLARIFICATION_PATTERN = r"\[NEEDS CLARIFICATION\]"

    def __init__(self, spec_path: str = None):
        """
        初始化验证器

        Args:
            spec_path: Spec文件路径，默认为.lingma/specs/current-spec.md
        """
        self.spec_path = spec_path or self._find_current_spec()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metadata: Dict = {}

    def _find_current_spec(self) -> str:
        """查找当前Spec文件"""
        # 从项目根目录查找
        project_root = self._find_project_root()
        spec_path = os.path.join(project_root, ".lingma", "specs", "current-spec.md")

        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Spec文件不存在: {spec_path}")

        return spec_path

    def _find_project_root(self) -> str:
        """查找项目根目录(包含.git的目录)"""
        current_dir = os.getcwd()

        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        # 如果没找到，返回当前目录
        return os.getcwd()

    def validate(self, mode: str = "manual") -> Dict:
        """
        执行验证

        Args:
            mode: 验证模式 (pre-commit/post-checkout/CI/manual)

        Returns:
            验证结果字典
        """
        start_time = datetime.now()

        try:
            # 1. 检查文件存在性
            if not os.path.exists(self.spec_path):
                return self._build_result(False, mode, start_time, ["Spec文件不存在"])

            # 2. 读取并解析Spec
            with open(self.spec_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 3. 提取元数据
            metadata = self._extract_metadata(content)
            self.metadata = metadata

            # 4. 验证必填字段
            self._validate_required_fields(metadata)

            # 5. 验证状态值
            if "status" in metadata:
                self._validate_status(metadata["status"])

            # 6. 验证优先级
            if "priority" in metadata:
                self._validate_priority(metadata["priority"])

            # 7. 检测澄清问题
            clarifications = self._detect_clarifications(content)

            # 8. 检查任务列表
            tasks = self._extract_tasks(content)
            self._validate_tasks(tasks, metadata.get("status"))

            # 9. 构建结果
            is_valid = len(self.errors) == 0 and len(clarifications) == 0

            return self._build_result(
                is_valid, mode, start_time, clarifications=clarifications, tasks=tasks
            )

        except Exception as e:
            return self._build_result(
                False, mode, start_time, [f"验证过程异常: {str(e)}"]
            )

    def _extract_metadata(self, content: str) -> Dict:
        """提取Spec元数据"""
        metadata = {}

        # 匹配元数据格式: - **字段名**: 值
        patterns = {
            "status": r"- \*\*状态\*\*:\s*(.+)",
            "priority": r"- \*\*优先级\*\*:\s*(.+)",
            "progress": r"- \*\*进度\*\*:\s*(.+)",
            "负责人": r"- \*\*负责人\*\*:\s*(.+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                metadata[key] = match.group(1).strip()

        return metadata

    def _validate_required_fields(self, metadata: Dict):
        """验证必填字段"""
        for field in self.REQUIRED_FIELDS:
            if field not in metadata or not metadata[field]:
                self.errors.append(f"缺少必填字段: {field}")

    def _validate_status(self, status: str):
        """验证状态值"""
        if status not in self.VALID_STATUSES:
            self.errors.append(
                f"无效的状态值: '{status}'。有效值: {', '.join(self.VALID_STATUSES)}"
            )

    def _validate_priority(self, priority: str):
        """验证优先级"""
        if priority not in self.VALID_PRIORITIES:
            self.errors.append(
                f"无效的优先级: '{priority}'。有效值: {', '.join(self.VALID_PRIORITIES)}"
            )

    def _detect_clarifications(self, content: str) -> List[str]:
        """检测未回答的澄清问题"""
        clarifications = []

        # 查找所有[NEEDS CLARIFICATION]标记
        matches = re.finditer(self.CLARIFICATION_PATTERN, content)

        for match in matches:
            # 获取上下文(前后50字符)
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].strip()

            clarifications.append({"position": match.start(), "context": context})

        return clarifications

    def _extract_tasks(self, content: str) -> List[Dict]:
        """提取任务列表"""
        tasks = []

        # 匹配任务项: - [ ] Task描述 或 - [x] Task描述
        task_pattern = r"- \[([ xX])\]\s+(Task-\d+|.*?)(?:\s+\((预计:.+?\)|✅|⚠️)?.*)?$"

        for match in re.finditer(task_pattern, content, re.MULTILINE):
            checkbox = match.group(1)
            task_desc = match.group(2).strip()

            tasks.append(
                {"completed": checkbox.lower() == "x", "description": task_desc}
            )

        return tasks

    def _validate_tasks(self, tasks: List[Dict], status: str):
        """验证任务列表"""
        if not tasks:
            self.warnings.append("Spec中未定义任务列表")
            return

        # 检查是否有未完成的任务但状态为completed
        if status == "completed":
            incomplete_tasks = [t for t in tasks if not t["completed"]]
            if incomplete_tasks:
                self.errors.append(
                    f"状态为'completed'但有{len(incomplete_tasks)}个未完成任务"
                )

    def _build_result(
        self,
        is_valid: bool,
        mode: str,
        start_time: datetime,
        errors: List[str] = None,
        clarifications: List = None,
        tasks: List = None,
    ) -> Dict:
        """构建验证结果"""
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        result = {
            "valid": is_valid,
            "mode": mode,
            "spec_path": self.spec_path,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round(duration_ms, 2),
            "metadata": self.metadata,
            "errors": errors or self.errors,
            "warnings": self.warnings,
        }

        if clarifications is not None:
            result["clarifications"] = clarifications
            result["has_unanswered_questions"] = len(clarifications) > 0

        if tasks is not None:
            total = len(tasks)
            completed = sum(1 for t in tasks if t["completed"])
            result["tasks"] = {
                "total": total,
                "completed": completed,
                "pending": total - completed,
                "completion_rate": (
                    round(completed / total * 100, 2) if total > 0 else 0
                ),
            }

        return result

    def format_report(self, result: Dict) -> str:
        """格式化验证报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("Spec验证报告")
        lines.append("=" * 60)
        lines.append("")

        # 基本信息
        lines.append(f"Spec文件: {result['spec_path']}")
        lines.append(f"验证模式: {result['mode']}")
        lines.append(f"验证时间: {result['timestamp']}")
        lines.append(f"耗时: {result['duration_ms']}ms")
        lines.append("")

        # 元数据
        if result["metadata"]:
            lines.append("--- 元数据 ---")
            for key, value in result["metadata"].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        # 任务进度
        if "tasks" in result:
            lines.append("--- 任务进度 ---")
            tasks = result["tasks"]
            lines.append(f"  总计: {tasks['total']}")
            lines.append(f"  已完成: {tasks['completed']}")
            lines.append(f"  待完成: {tasks['pending']}")
            lines.append(f"  完成率: {tasks['completion_rate']}%")
            lines.append("")

        # 验证结果
        status_icon = "✅" if result["valid"] else "❌"
        lines.append(f"验证结果: {status_icon} {'通过' if result['valid'] else '失败'}")
        lines.append("")

        # 错误
        if result["errors"]:
            lines.append("❌ 错误:")
            for error in result["errors"]:
                lines.append(f"  - {error}")
            lines.append("")

        # 警告
        if result["warnings"]:
            lines.append("⚠️  警告:")
            for warning in result["warnings"]:
                lines.append(f"  - {warning}")
            lines.append("")

        # 澄清问题
        if "clarifications" in result and result["clarifications"]:
            lines.append("❓ 未回答的澄清问题:")
            for i, clarification in enumerate(result["clarifications"], 1):
                lines.append(f"  {i}. {clarification['context']}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Spec验证中间件")
    parser.add_argument(
        "--mode",
        type=str,
        default="manual",
        choices=["pre-commit", "post-checkout", "CI", "manual"],
        help="验证模式",
    )
    parser.add_argument(
        "--spec",
        type=str,
        default=None,
        help="Spec文件路径(默认: .lingma/specs/current-spec.md)",
    )
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    parser.add_argument(
        "--strict", action="store_true", help="严格模式(警告也视为错误)"
    )

    args = parser.parse_args()

    try:
        # 创建验证器
        validator = SpecValidator(spec_path=args.spec)

        # 执行验证
        result = validator.validate(mode=args.mode)

        # 严格模式: 警告升级为错误
        if args.strict and result["warnings"]:
            result["valid"] = False
            result["errors"].extend(
                [f"警告(严格模式): {w}" for w in result["warnings"]]
            )

        # 输出结果
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            report = validator.format_report(result)
            print(report)

        # 退出码
        sys.exit(0 if result["valid"] else 1)

    except Exception as e:
        error_result = {
            "valid": False,
            "mode": args.mode,
            "timestamp": datetime.now().isoformat(),
            "errors": [f"验证器异常: {str(e)}"],
        }

        if args.json:
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 验证失败: {str(e)}")

        sys.exit(1)


if __name__ == "__main__":
    main()
