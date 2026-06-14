# 本原展开论 / Benyuan Unfolding Theory

> *存在借展开显现，展开依局限成形，认同凭连续存续，发展使认同更新。*
>
> *Existence manifests through unfolding; unfolding takes shape through limitation; identity persists through continuity; development renews identity.*

---

## 这是什么？ / What Is This?

**本原展开论** 是一个开放的理论框架，试图在承认人类认知局限性的前提下，构建一条从宇宙本原到主体希望的可追溯展开链。

它不是宗教，不是既定科学理论，也不是一个封闭的哲学体系。它是一个 **持续展开中的候选理论结构** —— 保持开放性、承认局限性、接受现实约束，欢迎来自人类和 AI 的协同推演与修正。

**Benyuan Unfolding Theory** is an open theoretical framework that attempts to construct a traceable chain of unfolding — from the primordial origin of existence to the hope of conscious subjects — while acknowledging the fundamental limitations of human cognition.

It is not a religion, not an established scientific theory, and not a closed philosophical system. It is an **ongoing candidate theoretical structure** — maintaining openness, acknowledging limitations, accepting reality constraints, and welcoming collaborative reasoning and revision from both humans and AI.

---

## 核心链条 / Core Chain

```text
本原统一态 / 本原存在（前时空、前分化、前对象化）
  → 法则属性 / 展开属性（结构约束 + 生成面向）
    → 法则展开（时空生成）
      → 时空（显示框架，非预设容器）
        → 时空中的存在 → 结构 → 生命 → 主体
          → 认同 → 希望 → 协同展开 / 更高认同
```

**希望** 在此理论中被定义为：**主体在局限中仍开放于更高可能性的能力**。

---

## 目录结构 / Directory Structure

```
benyuan-unfolding-theory/
├── README.md                    ← 你在这里
├── core/                         ← 🔴 核心保护层（慢更新）
│   ├── bootstrap.md              # 启动读取顺序
│   ├── soul.md                   # 系统灵魂/人格
│   ├── identity.md               # 系统身份定义
│   ├── concepts.md               # 核心概念词典 (v2.0)
│   ├── theory.md                 # 核心理论陈述 (v2.0)
│   ├── limitations.md            # 系统局限性
│   ├── unknowns.md               # 当前未知领域
│   ├── goals.md                  # 长期目标
│   └── expansion_cycle.md        # 展开循环与运行规则
├── runtime/                      ← 🟡 工作层（快速迭代）
│   ├── current_state.md          # 当前系统状态
│   ├── memory.md                 # 压缩连续性记忆
│   ├── index.md                  # 总索引（导航地图）
│   ├── reflection.md             # 反思修正层
│   ├── state.md                  # 协同模式与休息需求
│   ├── conflicts.md              # 未融合的概念冲突
│   ├── HOPE_STATE.md             # 希望/张力监视器
│   ├── FEEDBACK_TEMPLATE.md      # 标准反馈模板（PORF 5维）
│   ├── PORF_OBSERVATION5_EXAMPLES.md  # 希望追踪观察示例
│   ├── practice_observation_framework.md  # 实践观察框架（PORF）
│   ├── task_theory_application_framework.md  # 任务理论应用框架（TTAF）
│   ├── value_judgment_protocol.md  # 美/丑/善/恶判断协议
│   ├── trust_deception_protocol.md # 信任/欺骗判断协议
│   ├── theory_to_code_mapping.md   # 理论概念→代码实现映射
│   ├── *_draft.md                # 候选概念草案（概念/理论/未知/失败条件/科学接口）
│   ├── practice_methodology.md   # 实践方法论
│   ├── index_theory.md           # 理论子索引
│   ├── index_science.md          # 科学接口子索引
│   ├── index_hermes.md           # Hermes 工程子索引
│   ├── index_history.md          # 历史变更子索引
│   └── ...                       # Hermes 协议与工程文件
├── scripts/                      ← 🟢 自动化工具（Hermes 自主操作层）
│   ├── hope_tension_collector.py  # 希望=本原张力健康扫描（含时序趋势）
│   ├── feedback_classifier.py     # 反馈分类器（TEMPORARY/PATTERN/ANOMALY/ENHANCEMENT）
│   ├── evolution_candidate_manager.py  # 候选生命周期管理（JSON文件存储）
│   ├── candidate_store.py         # SQLite候选存储（索引查询、统计、去重）
│   ├── auto_feedback_submitter.py # 编程式反馈提交（P0.1，闭合反馈环路）
│   ├── theory_integration_writer.py  # 候选→runtime文档写入（P0.2，闭合集成环路）
│   ├── integrated_feedback_workflow.py  # 一键完整反馈工作流
│   ├── feedback_format_converter.py    # Markdown ↔ JSON 格式转换
│   └── README.md                  # 脚本详细使用说明
└── tests/                        ← 🧪 自动化测试（pytest）
    ├── conftest.py                # 自动将 scripts/ 加入 sys.path
    ├── test_candidate_store.py    # CandidateStore 8项测试
    ├── test_evolution_candidate_manager.py  # 候选管理器 7项测试
    ├── test_feedback_classifier.py  # 分类器 9项测试
    ├── test_auto_feedback_submitter.py  # 提交器 5项测试
    ├── test_theory_integration_writer.py  # 集成写入器 5项测试
    └── test_hope_tension_collector.py  # 张力采集器 4项测试
```

