#!/usr/bin/env python3
"""
文档完整性快速修复脚本
自动修复常见的文档问题
"""
import os
import re
import shutil
from pathlib import Path

def fix_reports_paths():
    """修复reports目录中的路径引用错误"""
    print("=" * 80)
    print("修复 reports/ 目录中的路径错误...")
    print("=" * 80)
    
    reports_dir = '.lingma/reports'
    if not os.path.exists(reports_dir):
        print(f"❌ 目录不存在: {reports_dir}")
        return
    
    fixed_count = 0
    for root, dirs, files in os.walk(reports_dir):
        # 跳过archive子目录
        if 'archive' in root:
            continue
            
        for file in files:
            if not file.endswith('.md'):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                content = original_content
                
                # 修复 .lingma/ 前缀
                # 例如: ](.lingma/docs/...) 应该改为 ](../docs/...)
                content = re.sub(r'\]\(\.lingma/', '](', content)
                
                # 修复其他常见错误模式
                # ](.lingma/rules/...) -> ](../rules/...)
                # 已经在上面的替换中处理
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    print(f"  ✅ 修复: {filepath}")
                    
            except Exception as e:
                print(f"  ❌ 处理失败 {filepath}: {e}")
    
    print(f"\n✅ 共修复 {fixed_count} 个文件\n")

def remove_empty_files():
    """删除空文件或仅含空白字符的文件"""
    print("=" * 80)
    print("清理空文件...")
    print("=" * 80)
    
    empty_files = [
        '.lingma/docs/reports/ARCHITECTURE-FIX-PLAN.md',
        '.lingma/docs/architecture/agent-system/supervisor-detailed.md',
    ]
    
    removed_count = 0
    for filepath in empty_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size == 0 or size < 10:  # 小于10字节视为空
                try:
                    os.remove(filepath)
                    print(f"  ✅ 删除: {filepath} ({size} bytes)")
                    removed_count += 1
                except Exception as e:
                    print(f"  ❌ 删除失败 {filepath}: {e}")
            else:
                print(f"  ⚠️  跳过非空文件: {filepath} ({size} bytes)")
        else:
            print(f"  ℹ️  文件不存在: {filepath}")
    
    print(f"\n✅ 共删除 {removed_count} 个空文件\n")

def suggest_backup_cleanup():
    """建议清理backups目录"""
    print("=" * 80)
    print("Backups目录清理建议")
    print("=" * 80)
    
    backups_dir = '.lingma/backups'
    if not os.path.exists(backups_dir):
        print("ℹ️  Backups目录不存在")
        return
    
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(backups_dir):
        for file in files:
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            total_size += size
            file_count += 1
    
    print(f"\n📊 统计:")
    print(f"   文件数: {file_count}")
    print(f"   总大小: {total_size / 1024:.2f} KB")
    print(f"\n💡 建议:")
    print(f"   1. Git已经提供版本控制，无需手动备份")
    print(f"   2. 如需保留历史版本，使用Git tag或branch")
    print(f"   3. 可以安全删除整个backups目录")
    print(f"\n🔧 执行删除命令:")
    print(f"   rm -rf .lingma/backups/")
    print()

def check_duplicate_docs():
    """检查可能的重复文档"""
    print("=" * 80)
    print("重复文档检测")
    print("=" * 80)
    
    duplicates = [
        {
            'files': [
                '.lingma/docs/spec-trigger-hard-constraint.md',
                '.lingma/docs/guides/spec-trigger-hard-constraint.md'
            ],
            'recommendation': '保留guides版本，删除根目录版本'
        },
        {
            'files': [
                '.lingma/docs/QUICKSTART.md',
                '.lingma/docs/guides/QUICK_START.md'
            ],
            'recommendation': '保留guides版本，删除根目录版本'
        }
    ]
    
    for i, dup_group in enumerate(duplicates, 1):
        print(f"\n{i}. 可能的重复组:")
        for filepath in dup_group['files']:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath) / 1024
                print(f"   - {filepath} ({size:.2f} KB)")
            else:
                print(f"   - {filepath} (不存在)")
        print(f"   💡 建议: {dup_group['recommendation']}")
    
    print()

def generate_missing_docs_list():
    """生成缺失文档清单"""
    print("=" * 80)
    print("缺失文档清单（需要手动创建）")
    print("=" * 80)
    
    missing_docs = [
        ('Agent详细文档', [
            '.lingma/docs/architecture/agent-system/code-review-agent-detailed.md',
            '.lingma/docs/architecture/agent-system/documentation-agent-detailed.md',
            '.lingma/docs/architecture/agent-system/spec-driven-core-agent-detailed.md',
            '.lingma/docs/architecture/agent-system/test-runner-agent-detailed.md',
        ]),
        ('Supervisor相关', [
            '.lingma/docs/architecture/agent-system/decision-log-format.md',
            '.lingma/docs/architecture/agent-system/orchestration-patterns.md',
        ]),
        ('Rules/Skills详细文档', [
            '.lingma/docs/architecture/automation-policy-detailed.md',
            '.lingma/docs/skills/spec-driven-development-detailed.md',
        ]),
        ('Specs模板', [
            '.lingma/specs/spec-template.md',
            '.lingma/specs/constitution.md',
        ]),
    ]
    
    for category, docs in missing_docs:
        print(f"\n{category}:")
        for doc in docs:
            exists = "✅" if os.path.exists(doc) else "❌"
            print(f"   {exists} {doc}")
    
    print()

def main():
    print("\n" + "=" * 80)
    print("文档完整性快速修复工具")
    print("=" * 80 + "\n")
    
    # 切换到项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')  # 从.lingma/scripts/到项目根
    
    print("开始执行修复...\n")
    
    # 1. 修复路径错误
    fix_reports_paths()
    
    # 2. 删除空文件
    remove_empty_files()
    
    # 3. 检查重复
    check_duplicate_docs()
    
    # 4. 生成缺失清单
    generate_missing_docs_list()
    
    # 5. Backups清理建议
    suggest_backup_cleanup()
    
    print("=" * 80)
    print("✅ 自动修复完成！")
    print("=" * 80)
    print("\n📋 下一步:")
    print("1. 查看上述缺失文档清单，手动创建必要文件")
    print("2. 根据建议清理backups目录")
    print("3. 运行 check_doc_integrity.py 验证修复效果")
    print("4. 提交更改到Git")
    print()

if __name__ == '__main__':
    main()

