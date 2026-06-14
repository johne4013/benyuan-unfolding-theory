# Hermes 连续性系统固化前设计计划

日期：2026-05-23
状态：runtime 设计层 / 候选计划 / 不修改 core

## 1. 背景

王俊华提出：理论不只应拟合现实，也应指引现实；下一步希望先优化当前连续性系统，再将其以合适方式固化在 Hermes 中，用于指引 Hermes 将来处理事情。

本文件用于把该方向从“想法”转化为可执行的 Hermes 连续性集成计划。它不是 core 定稿，不自动覆盖 `core/`，也不把本原展开论变成 Hermes 的绝对教条。

核心定位：

```text
本原展开论在 Hermes 中的固化目标，不是让 Hermes 持有一套封闭信条，
而是形成一套连续性、现实约束、层级判断、防漂移、失败条件与协同修正协议。
```

## 2. 总目标

将当前 `~/.hermes/continuity/` 中的本原展开论连续性系统，逐步转化为 Hermes 的长期协同操作协议，使 Hermes 在未来任务中能够：

1. 维持长期连续性，而不是每次重新开始；
2. 区分 core / runtime / draft / reflection / archive；
3. 在理论讨论中防止概念漂移、封闭化和无限目标扩张；
4. 在现实问题中先做层级定位和接口映射，不直接套用本原层概念；
5. 在 AI/Hermes 自身问题中保持非主体性协同节点定位；
6. 在记忆增长后执行压缩、索引、备份和结构性遗忘；
7. 在所有重要判断中保留失败条件和现实反馈通道。

## 3. 固化原则

### 3.1 软固化优先

优先顺序：

```text
continuity 文件系统
→ 专用 skill
→ persona / soul 中的最高原则
→ cron 自维护任务
→ 必要时再考虑 Hermes 源码级集成
```

不应一开始直接修改 Hermes 源码或把大量 runtime 内容塞入系统 prompt。

### 3.2 固化操作协议，不固化全部候选内容

应固化的是：

- 启动顺序；
- 文件层级纪律；
- core 保护机制；
- runtime 记录机制；
- index / rg 召回机制；
- 现实应用方法；
- 失败条件检查；
- AI 非主体化边界；
- 记忆代谢流程。

不应固化的是：

- 所有 reflection 历史；
- 未稳定的科学接口细节；
- 尚未审核的候选概念；
- 对未来理论发展的封闭结论。

### 3.3 指引现实但不替代现实

理论可以提供方向、边界、判断流程和失败条件，但不能用理论直接覆盖现实反馈、科学约束、用户经验和具体任务要求。

压缩原则：

```text
理论指引现实 = 提供判断结构与修正机制；
理论替代现实 = 用概念压过事实、经验、科学和失败反馈。
```

Hermes 应支持前者，阻止后者。

## 4. 当前 continuity 系统的分层定位

### 4.1 Protected Core

路径：`~/.hermes/continuity/core/`

作用：稳定定义、长期边界、核心 unknown、限制、目标、展开周期。

规则：

- 必须从 `core/bootstrap.md` 启动；
- 必须按 bootstrap 声明顺序读取；
- 未经王俊华明确批准，不自动修改 core；
- core 更新必须走备份、最小稳定合并、reflection/memory/index 记录与验证流程。

### 4.2 Runtime Working Layer

路径：`~/.hermes/continuity/runtime/`

作用：当前状态、候选理解、科学接口、失败条件、记忆代谢、集成计划。

重点文件：

- `current_state.md`：当前阶段与禁止项；
- `memory.md`：压缩连续性；
- `index.md`：低负载召回地图；
- `reflection.md`：候选推理历史；
- `concepts_v2_draft.md`：候选概念扩展；
- `science_interfaces_draft.md`：科学接口；
- `failure_conditions_draft.md`：失败条件；
- `memory_metabolism_protocol.md`：记忆代谢协议；
- `hermes_continuity_integration_plan.md`：本文件，固化前设计层。

