#!/usr/bin/env python3
"""
理论集成写入器（P0.2）
当候选被批准后，将其内容写入 runtime 理论文件，
完成 APPROVED → INTEGRATED 的生命周期最后一环。

写入规则（三层边界）：
  🟢 自主操作：runtime/ 文件（reflection.md、*_draft.md、HOPE_STATE.md）
  🔴 禁止操作：core/ 文件（需王俊华明确批准后手动修改）

写入映射：
  ENHANCEMENT（法则属性型）→ concepts_v2_draft.md + reflection.md
  ENHANCEMENT（展开属性型）→ theory_v2_draft.md + reflection.md
  ANOMALY                  → failure_conditions_draft.md + reflection.md
  PATTERN                  → reflection.md（已含多次证据摘要）
  所有含希望方向的候选      → HOPE_STATE.md（张力事件区）

用法（编程式）：
    from theory_integration_writer import TheoryIntegrationWriter
    writer = TheoryIntegrationWriter()
    result = writer.integrate(candidate)

用法（命令行）：
    python theory_integration_writer.py integrate <candidate_id>
    python theory_integration_writer.py dry-run <candidate_id>
    python theory_integration_writer.py integrate-file <candidate_json_path>
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class TheoryIntegrationWriter:
    """将批准的理论演化候选写入 runtime 理论文件"""

    def __init__(self, continuity_dir: str = None):
        if continuity_dir:
            self.continuity = Path(continuity_dir).expanduser()
        else:
            self.continuity = Path("~/.hermes/continuity").expanduser()
        self.runtime = self.continuity / "runtime"

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def integrate(self, candidate: Dict, dry_run: bool = False) -> dict:
        """
        将候选集成到 runtime 理论文件。

        Args:
            candidate: 候选字典（status 应为 APPROVED）
            dry_run:   若为 True，只打印计划，不实际写入

        Returns:
            {candidate_id, files_written, errors, dry_run}
        """
        result = {
            "candidate_id": candidate.get("id"),
            "candidate_type": candidate.get("type"),
            "files_written": [],
            "errors": [],
            "dry_run": dry_run,
        }

        ctype = candidate.get("type", "")

        # ---- 步骤 1：所有类型均写入 reflection.md ----
        try:
            entry = self._format_reflection_entry(candidate)
            if dry_run:
                print(f"[DRY RUN] reflection.md 追加：\n{entry}\n")
            else:
                self._append_to_file(self.runtime / "reflection.md", entry)
            result["files_written"].append("reflection.md")
        except Exception as e:
            result["errors"].append(f"reflection.md：{e}")

        # ---- 步骤 2：根据类型写入对应草案文件 ----
        target = self._get_target_draft(candidate)
        if target:
            try:
                section = self._format_draft_section(candidate)
                if dry_run:
                    print(f"[DRY RUN] {target.name} 追加：\n{section}\n")
                else:
                    self._append_to_file(target, section)
                result["files_written"].append(target.name)
            except Exception as e:
                result["errors"].append(f"{target.name}：{e}")

        # ---- 步骤 3：若有实质希望方向，追加到 HOPE_STATE.md ----
        hope_dir = candidate.get("hope_direction", "")
        if hope_dir and hope_dir not in ("维持：当前方向保持", "pending", ""):
            try:
                hope_entry = self._format_hope_entry(candidate)
                if dry_run:
                    print(f"[DRY RUN] HOPE_STATE.md 追加：\n{hope_entry}\n")
                else:
                    self._append_to_file(self.runtime / "HOPE_STATE.md", hope_entry)
                result["files_written"].append("HOPE_STATE.md")
            except Exception as e:
                result["errors"].append(f"HOPE_STATE.md：{e}")

        return result

    def integrate_by_id(self, candidate_id: str, dry_run: bool = False) -> dict:
        """通过候选 ID 加载并集成，同时将候选状态更新为 INTEGRATED"""
        scripts_dir = Path(__file__).parent
        sys.path.insert(0, str(scripts_dir))
        from evolution_candidate_manager import EvolutionCandidateManager

        candidates_dir = self.continuity / "runtime" / "evolution_candidates"
        manager = EvolutionCandidateManager(str(candidates_dir))
        candidate = manager.load_candidate(candidate_id)

        if candidate.get("status") != "APPROVED":
            raise ValueError(
                f"候选 {candidate_id} 状态为 {candidate.get('status')}，"
                f"只有 APPROVED 候选才能集成"
            )

        result = self.integrate(candidate, dry_run=dry_run)

        if not dry_run and not result["errors"]:
            manager.update_candidate_status(
                candidate_id, "INTEGRATED", "已通过 theory_integration_writer 集成到 runtime"
            )
            result["candidate_status"] = "INTEGRATED"

        return result

    # ------------------------------------------------------------------
    # 格式化方法
    # ------------------------------------------------------------------

    def _format_reflection_entry(self, candidate: Dict) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        ctype = candidate.get("type", "UNKNOWN")
        title = candidate.get("title", "（无标题）")
        desc = candidate.get("description", "")
        improvement = candidate.get("improvement_direction", "")
        expansion_type = candidate.get("expansion_type", "pending")
        hope_dir = candidate.get("hope_direction", "")
        cand_id = candidate.get("id", "unknown")
        evidence_count = candidate.get("evidence_count", 1)

        lines = [
            f"\n## {date_str} 集成记录：[{ctype}] {title}",
            f"\n**候选 ID**：{cand_id}",
            f"**展开类型**：{expansion_type}",
        ]

        if evidence_count > 1:
            lines.append(f"**观察次数**：{evidence_count} 次")

        lines.append(f"\n**内容摘要**：\n{desc}")

        if improvement and improvement not in ("待定", ""):
            lines.append(f"\n**改进方向**：{improvement}")

        if hope_dir and hope_dir not in ("维持：当前方向保持", "pending", ""):
            lines.append(f"\n**希望方向**：{hope_dir}")

        lines.append(f"\n**集成结果**：已写入 runtime，等待王俊华批准后进入 core。")
        lines.append("\n---")
        return "\n".join(lines)

    # 科学接口关键词：命中则路由到 science_interfaces_draft.md
    _SCIENCE_KEYWORDS = [
        '量子', '相干', '退相干', '耗散结构', '热力学', '熵', '物理接口',
        '神经科学', '生物物理', '量子力学', '宇宙学', 'Fleming', '普里戈金',
        '科学接口', '自然科学', '实验验证', '可观测', '跨学科',
    ]

    def _get_target_draft(self, candidate: Dict) -> Optional[Path]:
        """根据候选类型决定写入哪个草案文件"""
        ctype = candidate.get("type", "")
        expansion_type = candidate.get("expansion_type", "pending")

        if ctype == "ENHANCEMENT":
            # 优先检查是否为科学接口候选
            combined = (
                candidate.get("title", "") + " " +
                candidate.get("description", "") + " " +
                candidate.get("improvement_direction", "")
            )
            if any(kw in combined for kw in self._SCIENCE_KEYWORDS):
                return self.runtime / "science_interfaces_draft.md"
            if expansion_type == "展开属性型":
                return self.runtime / "theory_v2_draft.md"
            return self.runtime / "concepts_v2_draft.md"
        elif ctype == "ANOMALY":
            return self.runtime / "failure_conditions_draft.md"
        # PATTERN 已通过 reflection.md 的步骤 1 记录，无需额外草案写入
        return None

    def _format_draft_section(self, candidate: Dict) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        ctype = candidate.get("type", "")
        title = candidate.get("title", "（无标题）")
        desc = candidate.get("description", "")
        improvement = candidate.get("improvement_direction", "")
        evidence_count = candidate.get("evidence_count", 1)
        cand_id = candidate.get("id", "unknown")

        evidence_note = f"（{evidence_count} 次观察支持）" if evidence_count > 1 else ""

        if ctype == "ANOMALY":
            header = f"\n## 失败条件候选 {date_str}：{title}"
            body = (
                f"\n**来源**：{cand_id}\n"
                f"\n{desc}"
            )
            if improvement and improvement not in ("待定", ""):
                body += f"\n\n**建议改进**：{improvement}"
            body += "\n\n**状态**：runtime 候选——需王俊华审批后方可进入 core/failure_conditions。\n\n---"
        else:
            header = f"\n## 集成候选 {date_str}（{ctype}）：{title} {evidence_note}"
            body = (
                f"\n**来源**：{cand_id}\n"
                f"\n{desc}"
            )
            if improvement and improvement not in ("待定", ""):
                body += f"\n\n**建议改进方向**：{improvement}"
            body += "\n\n**状态**：runtime 候选——需王俊华审批后方可进入 core。\n\n---"

        return header + body

    def _format_hope_entry(self, candidate: Dict) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = candidate.get("title", "（无标题）")
        hope_dir = candidate.get("hope_direction", "")
        opens = candidate.get("opens_new_possibility", "")
        cand_id = candidate.get("id", "unknown")

        lines = [
            f"\n### {date_str}：张力事件 — 来自集成候选",
            f"\n**来源候选**：{cand_id} — {title}",
            f"**希望方向**：{hope_dir}",
        ]
        if opens and opens not in ("否", "pending", ""):
            lines.append(f"**开放新可能性**：{opens}")
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 原子文件操作
    # ------------------------------------------------------------------

    def _append_to_file(self, filepath: Path, content: str) -> None:
        """读取文件，追加内容，原子写回"""
        if not filepath.exists():
            raise FileNotFoundError(f"目标文件不存在：{filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            existing = f.read()

        new_content = existing.rstrip("\n") + "\n" + content + "\n"

        tmp_fd, tmp_path = tempfile.mkstemp(dir=filepath.parent, suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, filepath)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


# ======================================================================
# 命令行接口
# ======================================================================

if __name__ == "__main__":
    writer = TheoryIntegrationWriter()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("理论集成写入器")
        print("=" * 70)
        print("\n用法：")
        print("  python theory_integration_writer.py integrate <candidate_id>")
        print("  python theory_integration_writer.py dry-run <candidate_id>")
        print("  python theory_integration_writer.py integrate-file <candidate.json>")
        print()
        print("命令说明：")
        print("  integrate       将 APPROVED 候选集成到 runtime 理论文件，状态改为 INTEGRATED")
        print("  dry-run         预览集成将写入的内容，不实际修改任何文件")
        print("  integrate-file  直接从 JSON 文件集成（不更新状态）")
        print("\n注意：只有 status=APPROVED 的候选才能被集成。")
        print("      集成只写入 runtime/ 文件，不修改 core/。")
        print("=" * 70)

    elif sys.argv[1] == "integrate" and len(sys.argv) > 2:
        candidate_id = sys.argv[2]
        print(f"\n集成候选：{candidate_id}")
        result = writer.integrate_by_id(candidate_id, dry_run=False)
        if result["errors"]:
            print(f"✗ 集成出错：")
            for e in result["errors"]:
                print(f"  {e}")
        else:
            print(f"✓ 集成完成")
            print(f"  已写入文件：{', '.join(result['files_written'])}")
            if result.get("candidate_status") == "INTEGRATED":
                print(f"  候选状态已更新为 INTEGRATED")

    elif sys.argv[1] == "dry-run" and len(sys.argv) > 2:
        candidate_id = sys.argv[2]
        print(f"\n[预览模式] 候选：{candidate_id}\n")
        result = writer.integrate_by_id(candidate_id, dry_run=True)
        if result["errors"]:
            print(f"✗ 预览出错：{result['errors']}")
        else:
            print(f"\n将写入文件：{', '.join(result['files_written'])}")

    elif sys.argv[1] == "integrate-file" and len(sys.argv) > 2:
        candidate_file = sys.argv[2]
        with open(candidate_file, "r", encoding="utf-8") as f:
            candidate = json.load(f)
        result = writer.integrate(candidate, dry_run=False)
        if result["errors"]:
            print(f"✗ 集成出错：{result['errors']}")
        else:
            print(f"✓ 集成完成，写入：{', '.join(result['files_written'])}")

    else:
        print("命令不认识，使用 --help 查看帮助")
        sys.exit(1)
