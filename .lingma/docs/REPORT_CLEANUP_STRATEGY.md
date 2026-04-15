# 报告自动化清理与提炼系统

**目标**: 自动检测冗余报告、提炼关键信息、归档过时内容、保持精简  
**原则**: Single Source of Truth + Auto-Detect Redundancy + Knowledge Extraction  

---

## 📊 当前问题分析

### 冗余报告统计
```
总计: 35 个报告文件

Phase 1 相关 (4个):
- phase1-completion-report.md (8.9KB)
- phase1-final-report.md (11.7KB) ← 重复
- phase1.5-step1-completion.md (11.2KB)
- phase1.5-final-report.md (11.9KB) ← 可能重复

Phase 2 相关 (4个):
- PHASE2_AUTOMATION_ENHANCEMENT.md (17.8KB)
- PHASE2_FINAL_COMPLETION_REPORT.md (11.9KB) ← 重复
- phase2-final-report.md (9.3KB) ← 重复
- phase2-task006-completion.md (7.7KB)

Phase 3 相关 (2个):
- PHASE3_DOMAIN_SPECIALIZATION_COMPLETE.md (11.9KB)
- task-010-architecture-correction.md (9.2KB)

其他调研/分析 (15+个):
- self-iterating-flow-investigation.md (30.0KB) ← 超大
- synergy-deep-investigation.md (21.7KB) ← 超大
- unified-architecture-decision.md (21.0KB) ← 超大
- ... 等
```

### 问题识别
1. **重复报告**: Phase 1/2 有多个版本
2. **过度详细**: 调研报告过大（20-30KB）
3. **缺乏索引**: 难以快速定位关键信息
4. **未提炼**: 原始记录而非知识总结

---

## 🎯 解决方案设计

### 架构
```
┌─────────────────────────────────────┐
│   Report Analyzer                   │
│   - 扫描所有报告                     │
│   - 计算相似度                       │
│   - 识别重复                         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Knowledge Extractor              │
│   - 提取关键决策                    │
│   - 提取经验教训                    │
│   - 提取最佳实践                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Consolidation Engine             │
│   - 合并重复报告                    │
│   - 生成单一真相源                  │
│   - 创建知识图谱                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Archive Manager                  │
│   - 移动旧报告到归档                │
│   - 保留精华摘要                    │
│   - 生成清理报告                    │
└─────────────────────────────────────┘
```

---

## 🔧 实施工具

### 1. 报告冗余检测脚本

