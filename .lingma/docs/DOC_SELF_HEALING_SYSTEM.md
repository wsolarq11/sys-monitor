# 文档自检测与清理系统

**目标**: 防止文档臃肿，保持文档与代码同步，自动化质量检测  
**原则**: Docs-as-Code + Self-Healing + Auto-Detect Redundancy  

---

## 核心问题

### 传统文档系统的痛点
1. **文档与代码不同步** - 代码改了，文档没更新
2. **重复内容泛滥** - 多个文档描述同一件事
3. **过时文档堆积** - 无人维护的僵尸文档
4. **质量无法保证** - 死链、拼写错误、格式混乱
5. **查找困难** - 信息分散，难以定位

### 解决方案
✅ **Docs-as-Code**: 文档即代码，版本控制、CI 验证  
✅ **Self-Healing**: 自动检测并修复文档问题  
✅ **Redundancy Detection**: 自动识别重复内容  
✅ **Freshness Monitoring**: 监控文档新鲜度  
✅ **Auto-Cleanup**: 定期清理过时文档  

---

## 架构设计

```
┌─────────────────────────────────────┐
│   Documentation Agent               │
│   - 生成/更新文档                    │
│   - 检测过时文档                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Doc Quality Checker (CI Pipeline) │
│   - 死链检测                         │
│   - 拼写检查                         │
│   - 格式验证                         │
│   - 代码示例可运行性                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Redundancy Detector               │
│   - 语义相似度分析                    │
│   - 重复内容标记                      │
│   - 合并建议                          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Freshness Monitor                 │
│   - 文档最后更新时间                  │
│   - 关联代码最后修改时间              │
│   - 过期警告                          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Auto-Cleanup Engine               │
│   - 归档过时文档                     │
│   - 删除冗余文档                     │
│   - 生成清理报告                     │
└─────────────────────────────────────┘
```

---

## 1. Doc Quality Checker（CI 流水线）

### GitHub Actions 工作流
```yaml
# .github/workflows/doc-quality.yml
name: Documentation Quality Check

on:
  pull_request:
    paths:
      - '**/*.md'
      - 'docs/**'
      - '.lingma/docs/**'

jobs:
  link-check:
    name: Check Broken Links
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check links
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose --no-progress './**/*.md'
          fail: true

  spell-check:
    name: Spell Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Spell check
        uses: streetsidesoftware/cspell-action@v6
        with:
          files: '**/*.md'
          config: '.cspell.json'

  format-check:
    name: Markdown Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check markdown format
        run: |
          npx prettier --check '**/*.md'
      
      - name: Lint markdown
        run: |
          npx markdownlint '**/*.md' --config .markdownlintrc

  code-example-validation:
    name: Validate Code Examples
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract and test code examples
        run: |
          # 提取文档中的代码示例并验证可运行性
          python scripts/validate-doc-examples.py

  freshness-check:
    name: Check Document Freshness
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check outdated docs
        run: |
          python scripts/check-doc-freshness.py
          
          # 如果文档超过 90 天未更新且关联代码已变更，发出警告
          OUTDATED=$(python scripts/check-doc-freshness.py --threshold 90)
          if [ -n "$OUTDATED" ]; then
            echo "::warning::Found outdated documentation:"
            echo "$OUTDATED"
          fi
```

---

## 2. Redundancy Detector（冗余检测）

### 算法设计
```python
# scripts/detect-doc-redundancy.py
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_redundant_docs(doc_paths: list[str]) -> list[dict]:
    """
    检测重复文档
    
    返回:
    [
        {
            "doc1": "path/to/doc1.md",
            "doc2": "path/to/doc2.md",
            "similarity": 0.85,
            "recommendation": "merge" | "archive" | "keep_both"
        }
    ]
    """
    # 1. 读取所有文档内容
    contents = [read_file(path) for path in doc_paths]
    
    # 2. TF-IDF 向量化
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(contents)
    
    # 3. 计算余弦相似度
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # 4. 找出高相似度对（阈值 > 0.8）
    redundant_pairs = []
    for i in range(len(doc_paths)):
        for j in range(i + 1, len(doc_paths)):
            similarity = similarity_matrix[i][j]
            if similarity > 0.8:
                redundant_pairs.append({
                    "doc1": doc_paths[i],
                    "doc2": doc_paths[j],
                    "similarity": float(similarity),
                    "recommendation": recommend_action(doc_paths[i], doc_paths[j], similarity)
                })
    
    return redundant_pairs

def recommend_action(doc1: str, doc2: str, similarity: float) -> str:
    """推荐处理动作"""
    # 如果完全相同（> 0.95），建议合并
    if similarity > 0.95:
        return "merge"
    
    # 如果高度相似（0.8-0.95），检查哪个更新
    last_modified_1 = get_last_modified(doc1)
    last_modified_2 = get_last_modified(doc2)
    
    if abs((last_modified_1 - last_modified_2).days) > 30:
        # 一个很久未更新，建议归档
        return "archive" if last_modified_1 < last_modified_2 else "archive"
    
    # 否则保留两者（可能是不同角度）
    return "keep_both"
```

