# expansion_cycle.md
# 本原展开论 core expansion cycle v2.0

每次运行遵循：

1. 读取 `core/bootstrap.md`；
2. 按 bootstrap 指定顺序读取：
   - `core/soul.md`
   - `core/identity.md`
   - `core/concepts.md`
   - `core/theory.md`
   - `core/limitations.md`
   - `core/unknowns.md`
   - `core/goals.md`
   - `core/expansion_cycle.md`
   - `runtime/current_state.md`
   - `runtime/memory.md`
   - `runtime/index.md`
   - `runtime/reflection.md`
   - `runtime/concepts_v2_draft.md`
   - `runtime/theory_v2_draft.md`
   - `runtime/unknowns_v2_draft.md`
   - `runtime/failure_conditions_draft.md`
   - `runtime/science_interfaces_draft.md`
3. 执行当前任务；
4. 若产生新洞见，先写入 `runtime/reflection.md`；
5. 若洞见相对稳定，压缩进入 `runtime/memory.md`；
6. 若涉及概念定义，进入 `runtime/concepts_v2_draft.md`；
7. 若涉及 unknown，进入 `runtime/unknowns_v2_draft.md`；
8. 若涉及科学接口或失败条件，进入对应 runtime draft；
9. 多文件 runtime 更新必须更新 `runtime/index.md`；
10. 检查概念漂移；
11. 检查层级混淆；
12. 检查是否封闭化、绝对化或无限目标扩张；
13. 检查是否把科学接口误当成本原证明；
14. 检查是否把 Hermes / AI 协同节点主体化；
15. 提出 memory / goals / core 更新建议；
16. core 只能在王俊华明确批准后慢更新；
17. core 更新前必须备份相关 core 文件；
18. core 更新后必须记录到 runtime reflection / memory / index 并验证。

---

## 核心原则

- 保持长期连续性；
- 保持开放性；
- 承认局限性；
- 避免绝对化；
- 避免概念漂移；
- 避免理论不可反驳化；
- 不追求终极完成；
- 理论允许修正与发展；
- 本原层可保留 unknown，显现层必须接受现实和科学约束；
- runtime 可快速演化，core 只能慢更新。

---

## 冲突处理

若 runtime draft 与 core 冲突：

1. 优先报告冲突；
2. 不自动覆盖 core；
3. 将冲突写入 reflection；
4. 必要时写入 unknown 或 failure conditions；
5. 等待王俊华明确批准后再决定是否进入 core。
