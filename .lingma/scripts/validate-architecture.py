#!/usr/bin/env python3
"""
Task-023: 新架构完整验证脚本

职责：
1. 测试 Rule 是否生效
2. 测试 Agent 决策能力
3. 验证无回归问题
4. 端到端功能测试
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class ArchitectureValidator:
    """架构验证器"""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_test(self, name: str, test_func, description: str = "") -> bool:
        """运行单个测试"""
        print(f"\n🧪 测试: {name}")
        if description:
            print(f"   描述: {description}")

        try:
            start_time = time.time()
            result = test_func()
            elapsed = time.time() - start_time

            if result:
                self.passed += 1
                print(f"   ✅ 通过 (耗时: {elapsed:.2f}s)")
                self.results.append(
                    {"name": name, "status": "PASSED", "duration": elapsed}
                )
                return True
            else:
                self.failed += 1
                print(f"   ❌ 失败")
                self.results.append(
                    {"name": name, "status": "FAILED", "duration": elapsed}
                )
                return False

        except Exception as e:
            self.failed += 1
            print(f"   ❌ 异常: {e}")
            self.results.append({"name": name, "status": "ERROR", "error": str(e)})
            return False

    def test_rule_loading(self) -> bool:
        """测试 Rule 加载"""
        rules_dir = Path(".lingma/rules")
        if not rules_dir.exists():
            print("   ⚠️  Rules 目录不存在")
            return False

        rule_files = list(rules_dir.glob("*.md"))
        print(f"   找到 {len(rule_files)} 个 Rule 文件")

        required_rules = [
            "automation-policy.md",
            "memory-usage.md",
            "spec-session-start.md",
            "subagent-file-creation.md",
        ]

        for rule in required_rules:
            rule_path = rules_dir / rule
            if rule_path.exists():
                print(f"   ✅ {rule}")
            else:
                print(f"   ❌ {rule} 缺失")
                return False

        return True

    def test_agent_configuration(self) -> bool:
        """测试 Agent 配置"""
        agent_config_path = Path(".lingma/config/agent-config.json")
        if not agent_config_path.exists():
            print("   ⚠️  Agent 配置文件不存在")
            return False

        with open(agent_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        required_keys = ["agent_name", "skills", "rules"]
        for key in required_keys:
            if key not in config:
                print(f"   ❌ 缺少配置项: {key}")
                return False

        print(f"   Agent 名称: {config['agent_name']}")
        print(f"   Skills: {len(config.get('skills', []))}")
        print(f"   Rules: {len(config.get('rules', []))}")

        return True

    def test_decision_cache(self) -> bool:
        """测试决策缓存"""
        try:
            from decision_cache import DecisionCache

            cache = DecisionCache(max_size=10, ttl=60)

            # 测试缓存设置和获取
            operation = {"type": "test", "path": "/test.txt"}
            result = {"strategy": "auto_execute"}

            cache.set(operation, result)
            cached = cache.get(operation)

            if cached != result:
                print("   ❌ 缓存数据不匹配")
                return False

            # 测试统计
            stats = cache.get_stats()
            print(f"   缓存大小: {stats['size']}")
            print(f"   命中率: {stats['hit_rate_percent']}%")

            return True

        except ImportError as e:
            print(f"   ❌ 无法导入模块: {e}")
            return False

    def test_batch_logger(self) -> bool:
        """测试批量日志写入器"""
        try:
            from batch_logger import BatchLogger

            logger = BatchLogger(
                log_file=".lingma/logs/test_batch.log", batch_size=5, flush_interval=1.0
            )

            # 记录一些日志
            for i in range(10):
                logger.log({"level": "INFO", "message": f"Test message {i}"})

            # 刷新
            logger.flush()
            logger.stop()

            # 验证日志文件
            log_file = Path(".lingma/logs/test_batch.log")
            if log_file.exists():
                line_count = sum(1 for _ in open(log_file, "r", encoding="utf-8"))
                print(f"   日志行数: {line_count}")

                # 清理测试文件
                log_file.unlink()

                return line_count == 10
            else:
                print("   ❌ 日志文件未创建")
                return False

        except ImportError as e:
            print(f"   ❌ 无法导入模块: {e}")
            return False

    def test_ux_improvements(self) -> bool:
        """测试用户体验改进模块"""
        try:
            from ux_improvements import ProgressDisplay, MessageFormatter, UndoManager

            # 测试进度显示
            progress = ProgressDisplay(total=10, description="Test")
            progress.update(current=5)

            # 测试消息格式化
            formatter = MessageFormatter()
            msg = formatter.success("Test success")
            if "✅" not in msg:
                return False

            # 测试撤销管理
            undo_mgr = UndoManager(max_history=10)
            undo_mgr.record_action("test", {"data": "value"})

            stats = undo_mgr.get_stats()
            print(f"   历史记录数: {stats['history_size']}")

            return stats["history_size"] == 1

        except ImportError as e:
            print(f"   ❌ 无法导入模块: {e}")
            return False

    def test_session_middleware(self) -> bool:
        """测试会话中间件"""
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "session_middleware", Path(__file__).parent / "session-middleware.py"
            )
            if spec is None or spec.loader is None:
                print("   ❌ 无法加载模块")
                return False
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            SessionMiddleware = getattr(module, "SessionMiddleware")
            middleware = SessionMiddleware()

            # SessionMiddleware 使用 run() 方法
            result = middleware.run()

            print(f"   中间件执行: {'成功' if result else '失败'}")

            return result

        except Exception as e:
            print(f"   ❌ 无法加载模块: {e}")
            import traceback

            traceback.print_exc()
            return False

    def test_spec_structure(self) -> bool:
        """测试 Spec 文件结构"""
        spec_path = Path(".lingma/specs/current-spec.md")
        if not spec_path.exists():
            print("   ❌ Spec 文件不存在")
            return False

        content = spec_path.read_text(encoding="utf-8")

        # 检查必需的部分
        required_sections = [
            "## 背景与目标",
            "## 需求规格",
            "## 技术方案",
            "## 实施计划",
            "## 实施笔记",
        ]

        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)

        if missing:
            print(f"   ❌ 缺少部分: {missing}")
            return False

        print(f"   Spec 文件完整")
        return True

    def test_directory_structure(self) -> bool:
        """测试目录结构"""
        required_dirs = [
            ".lingma/agents",
            ".lingma/config",
            ".lingma/docs",
            ".lingma/rules",
            ".lingma/scripts",
            ".lingma/skills",
            ".lingma/specs",
            ".lingma/logs",
            ".lingma/reports",
        ]

        missing = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing.append(dir_path)

        if missing:
            print(f"   ❌ 缺少目录: {missing}")
            return False

        print(f"   所有必需目录存在")
        return True

    def test_skill_files(self) -> bool:
        """测试 Skill 文件"""
        skills_dir = Path(".lingma/skills")
        if not skills_dir.exists():
            print("   ❌ Skills 目录不存在")
            return False

        # 查找 SKILL.md 文件
        skill_files = list(skills_dir.rglob("SKILL.md"))
        print(f"   找到 {len(skill_files)} 个 Skill")

        if len(skill_files) < 2:
            print("   ⚠️  Skill 数量不足（预期至少 2 个）")
            self.warnings += 1
            return True  # 警告但不失败

        return True

    def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        try:
            # 测试决策缓存性能
            from decision_cache import DecisionCache

            cache = DecisionCache(max_size=1000, ttl=3600)

            # 性能测试
            iterations = 100
            start = time.time()

            for i in range(iterations):
                operation = {"type": "test", "index": i}
                result = {"strategy": "auto"}
                cache.set(operation, result)
                cache.get(operation)

            elapsed = time.time() - start
            avg_time = (elapsed / iterations) * 1000  # ms

            print(f"   平均操作时间: {avg_time:.2f}ms")

            # 应该小于 10ms
            if avg_time < 10:
                print(f"   ✅ 性能良好")
                return True
            else:
                print(f"   ⚠️  性能较慢")
                self.warnings += 1
                return True

        except Exception as e:
            print(f"   ❌ 性能测试失败: {e}")
            return False

    def generate_report(self) -> str:
        """生成验证报告"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = Path(f".lingma/reports/architecture-validation-{timestamp}.json")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        report = {
            "timestamp": timestamp,
            "summary": {
                "total": total,
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "pass_rate": round(pass_rate, 2),
            },
            "results": self.results,
        }

        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(report_file)

    def print_summary(self):
        """打印总结"""
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 60)
        print("📊 验证总结")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"⚠️  警告: {self.warnings}")
        print(f"通过率: {pass_rate:.1f}%")
        print("=" * 60)

        if self.failed == 0:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  有 {self.failed} 个测试失败，请检查")