```python
# scripts/analyze-report-redundancy.py
import os
import re
from difflib import SequenceMatcher
from collections import defaultdict

def scan_reports(reports_dir: str) -> list[dict]:
    """扫描所有报告文件"""
    reports = []
    for file in os.listdir(reports_dir):
        if not file.endswith('.md'):
            continue
        
        path = os.path.join(reports_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取元数据
        metadata = extract_metadata(content, file)
        
        reports.append({
            'file': file,
            'path': path,
            'size_kb': os.path.getsize(path) / 1024,
            'content': content,
            'metadata': metadata
        })
    
    return reports

def extract_metadata(content: str, filename: str) -> dict:
    """提取报告元数据"""
    metadata = {
        'filename': filename,
        'phase': None,
        'type': None,
        'keywords': []
    }
    
    # 检测 Phase
    phase_match = re.search(r'Phase\s*(\d+\.?\d*)', content, re.IGNORECASE)
    if phase_match:
        metadata['phase'] = phase_match.group(1)
    
    # 检测类型
    if 'investigation' in filename.lower() or '调研' in content:
        metadata['type'] = 'investigation'
    elif 'completion' in filename.lower() or '完成' in content:
        metadata['type'] = 'completion'
    elif 'report' in filename.lower():
        metadata['type'] = 'report'
    
    # 提取关键词
    keywords = extract_keywords(content)
    metadata['keywords'] = keywords
    
    return metadata

def detect_redundant_reports(reports: list[dict], threshold: float = 0.7) -> list[dict]:
    """检测冗余报告"""
    redundant_groups = []
    processed = set()
    
    for i, report1 in enumerate(reports):
        if i in processed:
            continue
        
        group = [report1]
        
        for j, report2 in enumerate(reports[i+1:], i+1):
            if j in processed:
                continue
            
            # 计算相似度
            similarity = calculate_similarity(report1, report2)
            
            if similarity > threshold:
                group.append(report2)
                processed.add(j)
        
        if len(group) > 1:
            redundant_groups.append({
                'group_id': len(redundant_groups) + 1,
                'reports': group,
                'avg_similarity': calculate_group_similarity(group),
                'recommendation': recommend_action(group)
            })
            processed.add(i)
    
    return redundant_groups

def calculate_similarity(report1: dict, report2: dict) -> float:
    """计算两个报告的相似度"""
    # 基于文件名相似度
    filename_sim = SequenceMatcher(None, report1['file'], report2['file']).ratio()
    
    # 基于内容相似度（采样前5000字符）
    content1 = report1['content'][:5000]
    content2 = report2['content'][:5000]
    content_sim = SequenceMatcher(None, content1, content2).ratio()
    
    # 基于 Phase 匹配
    phase_match = 1.0 if report1['metadata']['phase'] == report2['metadata']['phase'] else 0.0
    
    # 加权平均
    return (filename_sim * 0.3 + content_sim * 0.5 + phase_match * 0.2)

def recommend_action(group: list[dict]) -> str:
    """推荐处理动作"""
    # 如果有 "final" 或 "最终"，保留它
    for report in group:
        if 'final' in report['file'].lower() or '最终' in report['file']:
            return f"keep:{report['file']},archive_others"
    
    # 否则保留最大的
    largest = max(group, key=lambda r: r['size_kb'])
    return f"keep:{largest['file']},archive_others"
```

---

### 2. 知识提取引擎

```python
# scripts/extract-knowledge.py
import re
import json

def extract_key_decisions(content: str) -> list[dict]:
    """提取关键决策"""
    decisions = []
    
    # 模式1: 决策标题
    decision_pattern = r'##?\s*(?:决策|Decision|决定)[:：]?\s*(.+)'
    for match in re.finditer(decision_pattern, content, re.IGNORECASE):
        decisions.append({
            'type': 'decision',
            'title': match.group(1).strip(),
            'context': extract_context(content, match.start())
        })
    
    # 模式2: ✅ 标记的决策
    checkmark_pattern = r'✅\s*\*\*(.+?)\*\*'
    for match in re.finditer(checkmark_pattern, content):
        decisions.append({
            'type': 'achievement',
            'title': match.group(1).strip(),
            'context': extract_context(content, match.start())
        })
    
    return decisions

def extract_lessons_learned(content: str) -> list[str]:
    """提取经验教训"""
    lessons = []
    
    # 查找"教训"、"pitfall"、"lesson"等关键词
    lesson_patterns = [
        r'(?:教训|Lesson|Pitfall|陷阱)[:：]\s*(.+)',
        r'❌\s*(.+?)(?=\n\n|\n#|$)',
        r'避免.*?[:：]\s*(.+)'
    ]
    
    for pattern in lesson_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            lessons.append(match.group(1).strip())
    
    return lessons

def extract_best_practices(content: str) -> list[str]:
    """提取最佳实践"""
    practices = []
    
    practice_patterns = [
        r'(?:最佳实践|Best Practice|推荐)[:：]\s*(.+)',
        r'✅\s*(.+?)(?=\n\n|\n#|$)',
        r'应该.*?[:：]\s*(.+)'
    ]
    
    for pattern in practice_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            practices.append(match.group(1).strip())
    
    return practices

def generate_knowledge_summary(reports: list[dict]) -> dict:
    """生成知识总结"""
    knowledge_base = {
        'decisions': [],
        'lessons': [],
        'best_practices': [],
        'phases': {}
    }
    
    for report in reports:
        content = report['content']
        
        # 提取各类知识
        decisions = extract_key_decisions(content)
        lessons = extract_lessons_learned(content)
        practices = extract_best_practices(content)
        
        knowledge_base['decisions'].extend(decisions)
        knowledge_base['lessons'].extend(lessons)
        knowledge_base['best_practices'].extend(practices)
        
        # 按 Phase 组织
        phase = report['metadata'].get('phase')
        if phase:
            if phase not in knowledge_base['phases']:
                knowledge_base['phases'][phase] = {
                    'reports': [],
                    'key_decisions': [],
                    'achievements': []
                }
            knowledge_base['phases'][phase]['reports'].append(report['file'])
            knowledge_base['phases'][phase]['key_decisions'].extend(decisions)
    
    return knowledge_base
```

