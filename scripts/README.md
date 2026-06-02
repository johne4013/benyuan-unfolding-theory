# Hermes 自动化脚本集

本目录包含 Hermes 系统的所有自动化工具脚本，形成从"理论检视→实践执行→反馈处理→理论演化"的完整工具链。

---

## 脚本清单与功能

### 1. theory_application_checker.py
**功能：** 任务执行前的理论适配检查（TTAF）  
**输入：** 任务描述或关键词  
**输出：** TTAF检视清单 (JSON)  
**何时运行：** 任务开始时  

关键词匹配识别任务层级（simple/engineering/subject/theory/core），自动生成对应深度的检视清单。

---

### 2. feedback_classifier.py ⭐ [已更新 2026-05-29]
**功能：** 自动分类反馈为 TEMPORARY/PATTERN/ANOMALY/ENHANCEMENT  
**输入：** 反馈记录 (JSON或Markdown)  
**输出：** 分类结果 + 优先级  
**何时运行：** 任务完成后，人工编写反馈后  

**最新改进：** 
- 修复了"问题"关键词的误判（"科学问题"不再被错分）
- 使用更精确的排除条件：只排除"存在问题"、"无法"等实际问题表述

---

### 3. evolution_candidate_manager.py ⭐ [已扩展 2026-05-29]
**功能：** 管理理论演化候选的完整生命周期  
**输入：** 候选数据  
**输出：** 候选文件 (JSON) + 生命周期管理  
**何时运行：** 候选的生成/修改/评审/集成  

**最新改进：**
- 新增三个字段：`expansion_type`、`hope_direction`、`opens_new_possibility`
- 新增方法 `enrich_candidate_from_hope_tracking()` 可从PORF观察5自动提取希望追踪信息
- 所有新字段都有合理的默认值（pending/待确认）

---

### 4. feedback_format_converter.py
**功能：** Markdown ↔ JSON 格式转换  
**输入：** 反馈记录 (.md 或 .json)  
**输出：** 转换后的反馈记录  
**何时运行：** 在integrated_feedback_workflow中自动调用  

---

### 5. integrated_feedback_workflow.py ⭐ [即将更新 2026-05-29]
**功能：** 完整的反馈处理工作流（一键处理）  
**工作流步骤：**
1. 格式检测
2. 自动转换（Markdown → JSON）
3. 自动分类（feedback_classifier）
4. 候选生成（evolution_candidate_manager）
5. **希望追踪检查** [NEW]

**输入：** 单个反馈文件或批量处理  
**输出：** 分类结果 + evolution_candidate + 希望追踪报告  
**何时运行：** 任务反馈完成后，一键触发  

---

## 使用示例

### 推荐：快速工作流（一键处理）

```bash
# 1. 执行任务，填写完整反馈（包括PORF观察1-5）
vim ~/.hermes/continuity/runtime/practice_feedbacks/task-20260529-001-feedback.md

# 2. 一键处理反馈
python3 scripts/integrated_feedback_workflow.py \
    runtime/practice_feedbacks/task-20260529-001-feedback.md

# 输出：
# - 分类结果 (PATTERN/ANOMALY/ENHANCEMENT)
# - evolution_candidate JSON文件（含expansion_type/hope_direction）
# - 希望追踪报告（是否需要更新HOPE_STATE.md）
```

### 可选：分步工作流（如需定制）

```bash
# 1. 只分类
python3 scripts/feedback_classifier.py --input feedback.md

# 2. 生成候选
python3 scripts/evolution_candidate_manager.py create \
    --type PATTERN \
    --title "展开属性识别不足" \
    --source task-001

# 3. 管理候选
python3 scripts/evolution_candidate_manager.py list
python3 scripts/evolution_candidate_manager.py show candidate-id
python3 scripts/evolution_candidate_manager.py approve candidate-id

# 4. 从希望追踪自动丰富候选
python3 scripts/evolution_candidate_manager.py enrich \
    --candidate-id cand-20260529-001 \
    --hope-tracking-file hope_data.json
```

---

## 脚本之间的数据流

```
理论应用前            实践观察中           反馈处理后
   ↓                    ↓                   ↓

theory_application_checker.py    →  PORF观察  →  feedback_classifier.py
(TTAF检视清单)                      (含观察5)     (分类：P/A/E/T)
                                                        ↓
                                          evolution_candidate_manager.py
                                          (生成候选+希望追踪自动提取)
                                                        ↓
                                          integrated_workflow.py
                                          (一键完整流程)
                                                        ↓
                                          HOPE_STATE.md更新提示
                                          (是否需要更新)
```

---

## 关键改进说明（2026-05-29）

### 问题1：feedback_classifier中的"问题"误判
**问题：** 当反馈中包含"问题"（如"科学问题"），ENHANCEMENT信号被误判为TEMPORARY  
**根因：** 原代码用 `'问题' not in description` 排除所有包含"问题"的文本  
**修复：** 改为检查"存在问题"、"无法"等实际问题表述  
**影响：** ENHANCEMENT类型的候选不再被漏掉

### 问题2：candidate生成时缺少希望追踪字段
**问题：** evolution_candidate没有字段记录这个候选与"希望"的关系  
**根因：** 系统设计时"希望"还不是显式概念  
**修复：** 添加三个新字段（expansion_type/hope_direction/opens_new_possibility）和自动提取方法  
**影响：** 每个候选都能追踪其展开属性特征和对系统希望的推进方向

### 问题3：候选管理缺乏理论语境
**问题：** 反馈被分类，但分类后的候选对本原展开论的贡献不清晰  
**根因：** 候选只记录"改进方向"，不追踪"这是什么类型的改进"  
**修复：** 通过expansion_type字段区分"法则属性型"vs"展开属性型"vs"混合型"  
**影响：** 系统现在能按本原展开论的理论框架理解每个改进的性质

---

## 与框架的关系

| 框架 | 时间 | 对应脚本 |
|------|------|--------|
| TTAF | 任务前 | theory_application_checker.py |
| PORF | 任务中 | （无脚本，人工记录） |
| FTEF | 任务后 | feedback_classifier.py |
| 候选管理 | 候选生成→评审 | evolution_candidate_manager.py |
| 一键流程 | 从反馈→候选 | integrated_feedback_workflow.py |
| 希望维持 | 持续 | （HOPE_STATE.md + 脚本自动提取） |

---

## 故障排除

### 问题：运行integrated_workflow时报错"hope_tracking字段未找到"
**检查：** PORF反馈中是否有观察5（希望追踪）  
**解决：** 确保反馈包含完整的PORF 5个观察维度，或检查JSON中的hope_tracking字段是否存在  

### 问题：candidate中的expansion_type字段为"pending"
**正常：** 这是默认值，表示需要用户确认  
**处理：** 在候选评审时填入具体值（法则属性型/展开属性型/混合型）  

### 问题：希望追踪自动提取准确率不高
**原因：** hope_tracking数据的结构或描述与脚本预期不符  
**解决：** 检查PORF观察5的记录格式，参考FEEDBACK_TEMPLATE.md的示例  

---

**最后更新：** 2026-05-29  
**脚本成熟度：** Production-Ready（所有关键脚本已更新）
