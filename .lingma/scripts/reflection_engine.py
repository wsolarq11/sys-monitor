#!/usr/bin/env python3
"""
Reflection Engine - 自我反思引擎

职责：
1. 评估任务执行结果的质量
2. 识别问题和不足
3. 生成改进建议
4. 记录反思过程

设计原则：
- 模块化：每个组件独立可测试
- 可扩展：支持自定义评估标准
- 高性能：异步处理，不阻塞主流程
- 可追溯：完整记录反思历史
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum


# ==================== 数据模型 ====================

class IssueType(str, Enum):
    """问题类型枚举"""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    BEST_PRACTICE_VIOLATION = "best_practice_violation"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_RISK = "security_risk"
    DOCUMENTATION_GAP = "documentation_gap"
    COMPLETENESS_ISSUE = "completeness_issue"
    READABILITY_ISSUE = "readability_issue"


class SeverityLevel(str, Enum):
    """严重程度枚举"""
    CRITICAL = "critical"  # 必须修复
    HIGH = "high"          # 应该修复
    MEDIUM = "medium"      # 建议修复
    LOW = "low"            # 可选修复


@dataclass
class QualityScore:
    """质量分数"""
    overall: float = 0.0
    correctness: float = 0.0
    completeness: float = 0.0
    readability: float = 0.0
    performance: float = 0.0
    security: float = 0.0
    maintainability: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class Issue:
    """问题定义"""
    issue_type: IssueType
    severity: SeverityLevel
    description: str
    location: Optional[str] = None  # 代码行号或文档位置
    evidence: Optional[str] = None  # 问题证据
    impact: Optional[str] = None    # 影响说明
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence,
            "impact": self.impact
        }


@dataclass
class Suggestion:
    """改进建议"""
    issue_id: str
    action: str
    description: str
    example: Optional[str] = None
    expected_improvement: Optional[str] = None
    difficulty: str = "medium"  # easy/medium/hard
    priority: int = 1  # 1-5, 1最高
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReflectionResult:
    """反思结果"""
    task_id: str
    timestamp: str
    quality_score: QualityScore
    issues: List[Issue] = field(default_factory=list)
    suggestions: List[Suggestion] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "quality_score": self.quality_score.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "suggestions": [sugg.to_dict() for sugg in self.suggestions],
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }
    
    def save_to_file(self, filepath: Path):
        """保存反思结果到文件"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# ==================== 核心组件 ====================