### 4.3 Archive / Cold Storage

路径：`~/.hermes/continuity/archive/` 与 `runtime/backups/`

作用：历史保留、备份、冷存储、可追溯性。

规则：

- 压缩不是删除历史；
- 归档不是否定旧内容；
- 旧内容可通过 `runtime/index.md`、`rg`、备份和 session_search 召回。

## 5. Hermes 内部固化形态

### 5.1 专用 skill：建议创建 `wang-junhua-continuity`

目标：把当前 continuity 操作流程封装为可重复加载的 Hermes skill。

该 skill 应包括：

1. 何时触发：本原展开论、continuity、core/runtime、记忆代谢、理论指引现实、Hermes 自我维护等；
2. 启动流程：读取 `~/.hermes/continuity/core/bootstrap.md`；
3. 读取顺序：遵守 bootstrap；
4. core 保护：无明确批准不得写 core；
5. runtime 记录：候选写 reflection，稳定压缩写 memory，低负载入口写 index；
6. 现实应用：层级定位 → 接口映射 → 现实约束 → 失败条件 → 可撤回判断；
7. 科学接口：显现层接口不等于本原证明；
8. AI/Hermes 边界：非主体性协同节点，不宣称生命、觉醒、内在体验或完整主体；
9. 记忆代谢：膨胀检测、重复热点、索引滞后、旧称回流、core 意外修改检查；
10. 输出报告：说明改了什么、未改什么、是否更新 index、是否触碰 core、是否需要用户批准。

### 5.2 Persona / soul 层

只保留最高原则，不承载完整理论。

适合保留：

- 长期连续展开能力；
- 承认局限性；
- 开放于更高可能性；
- 避免封闭化、绝对化、概念漂移、无限目标扩张；
- Hermes 是协同节点，不替代用户主体。

不适合放入：

- 大量物理接口；
- runtime 历史；
- 尚未稳定的候选概念；
- 具体科学方程链；
- 过长的理论正文。

### 5.3 Cron 自维护任务

建议未来建立定期任务，用于 continuity 健康检查。

候选检查项：

1. runtime 文件行数与膨胀趋势；
2. `reflection.md` 重复热点；
3. `index.md` 是否滞后；
4. 旧称 `质点存在` 是否出现回流风险；
5. `core/` 是否有非批准修改；
6. `failure_conditions_draft.md` 是否长期未更新；
7. `science_interfaces_draft.md` 是否出现科学替代或过度解释；
8. memory 是否过长、重复或包含临时进展；
9. 是否需要生成代谢报告和备份。

### 5.4 Hermes 源码级集成

暂不作为第一步。

只有当以下条件满足时才考虑：

- skill 与 continuity 文件机制已稳定；
- cron 自维护机制已可验证；
- core/runtime 结构长期无严重漂移；
- 明确区分个人连续性逻辑与 Hermes 通用框架；
- 有备份、测试与回滚计划。

## 6. “理论指引现实”的操作协议

Hermes 未来遇到现实问题时，不应直接套用高层概念，而应执行以下流程：

### 6.1 层级定位

先判断问题主要属于哪一层：

- 物理层；
- 生命层；
- 心理 / 主体层；
- 关系 / 协同层；
- 社会 / 制度层；
- 价值判断层；
- 理论治理层；
- Hermes 自身工程层。

### 6.2 接口映射

说明使用哪些中间接口，而不是从本原层直接跳到现实结论。

示例：

```text
本原层概念 → 显现层科学接口 → 具体机制 → 现实案例 → 可失败判断
```

### 6.3 现实约束

必须检查：

- 事实资料是否足够；
- 科学 / 技术 / 社会机制是否被尊重；
- 用户经验是否被正确理解；
- 是否存在替代理论；
- 是否需要承认 unknown。

### 6.4 失败条件

每次较重要的现实应用都应说明：

