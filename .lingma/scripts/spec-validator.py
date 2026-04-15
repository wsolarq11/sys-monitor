#!/usr/bin/env python3
"""
Spec验证中间件 - 硬约束自动化核心组件

职责：
1. 验证Spec文件存在性和有效性
2. 强制执行Spec驱动开发流程
3. 阻止无Spec的代码提交
4. 提供清晰的错误提示和修复建议

使用场景：
- Git Hook调用（pre-commit, post-checkout）
- CI/CD流水线集成
- 手动验证脚本调用
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SpecValidationError(Exception):
    """Spec验证异常"""
    def __init__(self, message: str, suggestions: List[str] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.message)


class SpecValidator:
    """
    Spec验证器
    
    验证规则：
    1. current-spec.md 必须存在
    2. Spec状态不能是 draft（除非是新项目初始化）
    3. Spec必须包含必需的元数据字段
    4. 如果有未完成任务，必须有实施笔记记录进度
    """
    
    REQUIRED_FIELDS = [
        "元数据",
        "背景与目标",
        "需求规格",
        "实施计划"
    ]
    
    VALID_STATUSES = ["draft", "in-progress", "review", "completed", "archived"]
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.spec_path = self.repo_root / ".lingma" / "specs" / "current-spec.md"
        self.validation_errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self, strict_mode: bool = True) -> Tuple[bool, List[str], List[str]]:
        """
        执行Spec验证
        
        Args:
            strict_mode: 严格模式，阻止所有违规
            
        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.validation_errors = []
        self.warnings = []
        
        try:
            # 1. 检查Spec文件存在性
            if not self._check_spec_exists():
                return False, self.validation_errors, self.warnings
            
            # 2. 读取并解析Spec
            spec_content = self._read_spec()
            
            # 3. 验证必需字段
            self._validate_required_fields(spec_content)
            
            # 4. 验证元数据
            metadata = self._extract_metadata(spec_content)
            self._validate_metadata(metadata)
            
            # 5. 验证状态转换合法性
            self._validate_status_transition(metadata)
            
            # 6. 检查实施笔记
            self._validate_implementation_notes(spec_content, metadata)
            
            # 7. 检查任务完成度
            self._validate_task_completion(spec_content, metadata)
            
        except SpecValidationError as e:
            self.validation_errors.append(e.message)
            if e.suggestions:
                self.warnings.extend(e.suggestions)
        except Exception as e:
            self.validation_errors.append(f"验证过程出错: {str(e)}")
        
        is_valid = len(self.validation_errors) == 0
        
        if strict_mode and not is_valid:
            return False, self.validation_errors, self.warnings
        
        return is_valid, self.validation_errors, self.warnings
    
    def _check_spec_exists(self) -> bool:
        """检查Spec文件是否存在"""
        if not self.spec_path.exists():
            self.validation_errors.append(
                f"❌ Spec文件不存在: {self.spec_path}\n"
                f"   必须先创建Spec才能进行开发"
            )
            return False
        return True
    
    def _read_spec(self) -> str:
        """读取Spec文件内容"""
        try:
            return self.spec_path.read_text(encoding='utf-8')
        except Exception as e:
            raise SpecValidationError(
                f"无法读取Spec文件: {e}",
                ["检查文件权限", "确认文件编码为UTF-8"]
            )
    
    def _validate_required_fields(self, content: str):
        """验证必需字段是否存在"""
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if f"## {field}" not in content and f"### {field}" not in content:
                missing_fields.append(field)
        
        if missing_fields:
            raise SpecValidationError(
                f"❌ Spec缺少必需字段: {', '.join(missing_fields)}",
                [
                    "参考模板: .lingma/specs/templates/spec-template.md",
                    "确保包含所有必需章节"
                ]
            )
    
    def _extract_metadata(self, content: str) -> Dict:
        """提取元数据"""
        metadata = {}
        in_metadata = False
        
        for line in content.split('\n'):
            if line.strip() == "## 元数据":
                in_metadata = True
                continue
            elif line.strip().startswith("## ") and in_metadata:
                break
            
            if in_metadata and ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().lstrip("- ").strip()
                value = value.strip()
                if key and value:
                    metadata[key] = value
        
        return metadata
    
    def _validate_metadata(self, metadata: Dict):
        """验证元数据完整性"""
        required_metadata = ["创建日期", "状态", "优先级"]
        missing = [field for field in required_metadata if field not in metadata]
        
        if missing:
            raise SpecValidationError(
                f"❌ 元数据缺少必需字段: {', '.join(missing)}",
                ["在'## 元数据'章节添加缺失字段"]
            )
    
    def _validate_status_transition(self, metadata: Dict):
        """验证状态转换合法性"""
        status = metadata.get("状态", "").strip()
        
        if status not in self.VALID_STATUSES:
            raise SpecValidationError(
                f"❌ 无效的Spec状态: '{status}'",
                [f"有效状态: {', '.join(self.VALID_STATUSES)}"]
            )
        
        # 警告：draft状态的Spec不应该有实施笔记
        if status == "draft":
            self.warnings.append(
                "⚠️  Spec处于draft状态，应该先审批后再开始实施"
            )
    
    def _validate_implementation_notes(self, content: str, metadata: Dict):
        """验证实施笔记"""
        status = metadata.get("状态", "").strip()
        
        if status == "in-progress":
            if "## 实施笔记" not in content:
                self.warnings.append(
                    "⚠️  in-progress状态的Spec应该有实施笔记记录进度"
                )
    
    def _validate_task_completion(self, content: str, metadata: Dict):
        """验证任务完成度"""
        # 统计任务完成情况
        total_tasks = content.count("- [ ]") + content.count("- [x]")
        completed_tasks = content.count("- [x]")
        
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            status = metadata.get("状态", "").strip()
            
            # 如果所有任务完成但状态不是completed
            if completion_rate == 1.0 and status != "completed":
                self.warnings.append(
                    f"⚠️  所有任务已完成({completed_tasks}/{total_tasks})，但状态仍是'{status}'"
                )
            elif completion_rate < 1.0 and status == "completed":
                self.warnings.append(
                    f"⚠️  状态为'completed'但仍有未完成任务({completed_tasks}/{total_tasks})"
                )