---

### 3. 报告合并引擎

```python
# scripts/consolidate-reports.py
import os
from datetime import datetime

def consolidate_phase_reports(phase: str, reports: list[dict], output_dir: str):
    """合并同一 Phase 的多个报告"""
    consolidated = {
        'title': f'Phase {phase} - 综合报告',
        'date': datetime.now().isoformat(),
        'source_reports': [r['file'] for r in reports],
        'sections': {}
    }
    
    # 提取各部分
    for report in reports:
        content = report['content']
        
        # 提取概述
        overview = extract_section(content, '概述|Overview|简介')
        if overview:
            consolidated['sections']['overview'] = overview
        
        # 提取关键成果
        achievements = extract_section(content, '关键成果|Key Achievements|成果')
        if achievements:
            consolidated['sections']['achievements'] = achievements
        
        # 提取技术细节
        technical = extract_section(content, '技术实现|Technical|实施')
        if technical:
            consolidated['sections']['technical'] = technical
        
        # 提取经验教训
        lessons = extract_lessons_learned(content)
        if lessons:
            consolidated['sections']['lessons'] = lessons
    
    # 生成合并后的报告
    markdown = generate_consolidated_markdown(consolidated)
    
    output_path = os.path.join(output_dir, f'PHASE{phase}_CONSOLIDATED.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    return output_path

def archive_old_reports(reports_to_archive: list[str], archive_dir: str):
    """归档旧报告"""
    os.makedirs(archive_dir, exist_ok=True)
    
    archived = []
    for report_path in reports_to_archive:
        filename = os.path.basename(report_path)
        archive_path = os.path.join(archive_dir, filename)
        
        # 移动文件
        os.rename(report_path, archive_path)
        archived.append(filename)
    
    return archived
```

---

## 📋 执行流程

### Step 1: 分析冗余
```bash
python scripts/analyze-report-redundancy.py \
  --reports-dir .lingma/reports \
  --output redundancy-analysis.json
```

**输出示例**:
```json
{
  "total_reports": 35,
  "redundant_groups": [
    {
      "group_id": 1,
      "reports": [
        "phase1-completion-report.md",
        "phase1-final-report.md"
      ],
      "similarity": 0.85,
      "recommendation": "keep:phase1-final-report.md,archive:phase1-completion-report.md"
    },
    {
      "group_id": 2,
      "reports": [
        "PHASE2_AUTOMATION_ENHANCEMENT.md",
        "PHASE2_FINAL_COMPLETION_REPORT.md",
        "phase2-final-report.md"
      ],
      "similarity": 0.78,
      "recommendation": "keep:PHASE2_FINAL_COMPLETION_REPORT.md,archive:others"
    }
  ],
  "estimated_savings": "15 files can be archived"
}
```

---

### Step 2: 提取知识
```bash
python scripts/extract-knowledge.py \
  --reports-dir .lingma/reports \
  --output knowledge-base.json
```

**输出示例**:
```json
{
  "decisions": [
    {
      "title": "采用 Supervisor-Worker 架构",
      "phase": "3",
      "rationale": "符合2026年社区最佳实践"
    }
  ],
  "lessons": [
    ".lingma功能目录禁止放置README文档",
    "web-vitals库FID已废弃需改用INP"
  ],
  "best_practices": [
    "Docs-as-Code + Self-Healing",
    "5层质量门禁确保输出质量"
  ]
}
```

