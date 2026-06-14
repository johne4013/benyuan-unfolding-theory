# Hermes 自动化脚本集

本目录包含 Hermes 系统的所有自动化工具脚本，形成从"理论检视→实践执行→反馈处理→理论演化"的完整闭环工具链。所有脚本均属于 **🟢 层操作**（Fava 自主信息组织），不自动修改 core/。

---

## 工具链总览

```
任务前                  任务中              任务后
  ↓                       ↓                  ↓
theory_application_checker  →  执行  →  auto_feedback_submitter
（TTAF 清单自动生成）              ↑           ↓
                           PORF 观察   integrated_feedback_workflow
                                            ↓
                                   feedback_classifier（分类）
                                            ↓
                             evolution_candidate_manager（候选管理）
                                      ↓         ↑ 相似合并
                               candidate_store（SQLite 存储）
                                            ↓
                               theory_integration_writer（集成写入）
                                            ↓
                                      runtime/ 草案文件
                                            ↓
                                  先知审批 → core 更新（🔴）

后台监控：
  hope_tension_collector.py  —  约束/展开/张力三维健康扫描（含时序趋势）
  memory_metabolism.py       —  文件膨胀/失活/结构完整性扫描

认知操作工具链（新增）：
  llm_analogizer.py   —  LLM 类比与想象（类相干多方向推演，需 ANTHROPIC_API_KEY）

公共模块：
  paths.py            —  continuity 根目录统一解析（参数 > FAVA_CONTINUITY_ROOT > 仓库根 > ~/.hermes/continuity）
```

> 依赖：核心工具链仅依赖 Python 标准库，克隆后即可运行。`llm_analogizer.py` 需 `anthropic`（见 `pyproject.toml` 的 `llm` 可选依赖）；运行测试需 `pytest`（`test` 可选依赖）。

---

## 脚本清单

### 1. theory_application_checker.py ⭐ [2026-06-06]

**功能：** 任务前 TTAF（任务理论应用框架）检视清单自动生成  
**输入：** 任务描述字符串  
**输出：** 按层级生成的 D1～D6 维度 JSON 清单

关键词自动识别任务层级（simple / engineering / subject / theory / core），生成对应深度的检视清单。core 层操作自动附加警告提示。

```bash
python3 theory_application_checker.py "优化 SQLite 查询性能"
python3 theory_application_checker.py "修改 core/concepts.md" --level core
python3 theory_application_checker.py "展开属性与法则属性的边界" --save
```

---

### 2. feedback_classifier.py ⭐ [已更新 2026-06-06]

**功能：** 自动分类反馈为 TEMPORARY / PATTERN / ANOMALY / ENHANCEMENT  
**输入：** 反馈记录（JSON 文件）  
**输出：** 分类结果 + 候选生成

**新增：** 跨任务 PATTERN 相似度合并（CJK 二元组 Jaccard，阈值 0.15），相似 PATTERN 自动合并为证据而非创建重复候选。

---

### 3. evolution_candidate_manager.py ⭐ [已重构 2026-06-06]

**功能：** 管理理论演化候选完整生命周期  
**存储：** SQLite（通过 `candidate_store.py`，不再是纯 JSON 文件）  
**状态链：** `CANDIDATE → APPROVED → INTEGRATED`

```bash
python3 evolution_candidate_manager.py list
python3 evolution_candidate_manager.py list-pending
python3 evolution_candidate_manager.py show <id>
python3 evolution_candidate_manager.py approve <id>
python3 evolution_candidate_manager.py reject <id>
python3 evolution_candidate_manager.py integrate <id>   # 写入 runtime 草案
python3 evolution_candidate_manager.py dry-run <id>     # 预览，不写入
python3 evolution_candidate_manager.py add-evidence <id> <task> <描述>
```

---

### 4. candidate_store.py ⭐ [2026-06-06]

**功能：** SQLite 候选持久化存储（`evolution_candidate_manager` 的底层后端）  
**特性：** 带索引的多条件查询、统计、潜在重复检测、JSON 目录导入/导出（原子写入）

```bash
python3 candidate_store.py stats
python3 candidate_store.py list [--status CANDIDATE] [--type PATTERN] [--search 关键词]
python3 candidate_store.py duplicates
python3 candidate_store.py import <dir>
python3 candidate_store.py export <dir>
```

---

### 5. auto_feedback_submitter.py ⭐ [2026-06-06]

**功能：** 编程式反馈提交（P0.1，闭合反馈提交环路）  
**核心价值：** 无需手动填写模板，Hermes 可在任务完成后直接调用

```bash
# 完整提交（自动分类 + 候选生成）
python3 auto_feedback_submitter.py "任务名称" "观察" "局限" "建议"

# 快速提交
python3 auto_feedback_submitter.py --quick "任务名称" --rating good --summary "一句话总结"

# 查看已提交反馈
python3 auto_feedback_submitter.py --list
```

---

### 6. theory_integration_writer.py ⭐ [2026-06-06]

**功能：** APPROVED 候选→runtime 草案文件自动写入（P0.2，闭合集成环路）  
**路由逻辑：**
- ENHANCEMENT（法则属性型） → `concepts_v2_draft.md`
- ENHANCEMENT（展开属性型） → `theory_v2_draft.md`
- ANOMALY → `failure_conditions_draft.md`
- 所有类型 → `reflection.md` + `HOPE_STATE.md`（若 hope_direction 非空）

