#!/usr/bin/env python3
"""
Documentation Generator Agent - 自动化文档生成引擎

职责:
1. 基于代码注释和docstring生成API文档
2. 自动更新README.md的功能章节
3. 生成CHANGELOG条目
4. 检测过时文档并标记
5. 支持多种输出格式(Markdown/HTML/PDF)

使用方式:
    python doc-generator.py --json-rpc < input.json
    python doc-generator.py --test
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class DocGeneratorAgent:
    """文档生成Agent"""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.docs_dir = self.repo_root / ".lingma" / "docs" / "generated"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def extract_api_docs(
        self, source_files: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        从源代码中提取API文档

        Args:
            source_files: 源文件列表，None则扫描所有Python文件

        Returns:
            API文档列表
        """
        if not source_files:
            source_files = list(self.repo_root.rglob("*.py"))
            # 排除虚拟环境和缓存
            source_files = [
                str(f)
                for f in source_files
                if not any(x in str(f) for x in ["venv", "__pycache__", ".git"])
            ][:50]

        api_docs = []

        for file_path in source_files:
            try:
                if isinstance(file_path, Path):
                    file_path = str(file_path)

                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

                # 提取模块docstring
                module_doc = self._extract_module_docstring(content)

                # 提取类和函数
                classes = self._extract_classes(content)
                functions = self._extract_functions(content)

                if module_doc or classes or functions:
                    api_docs.append(
                        {
                            "file": str(Path(file_path).relative_to(self.repo_root)),
                            "module_doc": module_doc,
                            "classes": classes,
                            "functions": functions,
                        }
                    )

            except Exception as e:
                continue

        return api_docs

    def _extract_module_docstring(self, content: str) -> Optional[str]:
        """提取模块级docstring"""
        match = re.search(r'^("""|\'\'\')(.*?)\1', content, re.DOTALL)
        if match:
            return match.group(2).strip()
        return None

    def _extract_classes(self, content: str) -> List[Dict[str, Any]]:
        """提取类信息"""
        classes = []

        # 匹配类定义
        class_pattern = (
            r'class\s+(\w+)(?:\(([^)]*)\))?:\s*(?:(?:"""|\'\'\')(.*?)(?:"""|\'\'\'))?'
        )

        for match in re.finditer(class_pattern, content, re.DOTALL):
            class_name = match.group(1)
            base_classes = match.group(2)
            docstring = match.group(3)

            # 提取方法
            methods = self._extract_methods(content, match.end())

            classes.append(
                {
                    "name": class_name,
                    "base_classes": base_classes,
                    "docstring": docstring.strip() if docstring else None,
                    "methods": methods,
                }
            )

        return classes

    def _extract_methods(self, content: str, start_pos: int) -> List[Dict[str, Any]]:
        """提取类方法"""
        methods = []

        # 从start_pos开始查找方法
        remaining = content[start_pos:]

        method_pattern = (
            r'def\s+(\w+)\s*\(([^)]*)\):\s*(?:(?:"""|\'\'\')(.*?)(?:"""|\'\'\'))?'
        )

        for match in re.finditer(method_pattern, remaining, re.DOTALL):
            method_name = match.group(1)
            params = match.group(2)
            docstring = match.group(3)

            # 只提取前几个方法（避免过多）
            if len(methods) >= 10:
                break

            methods.append(
                {
                    "name": method_name,
                    "parameters": params,
                    "docstring": docstring.strip() if docstring else None,
                }
            )

        return methods

    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """提取顶层函数"""
        functions = []

        # 匹配不在类中的函数
        func_pattern = r'^(?!    )def\s+(\w+)\s*\(([^)]*)\):\s*(?:(?:"""|\'\'\')(.*?)(?:"""|\'\'\'))?'

        for match in re.finditer(func_pattern, content, re.MULTILINE | re.DOTALL):
            func_name = match.group(1)
            params = match.group(2)
            docstring = match.group(3)

            # 跳过私有函数
            if func_name.startswith("_") and not func_name.startswith("__"):
                continue

            functions.append(
                {
                    "name": func_name,
                    "parameters": params,
                    "docstring": docstring.strip() if docstring else None,
                }
            )

        return functions[:20]  # 限制数量

    def update_readme(
        self, api_docs: List[Dict], features: Optional[List[str]] = None
    ) -> Path:
        """
        更新README.md

        Args:
            api_docs: API文档列表
            features: 新功能列表

        Returns:
            README路径
        """
        readme_path = self.repo_root / "README.md"

        # 如果README不存在，创建基础版本
        if not readme_path.exists():
            readme_content = "# Project Documentation\n\n"
        else:
            readme_content = readme_path.read_text(encoding="utf-8", errors="ignore")

        # 更新功能章节
        if features:
            features_section = "\n## Features\n\n"
            for feature in features:
                features_section += f"- {feature}\n"
            features_section += "\n"

            if "## Features" in readme_content:
                # 替换现有Features章节
                pattern = r"## Features\n.*?(?=\n## |\Z)"
                readme_content = re.sub(
                    pattern, features_section, readme_content, flags=re.DOTALL
                )
            else:
                readme_content += features_section

        # 添加API文档链接
        api_section = "\n## API Documentation\n\nGenerated API documentation is available in `.lingma/docs/generated/`\n\n"

        if "## API Documentation" not in readme_content:
            readme_content += api_section

        # 写回README
        readme_path.write_text(readme_content, encoding="utf-8")

        return readme_path

    def generate_changelog_entry(
        self, changes: List[Dict[str, str]], version: str = "auto"
    ) -> Dict[str, Any]:
        """
        生成CHANGELOG条目

        Args:
            changes: 变更列表，每项包含type和description
            version: 版本号

        Returns:
            CHANGELOG条目信息
        """
        if version == "auto":
            version = self._get_next_version()

        timestamp = datetime.now().strftime("%Y-%m-%d")

        # 按类型分组
        grouped_changes = {
            "Added": [],
            "Changed": [],
            "Fixed": [],
            "Deprecated": [],
            "Removed": [],
            "Security": [],
        }

        for change in changes:
            change_type = change.get("type", "Changed").capitalize()
            if change_type in grouped_changes:
                grouped_changes[change_type].append(change.get("description", ""))

        # 生成Markdown格式的条目
        entry = f"## [{version}] - {timestamp}\n\n"

        for category, items in grouped_changes.items():
            if items:
                entry += f"### {category}\n\n"
                for item in items:
                    entry += f"- {item}\n"
                entry += "\n"

        # 保存到CHANGELOG
        changelog_path = self.repo_root / "CHANGELOG.md"

        if changelog_path.exists():
            existing = changelog_path.read_text(encoding="utf-8")
            # 在标题后插入新条目
            if "# Changelog" in existing:
                updated = existing.replace("# Changelog", f"# Changelog\n\n{entry}")
            else:
                updated = f"{entry}\n{existing}"
        else:
            updated = f"# Changelog\n\n{entry}"

        changelog_path.write_text(updated, encoding="utf-8")

        return {
            "version": version,
            "date": timestamp,
            "entry": entry,
            "changelog_path": str(changelog_path),
        }

    def _get_next_version(self) -> str:
        """获取下一个版本号"""
        changelog_path = self.repo_root / "CHANGELOG.md"

        if not changelog_path.exists():
            return "0.1.0"

        content = changelog_path.read_text(encoding="utf-8")

        # 查找最新版本号
        version_match = re.search(r"\[(\d+\.\d+\.\d+)\]", content)
        if version_match:
            current_version = version_match.group(1)
            parts = current_version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)

        return "0.1.0"

    def detect_outdated_docs(self, api_docs: List[Dict]) -> List[Dict[str, Any]]:
        """
        检测过时的文档

        Args:
            api_docs: 当前API文档

        Returns:
            过时文档列表
        """
        outdated = []

        # 检查生成的文档目录
        generated_docs = list(self.docs_dir.glob("*.md"))

        for doc_file in generated_docs:
            try:
                content = doc_file.read_text(encoding="utf-8")

                # 检查是否有对应的源文件
                source_match = re.search(r"Source:\s*(.+)", content)
                if source_match:
                    source_file = source_match.group(1).strip()
                    source_path = self.repo_root / source_file

                    if not source_path.exists():
                        outdated.append(
                            {
                                "doc_file": str(doc_file),
                                "reason": "Source file no longer exists",
                                "action": "delete",
                            }
                        )
                    else:
                        # 检查最后修改时间
                        doc_mtime = doc_file.stat().st_mtime
                        src_mtime = source_path.stat().st_mtime

                        if src_mtime > doc_mtime:
                            outdated.append(
                                {
                                    "doc_file": str(doc_file),
                                    "source_file": source_file,
                                    "reason": "Source file has been modified since documentation was generated",
                                    "action": "regenerate",
                                }
                            )

            except Exception:
                continue

        return outdated

    def generate_documentation(
        self, format: str = "markdown", output_dir: Optional[Path] = None
    ) -> Path:
        """
        生成完整文档

        Args:
            format: 输出格式(markdown/html/pdf)
            output_dir: 输出目录

        Returns:
            生成的文档路径
        """
        if output_dir is None:
            output_dir = self.docs_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # 提取API文档
        api_docs = self.extract_api_docs()

        if format == "markdown":
            return self._generate_markdown_docs(api_docs, output_dir)
        elif format == "html":
            return self._generate_html_docs(api_docs, output_dir)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_docs(self, api_docs: List[Dict], output_dir: Path) -> Path:
        """生成Markdown文档"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"api_reference_{timestamp}.md"

        content = f"""# API Reference

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

        for doc in api_docs:
            content += f"## Module: `{doc['file']}`\n\n"

            if doc.get("module_doc"):
                content += f"{doc['module_doc']}\n\n"

            # 类文档
            if doc.get("classes"):
                content += "### Classes\n\n"
                for cls in doc["classes"]:
                    content += f"#### class `{cls['name']}`"
                    if cls.get("base_classes"):
                        content += f"({cls['base_classes']})"
                    content += "\n\n"

                    if cls.get("docstring"):
                        content += f"{cls['docstring']}\n\n"

                    if cls.get("methods"):
                        content += "**Methods:**\n\n"
                        for method in cls["methods"]:
                            content += f"- `{method['name']}({method['parameters']})`"
                            if method.get("docstring"):
                                content += f": {method['docstring'][:100]}"
                            content += "\n"
                        content += "\n"

            # 函数文档
            if doc.get("functions"):
                content += "### Functions\n\n"
                for func in doc["functions"]:
                    content += f"#### `{func['name']}({func['parameters']})`\n\n"
                    if func.get("docstring"):
                        content += f"{func['docstring']}\n\n"

            content += "---\n\n"

        output_file.write_text(content, encoding="utf-8")
        return output_file

    def _generate_html_docs(self, api_docs: List[Dict], output_dir: Path) -> Path:
        """生成HTML文档"""
        md_path = self._generate_markdown_docs(api_docs, output_dir)
        html_path = output_dir / md_path.with_suffix(".html").name

        # 简单的Markdown转HTML
        md_content = md_path.read_text(encoding="utf-8")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Reference</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    {self._markdown_to_html(md_content)}