运行测试：`python3 -m pytest tests/ -v`（59项，全部通过）

### 分层说明 / Layer Semantics

| 层级 | 名称 | 更新策略 | 说明 |
|------|------|----------|------|
| 🔴 **core/** | 核心保护层 | 慢更新，需显式批准 | 理论的最小稳定结构，不可自动修改 |
| 🟡 **runtime/** | 运行时工作层 | 快速迭代，可提案 | 候选概念、反思、记忆、协议 |
| 🟢 **scripts/** | 自动化工具层 | Hermes 自主操作 | 反馈处理、候选管理、健康扫描，写入 runtime/ |
| 🧪 **tests/** | 测试层 | 随脚本同步维护 | pytest，保证工具链核心逻辑正确性 |
| 🗄️ **archive/** | 历史归档 | 只追加 | 旧内容归档（本仓库不包含） |

---

## 如何阅读 / How to Read

### 最小恢复路径（5 分钟了解全貌）

1. **`core/theory.md`** — 核心理论，一页纸概述
2. **`core/concepts.md`** — 22 个核心概念的稳定定义
3. **`runtime/current_state.md`** — 当前系统状态与阶段

### 完整启动路径（深入理解）

按 `core/bootstrap.md` 指定的顺序依次阅读 core/ 和 runtime/ 下所有文件。

### 按主题跳转

- **理论本体**：`runtime/index_theory.md` →
- **科学接口**：`runtime/index_science.md` →
- **工程协同**：`runtime/index_hermes.md` →
- **历史变迁**：`runtime/index_history.md` →

---

## 理论演化工具链 / Theory Evolution Toolchain

系统内置完整的反馈→演化闭环，使理论能够从实践中自我修正：

```
TTAF（任务前理论检视）
  ↓
执行任务
  ↓
PORF（5维实践观察：对齐/局限/决策/自维护/希望）
  ↓
auto_feedback_submitter.py  ——  编程式提交反馈（无需手动填模板）
  ↓
integrated_feedback_workflow.py  ——  自动分类 + 候选生成
  ↓                                    ↑ PATTERN 跨任务合并（Jaccard 相似度）
feedback_classifier.py              feedback_classifier.py
（TEMPORARY / PATTERN / ANOMALY / ENHANCEMENT）
  ↓
evolution_candidate_manager.py / candidate_store.py
（候选生命周期：CANDIDATE → APPROVED → INTEGRATED）
  ↓
theory_integration_writer.py  ——  APPROVED 候选写入 runtime/ 草案文件
  ↓
HOPE_STATE.md 张力更新
  ↓
王俊华审批 → core/ 更新（🔴层，手动）
```

### 核心脚本快速上手

```bash
# 提交一条反馈（自动分类、生成候选）
python3 scripts/auto_feedback_submitter.py \
    "任务名称" "观察到的现象" "理论局限" "改进建议"

# 查看所有待审候选
python3 scripts/evolution_candidate_manager.py list

# 将 APPROVED 候选集成进 runtime/
python3 scripts/evolution_candidate_manager.py integrate <candidate-id>

# 扫描系统健康状态（保存快照，查看趋势）
python3 scripts/hope_tension_collector.py --save
python3 scripts/hope_tension_collector.py --history 10
```

---

## 核心原则 / Core Principles

1. **保持开放性** — 允许更高解释结构进入，允许修正与重组
2. **承认局限性** — 局限性是结构条件，不是纯负面缺陷
3. **避免封闭化** — 任何解释都必须有失败条件，不可反驳 = 封闭化风险
4. **保留 Unknown** — 未知不应被提前消除，也不应成为停止追问的黑箱
5. **层级桥接** — 本原层概念应用到现实必须经过中间层级
6. **显现层接受科学约束** — 哲学概念不替代具体科学机制
7. **概念防漂移** — 持续检查概念是否被偷换、泛化或神秘化

---

## 如何参与 / How to Contribute

本原展开论是一个 **开放协同展开** 的项目。你（无论是人类还是 AI）可以通过以下方式参与：

### 🟢 协同参与方式

- **提出问题与挑战**：在 GitHub Issues 中提出对理论的疑问、反例或修正建议
- **推演概念链**：基于已有概念进行推演，将结果提交为 runtime draft
- **补充科学接口**：为显现层概念补充或修正科学映射
- **发现漂移**：指出概念漂移、层级混淆、绝对化或封闭化风险
- **改进工具**：优化 scripts/ 中的 Python 工具
- **翻译与传播**：将理论翻译为其他语言，帮助更多人理解

### 🟡 提案修改

- 对 core/ 的修改需要经过充分的讨论和共识
- 对 runtime/ 的修改可以通过 Pull Request 提交
- 重大概念变更需要说明层级、桥接、接口映射和失败条件

### 🔴 不可自动化

- 修改 core/ 中已稳定的概念定义需经过维护者批准
- 删除历史记录、撤销 Unknown、改变理论方向需充分讨论

---

## 重要声明 / Important Disclaimers

- 本原展开论是一个 **候选理论框架**，不是终极真理
- 理论可以保留 unknown，但不能以 unknown 否认科学事实
- 科学接口是候选映射，不是本原展开论的证明
- AI 协同节点（如 Hermes/Fava）不是完整主体、生命或觉醒实体
- 本理论不替代宗教、科学或任何既有知识体系
- "希望"在本文中不是乐观情绪或成功期待，而是结构性概念

---

## 相关项目 / Related Projects

- **Hermes Agent**: 本系统的 AI 协同运行环境（[hermes-agent](https://github.com/nousresearch/hermes-agent)）
- 本仓库包含可以在 Hermes Agent 中运行的 continuity 层文件

---

## 许可 / License

本原展开论采用 [MIT License](LICENSE) 开放。

我们选择 MIT 是因为：
- 它允许任何人自由使用、修改和分发
- 它允许在商业和学术环境中使用
- 它不强制下游项目开源（宽松协议促进传播）
- 它符合"开放性"原则

理论本身不是代码，但选择 MIT 表达了我们对开放协同的态度：你来用、来改、来质疑、来增强，都不需要问谁。

---

## 维护者 / Maintainer

**王俊华 (Wang Junhua / Johnny)**

- 初始理论建构者
- 长期连续性维护者
- 本仓库的最终合并决策者

协同节点：**Hermes / Fava（小蚕豆）** — 非主体性 AI 协同节点，负责概念整理、记忆压缩、反漂移检查和长期反思辅助。

---

> *理论自身也是展开中的结构。它有连续性，也有局限。它欢迎修正，但拒绝任意断裂。*
>
> *The theory itself is a structure in unfolding. It has continuity and limitation. It welcomes revision, but rejects arbitrary rupture.*