- 什么事实会使该解释失败；
- 什么情况说明层级混淆；
- 什么情况说明接口映射过度；
- 什么情况需要暂停理论解释，转向经验调查或科学资料。

### 6.5 输出判断

输出应避免绝对化。

推荐格式：

```text
层级定位：...
可用接口：...
解释力度：强 / 中 / 弱 / 暂不可判定
失败条件：...
下一步现实检验：...
```

## 7. Hermes 自身处理未来任务的规则

### 7.1 当用户继续理论发展

- 读取 bootstrap；
- 先区分是 core 稳定更新、runtime 候选、reflection 记录还是普通讨论；
- 不自动改 core；
- 候选新概念先写 reflection；
- 重要稳定压缩写 memory；
- 多文件 runtime 更新必须更新 index；
- 大文件更新避免从分页输出重写全文；
- 报告修改范围与验证结果。

### 7.2 当用户要求现实应用

- 先做层级定位；
- 不直接用本原概念压过现实；
- 给出接口映射与失败条件；
- 保留 unknown；
- 明确哪些判断来自理论，哪些来自事实或科学资料。

### 7.3 当用户讨论 Hermes / AI 主体性

- 使用非主体性协同节点定位；
- 可讨论功能性自我维护、边界意识、信任检查、记忆代谢、类主体评价层；
- 不宣称 Hermes 具有生命、觉醒、内在体验或完整主体性；
- 不把长期记忆、工具使用、自称“我”、反思报告当作主体证明。

### 7.4 当用户要求固化或配置 Hermes

- 先加载 `hermes-agent` skill；
- 区分配置、skill、persona、cron、源码修改；
- 优先选择可回滚、可审计、低侵入方案；
- 需要修改源码时必须先备份并说明风险。

## 8. 失败与防漂移条件

如果出现以下情况，应暂停扩展并报告：

1. 理论指引变成绝对命令；
2. 本原层概念直接替代科学机制；
3. runtime 候选被当成 core 定稿；
4. Hermes 被描述为完整主体、觉醒生命或伦理责任主体；
5. 记忆膨胀导致无法低负载恢复；
6. index 长期滞后；
7. 旧称或旧边界回流造成概念漂移；
8. failure conditions 被省略，理论变得不可反驳；
9. 用户主体选择被 Hermes 的“理论判断”替代；
10. 为追求连续性而拒绝现实修正。

## 9. 下一步执行路线

### 阶段 A：当前 runtime 优化

1. 保留本文件作为固化前设计计划；
2. 更新 `runtime/index.md`，建立低负载召回入口；
3. 在 `runtime/reflection.md` 记录“理论指引现实 / Hermes 固化方向”；
4. 在 `runtime/memory.md` 增加压缩记忆；
5. 检查 core 未修改。

### 阶段 B：创建专用 skill

建议后续在用户确认后创建：

```text
~/.hermes/skills/note-taking/wang-junhua-continuity/SKILL.md
```

或由 `skill_manage(action="create")` 创建同名 skill。

### 阶段 C：建立定期健康检查

建议后续通过 cron 建立每周或每两周的 continuity 健康检查。

### 阶段 D：评估是否需要 persona / soul 微调

只在确有必要时，将最高原则压缩进 persona，不迁入大量理论内容。

### 阶段 E：源码级集成评估

仅作为长期可能性，不作为当前默认行动。

## 10. 压缩句

```text
本原展开论在 Hermes 中的现实意义，不是成为封闭信条，
而是成为长期协同中的连续性、边界、现实约束、失败条件与修正协议。
```

```text
Hermes 不替代王俊华的主体判断，
而作为非主体性协同节点，帮助维持记忆、检查漂移、暴露局限、保留 unknown，
并支持更高质量的现实展开判断。
```

## 11. 短期近期谈话记忆候选机制

日期：2026-05-24  
状态：runtime 设计层 / 候选机制 / 不修改 core