class QualityEvaluator:
    """质量评估器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化质量评估器
        
        Args:
            config_path: 质量标准配置文件路径
        """
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """加载配置"""
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
            "weights": {
                "correctness": 0.3,
                "completeness": 0.2,
                "readability": 0.15,
                "performance": 0.15,
                "security": 0.1,
                "maintainability": 0.1
            },
            "thresholds": {
                "excellent": 0.9,
                "good": 0.7,
                "acceptable": 0.5,
                "poor": 0.3
            }
        }
    
    def evaluate(self, result: Any, context: Dict[str, Any] = None) -> QualityScore:
        """
        评估结果质量
        
        Args:
            result: 待评估的结果
            context: 上下文信息
            
        Returns:
            QualityScore: 质量分数
        """
        start_time = time.time()
        
        # 根据结果类型选择评估策略
        if isinstance(result, str):
            # 文本/代码评估
            scores = self._evaluate_text(result, context or {})
        elif isinstance(result, dict):
            # 结构化数据评估
            scores = self._evaluate_structured(result, context or {})
        else:
            # 通用评估
            scores = self._evaluate_generic(result, context or {})
        
        # 计算加权总分
        weights = self.config["weights"]
        overall = sum(
            scores.get(dim, 0.0) * weight 
            for dim, weight in weights.items()
        )
        
        execution_time = time.time() - start_time
        
        return QualityScore(
            overall=round(overall, 3),
            correctness=round(scores.get("correctness", 0.0), 3),
            completeness=round(scores.get("completeness", 0.0), 3),
            readability=round(scores.get("readability", 0.0), 3),
            performance=round(scores.get("performance", 0.0), 3),
            security=round(scores.get("security", 0.0), 3),
            maintainability=round(scores.get("maintainability", 0.0), 3)
        )
    
    def _evaluate_text(self, text: str, context: Dict) -> Dict[str, float]:
        """评估文本质量"""
        scores = {}
        
        # 正确性：检查是否有明显的错误标记
        error_indicators = ["error", "failed", "exception", "traceback"]
        has_errors = any(indicator in text.lower() for indicator in error_indicators)
        scores["correctness"] = 0.0 if has_errors else 0.8
        
        # 完整性：检查长度和结构
        lines = text.strip().split('\n')
        if len(lines) < 3:
            scores["completeness"] = 0.3
        elif len(lines) < 10:
            scores["completeness"] = 0.6
        else:
            scores["completeness"] = 0.8
        
        # 可读性：检查格式和注释
        has_structure = any(text.startswith(prefix) for prefix in ["def ", "class ", "# ", "## "])
        scores["readability"] = 0.7 if has_structure else 0.5
        
        # 性能：无法直接评估，给中性分数
        scores["performance"] = 0.5
        
        # 安全性：检查是否有明显的安全问题
        security_issues = ["eval(", "exec(", "__import__"]
        has_security_issues = any(issue in text for issue in security_issues)
        scores["security"] = 0.3 if has_security_issues else 0.9
        
        # 可维护性：检查是否有文档字符串
        has_docstring = '"""' in text or "'''" in text
        scores["maintainability"] = 0.8 if has_docstring else 0.6
        
        return scores
    
    def _evaluate_structured(self, data: Dict, context: Dict) -> Dict[str, float]:
        """评估结构化数据质量"""
        # 简化实现：检查必需字段
        required_fields = context.get("required_fields", [])
        present_fields = [f for f in required_fields if f in data]
        
        completeness = len(present_fields) / len(required_fields) if required_fields else 0.8
        
        return {
            "correctness": 0.8,
            "completeness": completeness,
            "readability": 0.7,
            "performance": 0.6,
            "security": 0.9,
            "maintainability": 0.7
        }
    
    def _evaluate_generic(self, result: Any, context: Dict) -> Dict[str, float]:
        """通用评估"""
        return {
            "correctness": 0.7,
            "completeness": 0.7,
            "readability": 0.6,
            "performance": 0.5,
            "security": 0.8,
            "maintainability": 0.6
        }


