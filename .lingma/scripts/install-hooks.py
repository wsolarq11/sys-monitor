#!/usr/bin/env python3
"""
Git Hook安装脚本 - 自动部署Spec强制验证Hook

功能:
1. 复制pre-commit.sh到.git/hooks/pre-commit
2. 设置执行权限
3. 验证安装成功
4. 提供使用说明

使用方式:
    python install-hooks.py
    python install-hooks.py --uninstall  # 卸载
"""

import os
import sys
import stat
import shutil
from pathlib import Path


def find_project_root() -> str:
    """查找项目根目录(包含.git的目录)"""
    current_dir = os.getcwd()
    
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, '.git')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    raise FileNotFoundError("未找到Git仓库，请在项目根目录运行此脚本")


def install_hooks():
    """安装Git Hooks"""
    project_root = find_project_root()
    
    hooks_source_dir = os.path.join(project_root, '.lingma', 'hooks')
    hooks_target_dir = os.path.join(project_root, '.git', 'hooks')
    
    # 确保目标目录存在
    os.makedirs(hooks_target_dir, exist_ok=True)
    
    print("=" * 60)
    print("Git Hook 安装程序")
    print("=" * 60)
    print(f"项目根目录: {project_root}")
    print(f"Hook源目录: {hooks_source_dir}")
    print(f"Hook目标目录: {hooks_target_dir}")
    print("=" * 60)
    print()
    
    # 安装pre-commit hook
    pre_commit_source = os.path.join(hooks_source_dir, 'pre-commit.sh')
    pre_commit_target = os.path.join(hooks_target_dir, 'pre-commit')
    
    if not os.path.exists(pre_commit_source):
        print(f"❌ 错误: 找不到Hook源文件: {pre_commit_source}")
        sys.exit(1)
    
    print("📦 安装 pre-commit hook...")
    
    # 复制文件
    shutil.copy2(pre_commit_source, pre_commit_target)
    
    # 设置执行权限 (Unix/Linux/Mac)
    if os.name != 'nt':  # 非Windows系统
        current_permissions = os.stat(pre_commit_target).st_mode
        os.chmod(pre_commit_target, current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        print("   ✅ 已设置执行权限")
    else:
        # Windows系统不需要chmod，但需要确保文件编码正确
        print("   ℹ️  Windows系统跳过权限设置")
    
    # 验证安装
    if os.path.exists(pre_commit_target):
        print(f"   ✅ Hook已安装: {pre_commit_target}")
        
        # 检查文件大小
        file_size = os.path.getsize(pre_commit_target)
        print(f"   📄 文件大小: {file_size} bytes")
    else:
        print(f"   ❌ Hook安装失败")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Git Hook 安装成功!")
    print("=" * 60)
    print()
    print("📖 使用说明:")
    print("  • 每次commit时会自动执行Spec验证")
    print("  • 如果验证失败，提交将被阻止")
    print("  • 紧急情况可使用 --no-verify 跳过验证:")
    print("    git commit --no-verify -m \"your message\"")
    print()
    print("🧪 测试安装:")
    print("  1. 修改任意文件")
    print("  2. git add .")
    print("  3. git commit -m \"test\"")
    print("  4. 观察Spec验证输出")
    print()
    print("🔧 卸载Hook:")
    print("  python install-hooks.py --uninstall")
    print()


def uninstall_hooks():
    """卸载Git Hooks"""
    project_root = find_project_root()
    hooks_target_dir = os.path.join(project_root, '.git', 'hooks')
    
    print("=" * 60)
    print("Git Hook 卸载程序")
    print("=" * 60)
    print()
    
    pre_commit_target = os.path.join(hooks_target_dir, 'pre-commit')
    
    if os.path.exists(pre_commit_target):
        print("🗑️  删除 pre-commit hook...")
        os.remove(pre_commit_target)
        print("   ✅ Hook已卸载")
    else:
        print("   ℹ️  Hook不存在，无需卸载")
    
    print()
    print("✅ Git Hook 卸载完成")
    print()


def verify_installation():
    """验证Hook安装状态"""
    project_root = find_project_root()
    pre_commit_target = os.path.join(project_root, '.git', 'hooks', 'pre-commit')
    
    print("=" * 60)
    print("Git Hook 安装状态检查")
    print("=" * 60)
    print()
    
    if os.path.exists(pre_commit_target):
        print("✅ pre-commit hook 已安装")
        print(f"   路径: {pre_commit_target}")
        print(f"   大小: {os.path.getsize(pre_commit_target)} bytes")
        
        # 检查执行权限
        if os.access(pre_commit_target, os.X_OK):
            print("   ✅ 具有执行权限")
        else:
            print("   ⚠️  缺少执行权限")
        
        print()
        sys.exit(0)  # 成功
    else:
        print("❌ pre-commit hook 未安装")
        print()
        print("   运行以下命令安装:")
        print("   python install-hooks.py")
        print()
        sys.exit(1)  # 失败


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Git Hook安装/卸载工具')
    parser.add_argument('--uninstall', action='store_true', help='卸载Hooks')
    parser.add_argument('--verify', action='store_true', help='验证安装状态')
    
    args = parser.parse_args()
    
    try:
        if args.uninstall:
            uninstall_hooks()
        elif args.verify:
            verify_installation()
        else:
            install_hooks()
    
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