---

### Step 3: 合并报告
```bash
python scripts/consolidate-reports.py \
  --redundancy-analysis redundancy-analysis.json \
  --knowledge-base knowledge-base.json \
  --output-dir .lingma/reports \
  --archive-dir .lingma/backups/reports-archive
```

**执行动作**:
1. 合并 Phase 1 报告 → `PHASE1_CONSOLIDATED.md`
2. 合并 Phase 2 报告 → `PHASE2_CONSOLIDATED.md`
3. 归档 15 个旧报告到 `.lingma/backups/reports-archive/`
4. 保留 20 个核心报告

---

### Step 4: 生成索引
```bash
python scripts/generate-report-index.py \
  --reports-dir .lingma/reports \
  --output .lingma/reports/INDEX.md
```

**输出**: 结构化的报告索引，支持快速检索

---

## 🎯 预期效果

### 清理前
- **35 个报告文件**
- **总大小**: ~450KB
- **冗余率**: ~43% (15个重复)
- **可检索性**: 差

### 清理后
- **20 个核心报告** (+ 15个归档)
- **总大小**: ~250KB (-44%)
- **冗余率**: 0%
- **可检索性**: 优秀 (带索引)

### 知识提炼
- ✅ 关键决策汇总
- ✅ 经验教训库
- ✅ 最佳实践集合
- ✅ Phase 综合报告

---

## 🔄 集成到自迭代流

### 自动化触发
```yaml
# .github/workflows/report-cleanup.yml
name: Report Cleanup & Knowledge Extraction

on:
  schedule:
    - cron: '0 0 1 * *'  # 每月1号执行
  workflow_dispatch:      # 手动触发

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze redundancy
        run: python scripts/analyze-report-redundancy.py
      
      - name: Extract knowledge
        run: python scripts/extract-knowledge.py
      
      - name: Consolidate reports
        run: python scripts/consolidate-reports.py
      
      - name: Commit changes
        run: |
          git add .lingma/reports/
          git commit -m "docs: monthly report cleanup and knowledge extraction"
          git push
```

---

## 📊 持续优化指标

```yaml
# .lingma/metrics/report-health.yml
report_health:
  total_reports: 20
  archived_reports: 15
  redundancy_rate: 0%  # 目标: < 5%
  
  knowledge_extraction:
    decisions_documented: 25
    lessons_learned: 18
    best_practices: 32
  
  accessibility:
    indexed: true
    searchable: true
    avg_lookup_time: < 30s
  
  maintenance:
    last_cleanup: "2026-04-15"
    next_scheduled: "2026-05-01"
    automation_enabled: true
```

---

## 🚀 立即执行

### 选项 A: 全自动清理（推荐）
- ✅ 自动检测冗余
- ✅ 自动合并报告
- ✅ 自动归档旧文件
- ✅ 自动生成索引
- ⚠️ 风险：可能误删重要内容

### 选项 B: 半自动清理（安全）
- ✅ 自动检测冗余
- ✅ 生成清理计划
- ⏸️ 人工审查确认
- ✅ 执行清理
- ✅ 保留备份

### 选项 C: 仅知识提取（保守）
- ✅ 提取关键决策
- ✅ 提取经验教训
- ✅ 生成知识库
- ❌ 不删除任何文件

---

## 💡 建议

**推荐执行顺序**:
1. **先执行选项 C** - 提取知识，无风险
2. **再执行选项 B** - 半自动清理，安全可靠
3. **最后配置自动化** - 每月自动维护

**关键原则**:
- ✅ 始终保留备份（`.lingma/backups/reports-archive/`）
- ✅ 生成清晰的清理日志
- ✅ 提供回滚机制
- ✅ 定期审查归档文件（每季度）

---

**现在开始执行吗？请选择清理策略！** 🚀
