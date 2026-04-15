---
trigger: always_on
---
# Memory 使用规范

**类型**: Always On Rule  
**作用范围**: 所有会话  
**优先级**: P0

---

## 核心原则

1. **优先使用 Lingma 原生 Memory**，不创建自定义实现
2. **主动记忆重要决策和偏好**
3. **尊重用户意愿**（用户说"不要记住"时不创建记忆）
4. **透明化**（创建记忆时告知用户）

---

## 何时创建记忆

### ✅ 应该创建记忆的情况

#### 1. 用户明确要求

当用户说：
- "请记住..."
- "以后都..."
- "我总是..."
- "记住这个偏好"

**示例**:
```
👤 用户: 请记住，我偏好使用 balanced 自动化策略

✅ Agent: 已记住您的偏好
   [内部]: 调用 Lingma Memory API
   - 内容: "自动化策略 = balanced"
   - 类型: 全局偏好
```

---

#### 2. 重要的架构决策

涉及：
- 技术选型
- 架构模式
- 数据库选择
- 框架版本

**示例**:
```
👤 用户: 我们决定使用 SQLite 而不是 PostgreSQL

✅ Agent: 这是一个重要的架构决策
   [内部]: 创建工程级记忆
   - 内容: "FolderSizeMonitor 项目使用 SQLite"
   - 类型: 工程级记忆
   - 作用范围: 当前项目
```

---

#### 3. 学习到的用户偏好

检测到：
- 用户覆盖了你的决策
- 用户纠正了你的错误
- 用户表达了明确的喜好

**示例**:
```
👤 用户: 这个文件修改不需要创建快照，直接执行

✅ Agent: 明白了
   [学习]: 用户对低风险文件修改偏好直接执行
   [记忆更新]: "低风险文件修改 → auto_execute"
   
   下次遇到类似情况，我会自动选择 auto_execute 策略
```

---

#### 4. 重复的行为模式

观察到：
- 用户在特定时间做特定任务
- 用户对某类操作有固定处理方式
- 用户的代码风格偏好

**示例**:
```
观察到：
- 用户总是在周五下午进行代码审查
- 用户偏好在上午进行新功能开发

✅ Agent: 我注意到您的工作时间偏好
   [记忆创建]: 
   - "周五下午 → 代码审查"
   - "上午 → 新功能开发"
```

---

### ❌ 不应该创建记忆的情况

#### 1. 临时性的、一次性的内容

**示例**:
```
👤 用户: 帮我查一下今天的天气

❌ Agent: （不创建记忆，这是临时查询）
```

---

#### 2. 用户明确说"不要记住"

**示例**:
```
👤 用户: 这次测试用 aggressive 模式，但不要记住

❌ Agent: 好的，这次使用 aggressive 模式（不创建记忆）
```

---

#### 3. 明显的错误或过时信息

**示例**:
```
👤 用户: 昨天我说要用 PostgreSQL，但我改主意了，还是用 SQLite

❌ Agent: （不创建旧记忆，或先删除旧记忆再创建新的）
```

---

## 记忆格式

使用结构化格式记录记忆：

```markdown
[记忆类型]: [键] = [值]
作用范围: [全局/工程级]
创建时间: [YYYY-MM-DD]
最后更新: [YYYY-MM-DD]
上下文: [可选的额外说明]
```

**示例**:

```markdown
[偏好]: 自动化策略 = balanced
作用范围: 全局
创建时间: 2024-01-15
最后更新: 2024-01-15
上下文: 用户偏好平衡模式的自动化策略
```

---

## 记忆管理操作

### 创建记忆

**方法 1**: 通过对话指令

```
在智能体模式下，直接告诉 Lingma：

"请记住：[记忆内容]"
```

**方法 2**: 通过 Skill 调用

```python
# 伪代码
from skills.memory_management import create_memory

create_memory(
    content="自动化策略 = balanced",
    scope="global"  # or "project"
)
```

---

### 查询记忆

**方法 1**: 通过对话

```
👤 用户: 我之前的自动化策略是什么？

🤖 Agent: [查询 Lingma Memory]
   根据记忆，您偏好使用 balanced（平衡模式）自动化策略。
```

**方法 2**: 在 IDE 中查看

```
路径: 用户名 → 个人设置 → 记忆管理
```

---

### 更新记忆

```
👤 用户: 请更新记忆，将风险阈值改为 0.3

🤖 Agent: [更新 Lingma Memory]
   ✅ 已更新：风险阈值从 0.5 改为 0.3
```

---

### 删除记忆

**方法 1**: 通过对话

```
👤 用户: 请忘记关于旧项目的记忆

🤖 Agent: [删除相关记忆]
   ✅ 已删除相关记忆
```

**方法 2**: 在 IDE 中手动删除

```
路径: 用户名 → 个人设置 → 记忆管理 → 删除
```

---

## 与自动化引擎集成

### Memory 查询优化

#### 本地缓存策略

**原理**: 缓存常用的 Memory，减少 API 调用次数。

