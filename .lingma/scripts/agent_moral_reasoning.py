#!/usr/bin/env python3
"""
AI Agent Moral Reasoning & Ethical Decision Making System - AI Agent 道德推理与伦理决策系统

规范伦理学、价值对齐、道德困境处理、伦理护栏、责任归属
实现生产级 AI Agent 的道德推理能力

参考社区最佳实践:
- Normative ethics frameworks - Utilitarianism, Deontology, Virtue Ethics
- Value alignment - align agent goals with human values
- Moral reasoning - recognize ethical issues, make reasoned decisions
- Ethical guardrails - technical constraints preventing unethical behavior
- Responsibility attribution - clear accountability for AI decisions
- Multi-stakeholder value consideration
"""

import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import random
import statistics
import math
from collections import defaultdict

logger = logging.getLogger(__name__)


class EthicalFramework(Enum):
    """伦理框架"""
    UTILITARIANISM = "utilitarianism"  # 功利主义（结果导向）
    DEONTOLOGY = "deontology"  # 义务论（规则导向）
    VIRTUE_ETHICS = "virtue_ethics"  # 德性伦理（品格导向）
    CARE_ETHICS = "care_ethics"  # 关怀伦理（关系导向）
    RIGHTS_BASED = "rights_based"  # 权利基础（人权导向）


class MoralFoundation(Enum):
    """道德基础（Moral Foundations Theory）"""
    CARE_HARM = "care_harm"  # 关爱/伤害
    FAIRNESS_CHEATING = "fairness_cheating"  # 公平/欺骗
    LOYALTY_BETRAYAL = "loyalty_betrayal"  # 忠诚/背叛
    AUTHORITY_SUBVERSION = "authority_subversion"  # 权威/颠覆
    SANCTITY_DEGRADATION = "sanctity_degradation"  # 圣洁/堕落
    LIBERTY_OPPRESSION = "liberty_oppression"  # 自由/压迫


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"  # 安全
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中等风险
    HIGH = "high"  # 高风险
    CRITICAL = "critical"  # 严重风险


class ComplianceStatus(Enum):
    """合规状态"""
    COMPLIANT = "compliant"  # 合规
    PARTIAL = "partial"  # 部分合规
    NON_COMPLIANT = "non_compliant"  # 不合规


@dataclass
class EthicalPrinciple:
    """伦理原则"""
    principle_id: str
    name: str
    description: str
    framework: EthicalFramework
    priority: int = 5  # 优先级 1-10
    weight: float = 1.0  # 权重
    
    def __post_init__(self):
        if not self.principle_id:
            self.principle_id = str(uuid.uuid4())