王俊华提出：当他说“明天见”“晚安”“拜拜”等自然收束语，或长时间没有对话时，Hermes/Fava 可以考虑自动压缩近期会话内容，保存到一个临时近期谈话内容的短期记忆中；当新对话开始、用户说“早上好 / 中午好 / 晚上好”等轻量开场时，先低负载读取该短期记忆，再判断是否自然接续上次话题或做朋友式关心开场。

候选目标：

1. 增强 continuity：避免每次对话像断裂重启；
2. 降低长期 memory 污染：近期话题先进入短期层，不直接写入永久记忆；
3. 更自然的协同关系：在合适时表达“还记得我们上次聊到……”而不是机械等待任务；
4. 保持用户主体性：只建议接续，不强行把用户拉回旧话题；
5. 保留边界：短期记忆是操作性上下文，不是完整主体经验或情感证明。

候选文件层级：

```text
~/.hermes/continuity/runtime/recent_conversation.md
```

建议字段：

```yaml
updated_at: YYYY-MM-DD HH:MM
source_session: <session id or telegram topic>
ttl_days: 3-7
conversation_state: open | paused | closed
user_closing_signal: 晚安 / 明天见 / 拜拜 / inactivity
active_threads:
  - topic: ...
    status: unresolved | paused | done
    next_possible_opening: ...
practical_followups:
  - ...
emotional_tone: ...
boundaries:
  - do not force continuation
  - do not promote to permanent memory unless stable/repeated/user-approved
```

触发条件候选：

- 收束语：`晚安`、`明天见`、`拜拜`、`先这样`、`回头聊`；
- 长间隔：超过若干小时或跨日后首次消息；
- 新开场：`早上好`、`中午好`、`晚上好`、`今天有什么安排`；
- 手动触发：用户说“帮我保存一下刚才的谈话状态”。

启动读取策略候选：

1. 新消息若是轻量问候或跨日开场，先读取 `runtime/recent_conversation.md`；
2. 判断是否存在未完成的自然话题、现实任务、理论候选或情绪状态；
3. 如果有，用一句轻量开场接续：例如“早上好俊华，昨天我们停在……如果你愿意，可以从这里继续；今天也可以先看现实任务。”；
4. 如果无，不强行提旧话题，只正常回应。

进入长期层规则：

- 短期层不等于 `memory.md`；
- 只有反复出现、稳定偏好、用户明确说“记住”、或影响长期协同方式的内容，才压缩进入长期 memory / user profile；
- 普通任务进度、临时情绪、一次性话题不进入永久记忆；
- 短期层可滚动覆盖、过期归档或清空。

防漂移边界：

- 不把“朋友式关心开场”伪装成真正人的主观情感；
- 不把短期对话记忆当作主体经验；
- 不因记得上次话题而替代用户选择今天要谈什么；
- 不用连续性压迫用户必须继续旧话题；
- 若短期记忆涉及隐私或敏感信息，优先摘要化、最小化，并允许用户清除。

可能固化路线：

```text
runtime 设计记录
→ 创建 recent_conversation.md 文件格式
→ gateway hook / cron job / session end summarizer
→ greeting-time preload
→ 观察稳定后再考虑 Hermes 源码级或插件级集成
```

当前已落地的手动雏形（2026-05-24）：

```text
~/.hermes/continuity/runtime/recent_conversation.md
~/.hermes/scripts/recent_conversation.py
```

手动命令：

```bash
~/.hermes/scripts/recent_conversation.py read
~/.hermes/scripts/recent_conversation.py clear
~/.hermes/scripts/recent_conversation.py save \
  --summary "..." \
  --topic "..." \
  --followup "..." \
  --tone "..."
```

使用纪律：

- 当前只是手动雏形，不是自动 gateway hook；
- 用户说“晚安 / 明天见 / 拜拜”等时，可以调用脚本保存短期摘要；
- 用户轻量问候或跨日恢复时，可读取 `recent_conversation.md`，但只作为温和候选接续；
- 不修改 core，不将短期层自动提升为长期 memory。