class SpecTriggerMiddleware:
    """
    Spec触发器中间件
    
    用于Git Hook和CI/CD集成
    """
    
    def __init__(self, repo_root: Path = None):
        self.validator = SpecValidator(repo_root)
        self.log_file = Path(repo_root or Path.cwd()) / ".lingma" / "logs" / "spec-validation.log"
    
    def pre_commit_check(self) -> int:
        """
        pre-commit钩子检查
        
        Returns:
            0: 通过, 1: 失败
        """
        print("🔍 执行Spec预提交检查...")
        
        is_valid, errors, warnings = self.validator.validate(strict_mode=True)
        
        # 输出警告
        for warning in warnings:
            print(f"  {warning}")
        
        # 输出错误
        if errors:
            print("\n❌ Spec验证失败:")
            for error in errors:
                print(f"  {error}")
            
            self._log_validation(False, errors, warnings)
            print("\n💡 修复建议:")
            print("  1. 确保 current-spec.md 存在且格式正确")
            print("  2. 参考模板: .lingma/specs/templates/spec-template.md")
            print("  3. 运行验证脚本: python .lingma/scripts/validate-spec.py")
            return 1
        
        print("✅ Spec验证通过")
        self._log_validation(True, [], warnings)
        return 0
    
    def post_checkout_check(self) -> int:
        """
        post-checkout钩子检查
        
        Returns:
            0: 通过, 1: 失败（仅警告）
        """
        print("🔍 执行Spec切换后检查...")
        
        is_valid, errors, warnings = self.validator.validate(strict_mode=False)
        
        if errors:
            print("\n⚠️  Spec存在问题:")
            for error in errors:
                print(f"  {error}")
            print("\n💡 建议修复后再继续开发")
        
        if warnings:
            print("\n⚠️  警告:")
            for warning in warnings:
                print(f"  {warning}")
        
        if not errors and not warnings:
            print("✅ Spec状态正常")
        
        self._log_validation(len(errors) == 0, errors, warnings)
        return 0  # post-checkout不阻止操作
    
    def ci_validation(self) -> int:
        """
        CI/CD流水线验证
        
        Returns:
            0: 通过, 1: 失败
        """
        print("🔍 CI/CD Spec验证...")
        
        is_valid, errors, warnings = self.validator.validate(strict_mode=True)
        
        if errors:
            print("\n❌ CI验证失败:")
            for error in errors:
                print(f"  {error}")
            self._log_validation(False, errors, warnings)
            return 1
        
        print(f"✅ CI验证通过 (警告: {len(warnings)})")
        for warning in warnings:
            print(f"  {warning}")
        
        self._log_validation(True, [], warnings)
        return 0
    
    def _log_validation(self, success: bool, errors: List[str], warnings: List[str]):
        """记录验证日志"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "errors_count": len(errors),
                "warnings_count": len(warnings),
                "errors": errors[:5],  # 只记录前5个错误
                "warnings": warnings[:5]
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️  无法记录验证日志: {e}", file=sys.stderr)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spec验证中间件")
    parser.add_argument(
        "mode",
        choices=["pre-commit", "post-checkout", "ci", "manual"],
        help="验证模式"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认当前目录）"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="严格模式（默认开启）"
    )
    
    args = parser.parse_args()
    
    middleware = SpecTriggerMiddleware(args.repo_root)
    
    if args.mode == "pre-commit":
        exit_code = middleware.pre_commit_check()
    elif args.mode == "post-checkout":
        exit_code = middleware.post_checkout_check()
    elif args.mode == "ci":
        exit_code = middleware.ci_validation()
    elif args.mode == "manual":
        is_valid, errors, warnings = middleware.validator.validate(strict_mode=args.strict)
        
        print(f"\n验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        if warnings:
            print(f"\n警告 ({len(warnings)}):")
            for w in warnings:
                print(f"  {w}")
        
        if errors:
            print(f"\n错误 ({len(errors)}):")
            for e in errors:
                print(f"  {e}")
        
        exit_code = 0 if is_valid else 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
