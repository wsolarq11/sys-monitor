#!/usr/bin/env python3
"""
文档完整性检查脚本
检查所有Markdown文件中的链接是否有效
"""

import os
import re
from pathlib import Path


def find_markdown_files(root_dir):
    """查找所有Markdown文件"""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        # 跳过archive目录
        if "archive" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    return md_files


def extract_links(content):
    """提取Markdown链接 [text](path)"""
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    matches = re.findall(pattern, content)
    return matches


def check_link_exists(base_dir, link_path):
    """检查链接文件是否存在"""
    # 忽略外部链接
    if link_path.startswith("http://") or link_path.startswith("https://"):
        return True, "外部链接"

    # 忽略锚点链接
    if link_path.startswith("#"):
        return True, "锚点链接"

    # 解析相对路径
    full_path = os.path.normpath(os.path.join(base_dir, link_path))

    if os.path.exists(full_path):
        return True, "存在"
    else:
        return False, f"缺失: {full_path}"


def main():
    root_dir = ".lingma"
    print("=" * 100)
    print("文档完整性检查报告")
    print("=" * 100)
    print()

    md_files = find_markdown_files(root_dir)
    print(f"找到 {len(md_files)} 个Markdown文件（排除archive）\n")

    broken_links = []
    large_files = []

    for md_file in sorted(md_files):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查文件大小
            file_size_kb = os.path.getsize(md_file) / 1024
            if file_size_kb > 10:  # 超过10KB的文件
                large_files.append((md_file, file_size_kb))

            # 提取并检查链接
            links = extract_links(content)
            base_dir = os.path.dirname(md_file)

            for text, path in links:
                exists, status = check_link_exists(base_dir, path)
                if (
                    not exists
                    and not path.startswith("http")
                    and not path.startswith("#")
                ):
                    broken_links.append(
                        {
                            "file": md_file,
                            "link_text": text,
                            "link_path": path,
                            "status": status,
                        }
                    )
        except Exception as e:
            print(f"处理文件 {md_file} 时出错: {e}")

    # 输出结果
    print("=" * 100)
    print("❌ 缺失的文档链接")
    print("=" * 100)
    if broken_links:
        for i, link in enumerate(broken_links, 1):
            print(f"\n{i}. 文件: {link['file']}")
            print(f"   链接文本: {link['link_text']}")
            print(f"   链接路径: {link['link_path']}")
            print(f"   状态: {link['status']}")
    else:
        print("\n✅ 未发现缺失的内部链接")

    print("\n" + "=" * 100)
    print("⚠️  大型文档文件（需要优化）")
    print("=" * 100)
    if large_files:
        print(f"\n{'文件路径':<80} {'大小(KB)':>10}")
        print("-" * 95)
        for path, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            rel_path = path.replace(".lingma/", "")
            print(f"{rel_path:<80} {size:>10.2f}")

        print(f"\n总计: {len(large_files)} 个文件超过10KB")
        print("\n建议:")
        print("- Agent文件应 ≤5KB")
        print("- Rule文件应 ≤3KB")
        print("- Skill文件应 ≤10KB")
        print("- 详细内容应移至 docs/architecture/ 或 docs/skills/")
    else:
        print("\n✅ 所有文档文件大小符合规范")

    print("\n" + "=" * 100)
    print("📊 统计摘要")
    print("=" * 100)
    print(f"检查的文件数: {len(md_files)}")
    print(f"缺失的链接数: {len(broken_links)}")
    print(f"大型文件数: {len(large_files)}")
    print(f"总问题数: {len(broken_links) + len(large_files)}")


if __name__ == "__main__":
    main()
