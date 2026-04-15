#!/usr/bin/env python3
"""
配置验证脚本

检查 Spec-Driven Development 系统的基本配置是否正确
"""

import json
from pathlib import Path


def verify_setup():
    """验证基本配置"""
    
    print("=" * 60)
    print("  Spec-Driven Development 配置验证")
    print("=" * 60)
    print()
    
    checks = []
    
    # 检查 1: Agent 文件
    agent_file = Path(".lingma/agents/spec-driven-core-agent.md")
    checks.append(("Agent 文件", agent_file.exists(), str(agent_file)))
    
    # 检查 2: Skills 目录
    skills_dir = Path(".lingma/skills")
    skills_exists = skills_dir.exists()
    checks.append(("Skills 目录", skills_exists, str(skills_dir)))
    
    if skills_exists:
        # 检查 spec-driven-development skill
        spec_skill = skills_dir / "spec-driven-development" / "SKILL.md"
        checks.append(("  └─ spec-driven-development Skill", 
                      spec_skill.exists(), str(spec_skill)))
    
    # 检查 3: Rules 目录
    rules_dir = Path(".lingma/rules")
    rules_exists = rules_dir.exists()
    checks.append(("Rules 目录", rules_exists, str(rules_dir)))
    
    if rules_exists:
        # 检查关键 rules
        session_rule = rules_dir / "spec-session-start.md"
        checks.append(("  └─ spec-session-start Rule", 
                      session_rule.exists(), str(session_rule)))
        
        automation_rule = rules_dir / "automation-policy.md"
        checks.append(("  └─ automation-policy Rule", 
                      automation_rule.exists(), str(automation_rule)))
    
    # 检查 4: Specs 目录
    specs_dir = Path(".lingma/specs")
    specs_exists = specs_dir.exists()
    checks.append(("Specs 目录", specs_exists, str(specs_dir)))
    
    if specs_exists:
        # 检查当前 spec
        current_spec = specs_dir / "current-spec.md"
        checks.append(("  └─ current-spec.md", 
                      current_spec.exists(), str(current_spec)))
        
        # 检查历史目录
        history_dir = specs_dir / "spec-history"
        checks.append(("  └─ spec-history 目录", 
                      history_dir.exists(), str(history_dir)))
    
    # 检查 5: 配置文件
    config_dir = Path(".lingma/config")
    if config_dir.exists():
        automation_config = config_dir / "automation.json"
        checks.append(("自动化配置", 
                      automation_config.exists(), str(automation_config)))
    
    # 输出结果
    print("检查结果:")
    print()
    
    passed = 0
    failed = 0
    
    for name, result, path in checks:
        status = "✅" if result else "❌"
        indent = "  " if name.startswith("  ") else ""
        print(f"{indent}{status} {name}")
        if not result:
            print(f"{indent}   路径: {path}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print("-" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print()
    
    if failed == 0:
        print("✅ 所有检查通过！系统配置正确。")
        print()
        print("下一步:")
        print("  1. 在 IDE 中打开项目")
        print("  2. 确保通义灵码插件已更新到最新版本")
        print("  3. 开始使用: '使用 spec-driven-core-agent 检查状态'")
        return True
    else:
        print(f"❌ {failed} 个检查失败，请修复后重试。")
        print()
        print("建议操作:")
        print("  1. 运行初始化脚本: bash .lingma/skills/spec-driven-development/scripts/init-spec.sh")
        print("  2. 检查文件路径是否正确")
        print("  3. 查看 INSTALLATION_GUIDE.md 获取帮助")
        return False


if __name__ == "__main__":
    import sys
    success = verify_setup()
    sys.exit(0 if success else 1)