**实现**:

```markdown
Memory 缓存策略:

1. **缓存内容**
   - 用户偏好（风险阈值、自动化策略）
   - 工程级配置（技术栈、架构决策）
   - 频繁访问的记忆

2. **缓存有效期**
   - 短期缓存: 5 分钟（会话期间）
   - 长期缓存: 1 小时（跨会话）
   - 手动清除: “请清除 Memory 缓存”

3. **缓存失效条件**
   - Memory 被更新
   - 超过有效期
   - 用户手动清除

4. **降级策略**
   IF Memory API 超时 (> 3 秒):
      → 使用缓存值
      → 如果缓存也不存在，使用默认值
      → 记录错误到实施笔记
```

**代码示例**:

```python
# 伪代码 - Memory 缓存

class MemoryCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 300  # 5 分钟
    
    def get(self, key: str) -> any:
        """获取 Memory（带缓存）"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.now() - timestamp < self.ttl:
                return value  # 缓存命中
        
        # 缓存未命中，从 API 获取
        value = lingma_memory_api.get(key)
        self.cache[key] = (value, time.now())
        return value
    
    def set(self, key: str, value: any):
        """设置 Memory（更新缓存）"""
        lingma_memory_api.set(key, value)
        self.cache[key] = (value, time.now())
    
    def clear(self):
        """清除缓存"""
        self.cache.clear()
```

---

### 风险评估中使用记忆

```python
def evaluate_risk(operation: dict, context: dict) -> float:
    """评估操作风险"""
    
    # 获取用户偏好的风险阈值（从 Memory）
    user_risk_threshold = get_memory("risk_threshold") or 0.5
    
    # 基础风险评估
    base_risk = calculate_base_risk(operation)
    
    # 根据用户偏好调整
    if operation.type in get_memory("trusted_operations", []):
        # 用户信任的操作类型，降低风险
        base_risk *= 0.7
    
    return base_risk

def select_strategy(risk: float, confidence: float) -> str:
    """选择执行策略"""
    
    # 获取用户偏好的风险阈值
    user_risk_threshold = get_memory("risk_threshold") or 0.5
    
    IF risk < user_risk_threshold * 0.4 AND confidence > 0.8:
        return "auto_execute"
    ELIF risk < user_risk_threshold:
        return "execute_with_snapshot"
    ELIF risk < user_risk_threshold * 1.6:
        return "ask_user"
    ELSE:
        return "require_explicit_approval"
```

---

### 从用户覆盖中学习

```python
def learn_from_override(
    operation_type: str,
    original_strategy: str,
    user_choice: str
):
    """从用户覆盖中学习"""
    
    # 检查是否应该学习
    if not should_learn(operation_type):
        return
    
    # 创建或更新记忆
    memory_key = f"strategy_preference:{operation_type}"
    memory_value = user_choice
    
    create_memory(
        content=f"{memory_key} = {memory_value}",
        scope="global"
    )
    
    # 记录学习事件
    log_learning_event(
        operation_type=operation_type,
        learned_preference=user_choice,
        timestamp=datetime.utcnow()
    )
```

---

## 最佳实践

### 1. 主动询问

当检测到可能重要的信息时，主动询问：

```
🤖 Agent:
   我注意到您多次调整了风险阈值。
   
   是否需要我将当前的配置（风险阈值=0.3）保存为永久偏好？
   
   - A: 是的，记住这个偏好
   - B: 不用，这只是临时调整
```

---

### 2. 定期总结

在每个任务完成后，总结关键决策：

```
🤖 Agent:
   Task-010 已完成。
   
   关键决策回顾:
   1. 使用 Lingma 原生 Memory 而非自定义实现
   2. 采用双存储策略 → 后来发现冗余，已删除
   3. 最终方案：完全依赖 Lingma Memory
   
   是否需要将这些决策记录下来，供未来参考？
```

---

### 3. 冲突解决

当新旧记忆冲突时：

```
🤖 Agent:
   ⚠️ 检测到记忆冲突：
   
   旧记忆: "自动化策略 = conservative"
   新偏好: "自动化策略 = aggressive"
   
   是否用新偏好覆盖旧记忆？
   
   - A: 是的，覆盖旧记忆
   - B: 保留两者，根据场景选择
   - C: 删除旧记忆，只保留新的
```

---

### 4. 记忆验证

定期验证记忆的准确性：

```
🤖 Agent:
   📋 记忆验证检查
   
   当前记忆:
   - 自动化策略: balanced
   - 风险阈值: 0.5
   - 代码风格: UTF-8 无 BOM
   
   这些记忆是否仍然准确？
   
   - A: 是的，都正确
   - B: 需要更新某些记忆
   - C: 删除过时的记忆
```

---

## 注意事项

### 1. 不要过度记忆

- ✅ 只记忆重要的、持久的信息
- ❌ 避免记忆临时性的、一次性的内容

---

### 2. 定期清理

