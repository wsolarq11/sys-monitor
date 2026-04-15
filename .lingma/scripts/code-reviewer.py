#!/usr/bin/env python3
"""
Code Reviewer Agent - 代码质量审查和分析引擎

职责:
1. 集成pylint/flake8/eslint进行静态分析
2. 检测安全漏洞(硬编码密钥、SQL注入等)
3. 计算代码质量分数(圈复杂度、重复率等)
4. 提供具体的修复建议和最佳实践
5. 生成审查报告(Markdown格式)

使用方式:
    python code-reviewer.py --json-rpc < input.json
    python code-reviewer.py --test
"""

import json
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class CodeReviewerAgent:
    """代码审查Agent"""
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.reports_dir = self.repo_root / ".lingma" / "reports" / "code-review"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def run_static_analysis(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        运行静态分析工具
        
        Args:
            file_path: 可选的特定文件路径，None则分析整个项目
            
        Returns:
            静态分析结果
        """
        results = {
            "pylint": None,
            "flake8": None,
            "security_scan": None
        }
        
        target = file_path or str(self.repo_root)
        
        # 运行pylint
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", target],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.repo_root)
            )
            
            if result.returncode < 32:  # pylint返回码<32表示成功或部分成功
                try:
                    results["pylint"] = json.loads(result.stdout)
                except json.JSONDecodeError:
                    results["pylint"] = {"raw_output": result.stdout[:2000]}
            else:
                results["pylint"] = {"error": result.stderr[:1000]}
                
        except FileNotFoundError:
            results["pylint"] = {"warning": "pylint not installed"}
        except Exception as e:
            results["pylint"] = {"error": str(e)}
        
        # 运行flake8
        try:
            result = subprocess.run(
                ["flake8", "--count", "--statistics", target],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.repo_root)
            )
            
            results["flake8"] = {
                "output": result.stdout[:2000],
                "error_count": result.returncode > 0
            }
            
        except FileNotFoundError:
            results["flake8"] = {"warning": "flake8 not installed"}
        except Exception as e:
            results["flake8"] = {"error": str(e)}
        
        # 安全扫描
        results["security_scan"] = self._scan_security_issues(target)
        
        return results
    
    def _scan_security_issues(self, target: str) -> Dict[str, Any]:
        """扫描安全问题"""
        issues = []
        
        # 扫描Python文件
        py_files = list(Path(target).rglob("*.py")) if Path(target).is_dir() else [Path(target)]
        
        for py_file in py_files[:50]:  # 限制扫描文件数量
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # 检测硬编码密钥
                secret_patterns = [
                    (r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
                    (r'(?i)(api_key|apikey|secret|token)\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key/secret'),
                    (r'(?i)(aws_access_key|aws_secret)', 'AWS credentials'),
                ]
                
                for pattern, issue_type in secret_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            "type": "security",
                            "severity": "high",
                            "file": str(py_file.relative_to(self.repo_root)),
                            "line": line_num,
                            "issue": issue_type,
                            "recommendation": "Use environment variables or a secrets manager"
                        })
                
                # 检测SQL注入风险
                if re.search(r'execute\s*\(\s*f["\']', content) or \
                   re.search(r'execute\s*\(\s*["\'].*%s', content):
                    issues.append({
                        "type": "security",
                        "severity": "critical",
                        "file": str(py_file.relative_to(self.repo_root)),
                        "issue": "Potential SQL injection",
                        "recommendation": "Use parameterized queries instead of string formatting"
                    })
                
                # 检测eval/exec使用
                if re.search(r'\beval\s*\(', content) or re.search(r'\bexec\s*\(', content):
                    issues.append({
                        "type": "security",
                        "severity": "medium",
                        "file": str(py_file.relative_to(self.repo_root)),
                        "issue": "Use of eval/exec (potential code injection)",
                        "recommendation": "Avoid eval/exec; use safer alternatives"
                    })
                    
            except Exception:
                continue
        
        return {
            "issues_found": len(issues),
            "issues": issues
        }
    
    def calculate_quality_metrics(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        计算代码质量指标
        
        Args:
            file_path: 可选的特定文件路径
            
        Returns:
            质量指标
        """
        metrics = {
            "files_analyzed": 0,
            "total_lines": 0,
            "code_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "complexity_score": 0,
            "duplication_rate": 0,
            "maintainability_index": 0
        }
        
        # 获取要分析的文件
        if file_path:
            files = [Path(file_path)]
        else:
            files = list(self.repo_root.rglob("*.py"))
            # 排除虚拟环境和缓存目录
            files = [f for f in files if not any(x in str(f) for x in ['venv', '__pycache__', '.git'])]
        
        metrics["files_analyzed"] = len(files)
        
        total_complexity = 0
        
        for py_file in files[:100]:  # 限制分析文件数量
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                metrics["total_lines"] += len(lines)
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        metrics["blank_lines"] += 1
                    elif stripped.startswith('#'):
                        metrics["comment_lines"] += 1
                    else:
                        metrics["code_lines"] += 1
                
                # 计算圈复杂度(简化版)
                complexity = self._calculate_cyclomatic_complexity(content)
                total_complexity += complexity
                
            except Exception:
                continue
        
        # 计算平均复杂度
        if metrics["files_analyzed"] > 0:
            metrics["complexity_score"] = round(total_complexity / metrics["files_analyzed"], 2)
        
        # 计算可维护性指数(简化公式)
        if metrics["total_lines"] > 0:
            comment_ratio = metrics["comment_lines"] / metrics["total_lines"]
            complexity_penalty = min(metrics["complexity_score"] / 20, 1)  # 归一化
            metrics["maintainability_index"] = round(
                max(0, 100 * (1 - complexity_penalty) * (0.5 + comment_ratio)),
                1
            )
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """计算圈复杂度(简化版)"""
        # 决策点关键字
        decision_keywords = [
            r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
            r'\band\b', r'\bor\b', r'\bexcept\b', r'\bcase\b'
        ]
        
        complexity = 1  # 基础复杂度
        
        for keyword in decision_keywords:
            matches = re.findall(keyword, code)
            complexity += len(matches)
        
        return complexity
    
    def generate_recommendations(self, static_analysis: Dict, metrics: Dict) -> List[Dict[str, Any]]:
        """生成修复建议"""
        recommendations = []
        
        # 基于静态分析的建议
        if static_analysis.get("pylint") and isinstance(static_analysis["pylint"], list):
            error_count = len(static_analysis["pylint"])
            if error_count > 10:
                recommendations.append({
                    "category": "code_quality",
                    "priority": "high",
                    "issue": f"Found {error_count} pylint issues",
                    "recommendation": "Review and fix pylint warnings, especially high-severity ones",
                    "action_items": [
                        "Run 'pylint --errors-only' to see critical issues",
                        "Fix import errors and undefined variables first",
                        "Address code style issues"
                    ]
                })
        
        # 基于安全扫描的建议
        security_issues = static_analysis.get("security_scan", {}).get("issues", [])
        if security_issues:
            critical_issues = [i for i in security_issues if i.get("severity") == "critical"]
            high_issues = [i for i in security_issues if i.get("severity") == "high"]
            
            if critical_issues:
                recommendations.append({
                    "category": "security",
                    "priority": "critical",
                    "issue": f"Found {len(critical_issues)} critical security issues",
                    "recommendation": "Immediately address critical security vulnerabilities",
                    "action_items": [
                        "Remove hardcoded credentials",
                        "Use parameterized queries for SQL",
                        "Implement proper input validation"
                    ]
                })
            
            if high_issues:
                recommendations.append({
                    "category": "security",
                    "priority": "high",
                    "issue": f"Found {len(high_issues)} high-severity security issues",
                    "recommendation": "Address high-severity security concerns",
                    "action_items": [
                        "Move secrets to environment variables",
                        "Review access control mechanisms"
                    ]
                })
        
        # 基于质量指标的建议
        if metrics.get("complexity_score", 0) > 10:
            recommendations.append({
                "category": "maintainability",
                "priority": "medium",
                "issue": f"High cyclomatic complexity: {metrics['complexity_score']}",
                "recommendation": "Refactor complex functions to reduce complexity",
                "action_items": [
                    "Break down large functions into smaller ones",
                    "Extract repeated logic into helper functions",
                    "Consider using design patterns"
                ]
            })
        
        if metrics.get("maintainability_index", 100) < 50:
            recommendations.append({
                "category": "maintainability",
                "priority": "medium",
                "issue": f"Low maintainability index: {metrics['maintainability_index']}",
                "recommendation": "Improve code documentation and structure",
                "action_items": [
                    "Add docstrings to functions and classes",
                    "Increase comment coverage",
                    "Simplify complex logic"
                ]
            })
        
        # 如果没有问题，给出正面反馈
        if not recommendations:
            recommendations.append({
                "category": "general",
                "priority": "info",
                "issue": "No major issues found",
                "recommendation": "Code quality looks good! Continue following best practices.",
                "action_items": []
            })
        
        return recommendations
    
    def generate_review_report(self, static_analysis: Dict, metrics: Dict, 
                              recommendations: List[Dict]) -> Path:
        """生成Markdown格式的审查报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"code_review_{timestamp}.md"
        
        # 计算总体评分
        quality_score = self._calculate_overall_score(static_analysis, metrics)
        
        report = f"""# Code Review Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Quality Score**: {quality_score}/100

---

## Summary

| Metric | Value |
|--------|-------|
| Files Analyzed | {metrics.get('files_analyzed', 0)} |
| Total Lines | {metrics.get('total_lines', 0)} |
| Code Lines | {metrics.get('code_lines', 0)} |
| Comment Lines | {metrics.get('comment_lines', 0)} |
| Complexity Score | {metrics.get('complexity_score', 0)} |
| Maintainability Index | {metrics.get('maintainability_index', 0)} |

---

## Static Analysis Results

### Pylint
{self._format_pylint_results(static_analysis.get('pylint'))}

### Flake8
{self._format_flake8_results(static_analysis.get('flake8'))}

### Security Scan
{self._format_security_results(static_analysis.get('security_scan'))}

---

## Recommendations

{self._format_recommendations(recommendations)}

---

## Next Steps

1. Address all critical and high-priority issues
2. Review medium-priority recommendations
3. Re-run code review after fixes
4. Ensure all tests pass

---

*Report generated by Code Reviewer Agent*
"""
        
        report_path.write_text(report, encoding='utf-8')
        return report_path
    
    def _calculate_overall_score(self, static_analysis: Dict, metrics: Dict) -> int:
        """计算总体质量分数"""
        score = 100
        
        # 扣分项
        security_issues = static_analysis.get("security_scan", {}).get("issues_found", 0)
        score -= security_issues * 5  # 每个安全问题扣5分
        
        pylint_issues = static_analysis.get("pylint")
        if isinstance(pylint_issues, list):
            score -= len(pylint_issues) * 0.5  # 每个pylint问题扣0.5分
        
        complexity = metrics.get("complexity_score", 0)
        if complexity > 10:
            score -= (complexity - 10) * 2
        
        maintainability = metrics.get("maintainability_index", 100)
        if maintainability < 50:
            score -= (50 - maintainability) * 0.5
        
        return max(0, min(100, round(score)))
    
    def _format_pylint_results(self, pylint_result) -> str:
        """格式化pylint结果"""
        if not pylint_result:
            return "Not available"
        
        if isinstance(pylint_result, dict) and "warning" in pylint_result:
            return f"⚠️ {pylint_result['warning']}"
        
        if isinstance(pylint_result, dict) and "error" in pylint_result:
            return f"❌ Error: {pylint_result['error']}"
        
        if isinstance(pylint_result, list):
            if len(pylint_result) == 0:
                return "✅ No issues found"
            return f"Found {len(pylint_result)} issues (see detailed report)"
        
        return "Results available"
    
    def _format_flake8_results(self, flake8_result) -> str:
        """格式化flake8结果"""
        if not flake8_result:
            return "Not available"
        
        if "warning" in flake8_result:
            return f"⚠️ {flake8_result['warning']}"
        
        if "error" in flake8_result:
            return f"❌ Error: {flake8_result['error']}"
        
        output = flake8_result.get("output", "")
        if not output.strip():
            return "✅ No issues found"
        
        return f"Issues found:\n```\n{output[:500]}\n```"
    
    def _format_security_results(self, security_result) -> str:
        """格式化安全扫描结果"""
        if not security_result:
            return "Not available"
        
        issues_found = security_result.get("issues_found", 0)
        if issues_found == 0:
            return "✅ No security issues found"
        
        issues = security_result.get("issues", [])
        result = f"⚠️ Found {issues_found} security issue(s):\n\n"
        
        for issue in issues[:5]:  # 最多显示5个
            result += f"- **{issue['severity'].upper()}**: {issue['issue']}\n"
            result += f"  - File: `{issue.get('file', 'N/A')}`\n"
            result += f"  - Recommendation: {issue.get('recommendation', '')}\n\n"
        
        return result
    
    def _format_recommendations(self, recommendations: List[Dict]) -> str:
        """格式化建议"""
        if not recommendations:
            return "No specific recommendations at this time."
        
        result = ""
        for rec in recommendations:
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "info": "ℹ️"
            }.get(rec.get("priority", "info"), "ℹ️")
            
            result += f"### {priority_emoji} [{rec['priority'].upper()}] {rec['category'].replace('_', ' ').title()}\n\n"
            result += f"**Issue**: {rec['issue']}\n\n"
            result += f"**Recommendation**: {rec['recommendation']}\n\n"
            
            if rec.get("action_items"):
                result += "**Action Items**:\n"
                for item in rec["action_items"]:
                    result += f"- [ ] {item}\n"
                result += "\n"
        
        return result
    
    def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求的主入口"""
        try:
            file_path = params.get("file_path")
            
            # Step 1: 运行静态分析
            static_analysis = self.run_static_analysis(file_path)
            
            # Step 2: 计算质量指标
            metrics = self.calculate_quality_metrics(file_path)
            
            # Step 3: 生成建议
            recommendations = self.generate_recommendations(static_analysis, metrics)
            
            # Step 4: 生成报告
            report_path = self.generate_review_report(static_analysis, metrics, recommendations)
            
            # Step 5: 返回结果
            quality_score = self._calculate_overall_score(static_analysis, metrics)
            
            return {
                "status": "success",
                "quality_score": quality_score,
                "static_analysis": static_analysis,
                "metrics": metrics,
                "recommendations": recommendations,
                "report_path": str(report_path),
                "passed": quality_score >= 80  # 质量门禁阈值
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }


def main():
    """主入口函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json-rpc":
        try:
            input_data = json.loads(sys.stdin.read())
            agent = CodeReviewerAgent()
            result = agent.process_request(input_data.get("params", {}))
            
            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": input_data.get("id", "")
            }
            
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": str(e)
                },
                "id": ""
            }
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
            sys.exit(1)
    else:
        print("用法:")
        print("  python code-reviewer.py --json-rpc < input.json")
        print("  python code-reviewer.py --test")


def run_tests():
    """运行单元测试"""
    import tempfile
    
    print("🧪 运行CodeReviewerAgent单元测试...\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)
        
        # 创建示例Python文件
        sample_file = repo_root / "sample.py"
        sample_file.write_text("""
# Sample module for testing

def simple_function(x):
    \"\"\"A simple function\"\"\"
    return x + 1

def complex_function(data):
    \"\"\"A more complex function\"\"\"
    if data:
        for item in data:
            if item > 0:
                if item < 100:
                    return item
    return None

# Hardcoded password (security issue)
password = "secret123"
""", encoding='utf-8')
        
        agent = CodeReviewerAgent(repo_root=repo_root)
        
        # 测试1: 静态分析
        print("✅ 测试1: 运行静态分析")
        analysis = agent.run_static_analysis(str(sample_file))
        assert "pylint" in analysis
        assert "flake8" in analysis
        assert "security_scan" in analysis
        print(f"   ✓ 静态分析完成")
        
        # 测试2: 安全扫描
        print("\n✅ 测试2: 安全扫描")
        security = analysis["security_scan"]
        assert security["issues_found"] > 0
        print(f"   ✓ 发现 {security['issues_found']} 个安全问题")
        
        # 测试3: 质量指标
        print("\n✅ 测试3: 计算质量指标")
        metrics = agent.calculate_quality_metrics(str(sample_file))
        assert metrics["files_analyzed"] > 0
        assert metrics["total_lines"] > 0
        print(f"   ✓ 质量指标计算完成: {metrics}")
        
        # 测试4: 生成建议
        print("\n✅ 测试4: 生成修复建议")
        recommendations = agent.generate_recommendations(analysis, metrics)
        assert len(recommendations) > 0
        print(f"   ✓ 生成 {len(recommendations)} 条建议")
        
        # 测试5: 生成报告
        print("\n✅ 测试5: 生成审查报告")
        report_path = agent.generate_review_report(analysis, metrics, recommendations)
        assert report_path.exists()
        assert report_path.suffix == ".md"
        print(f"   ✓ 报告生成: {report_path.name}")
        
        # 测试6: 完整流程
        print("\n✅ 测试6: 完整处理流程")
        params = {"file_path": str(sample_file)}
        result = agent.process_request(params)
        assert result["status"] == "success"
        assert "quality_score" in result
        assert "report_path" in result
        print(f"   ✓ 完整流程执行成功, 质量分数: {result['quality_score']}")
        
        print("\n✅ 所有测试通过！\n")


if __name__ == "__main__":
    main()