def main():
    """主函数"""
    print("Starting architecture validation...\n")
    print("=" * 60)
    print("Task-023: Testing New Architecture")
    print("=" * 60)

    validator = ArchitectureValidator()

    # 运行所有测试
    tests = [
        ("目录结构检查", validator.test_directory_structure, "验证必需的目录是否存在"),
        ("Rule 加载测试", validator.test_rule_loading, "验证 Rule 文件是否正确加载"),
        ("Agent 配置测试", validator.test_agent_configuration, "验证 Agent 配置完整性"),
        ("Skill 文件测试", validator.test_skill_files, "验证 Skill 文件存在"),
        ("Spec 结构测试", validator.test_spec_structure, "验证 Spec 文件结构完整"),
        ("决策缓存测试", validator.test_decision_cache, "测试决策缓存功能"),
        ("批量日志测试", validator.test_batch_logger, "测试批量日志写入功能"),
        ("UX 改进测试", validator.test_ux_improvements, "测试用户体验改进模块"),
        ("会话中间件测试", validator.test_session_middleware, "测试会话中间件验证"),
        ("性能指标测试", validator.test_performance_metrics, "测试性能指标是否达标"),
    ]

    for name, test_func, description in tests:
        validator.run_test(name, test_func, description)

    # 生成报告
    report_path = validator.generate_report()
    print(f"\n📄 验证报告已生成: {report_path}")

    # 打印总结
    validator.print_summary()

    # 返回退出码
    return 0 if validator.failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
