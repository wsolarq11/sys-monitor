#!/usr/bin/env python3
"""
度量指标收集器 - 收集Git Hook和Spec驱动开发的度量指标

功能:
1. 分析Hook执行情况
2. 评估Spec质量
3. 计算生产力指标
4. 生成可读报告
5. 输出JSON格式数据
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict


class MetricsCollector:
    """度量指标收集器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            self.project_root = Path.cwd()
        else:
            self.project_root = Path(project_root)
        
        self.audit_log = self.project_root / ".lingma/logs/audit.log"
        self.specs_dir = self.project_root / ".lingma/specs"
        self.hooks_dir = self.project_root / ".git/hooks"
        
    def collect(self) -> Dict[str, Any]:
        """收集所有指标"""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'project': str(self.project_root),
            'hooks': self.analyze_hooks(),
            'specs': self.analyze_specs(),
            'productivity': self.calculate_productivity(),
            'quality': self.assess_quality(),
            'recommendations': self.generate_recommendations()
        }
    
    def analyze_hooks(self) -> Dict[str, Any]:
        """分析Hook执行情况"""
        logs = self.parse_audit_log()
        
        # 按hook类型分类
        hook_events = defaultdict(list)
        for log in logs:
            if 'hook' in log:
                hook_events[log['hook']].append(log)
        
        # 统计pre-commit
        pre_commit_logs = hook_events.get('pre-commit', [])
        pre_commit_total = len([l for l in pre_commit_logs if l.get('event_type') == 'pre-commit-check'])
        pre_commit_blocked = len([l for l in pre_commit_logs if l.get('status') == 'failed'])
        
        # 统计pre-push
        pre_push_logs = hook_events.get('pre-push', [])
        pre_push_total = len([l for l in pre_push_logs if l.get('event_type') == 'pre-push'])
        pre_push_blocked = len([l for l in pre_push_logs if l.get('status') == 'failed'])
        
        # 统计post-commit
        post_commit_logs = hook_events.get('post-commit', [])
        post_commit_total = len(post_commit_logs)
        
        return {
            'pre_commit': {
                'total_commits': pre_commit_total,
                'blocked_commits': pre_commit_blocked,
                'block_rate': round(pre_commit_blocked / max(pre_commit_total, 1), 2),
                'pass_rate': round(1 - (pre_commit_blocked / max(pre_commit_total, 1)), 2)
            },
            'pre_push': {
                'total_pushes': pre_push_total,
                'blocked_pushes': pre_push_blocked,
                'block_rate': round(pre_push_blocked / max(pre_push_total, 1), 2),
                'pass_rate': round(1 - (pre_push_blocked / max(pre_push_total, 1)), 2)
            },
            'post_commit': {
                'total_notifications': post_commit_total,
                'success_rate': 1.0  # post-commit不阻塞，假设100%成功
            },
            'overall': {
                'total_validations': pre_commit_total + pre_push_total,
                'total_blocks': pre_commit_blocked + pre_push_blocked,
                'overall_block_rate': round((pre_commit_blocked + pre_push_blocked) / max(pre_commit_total + pre_push_total, 1), 2)
            }
        }
    
    def analyze_specs(self) -> Dict[str, Any]:
        """分析Spec质量"""
        if not self.specs_dir.exists():
            return {
                'active_specs': 0,
                'avg_completion_rate': 0,
                'avg_clarification_count': 0,
                'error': 'Specs directory not found'
            }
        
        spec_files = list(self.specs_dir.glob("*.md"))
        active_specs = len(spec_files)
        
        completion_rates = []
        clarification_counts = []
        
        for spec_file in spec_files:
            try:
                content = spec_file.read_text(encoding='utf-8')
                
                # 解析完成率
                if 'completion_rate' in content or '进度' in content:
                    # 简化：查找百分比
                    import re
                    matches = re.findall(r'(\d+)%', content)
                    if matches:
                        completion_rates.append(int(matches[-1]))
                
                # 统计澄清问题
                clarifications = content.count('[NEEDS CLARIFICATION]')
                clarification_counts.append(clarifications)
                
            except Exception as e:
                print(f"警告: 无法解析 {spec_file}: {e}", file=sys.stderr)
        
        return {
            'active_specs': active_specs,
            'avg_completion_rate': round(sum(completion_rates) / max(len(completion_rates), 1), 2) if completion_rates else 0,
            'avg_clarification_count': round(sum(clarification_counts) / max(len(clarification_counts), 1), 2) if clarification_counts else 0,
            'total_clarifications': sum(clarification_counts),
            'specs_with_clarifications': len([c for c in clarification_counts if c > 0])
        }
    
    def calculate_productivity(self) -> Dict[str, Any]:
        """计算生产力指标"""
        logs = self.parse_audit_log()
        
        # 统计最近7天的活动
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        recent_logs = []
        for log in logs:
            try:
                timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
                if timestamp >= week_ago:
                    recent_logs.append(log)
            except:
                continue
        
        # 按天分组
        daily_activity = defaultdict(int)
        for log in recent_logs:
            try:
                date_str = log['timestamp'][:10]
                daily_activity[date_str] += 1
            except:
                continue
        
        return {
            'last_7_days': {
                'total_events': len(recent_logs),
                'avg_events_per_day': round(len(recent_logs) / 7, 2),
                'most_active_day': max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None,
                'daily_breakdown': dict(daily_activity)
            },
            'commit_frequency': {
                'commits_last_7_days': len([l for l in recent_logs if l.get('hook') == 'post-commit']),
                'avg_commits_per_day': round(len([l for l in recent_logs if l.get('hook') == 'post-commit']) / 7, 2)
            }
        }
    
    def assess_quality(self) -> Dict[str, Any]:
        """评估整体质量"""
        hooks_metrics = self.analyze_hooks()
        specs_metrics = self.analyze_specs()
        
        # 质量评分（0-100）
        quality_score = 100
        
        # 扣分项1: Hook阻止率过高（理想: 5-15%）
        block_rate = hooks_metrics['overall']['overall_block_rate']
        if block_rate > 0.3:
            quality_score -= 20
        elif block_rate > 0.15:
            quality_score -= 10
        elif block_rate < 0.02:
            quality_score -= 5  # 可能验证不够严格
        
        # 扣分项2: Spec完成率低
        completion_rate = specs_metrics.get('avg_completion_rate', 0)
        if completion_rate < 50:
            quality_score -= 20
        elif completion_rate < 70:
            quality_score -= 10
        
        # 扣分项3: 未回答的澄清问题多
        avg_clarifications = specs_metrics.get('avg_clarification_count', 0)
        if avg_clarifications > 5:
            quality_score -= 20
        elif avg_clarifications > 2:
            quality_score -= 10
        
        return {
            'quality_score': max(0, min(100, quality_score)),
            'grade': self.score_to_grade(quality_score),
            'factors': {
                'hook_block_rate': block_rate,
                'spec_completion_rate': completion_rate,
                'avg_clarifications': avg_clarifications
            }
        }
    
    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        hooks_metrics = self.analyze_hooks()
        specs_metrics = self.analyze_specs()
        quality = self.assess_quality()
        
        # 基于Hook指标的建議
        if hooks_metrics['pre_commit']['block_rate'] > 0.3:
            recommendations.append(
                "⚠️  Pre-commit阻止率过高(>30%)，检查Spec模板是否过于复杂"
            )
        
        if hooks_metrics['pre_commit']['block_rate'] < 0.02:
            recommendations.append(
                "💡 Pre-commit阻止率过低(<2%)，可能验证不够严格，考虑增加检查项"
            )
        
        # 基于Spec质量的建议
        if specs_metrics.get('avg_completion_rate', 0) < 70:
            recommendations.append(
                "📊 Spec平均完成率低于70%，建议拆分大Spec为小任务"
            )
        
        if specs_metrics.get('avg_clarification_count', 0) > 3:
            recommendations.append(
                "❓ 平均每个Spec有超过3个未回答的澄清问题，建议在Spec评审阶段解决"
            )
        
        # 通用建议
        if quality['quality_score'] < 60:
            recommendations.append(
                "🎯 整体质量评分较低，建议review整个Spec驱动开发流程"
            )
        
        if not recommendations:
            recommendations.append("✅ 系统运行良好，继续保持！")
        
        return recommendations
    
    def parse_audit_log(self) -> List[Dict[str, Any]]:
        """解析审计日志"""
        if not self.audit_log.exists():
            return []
        
        logs = []
        try:
            with open(self.audit_log, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"警告: 无法读取审计日志: {e}", file=sys.stderr)
        
        return logs
    
    def score_to_grade(self, score: int) -> str:
        """将分数转换为等级"""
        if score >= 90:
            return "A (优秀)"
        elif score >= 80:
            return "B (良好)"
        elif score >= 70:
            return "C (中等)"
        elif score >= 60:
            return "D (及格)"
        else:
            return "F (需改进)"
    
    def generate_report(self) -> str:
        """生成可读报告"""
        metrics = self.collect()
        
        report = f"""
# 📊 Spec驱动开发度量报告

**生成时间**: {metrics['timestamp']}  
**项目路径**: {metrics['project']}

---

## 🔧 Hook执行统计

### Pre-Commit
- 总提交数: {metrics['hooks']['pre_commit']['total_commits']}
- 被阻止数: {metrics['hooks']['pre_commit']['blocked_commits']}
- 阻止率: {metrics['hooks']['pre_commit']['block_rate']:.1%}
- 通过率: {metrics['hooks']['pre_commit']['pass_rate']:.1%}

### Pre-Push
- 总推送数: {metrics['hooks']['pre_push']['total_pushes']}
- 被阻止数: {metrics['hooks']['pre_push']['blocked_pushes']}
- 阻止率: {metrics['hooks']['pre_push']['block_rate']:.1%}
- 通过率: {metrics['hooks']['pre_push']['pass_rate']:.1%}

### Post-Commit
- 总通知数: {metrics['hooks']['post_commit']['total_notifications']}

### 总体
- 总验证次数: {metrics['hooks']['overall']['total_validations']}
- 总阻止次数: {metrics['hooks']['overall']['total_blocks']}
- 整体阻止率: {metrics['hooks']['overall']['overall_block_rate']:.1%}

---

## 📝 Spec质量

- 活跃Spec数: {metrics['specs']['active_specs']}
- 平均完成率: {metrics['specs']['avg_completion_rate']:.1%}
- 平均澄清问题数: {metrics['specs']['avg_clarification_count']}
- 含澄清问题的Spec数: {metrics['specs']['specs_with_clarifications']}

---

## 📈 生产力指标

### 最近7天
- 总事件数: {metrics['productivity']['last_7_days']['total_events']}
- 日均事件数: {metrics['productivity']['last_7_days']['avg_events_per_day']}
- 最活跃日期: {metrics['productivity']['last_7_days']['most_active_day'] or 'N/A'}

### 提交频率
- 最近7天提交数: {metrics['productivity']['commit_frequency']['commits_last_7_days']}
- 日均提交数: {metrics['productivity']['commit_frequency']['avg_commits_per_day']}

---

## ⭐ 质量评估

- **质量评分**: {metrics['quality']['quality_score']}/100
- **等级**: {metrics['quality']['grade']}

### 影响因素
- Hook阻止率: {metrics['quality']['factors']['hook_block_rate']:.1%}
- Spec完成率: {metrics['quality']['factors']['spec_completion_rate']:.1%}
- 平均澄清问题: {metrics['quality']['factors']['avg_clarifications']}

---

## 💡 改进建议

"""
        
        for i, rec in enumerate(metrics['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
---

## 📋 原始数据（JSON格式）

```json
{json.dumps(metrics, indent=2, ensure_ascii=False)}
```

---

*报告由 metrics-collector.py 自动生成*
"""
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spec驱动开发度量指标收集器')
    parser.add_argument('--project-root', type=str, default=None,
                       help='项目根目录路径（默认: 当前目录）')
    parser.add_argument('--json', action='store_true',
                       help='输出JSON格式')
    parser.add_argument('--output', type=str, default=None,
                       help='输出文件路径（默认: stdout）')
    
    args = parser.parse_args()
    
    # 创建收集器
    collector = MetricsCollector(args.project_root)
    
    # 生成报告
    if args.json:
        metrics = collector.collect()
        output = json.dumps(metrics, indent=2, ensure_ascii=False)
    else:
        output = collector.generate_report()
    
    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding='utf-8')
        print(f"✅ 报告已保存到: {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