class IssueDetector:
    """问题检测器
    
    基于社区最佳实践的多层检测架构：
    1. 静态分析层 - 语法、风格检查
    2. 模式匹配层 - 最佳实践、安全漏洞
    3. 语义分析层 - 逻辑正确性（Phase 2）
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化问题检测器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """加载配置"""
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def detect(self, result: Any, context: Dict[str, Any] = None) -> List[Issue]:
        """
        检测结果中的问题
        
        Args:
            result: 待检测的结果
            context: 上下文信息
            
        Returns:
            List[Issue]: 问题列表
        """
        issues = []
        
        if isinstance(result, str):
            # 分层检测
            issues.extend(self._static_analysis(result, context or {}))
            issues.extend(self._pattern_matching(result, context or {}))
        elif isinstance(result, dict):
            issues.extend(self._detect_structured_issues(result, context or {}))
        
        # 去重和排序
        issues = self._deduplicate_and_sort(issues)
        
        return issues
    
    def _static_analysis(self, text: str, context: Dict) -> List[Issue]:
        """静态分析层 - 语法和基本结构检查"""
        issues = []
        
        # 检测语法错误
        syntax_errors = self._check_syntax_errors(text)
        issues.extend(syntax_errors)
        
        # 检测代码风格问题
        style_issues = self._check_code_style(text)
        issues.extend(style_issues)
        
        return issues
    
    def _pattern_matching(self, text: str, context: Dict) -> List[Issue]:
        """模式匹配层 - 最佳实践和安全检查"""
        issues = []
        
        # 检测安全风险
        security_issues = self._check_security_risks(text)
        issues.extend(security_issues)
        
        # 检测最佳实践违反
        best_practice_issues = self._check_best_practices(text, context)
        issues.extend(best_practice_issues)
        
        # 检测性能反模式
        performance_issues = self._check_performance_antipatterns(text)
        issues.extend(performance_issues)
        
        return issues
    
    def _check_syntax_errors(self, text: str) -> List[Issue]:
        """检查语法错误"""
        issues = []
        
        if "SyntaxError" in text or "IndentationError" in text:
            issues.append(Issue(
                issue_type=IssueType.SYNTAX_ERROR,
                severity=SeverityLevel.CRITICAL,
                description="检测到Python语法错误",
                evidence="包含 SyntaxError 或 IndentationError",
                impact="代码无法执行"
            ))
        
        # 检查括号匹配
        if text.count('(') != text.count(')'):
            issues.append(Issue(
                issue_type=IssueType.SYNTAX_ERROR,
                severity=SeverityLevel.CRITICAL,
                description="括号不匹配",
                evidence=f"左括号{ text.count('(') }个，右括号{ text.count(')') }个",
                impact="语法错误，代码无法解析"
            ))
        
        return issues
    
    def _check_code_style(self, text: str) -> List[Issue]:
        """检查代码风格"""
        issues = []
        
        # 检查行长度（PEP 8: 79字符）
        lines = text.split('\n')
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            issues.append(Issue(
                issue_type=IssueType.READABILITY_ISSUE,
                severity=SeverityLevel.LOW,
                description=f"发现{ len(long_lines) }行超过100字符",
                location=f"lines: { ', '.join(map(str, long_lines[:5])) }",
                impact="降低代码可读性"
            ))
        
        return issues
    
    def _check_security_risks(self, text: str) -> List[Issue]:
        """检查安全风险"""
        issues = []
        
        # 检测危险的函数调用
        dangerous_functions = {
            'eval(': ('使用 eval() 存在代码注入风险', SeverityLevel.HIGH),
            'exec(': ('使用 exec() 存在代码注入风险', SeverityLevel.HIGH),
            '__import__(': ('动态导入可能存在安全风险', SeverityLevel.MEDIUM),
            'os.system(': ('直接执行系统命令存在注入风险', SeverityLevel.HIGH),
            'subprocess.call(': ('未验证的用户输入可能导致命令注入', SeverityLevel.MEDIUM),
        }
        
        for func, (desc, severity) in dangerous_functions.items():
            if func in text:
                issues.append(Issue(
                    issue_type=IssueType.SECURITY_RISK,
                    severity=severity,
                    description=desc,
                    evidence=f"包含 { func }",
                    impact="可能导致安全漏洞"
                ))
        
        # 检测硬编码密码/密钥
        import re
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        
        for pattern in password_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(Issue(
                    issue_type=IssueType.SECURITY_RISK,
                    severity=SeverityLevel.HIGH,
                    description="检测到硬编码的敏感信息",
                    evidence=f"匹配模式: { pattern }",
                    impact="敏感信息泄露风险"
                ))
                break
        
        return issues
    
    def _check_best_practices(self, text: str, context: Dict) -> List[Issue]:
        """检查最佳实践"""
        issues = []
        
        # 检测缺少类型注解
        if text.startswith('def ') and ':' not in text.split('(')[1].split(')')[0]:
            issues.append(Issue(
                issue_type=IssueType.BEST_PRACTICE_VIOLATION,
                severity=SeverityLevel.MEDIUM,
                description="函数参数缺少类型注解",
                impact="降低代码可维护性和IDE支持"
            ))
        
        # 检测缺少文档字符串
        if (text.startswith('def ') or text.startswith('class ')) and '"""' not in text and "'''" not in text:
            issues.append(Issue(
                issue_type=IssueType.DOCUMENTATION_GAP,
                severity=SeverityLevel.LOW,
                description="缺少文档字符串（docstring）",
                impact="降低代码可读性和可维护性"
            ))
        
        # 检测魔法数字
        import re
        magic_numbers = re.findall(r'(?<!\w)\d{2,}(?!\w)', text)
        if len(magic_numbers) > 3:  # 超过3个魔法数字
            issues.append(Issue(
                issue_type=IssueType.BEST_PRACTICE_VIOLATION,
                severity=SeverityLevel.LOW,
                description=f"发现{ len(magic_numbers) }个魔法数字，建议使用常量",
                impact="降低代码可读性"
            ))
        
        return issues
    
    def _check_performance_antipatterns(self, text: str) -> List[Issue]:
        """检查性能反模式"""
        issues = []
        
        # 检测循环内的字符串拼接
        if 'for ' in text and '+=' in text and "'" in text:
            issues.append(Issue(
                issue_type=IssueType.PERFORMANCE_ISSUE,
                severity=SeverityLevel.MEDIUM,
                description="循环内使用字符串拼接，建议使用 list.join()",
                impact="O(n²) 时间复杂度，性能较差"
            ))
        
        # 检测不必要的列表复制
        if 'list(' in text and '[' in text:
            issues.append(Issue(
                issue_type=IssueType.PERFORMANCE_ISSUE,
                severity=SeverityLevel.LOW,
                description="可能存在不必要的列表复制",
                impact="额外的内存分配"
            ))
        
        return issues
    
    def _detect_text_issues(self, text: str, context: Dict) -> List[Issue]:
        """检测文本中的问题"""
        issues = []
        
        # 检测语法错误
        if "SyntaxError" in text or "IndentationError" in text:
            issues.append(Issue(
                issue_type=IssueType.SYNTAX_ERROR,
                severity=SeverityLevel.CRITICAL,
                description="检测到语法错误",
                evidence="包含 SyntaxError 或 IndentationError"
            ))
        
        # 检测最佳实践违反
        if not any(keyword in text for keyword in ["def ", "class ", "# "]):
            if len(text) > 100:  # 较长的代码应该有结构
                issues.append(Issue(
                    issue_type=IssueType.BEST_PRACTICE_VIOLATION,
                    severity=SeverityLevel.MEDIUM,
                    description="代码缺少基本结构（函数/类定义）",
                    impact="降低代码可读性和可维护性"
                ))
        
        # 检测文档缺失
        if '"""' not in text and "'''" not in text:
            if text.startswith("def ") or text.startswith("class "):
                issues.append(Issue(
                    issue_type=IssueType.DOCUMENTATION_GAP,
                    severity=SeverityLevel.LOW,
                    description="缺少文档字符串",
                    impact="降低代码可理解性"
                ))
        
        # 检测安全问题
        if "eval(" in text or "exec(" in text:
            issues.append(Issue(
                issue_type=IssueType.SECURITY_RISK,
                severity=SeverityLevel.HIGH,
                description="使用了不安全的函数（eval/exec）",
                evidence="包含 eval( 或 exec(",
                impact="可能导致代码注入攻击"
            ))
        
        return issues
    
    def _detect_structured_issues(self, data: Dict, context: Dict) -> List[Issue]:
        """检测结构化数据中的问题"""
        issues = []
        
        # 检查必需字段
        required_fields = context.get("required_fields", [])
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            issues.append(Issue(
                issue_type=IssueType.COMPLETENESS_ISSUE,
                severity=SeverityLevel.HIGH,
                description=f"缺少必需字段: {', '.join(missing_fields)}",
                impact="数据结构不完整"
            ))
        
        return issues
    
    def _deduplicate_and_sort(self, issues: List[Issue]) -> List[Issue]:
        """去重和排序问题"""
        # 基于描述去重
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = f"{issue.issue_type.value}:{issue.description}"
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        # 按严重程度排序
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3
        }
        
        unique_issues.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        return unique_issues


