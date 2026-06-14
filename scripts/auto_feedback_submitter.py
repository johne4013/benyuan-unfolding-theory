#!/usr/bin/env python3
"""
自动反馈提交器（P0.1）
为 Hermes 提供编程式反馈提交 API，消除任务完成后手动填写模板的步骤。
属于 🟢 层操作（自主信息组织）。

用法（编程式）：
    from auto_feedback_submitter import AutoFeedbackSubmitter
    submitter = AutoFeedbackSubmitter()
    result = submitter.submit(
        task_name="优化树遍历算法",
        observation="生成器方案打开了流式处理的新维度",
        limitation="理论未区分算法层的法则约束与展开约束",
        suggestion="在 TTAF D2 中增加算法层约束分类",
        hope_tracking={"impact_on_hope": "推进", "new_possibility_found": "是",
                       "possibility_description": "生成器方案打开了流式处理新维度"}
    )

用法（命令行）：
    python auto_feedback_submitter.py <task_name> <observation> <limitation> <suggestion>
    python auto_feedback_submitter.py --quick <task_name> <rating_1_10> <summary>
    python auto_feedback_submitter.py --list
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path


class AutoFeedbackSubmitter:
    """编程式反馈提交入口，供 Hermes 在任务完成后自动调用"""

    def __init__(self, feedbacks_dir: str = None):
        if feedbacks_dir:
            self.feedbacks_dir = Path(feedbacks_dir).expanduser()
        else:
            from paths import runtime_dir
            self.feedbacks_dir = runtime_dir() / "practice_feedbacks"
        self.feedbacks_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def submit(
        self,
        task_name: str,
        observation: str,
        limitation: str,
        suggestion: str,
        task_id: str = None,
        hope_tracking: dict = None,
        auto_process: bool = True,
        verbose: bool = False,
    ) -> dict:
        """
        提交一条反馈，可选择立即触发集成工作流。

        Args:
            task_name:      任务名称（简短描述）
            observation:    理论有效性观察（理论预期 vs 实际发生了什么）
            limitation:     发现的理论局限
            suggestion:     建议的改进方向
            task_id:        可选手动指定 ID；默认自动生成 task-YYYYMMDD-XXX
            hope_tracking:  可选希望追踪字典，字段见 PORF 观察 5
                            {impact_on_hope, new_possibility_found,
                             possibility_description, limitation_encountered}
            auto_process:   是否立即触发 IntegratedFeedbackWorkflow
            verbose:        workflow 执行时是否打印详细输出

        Returns:
            {task_id, feedback_file, workflow_result}
        """
        if not task_id:
            task_id = self._generate_task_id()

        feedback = {
            "task_id": task_id,
            "task_name": task_name,
            "submitted_at": datetime.now().isoformat(),
            "observation": observation,
            "limitation": limitation,
            "suggestion": suggestion,
        }
        if hope_tracking:
            feedback["hope_tracking"] = hope_tracking

        filepath = self._write_feedback(feedback, task_id)

        result = {
            "task_id": task_id,
            "feedback_file": str(filepath),
            "workflow_result": None,
        }

        if auto_process:
            result["workflow_result"] = self._run_workflow(str(filepath), verbose)

        return result

    def submit_quick(
        self,
        task_name: str,
        rating: int,
        summary: str,
        candidate_type: str = "NONE",
        auto_process: bool = True,
    ) -> dict:
        """
        快速提交（对应 FEEDBACK_TEMPLATE 快速版，5 分钟内可完成）。

        Args:
            task_name:      任务名称
            rating:         理论有效性评分 1-10
            summary:        一句话观察总结
            candidate_type: PATTERN / ANOMALY / ENHANCEMENT / NONE
        """
        observation = f"[评分 {rating}/10] {summary}"
        limitation = "（快速提交，局限未详细描述）"
        if candidate_type != "NONE":
            suggestion = f"候选类型：{candidate_type}，具体建议待后续补充"
        else:
            suggestion = "无改进候选"
        return self.submit(task_name, observation, limitation, suggestion,
                          auto_process=auto_process)

    def list_feedbacks(self, limit: int = 20) -> list:
        """列出最近提交的反馈文件"""
        files = sorted(
            self.feedbacks_dir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:limit]
        results = []
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                if not isinstance(data, dict):
                    results.append({"file": f.name, "error": "结构无效"})
                    continue
                results.append({
                    "file": f.name,
                    "task_id": data.get("task_id") or "<missing-task-id>",
                    "task_name": data.get("task_name") or "<missing-task-name>",
                    "submitted_at": data.get("submitted_at") or "<missing-date>",
                })
            except (json.JSONDecodeError, OSError):
                results.append({"file": f.name, "error": "无法读取"})
        return results

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _generate_task_id(self) -> str:
        """生成唯一任务 ID，格式：task-YYYYMMDD-XXX"""
        date_str = datetime.now().strftime("%Y%m%d")
        existing = list(self.feedbacks_dir.glob(f"task-{date_str}-*.json"))
        seq_nums = []
        for f in existing:
            stem = f.stem.replace("-feedback", "")
            parts = stem.split("-")
            if len(parts) >= 3:
                try:
                    seq_nums.append(int(parts[-1]))
                except ValueError:
                    pass
        next_seq = max(seq_nums, default=0) + 1
        return f"task-{date_str}-{next_seq:03d}"

    def _write_feedback(self, feedback: dict, task_id: str) -> Path:
        """原子写入反馈 JSON 文件"""
        filename = f"{task_id}-feedback.json"
        filepath = self.feedbacks_dir / filename

        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.feedbacks_dir, suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(feedback, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, filepath)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        return filepath

    def _run_workflow(self, feedback_file: str, verbose: bool) -> dict:
        """调用集成工作流处理刚提交的反馈"""
        scripts_dir = Path(__file__).parent
        sys.path.insert(0, str(scripts_dir))
        try:
            from integrated_feedback_workflow import IntegratedFeedbackWorkflow
            workflow = IntegratedFeedbackWorkflow()
            return workflow.process_feedback(feedback_file, verbose=verbose)
        except Exception as e:
            return {"errors": [f"工作流调用失败：{e}"], "steps_completed": []}


# ======================================================================
# 命令行接口
# ======================================================================

if __name__ == "__main__":
    submitter = AutoFeedbackSubmitter()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("自动反馈提交器")
        print("=" * 70)
        print("\n用法：")
        print("  完整提交：")
        print("    python auto_feedback_submitter.py <task_name> <observation> <limitation> <suggestion>")
        print()
        print("  快速提交：")
        print("    python auto_feedback_submitter.py --quick <task_name> <rating> <summary> [candidate_type]")
        print()
        print("  列出最近反馈：")
        print("    python auto_feedback_submitter.py --list")
        print()
        print("参数说明：")
        print("  task_name    任务名称")
        print("  observation  理论有效性观察（理论预期 vs 实际结果）")
        print("  limitation   发现的理论局限")
        print("  suggestion   建议的改进方向")
        print("  rating       理论有效性评分 1-10（快速版）")
        print("  summary      一句话观察（快速版）")
        print("  candidate_type  PATTERN/ANOMALY/ENHANCEMENT/NONE（快速版，默认 NONE）")
        print("\n" + "=" * 70)

    elif sys.argv[1] == "--list":
        feedbacks = submitter.list_feedbacks()
        if not feedbacks:
            print("暂无已提交反馈")
        else:
            print(f"\n最近 {len(feedbacks)} 条反馈：")
            print("-" * 60)
            for fb in feedbacks:
                if "error" in fb:
                    print(f"  {fb['file']} [读取失败]")
                else:
                    date = fb.get('submitted_at', '')
                    date = date[:10] if date and not date.startswith('<missing') else date
                    print(f"  {fb['task_id']} | {fb['task_name']} | {date}")

    elif sys.argv[1] == "--quick" and len(sys.argv) >= 5:
        task_name = sys.argv[2]
        rating = int(sys.argv[3])
        summary = sys.argv[4]
        ctype = sys.argv[5] if len(sys.argv) > 5 else "NONE"
        result = submitter.submit_quick(task_name, rating, summary, ctype, auto_process=True)
        print(f"\n✓ 快速反馈已提交")
        print(f"  任务 ID：{result['task_id']}")
        print(f"  文件：{result['feedback_file']}")
        if result["workflow_result"]:
            wr = result["workflow_result"]
            steps = len(wr.get("steps_completed", []))
            errors = wr.get("errors", [])
            print(f"  工作流：{steps} 步完成" + (f"，{len(errors)} 个错误" if errors else ""))

    elif len(sys.argv) >= 5:
        task_name = sys.argv[1]
        observation = sys.argv[2]
        limitation = sys.argv[3]
        suggestion = sys.argv[4]
        result = submitter.submit(task_name, observation, limitation, suggestion,
                                  verbose=True)
        print(f"\n✓ 反馈已提交")
        print(f"  任务 ID：{result['task_id']}")
        print(f"  文件：{result['feedback_file']}")

    else:
        print("参数不足，使用 --help 查看帮助")
        sys.exit(1)
