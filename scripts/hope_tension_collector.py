#!/usr/bin/env python3
"""
hope_tension_collector.py — 希望=本原张力 健康扫描器

只读扫描，输出信号，不修改任何文件。
属于 🟢 层操作（自主信息组织）。

扫描维度：
  1. 约束侧：core稳定性、边界完整性、规则一致性
  2. 展开侧：reflection活跃度、候选生成、代谢节律
  3. 张力：约束/展开比率、新结构生成、失衡告警
"""

import os, json, datetime, re
from pathlib import Path

CONTINUITY = os.path.expanduser("~/.hermes/continuity")
CORE = os.path.join(CONTINUITY, "core")
RUNTIME = os.path.join(CONTINUITY, "runtime")
ARCHIVE = os.path.join(CONTINUITY, "archive")
SCRIPTS = os.path.join(CONTINUITY, "scripts")


def file_age_days(path):
    """Days since last modification."""
    if not os.path.exists(path):
        return None
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.datetime.now() - mtime).total_seconds() / 86400


def file_size_kb(path):
    if not os.path.exists(path):
        return 0
    return os.path.getsize(path) / 1024


def count_lines(path):
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        return sum(1 for _ in f)


def count_recent_reflections(days=7):
    """Count reflection entries in the last N days."""
    ref_path = os.path.join(RUNTIME, "reflection.md")
    if not os.path.exists(ref_path):
        return 0
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    count = 0
    with open(ref_path) as f:
        for line in f:
            m = re.match(r'## (\d{4}-\d{2}-\d{2})', line)
            if m:
                date = datetime.datetime.strptime(m.group(1), "%Y-%m-%d")
                if date >= cutoff:
                    count += 1
    return count


def count_runtime_md():
    """Count .md files in runtime/."""
    count = 0
    for f in os.listdir(RUNTIME):
        if f.endswith(".md") and os.path.isfile(os.path.join(RUNTIME, f)):
            count += 1
    return count


def count_archive():
    """Count files in archive/."""
    count = 0
    for root, dirs, files in os.walk(ARCHIVE):
        count += len(files)
    return count


def check_core_integrity():
    """Check declared vs actual core files."""
    bootstrap = os.path.join(CORE, "bootstrap.md")
    if not os.path.exists(bootstrap):
        return {"error": "bootstrap.md missing"}
    declared = set()
    with open(bootstrap) as f:
        for line in f:
            m = re.match(r'\d+\.\s+core/(\S+\.md)', line.strip())
            if m:
                declared.add(m.group(1))
    actual = set()
    for f in os.listdir(CORE):
        if f.endswith(".md") and f != "bootstrap.md":
            actual.add(f)
    return {
        "declared": sorted(declared),
        "actual": sorted(actual),
        "missing": sorted(declared - actual),
        "undeclared": sorted(actual - declared),
        "intact": len(declared - actual) == 0
    }


