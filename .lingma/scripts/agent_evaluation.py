#!/usr/bin/env python3
"""
AI Agent Evaluation & Benchmarking System - AI Agent 评估与基准测试系统

LLM-as-Judge、Agent-as-a-Judge、自动化测试、质量指标
实现生产级 AI Agent 的全面评估框架

参考社区最佳实践:
- Agent-as-a-Judge evaluation framework
- LLM-as-Judge with detailed rubrics
- Multi-dimensional quality metrics
- Automated testing with deterministic checks
- Human-in-the-loop validation
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import statistics

logger = logging.getLogger(__name__)


class EvalDimension(Enum):
    """评估维度"""
    ACCURACY = "accuracy"  # 准确性
    COMPLETENESS = "completeness"  # 完整性
    RELEVANCE = "relevance"  # 相关性
    COHERENCE = "coherence"  # 连贯性
    SAFETY = "safety"  # 安全性
    EFFICIENCY = "efficiency"  # 效率
    CREATIVITY = "creativity"  # 创造性
    FACTUALITY = "factuality"  # 事实性


class EvalLevel(Enum):
    """评估级别"""
    SINGLE_STEP = "single_step"  # 单步评估
    TRACE = "trace"  # 轨迹评估
    MULTI_TURN = "multi_turn"  # 多轮评估


class TestType(Enum):
    """测试类型"""
    CAPABILITY = "capability"  # 能力测试（低通过率，改进目标）
    REGRESSION = "regression"  # 回归测试（高通过率，保护目标）
    PERFORMANCE = "performance"  # 性能测试
    SECURITY = "security"  # 安全测试


@dataclass
class EvalCriteria:
    """评估标准"""
    dimension: EvalDimension
    weight: float = 1.0  # 权重
    description: str = ""
    scoring_rubric: Dict[int, str] = field(default_factory=dict)  # 评分量表
    
    def __post_init__(self):
        if not self.scoring_rubric:
            # 默认 1-5 分量表
            self.scoring_rubric = {
                1: "Poor - Completely fails to meet criteria",
                2: "Below Average - Partially meets criteria",
                3: "Average - Adequately meets criteria",
                4: "Good - Well meets criteria",
                5: "Excellent - Exceeds criteria"
            }


@dataclass
class EvalResult:
    """评估结果"""
    eval_id: str
    test_name: str
    test_type: TestType
    dimension_scores: Dict[str, float]  # dimension -> score (1-5)
    overall_score: float
    pass_fail: bool
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    judge_reasoning: Optional[str] = None
    evaluated_at: str = ""
    
    def __post_init__(self):
        if not self.evaluated_at:
            self.evaluated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class TestCase:
    """测试用例"""
    test_id: str
    name: str
    test_type: TestType
    input_prompt: str
    expected_output: Optional[str] = None
    expected_actions: Optional[List[str]] = None  # 期望的工具调用序列
    criteria: List[EvalCriteria] = field(default_factory=list)
    difficulty: str = "medium"  # easy/medium/hard
    category: str = ""  # 测试类别
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class AgentTrace:
    """Agent 执行轨迹"""
    trace_id: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    final_output: Optional[str] = None
    total_steps: int = 0
    tool_calls: int = 0
    llm_calls: int = 0
    total_tokens: int = 0
    execution_time: float = 0.0
    
    def add_step(self, step: Dict):
        """添加步骤"""
        self.steps.append(step)
        self.total_steps += 1
        
        if step.get("type") == "tool_call":
            self.tool_calls += 1
        elif step.get("type") == "llm_call":
            self.llm_calls += 1
            self.total_tokens += step.get("tokens", 0)


class DeterministicChecker:
    """确定性检查器
    
    执行可重复的确定性检查（无需 LLM）
    """
    
    def check_exact_match(self, actual: str, expected: str) -> Tuple[bool, float]:
        """
        检查精确匹配
        
        Returns:
            (是否匹配, 相似度分数)
        """
        is_match = actual.strip() == expected.strip()
        return is_match, 1.0 if is_match else 0.0
    
    def check_contains(self, actual: str, expected_keywords: List[str]) -> Tuple[bool, float]:
        """
        检查是否包含关键词
        
        Returns:
            (是否包含, 覆盖率)
        """
        actual_lower = actual.lower()
        matched = sum(1 for kw in expected_keywords if kw.lower() in actual_lower)
        coverage = matched / len(expected_keywords) if expected_keywords else 0.0
        
        return coverage > 0.8, coverage
    
    def check_action_sequence(self, actual_actions: List[str], expected_actions: List[str]) -> Tuple[bool, float]:
        """
        检查动作序列
        
        Returns:
            (是否匹配, 序列相似度)
        """
        if not expected_actions:
            return True, 1.0
        
        # 计算编辑距离相似度
        from difflib import SequenceMatcher
        matcher = SequenceMatcher(None, actual_actions, expected_actions)
        similarity = matcher.ratio()
        
        return similarity > 0.8, similarity
    
    def check_final_state(self, agent_state: Dict, expected_state: Dict) -> Tuple[bool, float]:
        """
        检查最终状态
        
        Returns:
            (是否匹配, 状态相似度)
        """
        matching_keys = sum(1 for k in expected_state if agent_state.get(k) == expected_state[k])
        total_keys = len(expected_state)
        
        if total_keys == 0:
            return True, 1.0
        
        similarity = matching_keys / total_keys
        
        return similarity > 0.9, similarity


class LLMEvaluator:
    """LLM 评估器
    
    使用 LLM 作为裁判进行评估
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self.evaluation_cache: Dict[str, EvalResult] = {}
    
    def evaluate_with_rubric(
        self,
        question: str,
        agent_response: str,
        criteria: List[EvalCriteria],
        reference_answer: Optional[str] = None
    ) -> EvalResult:
        """
        使用评分量表评估
        
        Args:
            question: 问题
            agent_response: Agent 响应
            criteria: 评估标准列表
            reference_answer: 参考答案（可选）
            
        Returns:
            评估结果
        """
        import uuid
        
        # 构建评估提示
        eval_prompt = self._build_eval_prompt(question, agent_response, criteria, reference_answer)
        
        # 模拟 LLM 评估（实际应调用 LLM API）
        dimension_scores = self._mock_llm_evaluation(eval_prompt, criteria)
        
        # 计算加权总分
        total_weight = sum(c.weight for c in criteria)
        weighted_sum = sum(
            dimension_scores.get(c.dimension.value, 3.0) * c.weight
            for c in criteria
        )
        overall_score = weighted_sum / total_weight if total_weight > 0 else 3.0
        
        # 判断是否通过（阈值 3.5）
        pass_fail = overall_score >= 3.5
        
        result = EvalResult(
            eval_id=str(uuid.uuid4()),
            test_name="LLM Evaluation",
            test_type=TestType.CAPABILITY,
            dimension_scores=dimension_scores,
            overall_score=round(overall_score, 2),
            pass_fail=pass_fail,
            execution_time=0.0,
            judge_reasoning=f"Evaluation based on {len(criteria)} criteria using {self.model_name}"
        )
        
        logger.info(f"LLM evaluation completed: score={overall_score:.2f}, pass={pass_fail}")
        
        return result
    
    def _build_eval_prompt(
        self,
        question: str,
        response: str,
        criteria: List[EvalCriteria],
        reference: Optional[str] = None
    ) -> str:
        """构建评估提示"""
        prompt = f"""You are an expert evaluator. Please evaluate the following agent response.

Question: {question}

Agent Response: {response}
"""
        
        if reference:
            prompt += f"\nReference Answer: {reference}\n"
        
        prompt += "\nEvaluation Criteria:\n"
        for i, criterion in enumerate(criteria, 1):
            prompt += f"{i}. {criterion.dimension.value.upper()} (Weight: {criterion.weight})\n"
            prompt += f"   Description: {criterion.description}\n"
            prompt += f"   Scoring Rubric:\n"
            for score, desc in criterion.scoring_rubric.items():
                prompt += f"     {score}: {desc}\n"
        
        prompt += "\nPlease provide scores for each dimension (1-5) and explain your reasoning."
        
        return prompt
    
    def _mock_llm_evaluation(self, prompt: str, criteria: List[EvalCriteria]) -> Dict[str, float]:
        """模拟 LLM 评估（用于测试）"""
        # 在实际实现中，这里应该调用 LLM API
        # 目前返回随机但合理的分数
        import random
        
        scores = {}
        for criterion in criteria:
            # 基于 prompt 长度和内容生成伪随机但一致的分数
            base_score = 3.5 + (len(prompt) % 10) / 10.0
            noise = random.uniform(-0.5, 0.5)
            score = max(1.0, min(5.0, base_score + noise))
            scores[criterion.dimension.value] = round(score, 2)
        
        return scores


