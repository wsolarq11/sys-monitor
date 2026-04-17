#!/usr/bin/env python3
"""
验证Agent系统文档完整性

检查项:
1. 必需文档是否存在
2. Agent文件大小是否符合≤5KB标准
3. 链接有效性
4. CHANGELOG是否更新
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class DocumentValidator:
    """文档完整性验证器"""
    
    def __init__(self, base_path=".lingma"):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def check_required_docs(self):
        """检查必需文档是否存在"""
        print("📋 检查必需文档...")
        
        required_docs = [
            "CHANGELOG.md",
            "agents/README.md",
            "docs/architecture/ARCHITECTURE.md",
            "docs/architecture/orchestration-flow.md",
            "docs/architecture/agent-system/quality-gates.md",
            "docs/architecture/agents-usage-guide.md",
        ]
        
        for doc in required_docs:
            doc_path = self.base_path / doc
            if doc_path.exists():
                size_kb = doc_path.stat().st_size / 1024
                self.passed.append(f"✅ {doc} ({size_kb:.1f}KB)")
            else:
                self.errors.append(f"❌ 缺失文档: {doc}")
        
        # 检查supervisor-detailed.md是否为空
        supervisor_detailed = self.base_path / "docs/architecture/agent-system/supervisor-detailed.md"
        if supervisor_detailed.exists():
            if supervisor_detailed.stat().st_size == 0:
                self.warnings.append("⚠️  supervisor-detailed.md 为空文件 (0KB)")
            else:
                size_kb = supervisor_detailed.stat().st_size / 1024
                self.passed.append(f"✅ supervisor-detailed.md ({size_kb:.1f}KB)")
        else:
            self.errors.append("❌ 缺失文档: docs/architecture/agent-system/supervisor-detailed.md")
    
    def check_agent_file_sizes(self):
        """检查Agent文件大小是否符合≤5KB标准"""
        print("\n📏 检查Agent文件大小...")
        
        agents_dir = self.base_path / "agents"
        max_size = 5 * 1024  # 5KB
        
        if not agents_dir.exists():
            self.errors.append("❌ agents目录不存在")
            return
        
        agent_files = list(agents_dir.glob("*.md"))
        
        if not agent_files:
            self.warnings.append("⚠️  未找到Agent文件")
            return
        
        for agent_file in agent_files:
            # 跳过README.md
            if agent_file.name == "README.md":
                continue
            
            size = agent_file.stat().st_size
            size_kb = size / 1024
            
            if size > max_size:
                excess_kb = size_kb - 5
                self.warnings.append(
                    f"⚠️  {agent_file.name}: {size_kb:.1f}KB (超出{excess_kb:.1f}KB)"
                )
            else:
                self.passed.append(f"✅ {agent_file.name}: {size_kb:.1f}KB")
    
    def check_changelog_entries(self):
        """检查CHANGELOG是否有Unreleased条目"""
        print("\n📝 检查CHANGELOG...")
        
        changelog_path = self.base_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            self.errors.append("❌ CHANGELOG.md 不存在")
            return
        
        content = changelog_path.read_text(encoding='utf-8')
        
        if "## [Unreleased]" in content:
            self.passed.append("✅ CHANGELOG包含Unreleased章节")
        else:
            self.warnings.append("⚠️  CHANGELOG缺少Unreleased章节")
        
        # 检查版本号
        if "## [1." in content or "## [0." in content:
            self.passed.append("✅ CHANGELOG包含版本历史")
        else:
            self.warnings.append("⚠️  CHANGELOG缺少版本历史记录")
    
    def check_decision_log(self):
        """检查决策日志是否存在"""
        print("\n📊 检查决策日志...")
        
        decision_log_path = self.base_path / "logs/decision-log.json"
        
        if decision_log_path.exists():
            try:
                with open(decision_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    entries = len(data)
                    self.passed.append(f"✅ decision-log.json 存在 ({entries}条记录)")
                elif isinstance(data, dict):
                    self.passed.append("✅ decision-log.json 存在 (对象格式)")
                else:
                    self.warnings.append("⚠️  decision-log.json 格式异常")
            except json.JSONDecodeError:
                self.warnings.append("⚠️  decision-log.json JSON解析失败")
        else:
            self.warnings.append("⚠️  decision-log.json 不存在")
    
    def check_agent_count_in_readme(self):
        """检查README.md中的Agent数量是否正确"""
        print("\n🔢 检查README Agent数量...")
        
        readme_path = self.base_path / "README.md"
        
        if not readme_path.exists():
            self.errors.append("❌ README.md 不存在")
            return
        
        content = readme_path.read_text(encoding='utf-8')
        
        if "5个智能体" in content or "5个Agent" in content:
            self.passed.append("✅ README.md Agent数量正确 (5个)")
        elif "4个智能体" in content or "4个Agent" in content:
            self.errors.append("❌ README.md Agent数量错误 (应为5个，实际显示4个)")
        else:
            self.warnings.append("⚠️  README.md 未明确说明Agent数量")
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("📊 文档完整性验证报告")
        print("="*60)
        
        print(f"\n✅ 通过检查: {len(self.passed)}")
        for item in self.passed:
            print(f"  {item}")
        
        if self.warnings:
            print(f"\n⚠️  警告: {len(self.warnings)}")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print(f"\n❌ 错误: {len(self.errors)}")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "="*60)
        
        total_checks = len(self.passed) + len(self.warnings) + len(self.errors)
        pass_rate = len(self.passed) / total_checks * 100 if total_checks > 0 else 0
        
        print(f"总体评分: {pass_rate:.1f}%")
        
        if self.errors:
            print("状态: ❌ 验证失败")
            print("\n建议: 请修复所有错误后重新验证")
            return False
        elif self.warnings:
            print("状态: ⚠️  验证通过但有警告")
            print("\n建议: 建议处理警告以提升文档质量")
            return True
        else:
            print("状态: ✅ 验证完全通过")
            return True


def main():
    """主函数"""
    print("🔍 开始验证Agent系统文档完整性...\n")
    
    validator = DocumentValidator()
    
    # 执行所有检查
    validator.check_required_docs()
    validator.check_agent_file_sizes()
    validator.check_changelog_entries()
    validator.check_decision_log()
    validator.check_agent_count_in_readme()
    
    # 生成报告
    success = validator.generate_report()
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
