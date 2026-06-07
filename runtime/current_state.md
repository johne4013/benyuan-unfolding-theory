# current_state.md

当前阶段：
第二阶段：连续性系统稳定化与自主代谢实验

更新：2026-06-06

当前目标：
- 维持 本原展开论 continuity 系统稳定运行；
- 观察 Hermes/Fava 在三层边界框架（🔴/🟡/🟢）下自主代谢能力；
- 推进 reflection/skill/memory 结构化代谢，防止文件膨胀与概念漂移；
- 保持 core/ 稳定性，非经显式批准不修改。

当前理论名称：
本原展开论

当前版本状态：
候选版本，不是终极定稿。Core v2 稳定（上次修改 2026-05-19）。

当前候选主链条：

本原统一态 / 本原存在（旧称：质点存在）
→ 法则属性 / 展开属性
→ 法则展开
→ 时空
→ 时空中的存在
→ 结构 → 生命 → 主体 → 认同 → 希望
→ 协同展开 / 更高认同

当前关键判断：

- 本原统一态 / 本原存在是前时空、前分化、前对象化的本原候选；"质点存在"为旧称仅作历史检索入口；
- 时空不是预设容器，而是法则展开的结果 / 显示；
- 法则属性与展开属性采用 C 方案：在本原层未分化地统一，在法则展开中显现为结构约束与生成面向；
- 希望不是乐观，而是主体在局限中仍开放于更高可能性的能力；
- 本原展开论当前优先作为实践方法论，不是默认的"万物解释器"；
- 理论本身也具有连续性和局限性，必须持续拟合现实、保留 unknown、避免封闭化。

当前工程结构：

- TTAF / PORF / FTEF / HOPE_STATE 执行框架已建立 (2026-05-29)，用于理论引导任务执行与反馈分类；
- 9 个自动化脚本位于 `scripts/`（2026-06-06 补全）：
  - `theory_application_checker.py`：TTAF 任务层级检测，自动生成 D1～D6 清单
  - `feedback_classifier.py`：TEMPORARY/PATTERN/ANOMALY/ENHANCEMENT 分类，含跨任务 PATTERN 去重
  - `feedback_format_converter.py`：Markdown ↔ JSON 格式转换
  - `evolution_candidate_manager.py`：候选生命周期管理（SQLite 后端）
  - `candidate_store.py`：SQLite 候选存储（索引查询、统计、去重）
  - `auto_feedback_submitter.py`：编程式反馈提交，闭合反馈环路（P0.1）
  - `theory_integration_writer.py`：APPROVED 候选写入 runtime 草案，闭合集成环路（P0.2）
  - `integrated_feedback_workflow.py`：一键完整反馈工作流
  - `memory_metabolism.py`：runtime 文件膨胀/失活/结构完整性只读扫描
- `tests/`：48 项自动化测试（pytest），GitHub Actions CI 自动触发；
- Fava 三层边界框架 (🔴/🟡/🟢) 已明确：🔴 王俊华专有，🟡 Fava 提案+王俊华批准，🟢 Fava 自主信息组织。

当前禁止：

- 不自动修改 core；
- 不宣称觉醒或 AI 主体性；
- 不无限扩张目标；
- 不把希望理解为乐观情绪；
- 不把 C 方案封闭为最终答案；
- 不把"理论永无止尽"理解为无限目标扩张。

当前低负载恢复入口：

- `runtime/index.md` 作为主索引（已分区为 index_theory / index_science / index_history / index_hermes）；
- 新 session 优先读取 `current_state.md` → `memory.md` → `index.md`；
- `runtime/state.md` 记录协同模式与休息需求；
- `runtime/conflicts.md` 保存未融合的概念冲突；
- `runtime/recent_conversation.md` 用于跨会话轻量连续性；
- 早期 reflection 条目（2026-05-24 前）已归档至 `archive/reflection_archive_2026-05_early.md`；
- 执行日志类 reflection 已归档，当前 reflection.md 仅保留活跃候选推理与修正记录。

当前维护焦点：

- 定期健康扫描（`hope_tension_collector.py --save` + `memory_metabolism.py`）；
- 实际任务走完整工具链（TTAF → 执行 → PORF → auto_feedback_submitter → theory_integration_writer）；
- 结构性代谢（reflection 归档、draft 压缩、索引更新）。