> 说明：上述 `*_draft.md`、`reflection.md` 是工具链在运行时**按需生成**的候选/反思输出文件，
> 不随公开仓库分发；首次集成时会在 `runtime/` 下自动创建。

```bash
python3 theory_integration_writer.py integrate <candidate-id>
python3 theory_integration_writer.py dry-run <candidate-id>     # 预览
python3 theory_integration_writer.py integrate-file <path.json> # 直接集成文件
```

---

### 7. integrated_feedback_workflow.py [已更新 2026-06-06]

**功能：** 一键完整反馈处理工作流（格式检测→分类→候选生成→希望追踪）  
**原子写入：** 所有写操作均使用 `tempfile + os.replace` 防止写入中途损坏

```bash
python3 integrated_feedback_workflow.py <反馈文件>
```

---

### 8. feedback_format_converter.py

**功能：** Markdown ↔ JSON 反馈格式转换  
**何时运行：** 在 `integrated_feedback_workflow` 中自动调用

---

### 9. hope_tension_collector.py ⭐ [已增强 2026-06-06]

**功能：** 希望=本原张力健康扫描器（只读，🟢 层）  
**扫描维度：** 约束侧（core 稳定性）、展开侧（reflection 活跃度）、张力比率  
**新增：** JSONL 时序历史记录 + ↑↓→ 趋势箭头对比报告

```bash
python3 hope_tension_collector.py           # 即时扫描
python3 hope_tension_collector.py --save    # 扫描并保存快照
python3 hope_tension_collector.py --history # 显示最近 10 次趋势
python3 hope_tension_collector.py --history 20  # 最近 20 次
python3 hope_tension_collector.py --json    # 同时输出 JSON
```

---

### 10. memory_metabolism.py ⭐ [2026-06-06]

**功能：** runtime 记忆代谢扫描器（只读，🟢 层）  
**扫描维度：**
- 文件膨胀：`HOPE_STATE.md`、`index.md`、`theory_to_code_mapping.md` 等阈值告警
- 文件失活：`HOPE_STATE.md`(>21d)、`index.md`(>30d) 等长期未更新告警
- 结构完整性：bootstrap / index / HOPE_STATE / TTAF 四大结构件存在性检查

> 阈值字典（`SIZE_THRESHOLDS` / `STALE_THRESHOLDS`）在 `memory_metabolism.py` 顶部定义，
> 可按实际 runtime 文件集自行调整。

```bash
python3 memory_metabolism.py        # 人类可读报告
python3 memory_metabolism.py --json # 同时输出 JSON
```

---

### 11. llm_analogizer.py ⭐ [2026-06-07]

**功能：** LLM 增强的类比与想象工具（需要 `ANTHROPIC_API_KEY`）  
**两个子命令：**
- `compare`：识别两段描述的局限性相同，推断法则属性
- `imagine`：从起点出发，类相干模式下生成 N 个推演方向（维持多态共存，标注坍缩触发条件）

```bash
export ANTHROPIC_API_KEY=sk-ant-...

python3 llm_analogizer.py compare "描述A" "描述B"
python3 llm_analogizer.py imagine "当前理论：法则属性和展开属性在本原层未分化" --n 3
python3 llm_analogizer.py imagine "起点描述" --collapse "选择的方向"
python3 llm_analogizer.py compare --against-candidates "新观察"
```

---

## 快速上手：完整工作流示例

```bash
# 1. 任务前：生成 TTAF 检视清单
python3 scripts/theory_application_checker.py "优化候选存储查询性能"

# 2. 执行任务，完成后提交反馈
python3 scripts/auto_feedback_submitter.py \
    "候选存储查询优化" \
    "SQLite 索引使查询速度提升 10x" \
    "大数据量下全表扫描仍有瓶颈" \
    "可考虑增加复合索引"

# 3. 查看生成的候选
python3 scripts/evolution_candidate_manager.py list-pending

# 4. 批准并集成
python3 scripts/evolution_candidate_manager.py approve <id>
python3 scripts/evolution_candidate_manager.py integrate <id>

# 5. 健康监控
python3 scripts/hope_tension_collector.py --save
python3 scripts/memory_metabolism.py
```

---

## 与框架的关系

| 框架 | 时间 | 对应脚本 |
|------|------|--------|
| TTAF | 任务前 | `theory_application_checker.py` |
| PORF | 任务中 | （人工记录，结果传入 auto_feedback_submitter） |
| 反馈提交 | 任务后 | `auto_feedback_submitter.py` |
| 反馈分类 | 自动 | `feedback_classifier.py` via `integrated_feedback_workflow.py` |
| 候选管理 | 候选生成→审批 | `evolution_candidate_manager.py` + `candidate_store.py` |
| 候选集成 | APPROVED→INTEGRATED | `theory_integration_writer.py` |
| 健康监控 | 持续 | `hope_tension_collector.py` + `memory_metabolism.py` |
| 类比识别 | 随时 | `llm_analogizer.py compare`（需 API Key）|
| 想象推演 | 随时 | `llm_analogizer.py imagine`（类相干多方向，需 API Key）|

---

**最后更新：** 2026-06-07  
**测试覆盖：** 59 项（`python3 -m pytest tests/ -v`，全部通过）  
**CI：** GitHub Actions 每次 push/PR 自动触发