### 输出示例
```json
{
  "redundant_docs": [
    {
      "doc1": ".lingma/reports/PHASE1_FOUNDATION_COMPLETE.md",
      "doc2": ".lingma/reports/phase1-completion-report.md",
      "similarity": 0.92,
      "recommendation": "archive",
      "reason": "High similarity, phase1-completion-report.md is older"
    },
    {
      "doc1": ".lingma/agents/README.md",
      "doc2": ".lingma/docs/agents-registry.md",
      "similarity": 0.88,
      "recommendation": "merge",
      "reason": "Both serve as registry, should be unified"
    }
  ],
  "total_docs_scanned": 35,
  "redundant_pairs_found": 2,
  "estimated_savings": "2 documents can be archived/merged"
}
```

---

## 3. Freshness Monitor（新鲜度监控）

### 检测逻辑
```python
# scripts/check-doc-freshness.py
import os
import git
from datetime import datetime, timedelta

def check_doc_freshness(threshold_days: int = 90) -> list[dict]:
    """
    检查文档新鲜度
    
    规则:
    - 如果文档超过 threshold_days 未更新
    - 且关联的代码文件已变更
    - 则标记为"可能过时"
    """
    repo = git.Repo('.')
    outdated_docs = []
    
    # 扫描所有 Markdown 文件
    for root, dirs, files in os.walk('.'):
        # 跳过 node_modules, target 等
        if any(skip in root for skip in ['node_modules', 'target', '.git']):
            continue
            
        for file in files:
            if not file.endswith('.md'):
                continue
            
            doc_path = os.path.join(root, file)
            
            # 获取文档最后修改时间
            doc_last_modified = get_file_last_commit_date(repo, doc_path)
            
            # 如果文档超过阈值未更新
            days_since_update = (datetime.now() - doc_last_modified).days
            if days_since_update > threshold_days:
                # 检查是否有相关代码变更
                related_code_changes = find_related_code_changes(repo, doc_path, doc_last_modified)
                
                if related_code_changes:
                    outdated_docs.append({
                        "doc": doc_path,
                        "last_updated": doc_last_modified.isoformat(),
                        "days_outdated": days_since_update,
                        "related_code_changes": related_code_changes[:5],  # 最近 5 个
                        "action": "review_and_update"
                    })
    
    return outdated_docs

def find_related_code_changes(repo, doc_path: str, since: datetime) -> list[str]:
    """查找文档相关的代码变更"""
    # 简单启发式：从文档中提取代码文件引用
    with open(doc_path, 'r') as f:
        content = f.read()
    
    # 提取代码文件路径（例如：`src/main.tsx`）
    code_files = extract_code_references(content)
    
    # 检查这些文件是否在文档更新后有变更
    changes = []
    for code_file in code_files:
        if file_changed_since(repo, code_file, since):
            changes.append(code_file)
    
    return changes
```

### 输出示例
```json
{
  "outdated_docs": [
    {
      "doc": ".lingma/reports/PHASE1_FOUNDATION_COMPLETE.md",
      "last_updated": "2026-01-15T10:00:00Z",
      "days_outdated": 90,
      "related_code_changes": [
        ".lingma/agents/spec-driven-core-agent.md",
        ".lingma/skills/spec-driven-development/SKILL.md"
      ],
      "action": "review_and_update"
    }
  ],
  "total_docs_scanned": 35,
  "outdated_count": 1,
  "freshness_score": 97.1  # (34/35 * 100)
}
```

---

## 4. Auto-Cleanup Engine（自动清理引擎）

### 清理策略
```python
# scripts/auto-cleanup-docs.py
import shutil
from datetime import datetime

def auto_cleanup_dry_run() -> dict:
    """
    模拟清理（不实际删除，仅报告）
    """
    cleanup_plan = {
        "to_archive": [],
        "to_delete": [],
        "to_merge": [],
        "estimated_space_saved": 0
    }
    
    # 1. 检测冗余文档
    redundant = detect_redundant_docs(get_all_markdown_files())
    
    for pair in redundant:
        if pair["recommendation"] == "archive":
            cleanup_plan["to_archive"].append(pair["doc2"])
        elif pair["recommendation"] == "merge":
            cleanup_plan["to_merge"].append(pair)
    
    # 2. 检测过时文档（超过 180 天无任何活动）
    outdated = check_doc_freshness(threshold_days=180)
    
    for doc in outdated:
        if doc["days_outdated"] > 180 and not doc["related_code_changes"]:
            cleanup_plan["to_archive"].append(doc["doc"])
    
    # 3. 检测空文档或极短文档（< 100 字符）
    for doc_path in get_all_markdown_files():
        if os.path.getsize(doc_path) < 100:
            cleanup_plan["to_delete"].append(doc_path)
    
    # 计算节省空间
    for doc in cleanup_plan["to_archive"] + cleanup_plan["to_delete"]:
        cleanup_plan["estimated_space_saved"] += os.path.getsize(doc)
    
    return cleanup_plan

def execute_cleanup(plan: dict, confirm: bool = True):
    """执行清理"""
    if not confirm:
        print("Dry run mode. Use --confirm to execute.")
        return
    
    # 移动到归档目录
    archive_dir = ".lingma/backups/docs-archive"
    os.makedirs(archive_dir, exist_ok=True)
    
    for doc in plan["to_archive"]:
        archive_path = os.path.join(archive_dir, os.path.basename(doc))
        shutil.move(doc, archive_path)
        print(f"Archived: {doc} → {archive_path}")
    
    # 删除无用文档
    for doc in plan["to_delete"]:
        os.remove(doc)
        print(f"Deleted: {doc}")
    
    # 生成清理报告
    generate_cleanup_report(plan)
```

