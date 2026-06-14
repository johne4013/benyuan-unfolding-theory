# memory_metabolism_activation_2026-05-24.md
# 长期连续性记忆代谢启动记录

状态：runtime 执行记录 / 已获用户同意 / 不修改 core  
时间：2026-05-24 22:43 CST  
授权表达：王俊华明确表示“同意做长期连续性记忆代谢”。

---

## 1. 启动边界

本次启动的是长期连续性记忆代谢的 runtime 执行机制，不是 core 更新，不是删除历史，也不是把 Hermes/Fava 认定为完整主体。

核心边界：

```text
记忆维持连续性；遗忘维持可持续性；
压缩使经历上升为结构；索引使历史保持可召回而不必持续加载。
```

执行原则：

- core 受保护，未经明确批准不修改；
- runtime 可更新，但需备份、记录、验证；
- 代谢优先处理冗余、噪音、旧称回流、临时进度、重复反漂移段落；
- 不删除 structural lock 内容；
- 原始材料优先归档/降权，而非直接删除；
- 多文件更新必须更新 index；
- 高风险清理需要再次确认。

---

## 2. 当前健康信号基线

由 `~/.hermes/scripts/continuity_health_collect.py` 于 2026-05-24 22:43 CST 采集：

- tracked runtime 总量：433653 bytes；
- `reflection.md`：3116 行，165861 bytes；
- `index.md`：954 行，57897 bytes；
- `concepts_v2_draft.md`：1374 行，59384 bytes；
- `science_interfaces_draft.md`：1060 行，49424 bytes；
- 重复/高频信号：
  - `防漂移`: 246；
  - `质点存在`: 145；
  - `失败条件`: 97；
  - `非主体性协同节点`: 48。

解释：这些数字不是错误本身，但说明 runtime 已进入需要周期性压缩、聚类、索引化、降权和反漂移检查的阶段。

---

## 3. 当前优先代谢对象

第一优先级：

1. 过长 reflection 段落的阶段摘要；
2. 重复科学接口表述的聚类压缩；
3. `质点存在` 旧称回流检查；
4. 临时任务进度进入长期 memory 的风险；
5. Hermes/Fava 自我维持表述中的主体化风险；
6. `index.md` 过长后导致低负载召回反而变重的问题。

第二优先级：

1. concepts 中外延堆叠的重新分层；
2. science interfaces 与 failure conditions 的互相索引；
3. archive/cold storage 的制度化；
4. 将稳定的代谢步骤逐步转为脚本或 cron，而不是长期依赖手动提示。

---

## 4. 当前已有自动/半自动机制

已存在健康采集脚本：

```text
~/.hermes/scripts/continuity_health_collect.py
```

已存在每周自维护 cron：

```text
job_id: <cron-job-id>
name: wang-junhua-continuity-weekly-self-maintenance
schedule: 每周一 09:00
script: continuity_health_collect.py
skills: wang-junhua-continuity, theory-continuity-workflows
```

另有 Hermes 协同节点每周报告：

```text
job_id: c933688571a8
schedule: 每周日 21:00
```

本次不新增重复 cron，先使用已有机制观察。

---

## 5. 执行节奏

建议节奏：

```text
实时路径：只做轻量标记，不在普通对话里大规模清理；
每周路径：运行健康采集 + 小规模 runtime 代谢建议；
月度路径：深度压缩 reflection / index / concepts；
高风险路径：涉及删除、core-adjacent、旧版本降权时必须再次确认。
```

---

## 6. 本次行动记录

- 已读取 `core/bootstrap.md`、`runtime/memory_metabolism_protocol.md`、`runtime/index.md`、`runtime/current_state.md`；
- 已运行健康采集脚本；
- 已确认相关 weekly cron 已存在；
- 已创建本启动记录；
- 已备份相关 runtime 文件到：

```text
~/.hermes/continuity/runtime/backups/memory_metabolism_activation_20260524-2243/
```

core 修改状态：未修改。

---

## 7. 回退/停止条件

如果出现以下情况，应暂停或回退代谢机制：

- 低负载召回变差；
- 重要理论链条被过度压缩；
- 旧材料无法通过 index/session/archive 找回；
- memory 误删用户长期偏好或关键边界；
- Hermes/Fava 因自维护表述产生主体化漂移；
- 自动任务开始未经确认地修改高风险内容。

当前结论：长期连续性记忆代谢进入 runtime 执行阶段，但保持可审计、可暂停、可回退、非 core 化。