class SuggestionGenerator:
    """改进建议生成器
    
    基于问题类型生成具体、可执行的改进建议
    参考社区最佳实践：每个建议包含行动、描述、示例、预期效果
    """
    
    def __init__(self):
        """初始化建议生成器"""
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """加载建议模板"""
        return {
            "syntax_error": {
                "action": "修复语法错误",
                "description": "检查并修正代码中的语法错误",
                "example": "# 检查缩进、括号匹配等\n# 使用 linter 工具自动检测\npython -m py_compile your_file.py",
                "difficulty": "easy",
                "priority": 1
            },
            "security_risk_eval": {
                "action": "替换 eval() 为安全替代方案",
                "description": "使用 ast.literal_eval() 或专门的解析器",
                "example": "import ast\n# 不安全: result = eval(user_input)\n# 安全: result = ast.literal_eval(user_input)",
                "expected_improvement": "消除代码注入风险",
                "difficulty": "medium",
                "priority": 1
            },
            "best_practice_type_hints": {
                "action": "添加类型注解",
                "description": "为函数参数和返回值添加类型提示",
                "example": "def calculate_sum(a: int, b: int) -> int:\n    return a + b",
                "expected_improvement": "提高代码可读性和IDE支持",
                "difficulty": "easy",
                "priority": 2
            },
            "documentation_gap": {
                "action": "添加文档字符串",
                "description": "为函数和类添加 Google-style docstring",
                "example": '"""\n    函数说明\n    \n    Args:\n        param: 参数说明\n    \n    Returns:\n        返回值说明\n    """',
                "expected_improvement": "提高代码可理解性和可维护性",
                "difficulty": "easy",
                "priority": 3
            },
            "performance_string_concat": {
                "action": "使用 list.join() 替代循环拼接",
                "description": "将循环内的字符串拼接改为列表收集后 join",
                "example": "# 慢: result = ''\n#       for s in items: result += s\n# 快: result = ''.join(items)",
                "expected_improvement": "从 O(n²) 优化到 O(n)",
                "difficulty": "easy",
                "priority": 2
            }
        }
    
    def generate(self, issues: List[Issue], result: Any = None) -> List[Suggestion]:
        """
        基于问题生成改进建议
        
        Args:
            issues: 问题列表
            result: 原始结果（用于生成具体示例）
            
        Returns:
            List[Suggestion]: 建议列表
        """
        suggestions = []
        
        for i, issue in enumerate(issues):
            suggestion = self._generate_for_issue(issue, i, result)
            if suggestion:
                suggestions.append(suggestion)
        
        # 按优先级排序
        suggestions.sort(key=lambda s: s.priority)
        
        return suggestions
    
    def _generate_for_issue(self, issue: Issue, index: int, result: Any = None) -> Optional[Suggestion]:
        """为单个问题生成建议"""
        
        # 语法错误
        if issue.issue_type == IssueType.SYNTAX_ERROR:
            return Suggestion(
                issue_id=f"issue-{index}",
                action="修复语法错误",
                description="检查并修正代码中的语法错误",
                example="# 检查缩进、括号匹配等\n# 使用 linter 工具自动检测",
                expected_improvement="代码能够正常执行",
                difficulty="easy",
                priority=1
            )
        
        # 最佳实践违反
        elif issue.issue_type == IssueType.BEST_PRACTICE_VIOLATION:
            return Suggestion(
                issue_id=f"issue-{index}",
                action="重构代码结构",
                description="将代码组织为函数或类",
                example="def main():\n    # 主要逻辑\n    pass\n\nif __name__ == '__main__':\n    main()",
                expected_improvement="提高代码模块化和可重用性",
                difficulty="medium",
                priority=2
            )
        
        # 文档缺失
        elif issue.issue_type == IssueType.DOCUMENTATION_GAP:
            return Suggestion(
                issue_id=f"issue-{index}",
                action="添加文档字符串",
                description="为函数和类添加 docstring",
                example='def my_function(param):\n    """\n    函数说明\n    \n    Args:\n        param: 参数说明\n    """\n    pass',
                expected_improvement="提高代码可读性和可维护性",
                difficulty="easy",
                priority=3
            )
        
        # 安全风险
        elif issue.issue_type == IssueType.SECURITY_RISK:
            return Suggestion(
                issue_id=f"issue-{index}",
                action="移除不安全函数",
                description="使用更安全的替代方案",
                example="# 不使用 eval()\n# 改用 ast.literal_eval() 或专门的解析器\nimport ast\nresult = ast.literal_eval(user_input)",
                expected_improvement="消除安全漏洞",
                difficulty="medium",
                priority=1
            )
        
        # 完整性问题
        elif issue.issue_type == IssueType.COMPLETENESS_ISSUE:
            return Suggestion(
                issue_id=f"issue-{index}",
                action="补充缺失内容",
                description=issue.description,
                expected_improvement=issue.impact or "完善功能",
                difficulty="medium",
                priority=2
            )
        
        return None


