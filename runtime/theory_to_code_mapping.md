# 本原展开论→代码映射指南

**目的**：显式地映射本原展开论的核心概念 → 系统中的代码实现，使开发者理解每个字段、方法、配置与理论的对应关系。

**使用者**：维护脚本、扩展功能、理解设计决策的开发者。

---

## 核心概念→代码映射总览

| 理论概念 | 核心含义 | 代码体现 | 相关文件 |
|---------|--------|--------|--------|
| **法则属性** | 约束、规律、使结构成为可能的条件 | TTAF D2、约束字段、AGENT_PROFILE法则面 | task_theory_application_framework.md, AGENT_PROFILE.md |
| **展开属性** | 生成、创意、在约束中新状态的涌现 | expansion_type字段、PORF观察5、多算法方案 | evolution_candidate_manager.py, PORF_OBSERVATION5_EXAMPLES.md |
| **连续性** | 系统通过反馈循环自我完善的能力 | PORF完整5维观察、evolution_candidate生命周期、TTAF→执行→反馈 | practice_observation_framework.md, evolution_cycle.md |
| **局限性** | 系统在某个时刻的边界和约束 | PORF观察2、TTAF D4、limitation字段 | practice_observation_framework.md, task_theory_application_framework.md |
| **希望** | 在局限中仍开放于更高可能性的能力 | HOPE_STATE.md、PORF观察5、hope_direction字段、TTAF D6 | HOPE_STATE.md, PORF_OBSERVATION5_EXAMPLES.md |

---

## 逐概念详解

### 1️⃣ 法则属性（Law Attributes）

**理论定义**：不是"禁止"，而是"使结构得以成形的条件"。约束不是局限，而是可能性的基础。

**代码体现位置**：

#### A. TTAF D2 的"法则属性面"
**文件**：`runtime/task_theory_application_framework.md`

```markdown
【D2 法则-展开识别】
法则属性面（约束面）：
  - 什么边界/规律使这个任务的结构成为可能？
  - 不是"不能做什么"，而是"因为有这些约束，什么结构才得以成形"
```

**实现逻辑**：
- 用户在TTAF D2中识别法则属性面
- 这些约束被明确写入feedback的`limitation`字段
- 脚本`feedback_classifier.py`和`evolution_candidate_manager.py`会提取这些约束

#### B. AGENT_PROFILE 中的"法则属性面"
**文件**：`agents/codex/AGENT_PROFILE.md`（模板）

```markdown
### 法则属性面（Constraint-Enforcing）

这个工具擅长识别/施加/维持什么约束或规律？
- 编程语言约束（Python类型系统、语法）
- 代码规范（PEP 8、Google风格）
- 性能约束（时间/空间复杂度）
- ...
```

**实现逻辑**：
- 每个AGENT_PROFILE描述该工具的法则属性强度
- TTAF_config根据工具的法则属性调整D2的重点
- 在与工具协作时，用户可根据工具的法则强度选择是否使用

#### C. 脚本中的约束处理
**文件**：`scripts/evolution_candidate_manager.py`

```python
def enrich_candidate_from_hope_tracking(self, candidate, hope_tracking_data):
    # 从hope_tracking中提取约束相关信息
    limitation = hope_tracking_data.get('limitation_encountered', '')
    
    if '约束' in limitation or '限制' in limitation:
        candidate['expansion_type'] = '法则属性型'  # 改进主要涉及约束
    
    return candidate
```

**含义**：脚本识别当改进方向是"应对约束"时，标记为"法则属性型"。

---

### 2️⃣ 展开属性（Expansion Attributes）

**理论定义**：在约束中生成新状态、新可能性的能力。是"有生命力的"系统的标志。

**代码体现位置**：

#### A. expansion_type 字段
**文件**：`scripts/evolution_candidate_manager.py`

```python
candidate = {
    'expansion_type': 'pending',  # 待用户确认：法则属性型/展开属性型/混合型
    'hope_direction': '',         # 待用户填写：一句话描述希望方向
    'opens_new_possibility': '',  # 待用户确认：是/否及其原因
}
```

**含义**：
- `expansion_type`字段的三个值分别对应：
  - **法则属性型**：改进是对约束的更好应对，使结构更稳定
  - **展开属性型**：改进是对约束的创意突破，打开了新维度
  - **混合型**：既有约束应对，也有创意突破

