#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则解析引擎 - 解析和执行.lingma/rules/下的所有Rule文件

功能:
1. 解析.lingma/rules/下的所有Rule文件
2. 提取trigger条件（always_on/on_change/on_commit等）
3. 执行规则约束逻辑
4. 返回违规报告和修复建议
5. 支持规则优先级（P0/P1/P2）

使用方式:
    python rule-engine.py --validate-spec
    python rule-engine.py --list-rules
    python rule-engine.py --check-rule <rule_name>
"""

import sys
import io

# Windows下设置UTF-8编码
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class RulePriority:
    """规则优先级"""

    P0 = "P0"  # 关键，必须遵守
    P1 = "P1"  # 重要，应该遵守
    P2 = "P2"  # 建议，最好遵守


class TriggerType:
    """触发器类型"""

    ALWAYS_ON = "always_on"
    ON_CHANGE = "on_change"
    ON_COMMIT = "on_commit"
    ON_SPEC_UPDATE = "on_spec_update"
    MANUAL = "manual"


class ViolationSeverity:
    """违规严重程度"""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class Rule:
    """规则对象"""

    def __init__(self, name: str, content: str, file_path: str):
        """
        初始化规则

        Args:
            name: 规则名称
            content: 规则内容
            file_path: 规则文件路径
        """
        self.name = name
        self.content = content
        self.file_path = file_path
        self.metadata = self._parse_metadata()
        self.trigger = self.metadata.get("trigger", TriggerType.MANUAL)
        self.priority = self._extract_priority()
        self.description = self._extract_description()

    def _parse_metadata(self) -> Dict:
        """解析YAML front matter元数据"""
        metadata = {}

        # 匹配YAML front matter: --- ... ---
        pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            yaml_content = match.group(1)

            # 简单解析YAML键值对
            for line in yaml_content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

        return metadata

    def _extract_priority(self) -> str:
        """提取优先级"""
        # 从元数据或内容中提取优先级
        priority = self.metadata.get("priority", RulePriority.P1)

        # 验证优先级有效性
        if priority not in [RulePriority.P0, RulePriority.P1, RulePriority.P2]:
            priority = RulePriority.P1

        return priority

    def _extract_description(self) -> str:
        """提取规则描述"""
        lines = self.content.split("\n")

        # 跳过front matter
        in_front_matter = False
        description_lines = []

        for line in lines:
            if line.strip() == "---":
                if not in_front_matter:
                    in_front_matter = True
                    continue
                else:
                    break

            if in_front_matter and line.strip().startswith("#"):
                description_lines.append(line.strip())

        return " ".join(description_lines).strip() if description_lines else self.name


class Violation:
    """违规对象"""

    def __init__(self, rule: Rule, severity: str, message: str, suggestion: str = ""):
        """
        初始化违规

        Args:
            rule: 违反的规则
            severity: 严重程度
            message: 违规消息
            suggestion: 修复建议
        """
        self.rule = rule
        self.severity = severity
        self.message = message
        self.suggestion = suggestion
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "rule_name": self.rule.name,
            "rule_priority": self.rule.priority,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "timestamp": self.timestamp,
        }


class RuleEngine:
    """规则解析引擎"""

    def __init__(self, project_root: str = None):
        """
        初始化规则引擎

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root or self._find_project_root()
        self.rules_dir = os.path.join(self.project_root, ".lingma", "rules")
        self.spec_path = os.path.join(
            self.project_root, ".lingma", "specs", "current-spec.md"
        )
        self.audit_log_path = os.path.join(
            self.project_root, ".lingma", "logs", "audit.log"
        )

        # 确保目录存在
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

        # 加载规则
        self.rules = self._load_rules()

    def _find_project_root(self) -> str:
        """查找项目根目录"""
        current_dir = os.getcwd()

        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, ".git")):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        return os.getcwd()

    def _load_rules(self) -> List[Rule]:
        """加载所有规则文件"""
        rules = []

        if not os.path.exists(self.rules_dir):
            print(f"[WARN] 规则目录不存在: {self.rules_dir}")
            return rules

        # 遍历规则目录
        for file_name in os.listdir(self.rules_dir):
            if file_name.endswith(".md"):
                file_path = os.path.join(self.rules_dir, file_name)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    rule_name = file_name.replace(".md", "")
                    rule = Rule(name=rule_name, content=content, file_path=file_path)
                    rules.append(rule)

                except Exception as e:
                    print(f"[WARN] 加载规则失败 {file_name}: {e}")

        # 按优先级排序
        priority_order = {RulePriority.P0: 0, RulePriority.P1: 1, RulePriority.P2: 2}
        rules.sort(key=lambda r: priority_order.get(r.priority, 3))

        return rules

    def validate_spec(self) -> List[Violation]:
        """
        验证Spec合规性

        Returns:
            违规列表
        """
        violations = []

        # 检查Spec文件是否存在
        if not os.path.exists(self.spec_path):
            violation = Violation(
                rule=Rule("spec-exists", "", ""),
                severity=ViolationSeverity.ERROR,
                message="Spec文件不存在",
                suggestion=f"创建Spec文件: {self.spec_path}",
            )
            violations.append(violation)
            return violations

        # 读取Spec内容
        with open(self.spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()

        # 应用所有always_on规则
        for rule in self.rules:
            if rule.trigger == TriggerType.ALWAYS_ON:
                rule_violations = self._apply_rule(rule, spec_content)
                violations.extend(rule_violations)

        # 记录审计日志
        self._log_audit(
            "spec_validation",
            {"violations_count": len(violations), "rules_checked": len(self.rules)},
        )

        return violations

    def _apply_rule(self, rule: Rule, spec_content: str) -> List[Violation]:
        """
        应用单个规则

        Args:
            rule: 规则对象
            spec_content: Spec内容

        Returns:
            违规列表
        """
        violations = []

        # 根据规则名称应用不同的检查逻辑
        if "spec-session-start" in rule.name.lower():
            violations.extend(self._check_session_start(rule, spec_content))

        elif "automation-policy" in rule.name.lower():
            violations.extend(self._check_automation_policy(rule, spec_content))

        elif "memory-usage" in rule.name.lower():
            violations.extend(self._check_memory_usage(rule, spec_content))

        elif "doc-redundancy" in rule.name.lower():
            violations.extend(self._check_doc_redundancy(rule, spec_content))

        # 可以添加更多规则检查逻辑

        return violations

    def _check_session_start(self, rule: Rule, spec_content: str) -> List[Violation]:
        """检查会话启动规则"""
        violations = []

        # 检查是否有元数据部分
        if "## 元数据" not in spec_content and "## Metadata" not in spec_content:
            violation = Violation(
                rule=rule,
                severity=ViolationSeverity.WARNING,
                message="Spec缺少元数据部分",
                suggestion="添加'## 元数据'部分，包含创建日期、状态、优先级等信息",
            )
            violations.append(violation)

        # 检查是否有进度跟踪
        if "进度" not in spec_content and "progress" not in spec_content.lower():
            violation = Violation(
                rule=rule,
                severity=ViolationSeverity.INFO,
                message="Spec缺少进度跟踪",
                suggestion="添加进度跟踪行，例如：'- **进度**: 0% (0/0 任务)'",
            )
            violations.append(violation)

        return violations

    def _check_automation_policy(
        self, rule: Rule, spec_content: str
    ) -> List[Violation]:
        """检查自动化策略规则"""
        violations = []

        # 检查是否有风险评估相关内容
        if "风险" not in spec_content and "risk" not in spec_content.lower():
            violation = Violation(
                rule=rule,
                severity=ViolationSeverity.WARNING,
                message="Spec未明确风险评估策略",
                suggestion="在Spec中添加风险评估章节，定义操作的风险等级和执行策略",
            )
            violations.append(violation)

        return violations

    def _check_memory_usage(self, rule: Rule, spec_content: str) -> List[Violation]:
        """检查内存使用规则"""
        violations = []

        # 检查Spec文件大小
        spec_size = len(spec_content.encode("utf-8"))
        max_recommended_size = 50 * 1024  # 50KB

        if spec_size > max_recommended_size:
            violation = Violation(
                rule=rule,
                severity=ViolationSeverity.WARNING,
                message=f"Spec文件过大: {spec_size / 1024:.1f}KB (建议<{max_recommended_size / 1024:.0f}KB)",
                suggestion="将详细内容移至docs/目录，Spec仅保留核心指令和引用链接",
            )
            violations.append(violation)

        return violations

    def _check_doc_redundancy(self, rule: Rule, spec_content: str) -> List[Violation]:
        """检查文档冗余规则"""
        violations = []

        # 检查是否有重复的章节标题
        headings = re.findall(r"^#{1,6}\s+(.+)$", spec_content, re.MULTILINE)
        heading_counts = {}

        for heading in headings:
            heading_lower = heading.lower().strip()
            heading_counts[heading_lower] = heading_counts.get(heading_lower, 0) + 1

        duplicates = {h: c for h, c in heading_counts.items() if c > 1}

        if duplicates:
            violation = Violation(
                rule=rule,
                severity=ViolationSeverity.WARNING,
                message=f"发现重复的章节标题: {', '.join(duplicates.keys())}",
                suggestion="合并或删除重复的章节，保持文档结构清晰",
            )
            violations.append(violation)

        return violations

    def check_rule(self, rule_name: str) -> List[Violation]:
        """
        检查特定规则

        Args:
            rule_name: 规则名称

        Returns:
            违规列表
        """
        # 查找规则
        target_rule = None
        for rule in self.rules:
            if rule_name in rule.name:
                target_rule = rule
                break

        if not target_rule:
            print(f"[FAIL] 未找到规则: {rule_name}")
            return []

        # 读取Spec内容
        if not os.path.exists(self.spec_path):
            return [
                Violation(
                    rule=target_rule,
                    severity=ViolationSeverity.ERROR,
                    message="Spec文件不存在",
                )
            ]

        with open(self.spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()

        # 应用规则
        violations = self._apply_rule(target_rule, spec_content)

        return violations

    def list_rules(self) -> List[Dict]:
        """列出所有规则"""
        rules_info = []

        for rule in self.rules:
            rules_info.append(
                {
                    "name": rule.name,
                    "priority": rule.priority,
                    "trigger": rule.trigger,
                    "description": rule.description,
                    "file_path": rule.file_path,
                }
            )

        return rules_info

    def _log_audit(self, event_type: str, details: Dict):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "engine": "rule-engine",
            **details,
        }

        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[WARN] 审计日志写入失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="规则解析引擎")
    parser.add_argument("--validate-spec", action="store_true", help="验证Spec合规性")
    parser.add_argument("--list-rules", action="store_true", help="列出所有规则")
    parser.add_argument("--check-rule", type=str, help="检查特定规则")
    parser.add_argument("--project-root", type=str, default=None, help="项目根目录")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    try:
        engine = RuleEngine(project_root=args.project_root)

        if args.validate_spec:
            violations = engine.validate_spec()

            if args.json:
                print(
                    json.dumps(
                        [v.to_dict() for v in violations], indent=2, ensure_ascii=False
                    )
                )
            else:
                if violations:
                    print(f"\n[FAIL] 发现 {len(violations)} 个违规:\n")
                    for i, v in enumerate(violations, 1):
                        print(f"{i}. [{v.severity}] {v.message}")
                        print(f"   规则: {v.rule.name} (优先级: {v.rule.priority})")
                        if v.suggestion:
                            print(f"   建议: {v.suggestion}")
                        print()
                else:
                    print("\n[OK] Spec符合所有规则!")

            # 如果有ERROR级别的违规，退出码为1
            has_error = any(v.severity == ViolationSeverity.ERROR for v in violations)
            sys.exit(1 if has_error else 0)

        elif args.list_rules:
            rules = engine.list_rules()

            if args.json:
                print(json.dumps(rules, indent=2, ensure_ascii=False))
            else:
                print(f"\n[INFO] 已加载 {len(rules)} 条规则:\n")
                for i, rule in enumerate(rules, 1):
                    print(f"{i}. {rule['name']}")
                    print(f"   优先级: {rule['priority']}")
                    print(f"   触发器: {rule['trigger']}")
                    print(f"   描述: {rule['description'][:50]}...")
                    print()

        elif args.check_rule:
            violations = engine.check_rule(args.check_rule)

            if args.json:
                print(
                    json.dumps(
                        [v.to_dict() for v in violations], indent=2, ensure_ascii=False
                    )
                )
            else:
                if violations:
                    print(
                        f"\n[FAIL] 规则 '{args.check_rule}' 发现 {len(violations)} 个违规:\n"
                    )
                    for i, v in enumerate(violations, 1):
                        print(f"{i}. [{v.severity}] {v.message}")
                        if v.suggestion:
                            print(f"   建议: {v.suggestion}")
                        print()
                else:
                    print(f"\n[OK] 规则 '{args.check_rule}' 检查通过!")

        else:
            parser.print_help()

    except Exception as e:
        print(f"[FAIL] 规则引擎异常: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
