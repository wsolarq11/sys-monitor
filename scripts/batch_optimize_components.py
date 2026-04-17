#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量精简 .lingma 组件工具
一次性处理所有臃肿的 Agent/Rule/Skill 文件
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

# 确保 stdout 使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class ComponentOptimizer:
    def __init__(self):
        self.lingma_dir = Path('.lingma')
        self.optimized = []
        self.skipped = []
        self.errors = []
    
    def scan_all(self) -> dict:
        """全盘扫描所有组件"""
        result = {
            'agents': [],
            'rules': [],
            'skills': []
        }
        
        # 扫描 Agents
        agents_dir = self.lingma_dir / 'agents'
        if agents_dir.exists():
            for f in sorted(agents_dir.glob('*.md')):
                size_kb = os.path.getsize(f) / 1024
                lines = len(f.read_text(encoding='utf-8').splitlines())
                result['agents'].append({
                    'file': f,
                    'size_kb': size_kb,
                    'lines': lines,
                    'needs_optimize': size_kb > 5
                })
        
        # 扫描 Rules
        rules_dir = self.lingma_dir / 'rules'
        if rules_dir.exists():
            for f in sorted(rules_dir.glob('*.md')):
                size_kb = os.path.getsize(f) / 1024
                lines = len(f.read_text(encoding='utf-8').splitlines())
                result['rules'].append({
                    'file': f,
                    'size_kb': size_kb,
                    'lines': lines,
                    'needs_optimize': size_kb > 3
                })
        
        # 扫描 Skills
        skills_dir = self.lingma_dir / 'skills'
        if skills_dir.exists():
            for sf in skills_dir.iterdir():
                if sf.is_dir() and (sf/'SKILL.md').exists():
                    skill_file = sf/'SKILL.md'
                    size_kb = os.path.getsize(skill_file) / 1024
                    result['skills'].append({
                        'file': skill_file,
                        'size_kb': size_kb,
                        'needs_optimize': size_kb > 10
                    })
        
        return result
    
    def print_scan_result(self, scan_result: dict):
        """打印扫描结果"""
        print("="*70)
        print("📊 全盘扫描结果")
        print("="*70)
        
        total_issues = 0
        
        print("\n📦 AGENTS (目标: ≤5KB):")
        for agent in scan_result['agents']:
            status = '❌' if agent['needs_optimize'] else '✅'
            print(f"  {status} {agent['file'].name}: {agent['size_kb']:.1f}KB, {agent['lines']}行")
            if agent['needs_optimize']:
                total_issues += 1
        
        print("\n📋 RULES (目标: ≤3KB):")
        for rule in scan_result['rules']:
            status = '❌' if rule['needs_optimize'] else '✅'
            print(f"  {status} {rule['file'].name}: {rule['size_kb']:.1f}KB, {rule['lines']}行")
            if rule['needs_optimize']:
                total_issues += 1
        
        print("\n🛠️  SKILLS (目标: ≤10KB):")
        for skill in scan_result['skills']:
            status = '❌' if skill['needs_optimize'] else '✅'
            print(f"  {status} {skill['file'].parent.name}/SKILL.md: {skill['size_kb']:.1f}KB")
            if skill['needs_optimize']:
                total_issues += 1
        
        print("\n" + "="*70)
        print(f"总计: {total_issues} 个组件需要优化")
        print("="*70)
        
        return total_issues
    
    def create_shared_docs(self):
        """创建共享文档目录和文件"""
        print("\n📝 创建共享文档结构...")
        
        docs_structure = {
            'docs/architecture/agent-system': [
                'orchestration-patterns.md',
                'quality-gates.md',
                'decision-log-format.md'
            ],
            'docs/architecture/rules-system': [
                'session-management.md',
                'memory-guidelines.md'
            ],
            'docs/architecture/skills-system': [
                'spec-workflow-details.md'
            ]
        }
        
        for dir_path, files in docs_structure.items():
            dir_full = Path(dir_path)
            dir_full.mkdir(parents=True, exist_ok=True)
            
            for filename in files:
                file_path = dir_full / filename
                if not file_path.exists():
                    file_path.write_text(f"# {filename.replace('.md', '').replace('-', ' ').title()}\n\n详细内容待补充...\n", encoding='utf-8')
                    print(f"  ✅ 创建: {file_path}")
        
        print("  ✅ 共享文档结构创建完成")
    
    def generate_optimization_report(self, scan_result: dict):
        """生成优化报告"""
        report = []
        report.append("# 组件优化报告\n")
        report.append(f"**生成时间**: {Path.cwd()}\n")
        
        report.append("## 需要优化的组件\n")
        
        for category in ['agents', 'rules', 'skills']:
            items = [x for x in scan_result[category] if x['needs_optimize']]
            if items:
                report.append(f"\n### {category.upper()}\n")
                for item in items:
                    report.append(f"- {item['file'].name}: {item['size_kb']:.1f}KB")
        
        report_path = Path('.lingma/docs/OPTIMIZATION_REPORT.md')
        report_path.write_text('\n'.join(report), encoding='utf-8')
        print(f"\n📄 优化报告已生成: {report_path}")


def main():
    optimizer = ComponentOptimizer()
    
    # 1. 全盘扫描
    print("🔍 开始全盘扫描...\n")
    scan_result = optimizer.scan_all()
    
    # 2. 打印结果
    total_issues = optimizer.print_scan_result(scan_result)
    
    if total_issues == 0:
        print("\n✅ 所有组件符合规范，无需优化！")
        return
    
    # 3. 创建共享文档
    optimizer.create_shared_docs()
    
    # 4. 生成优化报告
    optimizer.generate_optimization_report(scan_result)
    
    # 5. 给出建议
    print("\n" + "="*70)
    print("💡 下一步建议:")
    print("="*70)
    print("1. 查看优化报告: .lingma/docs/OPTIMIZATION_REPORT.md")
    print("2. 手动精简每个组件（参考 SYSTEM_OPTIMIZATION_PLAN.md）")
    print("3. 或者等待自动化精简工具开发完成")
    print("="*70)


if __name__ == '__main__':
    main()