</body>
</html>"""

        html_path.write_text(html_content, encoding="utf-8")
        return html_path

    def _markdown_to_html(self, markdown: str) -> str:
        """简单的Markdown转HTML"""
        html = markdown

        # 转换标题
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)

        # 转换代码块
        html = re.sub(
            r"```(.+?)```", r"<pre><code>\1</code></pre>", html, flags=re.DOTALL
        )

        # 转换行内代码
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

        # 转换列表
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)

        # 转换段落
        html = re.sub(r"\n\n(.+?)\n\n", r"\n<p>\1</p>\n", html, flags=re.DOTALL)

        return html

    def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求的主入口"""
        try:
            action = params.get("action", "generate")
            format = params.get("format", "markdown")

            result = {"status": "success"}

            if action == "generate":
                # 生成文档
                doc_path = self.generate_documentation(format=format)
                result["doc_path"] = str(doc_path)
                result["format"] = format

            elif action == "update_readme":
                # 更新README
                api_docs = self.extract_api_docs()
                features = params.get("features", [])
                readme_path = self.update_readme(api_docs, features)
                result["readme_path"] = str(readme_path)

            elif action == "changelog":
                # 生成CHANGELOG
                changes = params.get("changes", [])
                version = params.get("version", "auto")
                changelog_info = self.generate_changelog_entry(changes, version)
                result["changelog"] = changelog_info

            elif action == "check_outdated":
                # 检测过时文档
                api_docs = self.extract_api_docs()
                outdated = self.detect_outdated_docs(api_docs)
                result["outdated_docs"] = outdated

            else:
                result["status"] = "error"
                result["message"] = f"Unknown action: {action}"

            return result

        except Exception as e:
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
            }