class ReflectionRecorder:
    """反思记录器"""
    
    def __init__(self, storage_dir: Path = None):
        """
        初始化记录器
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir or Path(".lingma/reflections")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def record(self, reflection: ReflectionResult):
        """
        记录反思结果
        
        Args:
            reflection: 反思结果
        """
        # 保存到文件
        filename = f"{reflection.task_id}_{int(time.time())}.json"
        filepath = self.storage_dir / filename
        reflection.save_to_file(filepath)
        
        # 更新索引
        self._update_index(reflection)
    
    def _update_index(self, reflection: ReflectionResult):
        """更新索引文件"""
        index_file = self.storage_dir / "index.json"
        
        # 加载现有索引
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"reflections": []}
        
        # 添加新记录
        index["reflections"].append({
            "task_id": reflection.task_id,
            "timestamp": reflection.timestamp,
            "quality_score": reflection.quality_score.overall,
            "issues_count": len(reflection.issues),
            "suggestions_count": len(reflection.suggestions),
            "file": f"{reflection.task_id}_{int(time.time())}.json"
        })
        
        # 保存索引
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def get_history(self, task_id: str = None, limit: int = 10) -> List[Dict]:
        """
        获取反思历史
        
        Args:
            task_id: 任务ID（可选）
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 历史记录
        """
        index_file = self.storage_dir / "index.json"
        
        if not index_file.exists():
            return []
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        reflections = index.get("reflections", [])
        
        # 过滤
        if task_id:
            reflections = [r for r in reflections if r["task_id"] == task_id]
        
        # 排序（最新的在前）
        reflections.sort(key=lambda r: r["timestamp"], reverse=True)
        
        return reflections[:limit]


# ==================== 主引擎 ====================

class ReflectionEngine:
    """自我反思引擎"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化反思引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.evaluator = QualityEvaluator(config_path)
        self.detector = IssueDetector()
        self.generator = SuggestionGenerator()
        self.recorder = ReflectionRecorder()
    
    def reflect_on_task(
        self,
        task_id: str,
        result: Any,
        context: Dict[str, Any] = None
    ) -> ReflectionResult:
        """
        对任务执行结果进行反思
        
        Args:
            task_id: 任务ID
            result: 执行结果
            context: 上下文信息
            
        Returns:
            ReflectionResult: 反思结果
        """
        start_time = time.time()
        
        # 1. 质量评估
        quality_score = self.evaluator.evaluate(result, context or {})
        
        # 2. 问题检测
        issues = self.detector.detect(result, context or {})
        
        # 3. 生成建议
        suggestions = self.generator.generate(issues, result)
        
        execution_time = time.time() - start_time
        
        # 4. 构建反思结果
        reflection = ReflectionResult(
            task_id=task_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            quality_score=quality_score,
            issues=issues,
            suggestions=suggestions,
            execution_time=round(execution_time, 3),
            metadata=context or {}
        )
        
        # 5. 记录反思
        self.recorder.record(reflection)
        
        return reflection
    
    def get_reflection_summary(self, task_id: str = None) -> Dict:
        """
        获取反思摘要
        
        Args:
            task_id: 任务ID（可选）
            
        Returns:
            Dict: 摘要信息
        """
        history = self.recorder.get_history(task_id, limit=100)
        
        if not history:
            return {"total": 0, "message": "无反思记录"}
        
        total = len(history)
        avg_quality = sum(r["quality_score"] for r in history) / total
        total_issues = sum(r["issues_count"] for r in history)
        total_suggestions = sum(r["suggestions_count"] for r in history)
        
        return {
            "total_reflections": total,
            "average_quality_score": round(avg_quality, 3),
            "total_issues_found": total_issues,
            "total_suggestions_generated": total_suggestions,
            "latest_reflection": history[0] if history else None
        }


# ==================== 便捷函数 ====================

def create_reflection_engine(config_path: Optional[Path] = None) -> ReflectionEngine:
    """创建反思引擎实例"""
    return ReflectionEngine(config_path)


def quick_reflect(task_id: str, result: Any, context: Dict = None) -> ReflectionResult:
    """快速反思（使用默认配置）"""
    engine = create_reflection_engine()
    return engine.reflect_on_task(task_id, result, context)


# ==================== 测试入口 ====================

if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("Reflection Engine 测试")
    print("="*60)
    
    engine = create_reflection_engine()
    
    # 测试1: 代码反思
    test_code = """
def calculate_sum(a, b):
    return a + b
"""
    
    print("\n📝 测试1: 代码质量评估")
    reflection = engine.reflect_on_task("test-001", test_code, {"type": "code"})
    print(f"   质量分数: {reflection.quality_score.overall}")
    print(f"   发现问题: {len(reflection.issues)}")
    print(f"   生成建议: {len(reflection.suggestions)}")
    print(f"   执行时间: {reflection.execution_time}s")
    
    # 测试2: 获取摘要
    print("\n📊 反思摘要")
    summary = engine.get_reflection_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n✅ 测试完成")