def scan():
    """Main scan function. Returns a dict of signals."""
    now = datetime.datetime.now()
    signals = {
        "timestamp": now.isoformat(),
        "law_side": {},
        "expansion_side": {},
        "tension": {},
        "alerts": [],
        "overall": "unknown"
    }

    # === LAW SIDE ===
    core_age = file_age_days(os.path.join(CORE, "concepts.md"))
    core_integrity = check_core_integrity()

    signals["law_side"] = {
        "core_age_days": round(core_age, 1) if core_age else None,
        "core_integrity": core_integrity["intact"],
        "core_files_missing": core_integrity["missing"],
        "core_files_undeclared": core_integrity["undeclared"],
        "memory_kb": round(file_size_kb(os.path.join(RUNTIME, "memory.md")), 1),
        "current_state_age_days": round(file_age_days(os.path.join(RUNTIME, "current_state.md")), 1),
    }

    if core_age and core_age > 60:
        signals["alerts"].append({"level": "warn", "side": "law", "msg": f"Core untouched >60 days ({core_age:.0f}d) — possible stagnation"})
    if not core_integrity["intact"]:
        signals["alerts"].append({"level": "critical", "side": "law", "msg": f"Core integrity broken: missing {core_integrity['missing']}"})
    if core_integrity["undeclared"]:
        signals["alerts"].append({"level": "warn", "side": "law", "msg": f"Undeclared core files: {core_integrity['undeclared']}"})

    # === EXPANSION SIDE ===
    ref_entries_7d = count_recent_reflections(7)
    ref_size_kb = file_size_kb(os.path.join(RUNTIME, "reflection.md"))
    concepts_v2_size_kb = file_size_kb(os.path.join(RUNTIME, "concepts_v2_draft.md"))
    runtime_md_count = count_runtime_md()
    archive_count = count_archive()
    science_iface_kb = file_size_kb(os.path.join(RUNTIME, "science_interfaces_draft.md"))

    signals["expansion_side"] = {
        "reflection_entries_7d": ref_entries_7d,
        "reflection_size_kb": round(ref_size_kb, 1),
        "concepts_v2_size_kb": round(concepts_v2_size_kb, 1),
        "science_interfaces_size_kb": round(science_iface_kb, 1),
        "runtime_md_count": runtime_md_count,
        "archive_count": archive_count,
    }

    if ref_entries_7d == 0:
        signals["alerts"].append({"level": "warn", "side": "expansion", "msg": "No reflection entries in 7 days — possible stagnation"})
    if ref_size_kb > 100:
        signals["alerts"].append({"level": "warn", "side": "expansion", "msg": f"reflection.md >100KB ({ref_size_kb:.0f}KB) — needs metabolism"})
    if concepts_v2_size_kb > 80:
        signals["alerts"].append({"level": "warn", "side": "expansion", "msg": f"concepts_v2_draft >80KB — consider split"})
    if science_iface_kb > 60:
        signals["alerts"].append({"level": "info", "side": "expansion", "msg": f"science_interfaces_draft >60KB — approaching critical"})

    # === TENSION ===
    law_signals = len([a for a in signals["alerts"] if a["side"] == "law"])
    expansion_signals = len([a for a in signals["alerts"] if a["side"] == "expansion"])
    critical_alerts = len([a for a in signals["alerts"] if a["level"] == "critical"])

    if expansion_signals > law_signals * 3:
        tension_status = "expansion_dominant"
    elif law_signals > expansion_signals * 3:
        tension_status = "law_dominant"
    elif law_signals == 0 and expansion_signals == 0:
        tension_status = "balanced_healthy"
    else:
        tension_status = "balanced_with_signals"

    signals["tension"] = {
        "status": tension_status,
        "law_alerts": law_signals,
        "expansion_alerts": expansion_signals,
        "critical_alerts": critical_alerts,
        "expansion_law_ratio": round(expansion_signals / max(law_signals, 1), 1),
    }

    # === OVERALL ===
    if critical_alerts > 0:
        signals["overall"] = "critical"
    elif law_signals + expansion_signals == 0:
        signals["overall"] = "healthy"
    elif tension_status in ("balanced_healthy", "balanced_with_signals"):
        signals["overall"] = "healthy_with_notes"
    elif tension_status == "expansion_dominant":
        signals["overall"] = "expansion_heavy"
    elif tension_status == "law_dominant":
        signals["overall"] = "constraint_heavy"
    else:
        signals["overall"] = "needs_review"

    return signals


def format_report(signals):
    """Format scan results as human-readable report."""
    law = signals["law_side"]
    exp = signals["expansion_side"]
    ten = signals["tension"]

    lines = []
    lines.append("=" * 60)
    lines.append("希望=本原张力 健康扫描")
    lines.append(f"时间: {signals['timestamp']}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("【约束侧 Law Side】")
    for k, v in law.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("【展开侧 Expansion Side】")
    for k, v in exp.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append("【张力 Tension】")
    for k, v in ten.items():
        lines.append(f"  {k}: {v}")
    lines.append("")
    lines.append(f"【总体判定】{signals['overall']}")

    if signals["alerts"]:
        lines.append("")
        lines.append("【告警】")
        for a in signals["alerts"]:
            icon = {"critical": "🔴", "warn": "🟡", "info": "ℹ️"}.get(a["level"], "•")
            lines.append(f"  {icon} [{a['side']}] {a['msg']}")

    return "\n".join(lines)


if __name__ == "__main__":
    signals = scan()
    print(format_report(signals))
    # Optionally output JSON for programmatic use
    if "--json" in os.sys.argv:
        print("\n--- JSON ---")
        print(json.dumps(signals, indent=2, ensure_ascii=False))