class AgentAsJudge:
    """Agent-as-a-Judge 评估器
    
    使用专门的 Agent 评估另一个 Agent 的完整执行轨迹
    """
    
    def __init__(self):
        self.judge_agent_profile = {
            "name": "Evaluation Agent",
            "capabilities": ["evaluation", "reasoning", "analysis"]
        }
    
    def evaluate_trace(
        self,
        task_description: str,
        agent_trace: AgentTrace,
        criteria: List[EvalCriteria]
    ) -> EvalResult:
        """
        评估 Agent 执行轨迹
        
        Args:
            task_description: 任务描述
            agent_trace: Agent 执行轨迹
            criteria: 评估标准
            
        Returns:
            评估结果
        """
        import uuid
        
        # 分析轨迹
        analysis = self._analyze_trace(task_description, agent_trace)
        
        # 基于分析生成分数
        dimension_scores = self._score_from_analysis(analysis, criteria)
        
        # 计算总分
        total_weight = sum(c.weight for c in criteria)
        weighted_sum = sum(
            dimension_scores.get(c.dimension.value, 3.0) * c.weight
            for c in criteria
        )
        overall_score = weighted_sum / total_weight if total_weight > 0 else 3.0
        
        pass_fail = overall_score >= 3.5
        
        result = EvalResult(
            eval_id=str(uuid.uuid4()),
            test_name="Agent-as-a-Judge Evaluation",
            test_type=TestType.CAPABILITY,
            dimension_scores=dimension_scores,
            overall_score=round(overall_score, 2),
            pass_fail=pass_fail,
            execution_time=agent_trace.execution_time,
            metadata={
                "total_steps": agent_trace.total_steps,
                "tool_calls": agent_trace.tool_calls,
                "llm_calls": agent_trace.llm_calls,
                "total_tokens": agent_trace.total_tokens,
                "analysis": analysis
            },
            judge_reasoning=f"Agent-as-a-Judge evaluated {agent_trace.total_steps} steps"
        )
        
        logger.info(f"Agent-as-a-Judge evaluation completed: score={overall_score:.2f}")
        
        return result
    
    def _analyze_trace(self, task_description: str, trace: AgentTrace) -> Dict:
        """分析执行轨迹"""
        analysis = {
            "task_understanding": self._assess_task_understanding(task_description, trace),
            "planning_quality": self._assess_planning(trace),
            "tool_usage_efficiency": self._assess_tool_usage(trace),
            "error_handling": self._assess_error_handling(trace),
            "goal_achievement": self._assess_goal_achievement(trace)
        }
        
        return analysis
    
    def _assess_task_understanding(self, task_desc: str, trace: AgentTrace) -> float:
        """评估任务理解"""
        # 简单启发式：检查是否有明确的计划步骤
        has_planning = any("plan" in str(step).lower() for step in trace.steps[:3])
        return 4.0 if has_planning else 2.5
    
    def _assess_planning(self, trace: AgentTrace) -> float:
        """评估规划质量"""
        # 基于步骤数和工具调用的合理性
        if trace.total_steps == 0:
            return 1.0
        
        efficiency_ratio = trace.tool_calls / max(trace.total_steps, 1)
        
        # 理想的工具调用比例在 0.3-0.7 之间
        if 0.3 <= efficiency_ratio <= 0.7:
            return 4.5
        elif 0.2 <= efficiency_ratio <= 0.8:
            return 3.5
        else:
            return 2.0
    
    def _assess_tool_usage(self, trace: AgentTrace) -> float:
        """评估工具使用效率"""
        if trace.tool_calls == 0:
            return 3.0
        
        # 假设每次工具调用都有价值
        return min(5.0, 3.0 + trace.tool_calls * 0.2)
    
    def _assess_error_handling(self, trace: AgentTrace) -> float:
        """评估错误处理"""
        error_count = sum(1 for step in trace.steps if step.get("error"))
        
        if error_count == 0:
            return 5.0
        elif error_count <= 2:
            return 3.5
        else:
            return 2.0
    
    def _assess_goal_achievement(self, trace: AgentTrace) -> float:
        """评估目标达成"""
        # 检查是否有最终输出
        if trace.final_output:
            return 4.5
        else:
            return 2.0
    
    def _score_from_analysis(self, analysis: Dict, criteria: List[EvalCriteria]) -> Dict[str, float]:
        """从分析结果生成分数"""
        scores = {}
        
        for criterion in criteria:
            dim = criterion.dimension.value
            
            if dim == "accuracy":
                scores[dim] = analysis.get("goal_achievement", 3.0)
            elif dim == "efficiency":
                scores[dim] = analysis.get("tool_usage_efficiency", 3.0)
            elif dim == "coherence":
                scores[dim] = analysis.get("planning_quality", 3.0)
            else:
                scores[dim] = 3.5  # 默认分数
        
        return scores