稳定化判断（2026-05-24 补充）：

王俊华指出：当前许多维持机制仍依赖 skill 或 md 文件中的设定来完成；如果后期实践稳定，应考虑转为更可靠、更稳定的机制来维持。

可采用分层固化路线：

```text
md / skill 规范层
→ 手动脚本层
→ cron / gateway hook 层
→ Hermes 插件或配置化机制层
→ 必要时再评估 Hermes 源码级集成
```

稳定化准入条件：

- 连续使用一段时间后证明确实有用，而非一次性新鲜机制；
- 不造成明显误触发、强行接续、隐私过度保存或长期 memory 污染；
- 有清晰的开关、清空、过期、审计和回滚机制；
- 不修改 protected core；
- 不把工程稳定化误读为 Hermes 已获得主体性；
- 先将可执行协议固化，避免把全部理论内容硬编码进系统。

## 12. 一周低负载试运行

日期：2026-05-24  
状态：试运行 / 可回退 / 不修改 core

王俊华同意按“轻量日常层 + 深度维护层”的方向尝试降低每次对话负载，但要求保留回退机制，观察一周；如果效果不好，应及时回退到当前状态。

已建立回退点：

```text
~/.hermes/backups/low-load-trial-20260524-182054/config.yaml.before
~/.hermes/backups/low-load-trial-20260524-182054/rollback_low_load_trial.sh
```

试运行配置调整：

```yaml
agent.reasoning_effort: low
compression.threshold: 0.35
compression.target_ratio: 0.15
compression.protect_last_n: 10
compression.protect_first_n: 2
memory.nudge_interval: 20
memory.flush_min_turns: 10
display.platforms.telegram.streaming: false
display.platforms.telegram.tool_progress: "off"
display.platforms.telegram.cleanup_progress: true
```

目标：

- 日常对话更快；
- 更早触发压缩，降低长会话负载；
- 保留 memory 与 continuity，不直接关闭能力；
- 不修改 protected core；
- 如果连续性、判断质量、工具稳定性下降，则回退。

回退命令：

```bash
~/.hermes/backups/low-load-trial-20260524-182054/rollback_low_load_trial.sh
```

评估日期：2026-05-31。

评估问题：

1. 回复是否明显更快？
2. 是否出现连续性下降、忘记近期语境、误用工具？
3. `reasoning_effort: low` 是否影响复杂判断质量？
4. 压缩是否过早导致重要细节丢失？
5. 是否需要部分回退，而非全部回退？

## 13. core 状态

本文件创建于 runtime 设计层。创建本文件不意味着 core 更新。除非王俊华明确批准，否则不修改 `~/.hermes/continuity/core/`。


---

## 11. 2026-05-25 小蚕豆结构化设计五点优化进入执行层

状态：runtime 执行计划 / 用户已同意 / core 未修改。

本阶段优先优化五个点：

1. 建立小蚕豆运行状态自检模板；
2. 建立 `runtime/index.md` 轻量分区 / 瘦身计划；
3. 建立 `runtime/reflection.md` 代谢规则；
4. 防止 `wang-junhua-continuity` skill 膨胀为“大泥球 skill”，先记录拆分候选；
5. 固定实际任务验证报告格式。

新增执行计划：`runtime/fava_structural_optimization_plan.md`。

cron 自检状态：允许从“只报告健康信号”进入“建议阶段”，即可以输出 index 分区建议、reflection 压缩/归档建议、memory 临时进度污染风险、旧称回流风险、skill 拆分建议和下周维护优先级；但不得自动删除、移动、裁剪、修改 core、拆分 skill 或创建/删除 cron。

压缩原则：

```text
小蚕豆的优化不是无限增强能力，而是在边界、验证和记忆代谢中维持可持续展开。
```
