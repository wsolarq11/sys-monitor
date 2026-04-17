#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自迭代流系统有效性验证工具
验证 Rules/Skills/Agents 是否正确配置并能跨会话生效
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict

# 确保 stdout 使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SystemVerifier:
    def __init__(self, lingma_dir: str = '.lingma'):
        self.lingma_dir = Path(lingma_dir)
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def verify_all(self) -> bool:
        """执行所有验证"""
        print("🔍 开始验证自迭代流系统...\n")
        
        self.verify_rules()
        self.verify_skills()
        self.verify_agents()
        self.verify_doc_structure()
        
        self.print_summary()
        
        return len(self.issues) == 0
    
    def verify_rules(self):
        """验证 Rules 配置"""
        print("1️⃣ 验证 Rules...")
        
        rules_dir = self.lingma_dir / 'rules'
        if not rules_dir.exists():
            self.issues.append("❌ .lingma/rules/ 目录不存在")
            return
        
        # 检查必需的 Rules
        required_rules = {
            'AGENTS.md': 'trigger: always_on',
            'spec-session-start.md': None,
            'automation-policy.md': None,
            'memory-usage.md': None,
        }
        
        for rule_file, required_content in required_rules.items():
            rule_path = rules_dir / rule_file
            if not rule_path.exists():
                self.issues.append(f"❌ 缺少必需 Rule: {rule_file}")
                continue
            
            content = rule_path.read_text(encoding='utf-8')
            
            # 检查必需内容
            if required_content and required_content not in content:
                self.issues.append(f"❌ {rule_file} 缺少 '{required_content}'")
            else:
                self.passed.append(f"✅ {rule_file}")
        
        # 检查是否有过多 Rules（可能导致上下文溢出）
        rule_count = len(list(rules_dir.glob('*.md')))
        if rule_count > 10:
            self.warnings.append(f"⚠️ Rules 数量过多 ({rule_count})，可能影响性能")
        
        print(f"   找到 {rule_count} 个 Rules\n")
    
    def verify_skills(self):
        """验证 Skills 配置"""
        print("2️⃣ 验证 Skills...")
        
        skills_dir = self.lingma_dir / 'skills'
        if not skills_dir.exists():
            self.issues.append("❌ .lingma/skills/ 目录不存在")
            return
        
        skill_count = 0
        for skill_folder in skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue
            
            skill_count += 1
            skill_md = skill_folder / 'SKILL.md'
            
            if not skill_md.exists():
                self.issues.append(f"❌ {skill_folder.name}/ 缺少 SKILL.md")
                continue
            
            content = skill_md.read_text(encoding='utf-8')
            
            # 检查是否有 description
            has_description = (
                'description:' in content or
                '## 描述' in content or
                '## Description' in content
            )
            
            if not has_description:
                self.warnings.append(f"⚠️ {skill_folder.name}/SKILL.md 可能缺少 description")
            else:
                self.passed.append(f"✅ {skill_folder.name}/SKILL.md")
        
        print(f"   找到 {skill_count} 个 Skills\n")
    
    def verify_agents(self):
        """验证 Agents 配置"""
        print("3️⃣ 验证 Agents...")
        
        agents_dir = self.lingma_dir / 'agents'
        if not agents_dir.exists():
            self.issues.append("❌ .lingma/agents/ 目录不存在")
            return
        
        required_fields = ['name:', 'description:', 'tools:']
        agent_count = 0
        
        for agent_file in agents_dir.glob('*.md'):
            agent_count += 1
            content = agent_file.read_text(encoding='utf-8')
            
            # 检查文件大小（防止臃肿）
            file_size_kb = len(content.encode('utf-8')) / 1024
            if file_size_kb > 5:
                self.warnings.append(f"⚠️ {agent_file.name} 过大 ({file_size_kb:.1f}KB > 5KB)，建议精简")
            
            # 检查是否有 frontmatter
            if not content.startswith('---'):
                self.issues.append(f"❌ {agent_file.name}: 缺少 frontmatter (---)")
                continue
            
            # 提取 frontmatter
            match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                self.issues.append(f"❌ {agent_file.name}: frontmatter 格式错误")
                continue
            
            frontmatter = match.group(1)
            
            # 检查必需字段
            missing_fields = []
            for field in required_fields:
                if field not in frontmatter:
                    missing_fields.append(field)
            
            if missing_fields:
                self.issues.append(
                    f"❌ {agent_file.name}: 缺少字段 {', '.join(missing_fields)}"
                )
            else:
                self.passed.append(f"✅ {agent_file.name}")
        
        print(f"   找到 {agent_count} 个 Agents\n")
    
    def verify_doc_structure(self):
        """验证文档结构（单一入口原则）"""
        print("4️⃣ 验证文档结构...")
        
        # 检查根目录是否有冗余入口文档
        allowed_root_docs = {'README.md'}
        forbidden_patterns = [
            'QUICK_START',
            'GUIDE',
            'ARCHITECTURE',
            'SYSTEM_',
            'INTRO',
            'OVERVIEW'
        ]
        
        for md_file in self.lingma_dir.glob('*.md'):
            if md_file.name not in allowed_root_docs:
                for pattern in forbidden_patterns:
                    if md_file.name.upper().startswith(pattern):
                        self.issues.append(
                            f"❌ {md_file.name} 应移至 docs/ 子目录"
                        )
                        break
        
        # 检查功能目录是否有 README
        functional_dirs = ['agents', 'rules', 'skills', 'mcp-templates']
        for dir_name in functional_dirs:
            readme_path = self.lingma_dir / dir_name / 'README.md'
            if readme_path.exists():
                self.issues.append(
                    f"❌ {dir_name}/README.md - 功能目录禁止放置 README"
                )
        
        if not any('文档结构' in issue for issue in self.issues):
            self.passed.append("✅ 文档结构符合单一入口原则")
        
        print("   检查完成\n")
    
    def print_summary(self):
        """打印验证摘要"""
        print("=" * 60)
        print("📊 验证结果摘要")
        print("=" * 60)
        
        if self.passed:
            print(f"\n✅ 通过 ({len(self.passed)}):")
            for item in self.passed[:10]:  # 最多显示10个
                print(f"   {item}")
            if len(self.passed) > 10:
                print(f"   ... 还有 {len(self.passed) - 10} 项")
        
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.issues:
            print(f"\n❌ 问题 ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   {issue}")
        
        print("\n" + "=" * 60)
        
        if self.issues:
            print(f"❌ 验证失败: {len(self.issues)} 个问题需要修复")
            print("\n💡 修复建议:")
            print("   - Rules 问题: 检查 trigger 字段和文件格式")
            print("   - Skills 问题: 添加清晰的 description")
            print("   - Agents 问题: 补充完整的 frontmatter")
            print("   - 文档问题: 遵循单一入口原则")
        else:
            print("✅ 验证通过！系统已准备就绪")
            print("\n📋 下一步:")
            print("   1. 打开 Lingma IDE")
            print("   2. 开始新会话")
            print("   3. 观察 Rules 是否自动触发")
            print("   4. 测试 Skills 是否按需加载")
            print("   5. 验证 Agents 是否能被正确委派")
        
        print("=" * 60)


def main():
    verifier = SystemVerifier()
    success = verifier.verify_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