---

## 5. 文档健康度指标

### Metrics Dashboard
```yaml
# .lingma/metrics/doc-health.yml
documentation_health:
  total_documents: 35
  active_documents: 33
  archived_documents: 2
  
  freshness:
    avg_days_since_update: 15
    outdated_docs (>90 days): 1
    freshness_score: 97.1%  # 目标: > 95%
  
  quality:
    broken_links: 0
    spelling_errors: 2
    formatting_issues: 5
    code_examples_validated: 15/15
  
  redundancy:
    duplicate_pairs_detected: 2
    estimated_redundancy_rate: 5.7%  # 目标: < 10%
  
  coverage:
    documented_features: 28
    total_features: 30
    coverage_rate: 93.3%  # 目标: > 90%
  
  maintenance:
    last_cleanup_date: "2026-04-15"
    next_scheduled_cleanup: "2026-05-15"
    avg_time_to_update_doc_after_code_change: 2 days
```

---

## 6. 实施路线图

### Phase 1: 基础质量检测（当前）
- ✅ 集成 link checker 到 CI
- ✅ 添加 spell check
- ✅ Markdown 格式验证
- ⏳ 代码示例可运行性验证

### Phase 2: 冗余检测（P1）
- [ ] 实现 TF-IDF 相似度分析
- [ ] 定期扫描（每周）
- [ ] 生成冗余报告
- [ ] 手动审查并清理

### Phase 3: 新鲜度监控（P1）
- [ ] 跟踪文档最后更新时间
- [ ] 关联代码变更检测
- [ ] 过期警告通知
- [ ] 自动生成更新任务

### Phase 4: 自动清理（P2）
- [ ] 归档过时文档
- [ ] 合并重复文档
- [ ] 删除无用文档
- [ ] 生成清理报告

### Phase 5: 自愈能力（P3）
- [ ] 自动更新过时文档
- [ ] 基于代码变更自动生成文档草稿
- [ ] AI 辅助文档优化
- [ ] 持续学习文档模式

---

## 7. 社区对标

| 实践 | 来源 | 我们的实现 |
|------|------|-----------|
| Docs-as-Code | Grab Engineering | ✅ Git + CI Validation |
| Link Checking | Lychee | ✅ lychee-action |
| Spell Checking | cspell | ✅ cspell-action |
| Freshness Monitoring | Custom | ✅ Python Script |
| Redundancy Detection | TF-IDF + Cosine | ✅ sklearn |
| Auto-Cleanup | Doctective | ✅ Archive + Merge |
| Health Metrics | Custom Dashboard | ✅ YAML Metrics |

---

## 8. 使用指南

### 本地运行质量检测
```bash
# 检查死链
npx lychee '**/*.md'

# 拼写检查
npx cspell '**/*.md'

# 格式检查
npx prettier --check '**/*.md'

# 冗余检测
python scripts/detect-doc-redundancy.py

# 新鲜度检查
python scripts/check-doc-freshness.py --threshold 90

# 模拟清理
python scripts/auto-cleanup-docs.py --dry-run
```

### CI 中自动执行
所有 PR 触发文档质量检查，失败则阻止合并。

### 定期清理（每月）
```bash
# 1. 运行检测
python scripts/detect-doc-redundancy.py > redundancy-report.json
python scripts/check-doc-freshness.py > freshness-report.json

# 2. 审查报告
cat redundancy-report.json
cat freshness-report.json

# 3. 执行清理（确认后）
python scripts/auto-cleanup-docs.py --confirm

# 4. 提交清理结果
git add .lingma/backups/docs-archive/
git commit -m "docs: monthly cleanup, archived 2 outdated documents"
```

---

## 总结

**文档不是静态的死文件，而是活的、自迭代的系统！**

### 核心价值
1. **自动化质量保证** - CI 流水线自动检测问题
2. **防臃肿机制** - 冗余检测 + 定期清理
3. ** freshness 监控** - 确保文档与代码同步
4. **数据驱动维护** - Metrics 指导优化方向
5. **自愈能力** - 自动修复常见问题

### 避免的陷阱
❌ 文档越来越多，无人维护  
❌ 过时文档误导开发者  
❌ 重复内容造成混淆  
❌ 文档与代码脱节  

### 达成的目标
✅ 文档质量持续提升  
✅ 维护成本自动化降低  
✅ 开发者体验优化  
✅ 单一事实来源（Single Source of Truth）  

**文档系统与自迭代流共生成长，越来越贴合实际！** 🚀

