#!/usr/bin/env python3
"""
根目录清洁度检查工具

功能：
1. 检查根目录是否有未授权的文件
2. 检测常见的临时文件
3. 生成清洁度报告
4. 提供清理建议

使用方法：
    python check_root_cleanliness.py
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple


class RootCleanlinessChecker:
    """根目录清洁度检查器"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.allowed_files = {
            'README.md',
            'LICENSE',
            '.gitignore',
            '.gitattributes',
            'sys-monitor打开GitHub仓库.url',  # 项目特定
        }
        self.allowed_dirs = {
            '.git',
            '.github',
            '.lingma',
            'sys-monitor',  # 项目特定
        }
        self.forbidden_patterns = [
            r'^\$null$',
            r'^null$',
            r'^\.DS_Store$',
            r'^Thumbs\.db$',
            r'^desktop\.ini$',
            r'^.*\.log$',
            r'^.*\.tmp$',
            r'^.*\.temp$',
            r'^.*\.bak$',
        ]
    
    def check(self) -> Tuple[int, List[str]]:
        """
        检查根目录清洁度
        
        Returns:
            (score, violations) - 分数(0-10)和违规列表
        """
        violations = []
        score = 10
        
        for item in self.root_dir.iterdir():
            name = item.name
            
            # 跳过允许的文件和目录
            if name in self.allowed_files or name in self.allowed_dirs:
                continue
            
            # 检查是否是隐藏目录（以 . 开头）
            if item.is_dir() and name.startswith('.'):
                continue
            
            # 检查是否是被允许的隐藏文件
            if name.startswith('.') and name not in self.allowed_files:
                # 检查是否在 forbidden_patterns 中
                if self._matches_forbidden(name):
                    violations.append(f"❌ {name} (临时文件)")
                    score -= 1
                else:
                    violations.append(f"⚠️  {name} (未授权的隐藏文件)")
                    score -= 0.5
                continue
            
            # 检查文件
            if item.is_file():
                if self._matches_forbidden(name):
                    violations.append(f"❌ {name} (临时文件)")
                    score -= 1
                else:
                    violations.append(f"⚠️  {name} (未授权的文件)")
                    score -= 1
            
            # 检查目录
            elif item.is_dir():
                violations.append(f"❌ {name}/ (未授权的目录)")
                score -= 2
        
        return max(0, score), violations
    
    def _matches_forbidden(self, filename: str) -> bool:
        """检查文件名是否匹配禁止模式"""
        for pattern in self.forbidden_patterns:
            if re.match(pattern, filename):
                return True
        return False
    
    def print_report(self):
        """打印检查报告"""
        score, violations = self.check()
        
        print("=" * 70)
        print("  根目录清洁度检查报告")
        print("=" * 70)
        print()
        print(f"工作区脏度: {score}/10")
        print()
        
        if violations:
            print("违规项:")
            for v in violations:
                print(f"  {v}")
            print()
            
            if score < 5:
                print("🚨 严重: 根目录非常混乱，请立即清理！")
            elif score < 8:
                print("⚠️  警告: 根目录有一些不需要的文件")
            else:
                print("ℹ️  提示: 根目录基本清洁，但有小问题")
        else:
            print("✅ 根目录完美清洁！")
        
        print()
        print("=" * 70)
        
        return score == 10


def main():
    root = Path(".")
    checker = RootCleanlinessChecker(root)
    is_clean = checker.print_report()
    
    sys.exit(0 if is_clean else 1)


if __name__ == "__main__":
    main()