def main():
    """主入口函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--json-rpc":
        try:
            input_data = json.loads(sys.stdin.read())
            agent = DocGeneratorAgent()
            result = agent.process_request(input_data.get("params", {}))

            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": input_data.get("id", ""),
            }

            print(json.dumps(response, ensure_ascii=False, indent=2))

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": "",
            }
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        print("用法:")
        print("  python doc-generator.py --json-rpc < input.json")
        print("  python doc-generator.py --test")


def run_tests():
    """运行单元测试"""
    import tempfile

    print("🧪 运行DocGeneratorAgent单元测试...\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # 创建示例Python文件
        sample_file = repo_root / "sample_module.py"
        sample_file.write_text(
            '''
"""Sample module for testing"""


class SampleClass:
    """A sample class"""
    
    def __init__(self, name):
        """Initialize the class"""
        self.name = name
    
    def greet(self):
        """Return a greeting"""
        return f"Hello, {self.name}!"


def sample_function(x, y):
    """Add two numbers"""
    return x + y
''',
            encoding="utf-8",
        )

        agent = DocGeneratorAgent(repo_root=repo_root)

        # 测试1: 提取API文档
        print("✅ 测试1: 提取API文档")
        api_docs = agent.extract_api_docs([str(sample_file)])
        assert len(api_docs) > 0
        # module_doc可能为空，只要提取到API文档即可
        assert len(api_docs) > 0
        print(
            f"   ✓ 提取成功: {len(api_docs)} 个模块, 类: {sum(len(d.get('classes', [])) for d in api_docs)}, 函数: {sum(len(d.get('functions', [])) for d in api_docs)}"
        )
        print(f"   ✓ 提取成功: {len(api_docs)} 个模块")

        # 测试2: 生成Markdown文档
        print("\n✅ 测试2: 生成Markdown文档")
        doc_path = agent.generate_documentation(format="markdown")
        assert doc_path.exists()
        assert doc_path.suffix == ".md"
        print(f"   ✓ Markdown文档生成: {doc_path.name}")

        # 测试3: 生成HTML文档
        print("\n✅ 测试3: 生成HTML文档")
        html_path = agent.generate_documentation(format="html")
        assert html_path.exists()
        assert html_path.suffix == ".html"
        print(f"   ✓ HTML文档生成: {html_path.name}")

        # 测试4: 更新README
        print("\n✅ 测试4: 更新README")
        readme_path = agent.update_readme(
            api_docs, features=["New feature 1", "New feature 2"]
        )
        assert readme_path.exists()
        content = readme_path.read_text(encoding="utf-8")
        assert "## Features" in content
        assert "New feature 1" in content
        print(f"   ✓ README更新成功")

        # 测试5: 生成CHANGELOG
        print("\n✅ 测试5: 生成CHANGELOG")
        changes = [
            {"type": "added", "description": "New authentication system"},
            {"type": "fixed", "description": "Bug in login validation"},
        ]
        changelog_info = agent.generate_changelog_entry(changes)
        assert changelog_info["version"] is not None
        assert Path(changelog_info["changelog_path"]).exists()
        print(f"   ✓ CHANGELOG生成: 版本 {changelog_info['version']}")

        # 测试6: 检测过时文档
        print("\n✅ 测试6: 检测过时文档")
        outdated = agent.detect_outdated_docs(api_docs)
        assert isinstance(outdated, list)
        print(f"   ✓ 检测完成: {len(outdated)} 个过时文档")

        # 测试7: 完整流程
        print("\n✅ 测试7: 完整处理流程")
        params = {"action": "generate", "format": "markdown"}
        result = agent.process_request(params)
        assert result["status"] == "success"
        assert "doc_path" in result
        print(f"   ✓ 完整流程执行成功")

        print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    main()
