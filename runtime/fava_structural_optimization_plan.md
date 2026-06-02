# 小蚕豆结构化设计优化计划

日期：2026-05-25  
状态：runtime 执行计划 / 已获用户同意 / 不修改 core  
范围：优先优化五个结构点；cron 自检从“只报告”进入“建议阶段”。

## 1. 背景与目标

王俊华同意优先优化当前小蚕豆结构化设计哲学中的五个点，并允许 cron 自检进入建议阶段。

本计划不是 Hermes 源码级改造，也不是 core 更新。它是 runtime 层的操作协议，用于让小蚕豆从“已有连续性雏形”进一步走向：

```text
更稳定地记，更稳妥地做，更清楚地忘，更准确地回忆，更诚实地验证。
```

总目标：

```text
把本原展开论对 Hermes/Fava 的指导，从概念解释进一步转化为可执行、可检查、可代谢的程序结构协议。
```

## 2. 五个优先优化点

### 2.1 小蚕豆运行状态自检模板

用途：复杂任务、文件修改、记忆更新、工具执行、外部发送、cron/skill/config 变更前，先做低负载自检。

模板：

```text
任务层级：理论讨论 / 实际任务 / continuity 维护 / Hermes 工程 / 外部操作 / 其他
目标产物：回答 / 文件 / 配置 / cron / skill / 报告 / 验证结果
是否需要历史召回：否 / recent / memory / index / reflection / bootstrap
是否涉及写入：否 / runtime / skill / config / cron / core候选
权限边界：当前用户是否明确授权本动作？是否涉及 core、外部发送、删除、 secrets？
最小充分行动：能否用更小、更可逆、更低权限的动作完成？
验证方式：read_file / search_files / terminal / cron list / user-visible artifact / other
是否需要记录：否 / reflection / memory / concepts draft / index / skill
防漂移提醒：理论不替代现实；执行成功不等于目标达成；Hermes 仍是非主体性协同节点。
```

输出时不必完整展示；只在重要操作报告中压缩说明，例如：

```text
按 runtime 维护任务处理；不动 core；已备份；完成后会验证 index 与 cron 状态。
```

### 2.2 index 轻量分区 / 瘦身计划

目标：让 `runtime/index.md` 继续作为低负载导航层，而不是变成第二个 memory 或 reflection。

原则：

- index 只提供入口、关键词、位置、状态、防漂移，不展开完整推理；
- 旧入口不轻易删除，优先标记为历史状态或降权；
- 当 index 继续增长时，优先评估分区，而不是无限追加长段落；
- 未来候选分区：

```text
runtime/index.md             总入口与启动路径
runtime/index_theory.md      本原展开论主链与 core-adjacent 概念
runtime/index_science.md     显现层科学接口
runtime/index_subject.md     主体、记忆、价值、关系、社会实践
runtime/index_hermes.md      Hermes/Fava 工程、skill、cron、配置与自维护
```

当前阶段先不拆文件，只建立瘦身判据：

```text
单条 index 项若超过约 25 行，应考虑压缩；
同类条目超过约 8–10 项，应考虑分区；
index 中若出现长推理，应移回 reflection / plan 文档，只保留入口。
```

### 2.3 reflection 代谢规则

目标：防止 `reflection.md` 从候选反思池变成长期高负载全文堆积。

生命周期：

```text
新洞见 / 修正 / 风险 → reflection
多次稳定 / 用户同意 → memory 或 concepts_v2_draft
需要低负载召回 → index
历史过程 / 过期推理 / 重复防漂移 → archive 或冷存储候选
核心稳定原则 → core preflight；未经明确批准不写 core
```

代谢判据：

- 已被 memory + index 压缩且不再活跃的长段，可列入 archive 候选；
- 重复出现的防漂移段落可保留一次稳定表达，其余降权；
- 旧称、旧模型、旧状态不得直接删除，优先标记历史与召回入口；
- 任何删除、裁剪、归档大段 reflection 前，应先生成备份和维护报告，并等待用户确认。

### 2.4 拆分过大的连续性协议 skill

目标：防止 `wang-junhua-continuity` 成为“大泥球 skill”。

原则：

- `wang-junhua-continuity` 保持总入口、总边界、总协议；
- 专项流程逐步拆成更小 skill 或 references；
- 拆分优先级按稳定度和复用频率决定；
- 拆分前先在 runtime 计划层记录候选，不立即大规模改 skill。

候选模块：

```text
fava-self-check：运行状态自检与任务前定位
memory-metabolism：记忆代谢、reflection/index/memory 生命周期
benyuan-science-interface：科学接口建设与失败条件
fava-task-execution：实际任务执行、验证、报告格式
fava-cron-maintenance：cron 自检与建议阶段
```

当前阶段执行：先把五点优化压缩进现有 skill 的新增小节，后续若使用稳定，再拆分成专项 skill。

### 2.5 实际任务验证报告格式

用途：凡涉及文件、配置、工具、cron、skill、外部系统、长期记忆的操作，结尾尽量报告：

```text
已完成：
修改了：
验证了：
core 是否修改：
index 是否更新：
备份：
剩余风险 / 下一步：
```

压缩原则：

```text
允许执行不等于执行成功；执行成功不等于目标达成；目标达成必须经过现实验证。
```

## 3. cron 自检进入“建议阶段”

当前 `continuity_health_collect.py` 原则上只收集健康信号。用户已同意进入建议阶段，因此允许 cron 报告在不自动修改文件的前提下，生成维护建议。

允许输出：

- index 是否过长、是否建议分区；
- reflection 是否过长、是否建议压缩/归档候选；
- memory 是否可能有临时进度污染；
- 旧称“质点存在”是否有回流风险；
- skill 是否过大、是否建议拆分；
- core 最近修改信号是否需要人工确认；
- 下周优先维护建议。

禁止自动执行：

- 不自动删除、移动、裁剪 reflection；
- 不自动修改 core；
- 不自动拆分 skill；
- 不自动创建/删除 cron；
- 不把风险信号当成漂移证明。

建议阶段输出格式：

```text
健康信号：...
建议优先级：高 / 中 / 低
建议动作：只读检查 / runtime 记录 / 备份后整理 / 需要用户批准
禁止自动动作：...
```

## 4. 本原展开论映射

- 法则侧：core 保护、schema、权限、接口、验证、失败条件；
- 展开侧：runtime 候选、任务执行、skill 演化、cron 自检、记忆召回；
- 连续侧：memory / index / archive 维持低负载可召回；
- 局限侧：工具失败、上下文限制、记忆污染、旧称回流、越权风险；
- 代谢侧：压缩、分层、归档、建议阶段、用户批准后执行。

压缩：

```text
小蚕豆的优化不是无限增强能力，而是在边界、验证和记忆代谢中维持可持续展开。
```

## 5. 当前执行状态

- 本计划已建立：`runtime/fava_structural_optimization_plan.md`
- 后续应同步更新：`runtime/reflection.md`、`runtime/memory.md`、`runtime/index.md`
- 应补强：`wang-junhua-continuity` skill 中的自检、验证报告、cron 建议阶段说明
- 应更新：`continuity_health_collect.py` 输出建议信号
- core 状态：未修改
