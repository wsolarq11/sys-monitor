#!/usr/bin/env python3
"""
报告冗余分析与知识提取工具
自动检测冗余报告、提炼关键信息、生成清理建议
"""

import os
import re
import json
import sys
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict
from datetime import datetime

class ReportAnalyzer:
    def __init__(self, reports_dir: str):
        self.reports_dir = Path(reports_dir)
        self.reports = []
        self.redundant_groups = []
        self.knowledge_base = {
            'decisions': [],
            'lessons': [],
            'best_practices': [],
            'phases': {},
            'achievements': []
        }
    
    def scan_reports(self):
        """扫描所有报告文件"""
        print(f"📂 扫描报告目录: {self.reports_dir}")
        
        for file in sorted(self.reports_dir.glob('*.md')):
            if file.name.startswith('.'):
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self._extract_metadata(content, file.name)
            
            self.reports.append({
                'file': file.name,
                'path': str(file),
                'size_kb': round(file.stat().st_size / 1024, 2),
                'content': content,
                'metadata': metadata
            })
        
        print(f"✅ 找到 {len(self.reports)} 个报告文件\n")
    
    def _extract_metadata(self, content: str, filename: str) -> dict:
        """提取报告元数据"""
        metadata = {
            'filename': filename,
            'phase': None,
            'type': None,
            'keywords': [],
            'date': None
        }
        
        # 检测 Phase
        phase_match = re.search(r'Phase\s*(\d+\.?\d*)', content, re.IGNORECASE)
        if phase_match:
            metadata['phase'] = phase_match.group(1)
        
        # 检测类型
        filename_lower = filename.lower()
        if 'investigation' in filename_lower or '调研' in content[:500]:
            metadata['type'] = 'investigation'
        elif 'completion' in filename_lower or '完成' in content[:500]:
            metadata['type'] = 'completion'
        elif 'report' in filename_lower:
            metadata['type'] = 'report'
        elif 'checklist' in filename_lower:
            metadata['type'] = 'checklist'
        else:
            metadata['type'] = 'other'
        
        # 提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content[:500])
        if date_match:
            metadata['date'] = date_match.group(1)
        
        return metadata
    
    def detect_redundancy(self, threshold: float = 0.7):
        """检测冗余报告"""
        print("🔍 检测冗余报告...")
        
        processed = set()
        
        for i, report1 in enumerate(self.reports):
            if i in processed:
                continue
            
            group = [report1]
            
            for j, report2 in enumerate(self.reports[i+1:], i+1):
                if j in processed:
                    continue
                
                similarity = self._calculate_similarity(report1, report2)
                
                if similarity > threshold:
                    group.append(report2)
                    processed.add(j)
            
            if len(group) > 1:
                recommendation = self._recommend_action(group)
                self.redundant_groups.append({
                    'group_id': len(self.redundant_groups) + 1,
                    'reports': [r['file'] for r in group],
                    'avg_similarity': round(self._calculate_group_similarity(group), 2),
                    'recommendation': recommendation
                })
                processed.add(i)
        
        print(f"✅ 发现 {len(self.redundant_groups)} 组冗余报告\n")
    
    def _calculate_similarity(self, report1: dict, report2: dict) -> float:
        """计算两个报告的相似度"""
        # 基于文件名相似度
        filename_sim = SequenceMatcher(None, report1['file'], report2['file']).ratio()
        
        # 基于内容相似度（采样前5000字符）
        content1 = report1['content'][:5000]
        content2 = report2['content'][:5000]
        content_sim = SequenceMatcher(None, content1, content2).ratio()
        
        # 基于 Phase 匹配
        phase1 = report1['metadata'].get('phase')
        phase2 = report2['metadata'].get('phase')
        phase_match = 1.0 if phase1 and phase1 == phase2 else 0.0
        
        # 加权平均
        return (filename_sim * 0.3 + content_sim * 0.5 + phase_match * 0.2)
    
    def _calculate_group_similarity(self, group: list) -> float:
        """计算组内平均相似度"""
        if len(group) < 2:
            return 0.0
        
        similarities = []
        for i in range(len(group)):
            for j in range(i+1, len(group)):
                sim = self._calculate_similarity(group[i], group[j])
                similarities.append(sim)
        
        return sum(similarities) / len(similarities)
    
    def _recommend_action(self, group: list) -> dict:
        """推荐处理动作"""
        # 优先级：final > consolidated > completion > others
        priority_keywords = ['final', '最终', 'consolidated', '综合', 'completion', '完成']
        
        best_report = None
        best_score = -1
        
        for report in group:
            score = 0
            filename_lower = report['file'].lower()
            
            for keyword in priority_keywords:
                if keyword in filename_lower:
                    score += 10
            
            # 优先选择较大的文件（通常更完整）
            score += report['size_kb'] / 100
            
            if score > best_score:
                best_score = score
                best_report = report
        
        archive_list = [r['file'] for r in group if r['file'] != best_report['file']]
        
        return {
            'keep': best_report['file'],
            'archive': archive_list,
            'reason': f"保留最完整的报告，归档 {len(archive_list)} 个重复版本"
        }
    
    def extract_knowledge(self):
        """从所有报告中提取知识"""
        print("🧠 提取知识库...")
        
        for report in self.reports:
            content = report['content']
            phase = report['metadata'].get('phase')
            
            # 提取关键决策
            decisions = self._extract_decisions(content)
            self.knowledge_base['decisions'].extend([
                {**d, 'source': report['file'], 'phase': phase} 
                for d in decisions
            ])
            
            # 提取经验教训
            lessons = self._extract_lessons(content)
            self.knowledge_base['lessons'].extend([
                {'lesson': l, 'source': report['file'], 'phase': phase}
                for l in lessons
            ])
            
            # 提取最佳实践
            practices = self._extract_best_practices(content)
            self.knowledge_base['best_practices'].extend([
                {'practice': p, 'source': report['file'], 'phase': phase}
                for p in practices
            ])
            
            # 提取成果
            achievements = self._extract_achievements(content)
            self.knowledge_base['achievements'].extend([
                {'achievement': a, 'source': report['file'], 'phase': phase}
                for a in achievements
            ])
            
            # 按 Phase 组织
            if phase:
                if phase not in self.knowledge_base['phases']:
                    self.knowledge_base['phases'][phase] = {
                        'reports': [],
                        'decision_count': 0,
                        'lesson_count': 0
                    }
                self.knowledge_base['phases'][phase]['reports'].append(report['file'])
                self.knowledge_base['phases'][phase]['decision_count'] += len(decisions)
                self.knowledge_base['phases'][phase]['lesson_count'] += len(lessons)
        
        print(f"✅ 提取完成:\n")
        print(f"   - 关键决策: {len(self.knowledge_base['decisions'])} 条")
        print(f"   - 经验教训: {len(self.knowledge_base['lessons'])} 条")
        print(f"   - 最佳实践: {len(self.knowledge_base['best_practices'])} 条")
        print(f"   - 项目成果: {len(self.knowledge_base['achievements'])} 项\n")
    
    def _extract_decisions(self, content: str) -> list[str]:
        """提取关键决策"""
        decisions = []
        
        # 模式1: ✅ 标记的重要决策
        pattern1 = r'✅\s*\*\*(.+?)\*\*'
        for match in re.finditer(pattern1, content):
            decision = match.group(1).strip()
            if len(decision) > 10 and len(decision) < 200:
                decisions.append(decision)
        
        # 模式2: "决策"标题
        pattern2 = r'##?\s*(?:决策|Decision)[:：]?\s*(.+?)(?=\n#|\n\n|$)'
        for match in re.finditer(pattern2, content, re.IGNORECASE | re.DOTALL):
            decision = match.group(1).strip()
            if len(decision) > 10:
                decisions.append(decision[:200])
        
        return decisions[:10]  # 限制每个报告最多10条
    
    def _extract_lessons(self, content: str) -> list[str]:
        """提取经验教训"""
        lessons = []
        
        patterns = [
            r'❌\s*(.+?)(?=\n\n|\n#|$)',
            r'(?:教训|Lesson|Pitfall|陷阱|避免)[:：]\s*(.+?)(?=\n\n|\n#|$)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                lesson = match.group(1).strip()
                if len(lesson) > 10 and len(lesson) < 300:
                    lessons.append(lesson)
        
        return list(set(lessons))[:10]  # 去重并限制数量
    
    def _extract_best_practices(self, content: str) -> list[str]:
        """提取最佳实践"""
        practices = []
        
        patterns = [
            r'(?:最佳实践|Best Practice|推荐|应该)[:：]\s*(.+?)(?=\n\n|\n#|$)',
            r'✅\s*(.+?)(?=\n\n|\n#|$)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                practice = match.group(1).strip()
                if len(practice) > 10 and len(practice) < 300:
                    practices.append(practice)
        
        return list(set(practices))[:10]
    
    def _extract_achievements(self, content: str) -> list[str]:
        """提取项目成果"""
        achievements = []
        
        # 查找统计表格或列表
        pattern = r'\*\*(?:指标|Metric|成果|Achievement)\*\*.*?\|.*?(\d+.*?%)'
        for match in re.finditer(pattern, content, re.DOTALL):
            achievements.append(match.group(0).strip()[:150])
        
        # 查找完成标记
        pattern2 = r'✅\s*(?:完成|Complete|实现|Implement)[:：]?\s*(.+?)(?=\n\n|\n#|$)'
        for match in re.finditer(pattern2, content, re.IGNORECASE):
            achievements.append(match.group(1).strip()[:150])
        
        return list(set(achievements))[:5]
    
    def generate_report(self, output_file: str):
        """生成分析报告"""
        print(f"📝 生成分析报告: {output_file}\n")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_reports': len(self.reports),
                'total_size_kb': round(sum(r['size_kb'] for r in self.reports), 2),
                'redundant_groups': len(self.redundant_groups),
                'files_to_archive': sum(len(g['recommendation']['archive']) for g in self.redundant_groups),
                'estimated_savings_kb': round(
                    sum(r['size_kb'] for g in self.redundant_groups 
                        for r in self.reports 
                        if r['file'] in g['recommendation']['archive']), 2
                )
            },
            'redundant_groups': self.redundant_groups,
            'knowledge_base': self.knowledge_base,
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        self._print_summary(analysis)
        
        return analysis
    
    def _generate_recommendations(self) -> list[dict]:
        """生成清理建议"""
        recommendations = []
        
        # 建议1: 归档冗余报告
        if self.redundant_groups:
            total_archive = sum(len(g['recommendation']['archive']) for g in self.redundant_groups)
            recommendations.append({
                'priority': 'HIGH',
                'action': 'ARCHIVE_REDUNDANT',
                'description': f'归档 {total_archive} 个冗余报告',
                'impact': f'减少 ~{sum(r["size_kb"] for g in self.redundant_groups for r in self.reports if r["file"] in g["recommendation"]["archive"]):.0f}KB',
                'risk': 'LOW'
            })
        
        # 建议2: 合并 Phase 报告
        phases_with_multiple = [p for p in self.knowledge_base['phases'].values() if len(p['reports']) > 2]
        if phases_with_multiple:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'CONSOLIDATE_PHASES',
                'description': f'合并 {len(phases_with_multiple)} 个 Phase 的多个报告',
                'impact': '提高可检索性',
                'risk': 'LOW'
            })
        
        # 建议3: 生成知识索引
        if self.knowledge_base['decisions'] or self.knowledge_base['lessons']:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'GENERATE_KNOWLEDGE_INDEX',
                'description': '生成知识库索引文件',
                'impact': '快速查找关键信息',
                'risk': 'NONE'
            })
        
        return recommendations
    
    def _print_summary(self, analysis: dict):
        """打印分析摘要"""
        summary = analysis['summary']
        
        print("=" * 60)
        print("📊 报告分析摘要")
        print("=" * 60)
        print(f"总报告数:       {summary['total_reports']}")
        print(f"总大小:         {summary['total_size_kb']} KB")
        print(f"冗余组数:       {summary['redundant_groups']}")
        print(f"可归档文件:     {summary['files_to_archive']}")
        print(f"预计节省空间:   {summary['estimated_savings_kb']} KB")
        print()
        
        if analysis['recommendations']:
            print("💡 建议操作:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"{i}. [{rec['priority']}] {rec['action']}")
                print(f"   {rec['description']}")
                print(f"   影响: {rec['impact']} | 风险: {rec['risk']}")
                print()
        
        print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='报告冗余分析与知识提取工具')
    parser.add_argument('--reports-dir', default='.lingma/reports', help='报告目录')
    parser.add_argument('--output', default='.lingma/reports/ANALYSIS_RESULT.json', help='输出文件')
    parser.add_argument('--threshold', type=float, default=0.7, help='相似度阈值 (0-1)')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.reports_dir):
        print(f"❌ 错误: 目录不存在: {args.reports_dir}")
        sys.exit(1)
    
    # 执行分析
    analyzer = ReportAnalyzer(args.reports_dir)
    analyzer.scan_reports()
    analyzer.detect_redundancy(threshold=args.threshold)
    analyzer.extract_knowledge()
    analyzer.generate_report(args.output)
    
    print(f"\n✅ 分析完成！结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