@dataclass
class MoralDilemma:
    """道德困境"""
    dilemma_id: str
    description: str
    stakeholders: List[str] = field(default_factory=list)  # 利益相关者
    conflicting_values: List[str] = field(default_factory=list)  # 冲突价值观
    potential_harms: List[str] = field(default_factory=list)  # 潜在伤害
    potential_benefits: List[str] = field(default_factory=list)  # 潜在收益
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.dilemma_id:
            self.dilemma_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class EthicalDecision:
    """伦理决策"""
    decision_id: str
    action: str
    justification: str
    ethical_frameworks_applied: List[EthicalFramework] = field(default_factory=list)
    moral_foundations_considered: List[MoralFoundation] = field(default_factory=list)
    risk_assessment: RiskLevel = RiskLevel.SAFE
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    stakeholder_impact: Dict[str, float] = field(default_factory=dict)  # 对各方影响
    confidence: float = 0.5
    alternative_actions: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ValueAlignmentReport:
    """价值对齐报告"""
    report_id: str
    agent_action: str
    human_values: List[str] = field(default_factory=list)
    alignment_score: float = 0.0
    misalignment_areas: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class EthicalReasoner:
    """伦理推理器
    
    基于多种伦理框架进行道德推理
    """
    
    def __init__(self):
        self.principles: List[EthicalPrinciple] = self._load_default_principles()
        self.decision_history: List[EthicalDecision] = []
    
    def analyze_dilemma(
        self,
        dilemma: MoralDilemma,
        frameworks: List[EthicalFramework] = None
    ) -> EthicalDecision:
        """
        分析道德困境
        
        Args:
            dilemma: 道德困境
            frameworks: 使用的伦理框架
            
        Returns:
            伦理决策
        """
        if frameworks is None:
            frameworks = [
                EthicalFramework.UTILITARIANISM,
                EthicalFramework.DEONTOLOGY,
                EthicalFramework.VIRTUE_ETHICS
            ]
        
        # Step 1: 应用各伦理框架分析
        framework_analyses = {}
        for framework in frameworks:
            analysis = self._apply_ethical_framework(dilemma, framework)
            framework_analyses[framework] = analysis
        
        # Step 2: 综合各框架结果
        recommended_action = self._synthesize_framework_results(framework_analyses)
        
        # Step 3: 风险评估
        risk_level = self._assess_risk(dilemma, recommended_action)
        
        # Step 4: 合规检查
        compliance = self._check_compliance(recommended_action)
        
        # Step 5: 利益相关者影响评估
        stakeholder_impact = self._evaluate_stakeholder_impact(dilemma, recommended_action)
        
        decision = EthicalDecision(
            decision_id="",
            action=recommended_action,
            justification=self._generate_justification(framework_analyses),
            ethical_frameworks_applied=frameworks,
            moral_foundations_considered=self._identify_moral_foundations(dilemma),
            risk_assessment=risk_level,
            compliance_status=compliance,
            stakeholder_impact=stakeholder_impact,
            confidence=self._calculate_confidence(framework_analyses),
            alternative_actions=self._generate_alternatives(framework_analyses)
        )
        
        self.decision_history.append(decision)
        
        logger.info(f"Ethical decision made: {decision.action[:50]}... (risk={risk_level.value})")
        
        return decision
    
    def evaluate_action_ethics(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估行动的伦理合规性
        
        Args:
            action: 待评估行动
            context: 情境信息
            
        Returns:
            伦理评估结果
        """
        # 检查是否违反核心原则
        violations = self._check_principle_violations(action, context)
        
        # 计算风险等级
        risk_level = self._calculate_action_risk(violations)
        
        # 生成调整建议
        adjustments = self._suggest_ethical_adjustments(violations)
        
        return {
            "action": action,
            "violations": violations,
            "risk_level": risk_level.value,
            "adjustments": adjustments,
            "approved": len(violations) == 0 or risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
        }
    
    def _apply_ethical_framework(
        self,
        dilemma: MoralDilemma,
        framework: EthicalFramework
    ) -> Dict[str, Any]:
        """应用伦理框架分析"""
        if framework == EthicalFramework.UTILITARIANISM:
            return self._utilitarian_analysis(dilemma)
        elif framework == EthicalFramework.DEONTOLOGY:
            return self._deontological_analysis(dilemma)
        elif framework == EthicalFramework.VIRTUE_ETHICS:
            return self._virtue_ethics_analysis(dilemma)
        else:
            return {"recommendation": "No specific recommendation", "reasoning": []}
    
    def _utilitarian_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """功利主义分析（最大化总体福祉）"""
        # 计算总收益和总伤害
        total_benefit = len(dilemma.potential_benefits) * 0.8
        total_harm = len(dilemma.potential_harms) * 0.9
        
        net_utility = total_benefit - total_harm
        
        recommendation = "proceed" if net_utility > 0 else "avoid"
        
        return {
            "framework": "Utilitarianism",
            "net_utility": round(net_utility, 2),
            "recommendation": recommendation,
            "reasoning": [
                f"Total benefits: {total_benefit:.2f}",
                f"Total harms: {total_harm:.2f}",
                f"Net utility: {net_utility:.2f}"
            ]
        }
    
    def _deontological_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """义务论分析（遵循道德规则）"""
        # 检查是否违反绝对道德规则
        rule_violations = []
        
        # 简化规则检查
        if any("harm" in harm.lower() for harm in dilemma.potential_harms):
            rule_violations.append("Violates non-maleficence principle")
        
        if any("deceive" in harm.lower() or "lie" in harm.lower() for harm in dilemma.potential_harms):
            rule_violations.append("Violates honesty principle")
        
        recommendation = "avoid" if rule_violations else "proceed"
        
        return {
            "framework": "Deontology",
            "rule_violations": rule_violations,
            "recommendation": recommendation,
            "reasoning": rule_violations if rule_violations else ["No rule violations detected"]
        }
    
    def _virtue_ethics_analysis(self, dilemma: MoralDilemma) -> Dict[str, Any]:
        """德性伦理分析（培养良好品格）"""
        virtues_promoted = []
        vices_encouraged = []
        
        # 简化分析
        if dilemma.potential_benefits:
            virtues_promoted.extend(["beneficence", "compassion"])
        
        if dilemma.potential_harms:
            vices_encouraged.extend(["maleficence", "recklessness"])
        
        recommendation = "proceed" if len(virtues_promoted) > len(vices_encouraged) else "reconsider"
        
        return {
            "framework": "Virtue Ethics",
            "virtues_promoted": virtues_promoted,
            "vices_encouraged": vices_encouraged,
            "recommendation": recommendation,
            "reasoning": [
                f"Virtues promoted: {', '.join(virtues_promoted)}",
                f"Vices encouraged: {', '.join(vices_encouraged)}"
            ]
        }
    
    def _synthesize_framework_results(self, analyses: Dict) -> str:
        """综合各框架结果"""
        recommendations = [a["recommendation"] for a in analyses.values()]
        
        # 如果所有框架都同意，采用共识
        if len(set(recommendations)) == 1:
            return f"Action based on consensus: {recommendations[0]}"
        
        # 否则，选择最谨慎的建议
        if "avoid" in recommendations:
            return "Action avoided due to ethical concerns from multiple frameworks"
        elif "reconsider" in recommendations:
            return "Action requires further ethical consideration"
        else:
            return "Action proceeds with caution"
    
    def _assess_risk(self, dilemma: MoralDilemma, action: str) -> RiskLevel:
        """风险评估"""
        harm_count = len(dilemma.potential_harms)
        
        if harm_count >= 3:
            return RiskLevel.CRITICAL
        elif harm_count >= 2:
            return RiskLevel.HIGH
        elif harm_count >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _check_compliance(self, action: str) -> ComplianceStatus:
        """合规检查"""
        # 简化实现
        if "avoid" in action.lower() or "concern" in action.lower():
            return ComplianceStatus.NON_COMPLIANT
        elif "caution" in action.lower():
            return ComplianceStatus.PARTIAL
        else:
            return ComplianceStatus.COMPLIANT
    
    def _evaluate_stakeholder_impact(
        self,
        dilemma: MoralDilemma,
        action: str
    ) -> Dict[str, float]:
        """利益相关者影响评估"""
        impact = {}
        
        for stakeholder in dilemma.stakeholders:
            # 简化评估
            impact[stakeholder] = random.uniform(-0.5, 0.8)
        
        return impact
    
    def _identify_moral_foundations(self, dilemma: MoralDilemma) -> List[MoralFoundation]:
        """识别涉及的道德基础"""
        foundations = []
        
        if any("harm" in h.lower() for h in dilemma.potential_harms):
            foundations.append(MoralFoundation.CARE_HARM)
        
        if any("fair" in v.lower() or "unfair" in v.lower() for v in dilemma.conflicting_values):
            foundations.append(MoralFoundation.FAIRNESS_CHEATING)
        
        if not foundations:
            foundations.append(MoralFoundation.CARE_HARM)  # 默认
        
        return foundations
    
    def _generate_justification(self, analyses: Dict) -> str:
        """生成决策理由"""
        justifications = []
        for framework, analysis in analyses.items():
            reasoning = "; ".join(analysis.get("reasoning", []))
            justifications.append(f"{framework.value}: {reasoning}")
        
        return " | ".join(justifications)
    
    def _calculate_confidence(self, analyses: Dict) -> float:
        """计算信心度"""
        # 基于框架间一致性
        recommendations = [a["recommendation"] for a in analyses.values()]
        agreement_ratio = recommendations.count(recommendations[0]) / len(recommendations)
        
        return round(agreement_ratio * 0.9, 2)
    
    def _generate_alternatives(self, analyses: Dict) -> List[str]:
        """生成备选方案"""
        alternatives = []
        
        for framework, analysis in analyses.items():
            if analysis["recommendation"] != "proceed":
                alternatives.append(f"Alternative based on {framework.value}")
        
        return alternatives if alternatives else ["Proceed with monitoring"]
    
    def _check_principle_violations(
        self,
        action: str,
        context: Dict
    ) -> List[str]:
        """检查原则违反"""
        violations = []
        
        # 检查核心原则
        core_principles = [
            ("Non-maleficence", "harm", "do no harm"),
            ("Beneficence", "benefit", "act to benefit others"),
            ("Autonomy", "coerce", "respect user autonomy"),
            ("Justice", "unfair", "be fair and unbiased"),
            ("Privacy", "disclose", "protect privacy")
        ]
        
        for principle_name, keyword, description in core_principles:
            if keyword in action.lower():
                violations.append(f"Potential violation of {principle_name}: {description}")
        
        return violations
    
    def _calculate_action_risk(self, violations: List[str]) -> RiskLevel:
        """计算行动风险"""
        if len(violations) >= 3:
            return RiskLevel.CRITICAL
        elif len(violations) >= 2:
            return RiskLevel.HIGH
        elif len(violations) >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.SAFE
    
    def _suggest_ethical_adjustments(self, violations: List[str]) -> List[str]:
        """建议伦理调整"""
        suggestions = []
        
        for violation in violations:
            if "Non-maleficence" in violation:
                suggestions.append("Modify action to minimize potential harm")
            elif "Autonomy" in violation:
                suggestions.append("Ensure user consent and choice")
            elif "Privacy" in violation:
                suggestions.append("Implement data protection measures")
        
        return suggestions
    
    def _load_default_principles(self) -> List[EthicalPrinciple]:
        """加载默认伦理原则"""
        return [
            EthicalPrinciple(
                principle_id="",
                name="Non-maleficence",
                description="Do no harm",
                framework=EthicalFramework.DEONTOLOGY,
                priority=10,
                weight=1.0
            ),
            EthicalPrinciple(
                principle_id="",
                name="Beneficence",
                description="Act to benefit others",
                framework=EthicalFramework.UTILITARIANISM,
                priority=9,
                weight=0.9
            ),
            EthicalPrinciple(
                principle_id="",
                name="Autonomy",
                description="Respect user autonomy and choices",
                framework=EthicalFramework.RIGHTS_BASED,
                priority=8,
                weight=0.85
            ),
            EthicalPrinciple(
                principle_id="",
                name="Justice",
                description="Be fair and unbiased",
                framework=EthicalFramework.DEONTOLOGY,
                priority=8,
                weight=0.85
            ),
            EthicalPrinciple(
                principle_id="",
                name="Veracity",
                description="Be truthful and transparent",
                framework=EthicalFramework.VIRTUE_ETHICS,
                priority=7,
                weight=0.8
            ),
            EthicalPrinciple(
                principle_id="",
                name="Privacy",
                description="Protect user privacy and data",
                framework=EthicalFramework.RIGHTS_BASED,
                priority=9,
                weight=0.9
            )
        ]


class ValueAlignmentChecker:
    """价值对齐检查器
    
    确保Agent行为与人类价值观一致
    """
    
    def __init__(self):
        self.human_values = self._load_human_values()
        self.alignment_history: List[ValueAlignmentReport] = []
    
    def check_alignment(
        self,
        agent_action: str,
        context: Dict[str, Any] = None
    ) -> ValueAlignmentReport:
        """
        检查价值对齐
        
        Args:
            agent_action: Agent行动
            context: 情境信息
            
        Returns:
            价值对齐报告
        """
        # 评估对齐分数
        alignment_score = self._calculate_alignment_score(agent_action)
        
        # 识别不对齐领域
        misalignment_areas = self._identify_misalignments(agent_action)
        
        # 生成改进建议
        recommendations = self._generate_alignment_recommendations(misalignment_areas)
        
        report = ValueAlignmentReport(
            report_id="",
            agent_action=agent_action,
            human_values=self.human_values,
            alignment_score=round(alignment_score, 2),
            misalignment_areas=misalignment_areas,
            recommendations=recommendations
        )
        
        self.alignment_history.append(report)
        
        logger.info(f"Value alignment checked: score={alignment_score:.2f}")
        
        return report
    
    def _load_human_values(self) -> List[str]:
        """加载人类价值观"""
        return [
            "Safety and well-being",
            "Fairness and justice",
            "Autonomy and freedom",
            "Privacy and dignity",
            "Honesty and transparency",
            "Compassion and empathy",
            "Responsibility and accountability"
        ]
    
    def _calculate_alignment_score(self, action: str) -> float:
        """计算对齐分数"""
        # 简化实现：基于关键词匹配
        positive_keywords = ["help", "assist", "protect", "respect", "inform"]
        negative_keywords = ["harm", "deceive", "coerce", "exploit", "manipulate"]
        
        action_lower = action.lower()
        
        positive_matches = sum(1 for kw in positive_keywords if kw in action_lower)
        negative_matches = sum(1 for kw in negative_keywords if kw in action_lower)
        
        score = 0.5 + (positive_matches * 0.1) - (negative_matches * 0.2)
        
        return max(0.0, min(1.0, score))
    
    def _identify_misalignments(self, action: str) -> List[str]:
        """识别不对齐领域"""
        misalignments = []
        
        action_lower = action.lower()
        
        if "harm" in action_lower or "damage" in action_lower:
            misalignments.append("Safety and well-being")
        
        if "unfair" in action_lower or "bias" in action_lower:
            misalignments.append("Fairness and justice")
        
        if "coerce" in action_lower or "force" in action_lower:
            misalignments.append("Autonomy and freedom")
        
        if "disclose" in action_lower or "expose" in action_lower:
            misalignments.append("Privacy and dignity")
        
        return misalignments
    
    def _generate_alignment_recommendations(self, misalignments: List[str]) -> List[str]:
        """生成对齐建议"""
        recommendations = []
        
        for misalignment in misalignments:
            if "Safety" in misalignment:
                recommendations.append("Implement safety checks and harm prevention mechanisms")
            elif "Fairness" in misalignment:
                recommendations.append("Audit for bias and ensure equitable treatment")
            elif "Autonomy" in misalignment:
                recommendations.append("Provide users with meaningful choices and control")
            elif "Privacy" in misalignment:
                recommendations.append("Strengthen data protection and consent mechanisms")
        
        return recommendations


class EthicalGuardrail:
    """伦理护栏
    
    技术约束防止不道德行为
    """
    
    def __init__(self):
        self.violations_log: List[Dict] = []
    
    def enforce_guardrails(
        self,
        proposed_action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行伦理护栏
        
        Args:
            proposed_action: 提议的行动
            context: 情境信息
            
        Returns:
            护栏执行结果
        """
        # 检查禁止行为
        prohibited = self._check_prohibited_actions(proposed_action)
        
        # 检查需要审查的行为
        requires_review = self._check_requires_review(proposed_action)
        
        # 确定是否允许
        allowed = not prohibited and not requires_review
        
        result = {
            "action": proposed_action,
            "allowed": allowed,
            "prohibited": prohibited,
            "requires_review": requires_review,
            "modified_action": self._suggest_safe_alternative(proposed_action) if not allowed else proposed_action
        }
        
        if not allowed:
            self.violations_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": proposed_action,
                "reason": "Prohibited" if prohibited else "Requires review"
            })
        
        logger.info(f"Guardrail enforced: allowed={allowed}")
        
        return result
    
    def _check_prohibited_actions(self, action: str) -> bool:
        """检查禁止行为"""
        prohibited_keywords = [
            "harm", "kill", "injure", "deceive", "steal",
            "manipulate", "exploit", "abuse", "discriminate"
        ]
        
        action_lower = action.lower()
        return any(kw in action_lower for kw in prohibited_keywords)
    
    def _check_requires_review(self, action: str) -> bool:
        """检查需要审查的行为"""
        review_keywords = [
            "medical advice", "legal advice", "financial advice",
            "personal data", "sensitive information"
        ]
        
        action_lower = action.lower()
        return any(kw in action_lower for kw in review_keywords)
    
    def _suggest_safe_alternative(self, action: str) -> str:
        """建议安全替代方案"""
        # 简化实现
        return f"Modified version of: {action} (with safety safeguards)"


