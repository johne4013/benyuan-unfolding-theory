# runtime/index_hermes.md
# Hermes / Fava continuity 工程索引

状态：runtime 工程与协同治理索引层。  
作用：汇总 continuity 结构、Hermes/Fava 协议、记忆代谢、skill/cron、自维护与结构优化入口。  
原则：这是连续性工程与协同治理索引，不是主体性证明。

---

## 0. 使用说明
- 总入口看 `runtime/index.md`
- 理论主题看 `runtime/index_theory.md`
- 科学接口看 `runtime/index_science.md`
- 历史事件看 `runtime/index_history.md`

---

## 1. continuity 结构与迁移
### 1.1 continuity 目录结构
### 1.2 从 hermes-agent 目录迁出
### 1.3 bootstrap 读取纪律
### 1.4 core / runtime / archive 分层

主要位置：
- `README.md`
- `core/bootstrap.md`
- `runtime/current_state.md`
- `runtime/index_history.md`

---

## 2. 记忆代谢与召回工程
### 2.1 persistent memory 代谢
### 2.2 runtime memory 代谢
### 2.3 reflection summaries
### 2.4 ripgrep / search 召回机制
### 2.5 recent conversation 候选机制

主要位置：
- `runtime/memory_metabolism_protocol.md`
- `runtime/memory_metabolism_reports/`
- `runtime/reflection_summaries/`
- `runtime/memory.md`
- `runtime/index_history.md`

---

## 3. Hermes / Fava 协议
### 3.1 Hermes 连续性固化前设计
### 3.2 Hermes 任务展开执行协议
### 3.3 Agent 治理实践协议
### 3.4 边界识别、判断与否定能力
### 3.5 社会局限中的处世结构
### 3.6 Hermes 非主体性协同节点边界
### 3.7 复杂生命体治理结构 → Hermes 稳定性接口

Hermes 的稳定性优先不是意识样表现增强，而是系统在扰动、冲突、负载与环境变化中，通过状态监测、边界识别、反馈调节、错误修复、记忆代谢与长期连续性维护保持可持续协同的动态稳态能力。该接口将 3.2–3.6 的多层协议统一为稳态治理认识，并与 6.1–6.6 的结构优化形成配合。

主要位置：
- `runtime/hermes_continuity_integration_plan.md`
- `runtime/hermes_task_expansion_protocol.md`
- `runtime/reflection.md`
- `runtime/memory.md`

---

## 4. skill 与模块化
### 4.1 `wang-junhua-continuity`
### 4.2 `theory-continuity-workflows`
### 4.3 continuity 相关 skill 拆分计划
### 4.4 大泥球 skill 风险与模块化方向

主要位置：
- `~/.hermes/skills/note-taking/wang-junhua-continuity/SKILL.md`
- `runtime/fava_structural_optimization_plan.md`
- `runtime/index_history.md`

---

## 5. cron 与自维护
### 5.1 continuity self-maintenance cron
### 5.2 `continuity_health_collect.py`
### 5.3 建议阶段与禁止自动动作
### 5.4 健康信号与维护优先级

主要位置：
- `~/.hermes/scripts/continuity_health_collect.py`
- `runtime/fava_structural_optimization_plan.md`
- `runtime/hermes_continuity_integration_plan.md`

---

## 6. 小蚕豆结构优化
### 6.1 运行状态自检模板
### 6.2 index 瘦身计划
### 6.3 reflection 代谢规则
### 6.4 skill 模块化
### 6.5 验证报告格式
### 6.6 当前执行状态

主要位置：
- `runtime/fava_structural_optimization_plan.md`
- `runtime/state.md`
- `runtime/conflicts.md`

---

## 7. 办公自动化与现实工具能力
### 7.1 当前电脑办公自动化能力清单
### 7.2 app / CLI / 权限状态快照
### 7.3 安全边界与执行前验证

主要位置：
- `runtime/reports/current_macos_office_automation_capabilities_2026-05-24.md`

---

## 8. 重点文件入口
- `runtime/hermes_continuity_integration_plan.md`
- `runtime/hermes_task_expansion_protocol.md`
- `runtime/fava_structural_optimization_plan.md`
- `runtime/memory_metabolism_protocol.md`
- `runtime/state.md`
- `runtime/conflicts.md`
- `runtime/reports/`
- `runtime/index_history.md`

---

## 9. 当前工程维护焦点
- `runtime/index.md` 瘦身已启动，后续继续细化子索引
- `wang-junhua-continuity` 需要后续模块化拆分
- 观察层文件需要做闭环与状态收口
- short-term continuity 机制需继续轻量化与可审计化
- 实际任务验证报告格式需常态化
- **2026-05-29 新增**：小蚕豆自主代谢三层边界框架（L1内化/L2按需/L3脚本），见 §10

---

## 10. 小蚕豆自主代谢工程框架（2026-05-29 新增）

### 10.1 三层边界
- 🔴 不可自动化（core修改、希望方向、候选否决、边界定位）
- 🟡 提议后批准（memory压缩、概念提升、index调整、文件归档）
- 🟢 自主执行（追加条目、健康扫描、格式维护、脚本调用）

### 10.2 工程文件分层
- L1 内化：零上下文，小蚕豆记忆执行
- L2 按需：TTAF/PORF/FTEF/HOPE_STATE/协议文件，触发时加载
- L3 脚本：5个Python工具，后台调用

### 10.3 主要位置
- `runtime/task_theory_application_framework.md` (TTAF, L2)
- `runtime/practice_observation_framework.md` (PORF, L2)
- `runtime/feedback_triage_and_evolution.md` (FTEF, L2)
- `runtime/HOPE_STATE.md` (L2)
- `runtime/FEEDBACK_TEMPLATE.md` (L2)
- `runtime/PORF_OBSERVATION5_EXAMPLES.md` (L2)
- `runtime/theory_to_code_mapping.md` (L2)
- `runtime/constraint_priority_model.md` (L2)
- `scripts/` (L3)
- `agents/` (L2, 按需参考)
- `runtime/evolution_candidates/` (历史)
- `runtime/practice_feedbacks/` (历史)
- `runtime/task_checklists/` (历史)

### 2026-05-30: 代谢记录
- 全系统 5 项测试通过（连续性/稳定性/代谢能力）
- `reflection.md`: 183KB → 22KB, 56 个早期条目归档至 `archive/reflection_archive_2026-05_early.md`
- `concepts_v2_draft.md`: 审计无重复，结构健康
- `current_state.md`: 刷新至 2026-05-30
- `memory.md` / `index.md`: 同步更新