#### B. PORF 观察5 中的"可能性发现"
**文件**：`runtime/PORF_OBSERVATION5_EXAMPLES.md`

```json
{
  "new_possibility_found": "是",
  "possibility_description": "生成器模式打开了'流式处理'的新维度"
}
```

**实现逻辑**：
- 用户在观察5中描述发现的新可能性
- `enrich_candidate_from_hope_tracking()`自动提取这些信息
- 如果检测到关键词（"生成"、"展开"、"打开"），自动标记为"展开属性型"

#### C. agents 目录中的多方案展示
**文件**：`agents/codex/practice_feedbacks/task-20260530-codex-tree-feedback.json`

```python
# 代码中的5种实现：
def dfs_recursive()      # 传统方案
def dfs_iterative()      # 标准替代
def dfs_generator()      # 创意突破（展开属性）
def dfs_preallocated()   # 优化变体
def bfs()                # 另一维度
```

**含义**：展开属性在实践中的体现就是"在约束内生成多个满足条件的不同方案"。

---

### 3️⃣ 连续性（Continuity）

**理论定义**：系统通过完整的反馈循环自我维持和完善的能力。

**代码体现位置**：

#### A. 完整的PORF 5维观察
**文件**：`runtime/practice_observation_framework.md`

```
【观察1】理论与实践的对齐
【观察2】局限暴露
【观察3】决策点追踪
【观察4】自维护能力
【观察5】希望追踪
```

**实现逻辑**：
- 每个观察维度都是"系统自我认识"的一个切面
- 5个维度合在一起形成"完整的自我反思"
- 这个反思过程本身就是连续性的体现

#### B. evolution_candidate 的生命周期
**文件**：`scripts/evolution_candidate_manager.py`

```python
candidate = {
    'status': 'CANDIDATE',      # 初始：提名阶段
    # ... 经历 →
    'status': 'APPROVED',       # 中间：被认可
    # ... 经历 →
    'status': 'INTEGRATED',     # 最终：融入系统
}
```

**含义**：候选从生成到集成的完整生命周期，体现了系统的"代谢"过程。

#### C. TTAF→执行→PORF→反馈→HOPE_STATE更新 的闭环
**文件**：`core/expansion_cycle.md`

```
TTAF（理论应用检视）
  ↓
执行任务
  ↓
PORF（5维观察）
  ↓
integrated_feedback_workflow（自动处理）
  ↓
evolution_candidate（演化候选）
  ↓
HOPE_STATE.md（系统希望更新）
```

**含义**：这个完整的循环是连续性的核心机制。每一轮都使系统更完善。

---

### 4️⃣ 局限性（Limitation）

**理论定义**：系统在某个时刻无法超越的边界。不是缺陷，而是认识的起点。

**代码体现位置**：

#### A. PORF 观察2
**文件**：`runtime/practice_observation_framework.md`

```
【观察2】局限暴露

发现的理论局限：
- 现象：[系统表现出的现象]
- 理论无法解释的地方：[理论与现实的偏离]
- 可能的原因：[初步分析]
```

**实现逻辑**：
- 用户显式地记录遭遇的局限
- 这些局限不是"问题"，而是"理论需要调整的信号"

#### B. TTAF D4：失败条件定义
**文件**：`runtime/task_theory_application_framework.md`

```
【D4】失败条件定义
哪些条件会导致这个任务的执行失败？
- 理论层失败：[理论预测不对时]
- 实践层失败：[执行无法进行时]
```

**实现逻辑**：
- 提前定义失败条件，使系统对自己的局限有清晰认识
- 当真的失败时，能系统地分析原因

#### C. feedback 中的 limitation 字段
**文件**：`scripts/feedback_classifier.py`

```python
def classify_feedback(self, feedback_dict):
    limitation = feedback_dict.get('limitation', '')
    # 处理这个局限信息
```

**含义**：每个反馈都包含"局限"字段，系统学会了主动识别和记录局限。

---

### 5️⃣ 希望（Hope）

**理论定义**：在局限中仍开放于更高可能性的能力。系统的生命力所在。

**代码体现位置**：

#### A. HOPE_STATE.md 的三层希望
**文件**：`runtime/HOPE_STATE.md`

```markdown
### 理论希望
在向什么方向发展：...

### 系统希望（Hermes与用户协同）
阶段目标：...

### 协同希望（人-AI协同体）
方向：...
```

