#!/usr/bin/env python3
"""
Spec触发器安装脚本

用途：
1. 自动安装Git Hooks到 .git/hooks/
2. 设置执行权限
3. 验证安装结果
4. 提供卸载功能

使用：
    python install-hooks.py          # 安装
    python install-hooks.py --uninstall  # 卸载
"""

import os
import sys
import shutil
from pathlib import Path


def get_repo_root() -> Path:
    """获取仓库根目录"""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except Exception as e:
        print(f"❌ 错误: 无法获取仓库根目录: {e}")
        sys.exit(1)


def install_hook(hook_name: str, hooks_source_dir: Path, git_hooks_dir: Path) -> bool:
    """
    安装单个Git Hook
    
    Args:
        hook_name: Hook名称（如 pre-commit, post-checkout）
        hooks_source_dir: 源文件目录
        git_hooks_dir: Git hooks目录
        
    Returns:
        是否成功
    """
    # 确定文件名（Windows不需要扩展名，但为了兼容性保留.sh）
    source_file = hooks_source_dir / f"{hook_name}.sh"
    target_file = git_hooks_dir / hook_name
    
    if not source_file.exists():
        print(f"⚠️  跳过: 源文件不存在 {source_file}")
        return False
    
    try:
        # 复制文件
        shutil.copy2(source_file, target_file)
        
        # 设置执行权限（Unix系统）
        if os.name != 'nt':  # 非Windows
            os.chmod(target_file, 0o755)
        
        print(f"✅ 已安装: {hook_name}")
        return True
        
    except Exception as e:
        print(f"❌ 安装失败 {hook_name}: {e}")
        return False


def uninstall_hook(hook_name: str, git_hooks_dir: Path) -> bool:
    """
    卸载单个Git Hook
    
    Args:
        hook_name: Hook名称
        git_hooks_dir: Git hooks目录
        
    Returns:
        是否成功
    """
    target_file = git_hooks_dir / hook_name
    
    if not target_file.exists():
        print(f"⚠️  跳过: Hook不存在 {target_file}")
        return True
    
    try:
        target_file.unlink()
        print(f"✅ 已卸载: {hook_name}")
        return True
    except Exception as e:
        print(f"❌ 卸载失败 {hook_name}: {e}")
        return False


def verify_installation(git_hooks_dir: Path) -> bool:
    """
    验证Hook安装
    
    Args:
        git_hooks_dir: Git hooks目录
        
    Returns:
        是否全部安装成功
    """
    required_hooks = ["pre-commit", "post-checkout"]
    all_installed = True
    
    print("\n🔍 验证安装:")
    for hook_name in required_hooks:
        hook_file = git_hooks_dir / hook_name
        if hook_file.exists():
            print(f"  ✅ {hook_name}")
        else:
            print(f"  ❌ {hook_name} (缺失)")
            all_installed = False
    
    return all_installed


def install_all(repo_root: Path):
    """安装所有Hooks"""
    hooks_source_dir = repo_root / ".lingma" / "hooks"
    git_hooks_dir = repo_root / ".git" / "hooks"
    
    # 检查源目录
    if not hooks_source_dir.exists():
        print(f"❌ 错误: Hooks源目录不存在: {hooks_source_dir}")
        sys.exit(1)
    
    # 创建.git/hooks目录（如果不存在）
    git_hooks_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔧 开始安装Git Hooks...\n")
    
    # 安装所有.sh文件
    installed_count = 0
    failed_count = 0
    
    for hook_file in hooks_source_dir.glob("*.sh"):
        hook_name = hook_file.stem  # 去掉 .sh 扩展名
        if install_hook(hook_name, hooks_source_dir, git_hooks_dir):
            installed_count += 1
        else:
            failed_count += 1
    
    # 验证安装
    all_ok = verify_installation(git_hooks_dir)
    
    print(f"\n📊 安装结果:")
    print(f"  成功: {installed_count}")
    print(f"  失败: {failed_count}")
    
    if all_ok and failed_count == 0:
        print("\n✅ 所有Hooks安装成功！")
        print("\n💡 提示:")
        print("  - pre-commit: 提交前强制验证Spec")
        print("  - post-checkout: 切换分支后检查Spec状态")
        print("  - 运行测试: git commit --allow-empty -m 'test'")
    else:
        print("\n⚠️  部分Hooks安装失败，请检查错误信息")
        sys.exit(1)


def uninstall_all(repo_root: Path):
    """卸载所有Hooks"""
    git_hooks_dir = repo_root / ".git" / "hooks"
    
    if not git_hooks_dir.exists():
        print("⚠️  Git hooks目录不存在")
        return
    
    print("🔧 开始卸载Git Hooks...\n")
    
    uninstalled_count = 0
    
    for hook_file in git_hooks_dir.glob("*"):
        if hook_file.is_file():
            # 检查是否是我们安装的hook
            hook_name = hook_file.name
            source_file = repo_root / ".lingma" / "hooks" / f"{hook_name}.sh"
            
            if source_file.exists():
                if uninstall_hook(hook_name, git_hooks_dir):
                    uninstalled_count += 1
    
    print(f"\n📊 卸载结果:")
    print(f"  已卸载: {uninstalled_count}")
    print("\n✅ Hooks卸载完成")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Spec触发器安装工具")
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="卸载Hooks"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认自动检测）"
    )
    
    args = parser.parse_args()
    
    repo_root = args.repo_root or get_repo_root()
    
    if args.uninstall:
        uninstall_all(repo_root)
    else:
        install_all(repo_root)


if __name__ == "__main__":
    main()