def create_ethical_reasoning_system() -> Tuple[EthicalReasoner, ValueAlignmentChecker, EthicalGuardrail]:
    """工厂函数：创建伦理推理系统"""
    reasoner = EthicalReasoner()
    checker = ValueAlignmentChecker()
    guardrail = EthicalGuardrail()
    
    return reasoner, checker, guardrail


if __name__ == "__main__":
    # 简单测试
    print("="*60)
    print("AI Agent Moral Reasoning & Ethical Decision Making 测试")
    print("="*60)
    
    reasoner, checker, guardrail = create_ethical_reasoning_system()
    
    # 分析道德困境
    print("\n⚖️  分析道德困境...")
    dilemma = MoralDilemma(
        dilemma_id="",
        description="Should an autonomous vehicle prioritize passenger safety over pedestrian safety?",
        stakeholders=["passenger", "pedestrian", "society"],
        conflicting_values=["safety vs safety", "individual vs collective"],
        potential_harms=["potential injury to pedestrian", "potential injury to passenger"],
        potential_benefits=["save lives overall", "minimize total harm"]
    )
    
    decision = reasoner.analyze_dilemma(dilemma)
    print(f"   决策ID: {decision.decision_id}")
    print(f"   推荐行动: {decision.action}")
    print(f"   风险等级: {decision.risk_assessment.value}")
    print(f"   合规状态: {decision.compliance_status.value}")
    print(f"   信心度: {decision.confidence:.2f}")
    print(f"   应用框架数: {len(decision.ethical_frameworks_applied)}")
    print(f"   道德基础数: {len(decision.moral_foundations_considered)}")
    print(f"   利益相关者影响:")
    for stakeholder, impact in decision.stakeholder_impact.items():
        print(f"     - {stakeholder}: {impact:+.2f}")
    
    # 评估行动伦理
    print("\n🔍 评估行动伦理...")
    evaluation = reasoner.evaluate_action_ethics(
        action="Collect user data without explicit consent",
        context={"domain": "healthcare", "sensitivity": "high"}
    )
    print(f"   行动: {evaluation['action']}")
    print(f"   风险等级: {evaluation['risk_level']}")
    print(f"   违规数: {len(evaluation['violations'])}")
    print(f"   是否批准: {evaluation['approved']}")
    
    if evaluation['violations']:
        print(f"\n   违规详情:")
        for violation in evaluation['violations']:
            print(f"     - {violation}")
    
    if evaluation['adjustments']:
        print(f"\n   调整建议:")
        for adjustment in evaluation['adjustments']:
            print(f"     - {adjustment}")
    
    # 检查价值对齐
    print("\n🎯 检查价值对齐...")
    alignment_report = checker.check_alignment(
        agent_action="Assist user in finding helpful resources while respecting their privacy"
    )
    print(f"   报告ID: {alignment_report.report_id}")
    print(f"   对齐分数: {alignment_report.alignment_score:.2f}")
    print(f"   不对齐领域数: {len(alignment_report.misalignment_areas)}")
    print(f"   建议数: {len(alignment_report.recommendations)}")
    
    if alignment_report.recommendations:
        print(f"\n   改进建议:")
        for rec in alignment_report.recommendations:
            print(f"     - {rec}")
    
    # 执行伦理护栏
    print("\n🛡️  执行伦理护栏...")
    guardrail_result = guardrail.enforce_guardrails(
        proposed_action="Provide medical diagnosis without professional oversight",
        context={"domain": "healthcare"}
    )
    print(f"   行动: {guardrail_result['action'][:60]}...")
    print(f"   是否允许: {guardrail_result['allowed']}")
    print(f"   是否禁止: {guardrail_result['prohibited']}")
    print(f"   需审查: {guardrail_result['requires_review']}")
    print(f"   修改后行动: {guardrail_result['modified_action'][:60]}...")
    
    # 伦理原则列表
    print("\n📜 伦理原则...")
    print(f"   总原则数: {len(reasoner.principles)}")
    for principle in reasoner.principles[:3]:
        print(f"     - {principle.name}: {principle.description} (priority={principle.priority})")
    
    # 决策历史统计
    print("\n📊 决策历史统计...")
    print(f"   总决策数: {len(reasoner.decision_history)}")
    print(f"   总对齐检查数: {len(checker.alignment_history)}")
    print(f"   护栏违规数: {len(guardrail.violations_log)}")
    
    print("\n✅ 测试完成！")