**实现逻辑**：
- 显式地记录系统、理论、协同三个层级的希望
- 每个任务都评估其对这些希望的推进/挑战/维持作用
- 希望状态被定期更新，成为系统的"灯塔"

#### B. PORF 观察5：希望追踪
**文件**：`runtime/PORF_OBSERVATION5_EXAMPLES.md`

```json
{
  "impact_on_hope": "推进/挑战/维持",
  "hope_impact_details": "[详细说明对哪个层级的希望的具体影响]"
}
```

**实现逻辑**：
- 每个任务都被要求填写"对希望的影响"
- 这使得希望成为了明确的评估指标，而非模糊的抽象

#### C. TTAF D6：希望生成
**文件**：`runtime/task_theory_application_framework.md`

```
【D6】希望生成
任务完成后会打开什么新的可能性空间？
这个可能性空间如何推进系统的"希望"？
是否需要更新 HOPE_STATE.md？
```

**实现逻辑**：
- 从被动的"维持现状"升级为主动的"生成新可能"
- 任务不仅要完成，还要被评估"是否打开了新维度"

#### D. hope_direction 字段
**文件**：`scripts/evolution_candidate_manager.py`

```python
def enrich_candidate_from_hope_tracking(self, candidate, hope_tracking_data):
    impact = hope_tracking_data.get('impact_on_hope', '')
    if impact == '推进':
        candidate['hope_direction'] = f"推进：{description}"
    elif impact == '挑战':
        candidate['hope_direction'] = f"挑战：{description}"
    else:
        candidate['hope_direction'] = f"维持：当前方向保持"
```

**含义**：希望方向被明确化、可追踪、可自动识别。

---

## 映射的验证

### 通过 Codex 集成验证的映射

**任务**：树遍历算法优化  
**涉及的映射**：

| 理论概念 | 在任务中的体现 | 代码现场 |
|---------|-------------|--------|
| 法则属性 | Python类型系统、Google风格 | TTAF_config中的约束定义 |
| 展开属性 | 5种算法实现 + 生成器模式 | tree_traversal_codex.py中的5个函数 |
| 连续性 | TTAF→执行→PORF→feedback | task-20260530-codex-tree-feedback.json的完整流程 |
| 局限性 | 约束维度的复杂性 | observation_2_limitation中的3个发现 |
| 希望 | 对协同设计者身份的推进 | observation_5_hope_tracking中的impact_on_hope |

**验证结论**：✅ 所有5个概念在代码中都有清晰的体现。

---

## 维护指南

### 当修改脚本时

**检查清单**：
- [ ] 这个修改涉及哪个理论概念的代码表示？
- [ ] 是否修改了对应的注释/文档？
- [ ] 是否需要更新本映射文档？
- [ ] 是否需要更新PORF_OBSERVATION5_EXAMPLES.md中的范例？

### 当添加新字段时

**流程**：
1. 确定这个字段对应哪个理论概念
2. 在本文档中添加映射关系
3. 在代码中添加清晰的注释
4. 更新相关的示例文档

### 当发现映射不准确时

**处理**：
- 不要直接修改代码"适应"理论
- 而是停下来思考：理论理解有问题？还是代码设计有问题？
- 在PORF中记录这个发现
- 和用户讨论是否需要调整理论或代码

---

## 快速导航

需要找某个字段的含义？

```
法则属性相关：
  ↳ TTAF D2 的法则属性面
  ↳ AGENT_PROFILE.md 的法则面描述
  ↳ limitation 字段
  ↳ TTAF_config.md

展开属性相关：
  ↳ expansion_type 字段
  ↳ PORF 观察5
  ↳ PORF_OBSERVATION5_EXAMPLES.md
  ↳ agents 目录中的多方案对比

连续性相关：
  ↳ PORF 5维观察
  ↳ evolution_candidate 生命周期
  ↳ expansion_cycle.md
  ↳ integrated_feedback_workflow.py

局限性相关：
  ↳ PORF 观察2
  ↳ TTAF D4
  ↳ limitation 字段
  ↳ task_theory_application_framework.md

希望相关：
  ↳ HOPE_STATE.md
  ↳ PORF 观察5
  ↳ TTAF D6
  ↳ hope_direction 字段
  ↳ PORF_OBSERVATION5_EXAMPLES.md
```

---

**创建日期**：2026-05-30  
**目的**：降低维护学习曲线，帮助开发者理解"理论→代码"的对应关系  
**更新时机**：每次添加新机制或修改核心字段后