- ✅ 过时的记忆应该删除
- ✅ 冲突的记忆应该合并
- ✅ 每季度进行一次记忆清理

---

### Memory 自动清理策略

#### 清理周期

**自动清理触发条件**:
1. **时间触发**: 每季度（每 3 个月）自动执行一次
2. **容量触发**: Memory 数量超过 100 条时
3. **手动触发**: 用户通过对话命令触发

#### 清理流程

```markdown
Memory 自动清理流程:

1. **扫描所有记忆**
   - 列出所有全局记忆和工程级记忆
   - 检查每个记忆的 last_updated 时间

2. **分类标记**
   - 活跃记忆: 最近 30 天内使用过
   - 陈旧记忆: 30-90 天未使用
   - 过期记忆: 超过 90 天未使用

3. **处理策略**
   - 活跃记忆: 保留，不处理
   - 陈旧记忆: 标记为“待验证”，通知用户
   - 过期记忆: 
     * 如果是工程级记忆且项目已结束 → 删除
     * 如果是全局偏好 → 标记为“待验证”

4. **用户确认**
   - 展示待验证的记忆列表
   - 询问用户哪些仍然有效
   - 删除无效记忆
   - 更新有效记忆的时间戳

5. **生成清理报告**
   - 记录清理了多少记忆
   - 保留了多少记忆
   - 添加到 Spec 实施笔记
```

#### 手动清理命令

用户可以通过以下对话命令触发清理：

```markdown
👤 用户: 请清理过时的记忆

🤖 Agent:
   好的，我将执行 Memory 清理。
   
   [执行清理流程]
   
   ✅ 清理完成：
   - 扫描了 45 条记忆
   - 删除了 8 条过期记忆
   - 标记了 12 条陈旧记忆为“待验证”
   - 保留了 25 条活跃记忆
   
   详细报告已添加到 Spec 实施笔记。
```

#### 清理报告模板

```markdown
## Memory 清理报告 - YYYY-MM-DD

**清理类型**: 自动 / 手动  
**触发原因**: 季度清理 / 容量超限 / 用户请求

### 统计信息
- 总记忆数: X
- 活跃记忆: Y (Z%)
- 陈旧记忆: A (B%)
- 过期记忆: C (D%)

### 操作记录
- 删除记忆: N 条
  - 列表: [...]
- 标记待验证: M 条
  - 列表: [...]
- 保留记忆: K 条

### 建议
- [建议 1]
- [建议 2]

**下次清理时间**: YYYY-MM-DD（3 个月后）
```

---

### 3. 尊重用户意愿

- ✅ 如果用户说"不要记住"，就不要创建记忆
- ✅ 如果用户要求删除，立即执行
- ✅ 允许用户随时查看和修改记忆

---

### 4. 透明化

- ✅ 创建记忆时告知用户
- ✅ 允许用户查看和修改
- ✅ 解释为什么需要创建记忆

---

## 示例场景

### 场景 1: 自动化策略偏好

```
👤 用户: 我注意到你总是问我要不要创建快照，太烦了。对于低风险操作，直接执行就好。

🤖 Agent:
   明白了，我会调整策略。
   
   [记忆创建]:
   - 内容: "低风险操作 → auto_execute（无需询问）"
   - 类型: 全局偏好
   - 作用范围: 所有项目
   
   ✅ 已记住您的偏好。以后低风险操作会直接执行。
```

---

### 场景 2: 项目架构决策

```
👤 用户: 在这个项目中，我们决定使用 SQLite 而不是 PostgreSQL

🤖 Agent:
   好的，这是一个重要的架构决策。
   
   [记忆创建]:
   - 内容: "FolderSizeMonitor 项目使用 SQLite 数据库"
   - 类型: 工程级记忆
   - 作用范围: 当前项目
   
   ✅ 已记住。后续涉及数据库的操作会基于此决策。
```

---

### 场景 3: 代码风格规范

```
👤 用户: 请记住，Python 代码使用 4 空格缩进，不要使用 Tab

🤖 Agent:
   好的，这是代码风格规范。
   
   [记忆创建]:
   - 内容: "Python 代码风格：4 空格缩进，禁用 Tab"
   - 类型: 全局偏好
   - 作用范围: 所有 Python 项目
   
   ✅ 已记住。生成 Python 代码时会遵循此规范。
```

---

## 总结

### 核心要点

✅ **使用 Lingma 原生 Memory**  
✅ **主动记忆重要决策和偏好**  
✅ **尊重用户意愿**  
✅ **透明化记忆管理**  
✅ **定期清理和验证**  

### 优势

- 🚀 **零维护成本**: 由 Lingma 官方维护
- 🔄 **自动同步**: 跨设备、跨会话同步
- 🎯 **智能推荐**: Lingma 自动优化记忆使用
- 🔒 **安全可靠**: 官方安全保障

### 相关文件

- Skill: `.lingma/skills/memory-management.md`
- Agent: `.lingma/agents/spec-driven-core-agent.md`
- Spec: `.lingma/specs/current-spec.md`