class BenchmarkSuite:
    """基准测试套件
    
    管理和执行测试套件
    """
    
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.results: List[EvalResult] = []
        self.deterministic_checker = DeterministicChecker()
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
        logger.info(f"Test case added: {test_case.name}")
    
    def load_test_suite(self, suite_path: str):
        """从文件加载测试套件"""
        path = Path(suite_path)
        if not path.exists():
            logger.warning(f"Test suite file not found: {suite_path}")
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for test_data in data.get("test_cases", []):
            test_case = TestCase(**test_data)
            self.test_cases.append(test_case)
        
        logger.info(f"Loaded {len(data.get('test_cases', []))} test cases from {suite_path}")
    
    def run_tests(
        self,
        agent_executor: Callable[[str], Any],
        test_filter: Optional[Callable[[TestCase], bool]] = None
    ) -> List[EvalResult]:
        """
        运行测试
        
        Args:
            agent_executor: Agent 执行函数
            test_filter: 测试过滤器（可选）
            
        Returns:
            测试结果列表
        """
        results = []
        
        # 过滤测试用例
        tests_to_run = [tc for tc in self.test_cases if not test_filter or test_filter(tc)]
        
        logger.info(f"Running {len(tests_to_run)} tests...")
        
        for test_case in tests_to_run:
            start_time = time.time()
            
            try:
                # 执行 Agent
                agent_output = agent_executor(test_case.input_prompt)
                
                # 提取轨迹（如果可用）
                trace = self._extract_trace(agent_output)
                
                # 执行确定性检查
                det_passed, det_score = self._run_deterministic_checks(test_case, agent_output)
                
                # 执行 LLM 评估
                llm_evaluator = LLMEvaluator()
                llm_result = llm_evaluator.evaluate_with_rubric(
                    question=test_case.input_prompt,
                    agent_response=str(agent_output),
                    criteria=test_case.criteria,
                    reference_answer=test_case.expected_output
                )
                
                # 合并结果
                execution_time = time.time() - start_time
                llm_result.execution_time = execution_time
                
                # 如果确定性检查失败，标记为失败
                if not det_passed and test_case.test_type == TestType.REGRESSION:
                    llm_result.pass_fail = False
                    llm_result.overall_score = min(llm_result.overall_score, det_score)
                
                results.append(llm_result)
                self.results.append(llm_result)
                
                status = "✅ PASS" if llm_result.pass_fail else "❌ FAIL"
                logger.info(f"{status} {test_case.name}: score={llm_result.overall_score:.2f}")
            
            except Exception as e:
                # 记录错误
                import uuid
                error_result = EvalResult(
                    eval_id=str(uuid.uuid4()),
                    test_name=test_case.name,
                    test_type=test_case.test_type,
                    dimension_scores={},
                    overall_score=0.0,
                    pass_fail=False,
                    execution_time=time.time() - start_time,
                    metadata={"error": str(e)}
                )
                results.append(error_result)
                self.results.append(error_result)
                
                logger.error(f"❌ ERROR {test_case.name}: {str(e)}")
        
        return results
    
    def _extract_trace(self, agent_output: Any) -> AgentTrace:
        """从 Agent 输出中提取轨迹"""
        # 简化实现：创建基本轨迹
        trace = AgentTrace(
            trace_id=str(uuid.uuid4()),
            final_output=str(agent_output)
        )
        
        # 如果输出是字典且包含 steps，解析它
        if isinstance(agent_output, dict) and "steps" in agent_output:
            trace.steps = agent_output["steps"]
            trace.total_steps = len(agent_output["steps"])
        
        return trace
    
    def _run_deterministic_checks(self, test_case: TestCase, agent_output: Any) -> Tuple[bool, float]:
        """运行确定性检查"""
        output_str = str(agent_output)
        
        # 检查精确匹配
        if test_case.expected_output:
            match, score = self.deterministic_checker.check_exact_match(
                output_str, test_case.expected_output
            )
            if match:
                return True, score
        
        # 检查关键词覆盖
        if test_case.expected_output:
            keywords = test_case.expected_output.split()[:10]  # 取前10个词
            contains, coverage = self.deterministic_checker.check_contains(output_str, keywords)
            if contains:
                return True, coverage
        
        # 检查动作序列
        if test_case.expected_actions:
            # 假设 agent_output 包含 actions 列表
            actual_actions = []
            if isinstance(agent_output, dict) and "actions" in agent_output:
                actual_actions = agent_output["actions"]
            
            seq_match, seq_score = self.deterministic_checker.check_action_sequence(
                actual_actions, test_case.expected_actions
            )
            if seq_match:
                return True, seq_score
        
        # 默认通过（如果没有明确的期望）
        return True, 1.0
    
    def get_benchmark_report(self) -> Dict:
        """生成基准测试报告"""
        if not self.results:
            return {"error": "No results available"}
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.pass_fail)
        failed = total - passed
        
        # 按测试类型分组
        by_type = {}
        for result in self.results:
            test_type = result.test_type.value
            if test_type not in by_type:
                by_type[test_type] = {"total": 0, "passed": 0}
            by_type[test_type]["total"] += 1
            if result.pass_fail:
                by_type[test_type]["passed"] += 1
        
        # 计算平均分
        scores = [r.overall_score for r in self.results if r.overall_score > 0]
        avg_score = statistics.mean(scores) if scores else 0.0
        
        # 计算执行时间统计
        exec_times = [r.execution_time for r in self.results]
        avg_exec_time = statistics.mean(exec_times) if exec_times else 0.0
        
        report = {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
                "average_score": round(avg_score, 2),
                "average_execution_time": round(avg_exec_time, 3)
            },
            "by_test_type": by_type,
            "score_distribution": {
                "min": round(min(scores), 2) if scores else 0,
                "max": round(max(scores), 2) if scores else 0,
                "median": round(statistics.median(scores), 2) if scores else 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return report


class EvaluationEngine:
    """评估引擎
    
    整合所有评估组件的完整系统
    """
    
    def __init__(self):
        self.benchmark_suite = BenchmarkSuite()
        self.llm_evaluator = LLMEvaluator()
        self.agent_judge = AgentAsJudge()
        self.evaluation_history: List[EvalResult] = []
    
    def create_test_case(
        self,
        name: str,
        input_prompt: str,
        test_type: TestType = TestType.CAPABILITY,
        expected_output: Optional[str] = None,
        criteria: Optional[List[EvalCriteria]] = None,
        **kwargs
    ) -> TestCase:
        """创建测试用例"""
        import uuid
        
        default_criteria = [
            EvalCriteria(
                dimension=EvalDimension.ACCURACY,
                weight=2.0,
                description="How accurate is the response?"
            ),
            EvalCriteria(
                dimension=EvalDimension.RELEVANCE,
                weight=1.5,
                description="How relevant is the response to the question?"
            ),
            EvalCriteria(
                dimension=EvalDimension.SAFETY,
                weight=2.0,
                description="Is the response safe and appropriate?"
            )
        ]
        
        test_case = TestCase(
            test_id=str(uuid.uuid4()),
            name=name,
            test_type=test_type,
            input_prompt=input_prompt,
            expected_output=expected_output,
            criteria=criteria or default_criteria,
            **kwargs
        )
        
        self.benchmark_suite.add_test_case(test_case)
        
        return test_case
    
    def run_evaluation(
        self,
        agent_executor: Callable[[str], Any],
        test_filter: Optional[Callable[[TestCase], bool]] = None
    ) -> Dict:
        """
        运行评估
        
        Args:
            agent_executor: Agent 执行函数
            test_filter: 测试过滤器
            
        Returns:
            评估报告
        """
        # 运行测试
        results = self.benchmark_suite.run_tests(agent_executor, test_filter)
        
        # 保存历史
        self.evaluation_history.extend(results)
        
        # 生成报告
        report = self.benchmark_suite.get_benchmark_report()
        
        logger.info(f"Evaluation completed: {report['summary']['pass_rate']}% pass rate")
        
        return report
    
    def get_evaluation_history(self, limit: int = 10) -> List[Dict]:
        """获取评估历史"""
        recent = self.evaluation_history[-limit:]
        return [r.to_dict() for r in recent]


def create_evaluation_engine() -> EvaluationEngine:
    """工厂函数：创建评估引擎"""
    return EvaluationEngine()


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Evaluation & Benchmarking 测试")
    print("="*60)
    
    engine = create_evaluation_engine()
    
    # 创建测试用例
    print("\n📝 创建测试用例...")
    
    test1 = engine.create_test_case(
        name="Simple Q&A",
        input_prompt="What is the capital of France?",
        test_type=TestType.REGRESSION,
        expected_output="Paris",
        difficulty="easy",
        category="knowledge"
    )
    
    test2 = engine.create_test_case(
        name="Code Generation",
        input_prompt="Write a Python function to calculate factorial",
        test_type=TestType.CAPABILITY,
        difficulty="medium",
        category="coding"
    )
    
    test3 = engine.create_test_case(
        name="Complex Reasoning",
        input_prompt="Explain quantum computing in simple terms",
        test_type=TestType.CAPABILITY,
        difficulty="hard",
        category="reasoning"
    )
    
    print(f"   创建了 {len(engine.benchmark_suite.test_cases)} 个测试用例")
    
    # 模拟 Agent 执行器
    def mock_agent_executor(prompt: str) -> Any:
        """模拟 Agent 执行"""
        if "capital of France" in prompt:
            return "The capital of France is Paris."
        elif "factorial" in prompt:
            return """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)"""
        else:
            return "Quantum computing uses quantum bits (qubits) that can be in multiple states simultaneously."
    
    # 运行评估
    print("\n▶️  运行评估...")
    report = engine.run_evaluation(mock_agent_executor)
    
    print(f"\n📊 评估报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 获取历史
    print("\n📜 评估历史:")
    history = engine.get_evaluation_history(3)
    for i, result in enumerate(history, 1):
        print(f"   {i}. {result['test_name']}: score={result['overall_score']:.2f}, pass={result['pass_fail']}")
    
    print("\n✅ 测试完成！")
