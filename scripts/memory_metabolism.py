"""
memory_metabolism.py — Memory Metabolism Scanner

Implements the memory metabolism protocol from runtime/memory_metabolism_protocol.md.
Scans runtime/*.md files, checks sizes, ages, and self-alignment, then reports
what needs attention.

READ-ONLY (green layer) — never modifies any files.
"""

import os
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    from paths import runtime_dir as _runtime_dir
    _PATHS_AVAILABLE = True
except ImportError:
    _PATHS_AVAILABLE = False


def _resolve_runtime(override=None):
    if override:
        return Path(override)
    if _PATHS_AVAILABLE:
        return _runtime_dir()
    return Path("~/.hermes/continuity/runtime").expanduser()


# File size thresholds (KB) — warn when exceeded
SIZE_THRESHOLDS = {
    "HOPE_STATE.md": 60,
    "index.md": 80,
    "theory_to_code_mapping.md": 60,
}

# Age thresholds (days) — warn when file NOT updated within this period
STALE_THRESHOLDS = {
    "HOPE_STATE.md": 21,
    "index.md": 30,
}


class MemoryMetabolismScanner:
    """Scans runtime memory files for size, staleness, and structural integrity."""

    def __init__(self, runtime_dir=None):
        self.runtime_dir = _resolve_runtime(runtime_dir)

    # ------------------------------------------------------------------
    # Individual scan methods
    # ------------------------------------------------------------------

    def scan_file_sizes(self) -> list:
        """Return size check results for all files listed in SIZE_THRESHOLDS.

        Returns a list of dicts:
          {"file": name, "size_kb": float, "threshold_kb": int, "exceeds": bool}
        Only files that exist on disk are included.
        """
        results = []
        for filename, threshold_kb in SIZE_THRESHOLDS.items():
            path = self.runtime_dir / filename
            if not path.exists():
                continue
            size_kb = path.stat().st_size / 1024.0
            results.append(
                {
                    "file": filename,
                    "size_kb": round(size_kb, 2),
                    "threshold_kb": threshold_kb,
                    "exceeds": size_kb > threshold_kb,
                }
            )
        return results

    def scan_stale_files(self) -> list:
        """Return staleness check results for all files listed in STALE_THRESHOLDS.

        Returns a list of dicts:
          {"file": name, "age_days": float, "threshold_days": int, "stale": bool}
        Only files that exist on disk are included.
        """
        results = []
        now = datetime.now(timezone.utc)
        for filename, threshold_days in STALE_THRESHOLDS.items():
            path = self.runtime_dir / filename
            if not path.exists():
                continue
            mtime = path.stat().st_mtime
            mod_time = datetime.fromtimestamp(mtime, tz=timezone.utc)
            age_days = (now - mod_time).total_seconds() / 86400.0
            results.append(
                {
                    "file": filename,
                    "age_days": round(age_days, 2),
                    "threshold_days": threshold_days,
                    "stale": age_days > threshold_days,
                }
            )
        return results

    def self_alignment_check(self) -> dict:
        """Check structural integrity of the runtime memory system.

        Checks:
          - core/bootstrap.md exists (relative to runtime/../core/)
          - index.md exists in runtime
          - HOPE_STATE.md exists in runtime
          - memory.md exists in runtime

        Returns:
          {"passed": bool, "checks": [{"name": str, "ok": bool}]}
        """
        core_dir = self.runtime_dir.parent / "core"

        checks = [
            {
                "name": "core/bootstrap.md exists",
                "ok": (core_dir / "bootstrap.md").exists(),
            },
            {
                "name": "runtime/index.md exists",
                "ok": (self.runtime_dir / "index.md").exists(),
            },
            {
                "name": "runtime/HOPE_STATE.md exists",
                "ok": (self.runtime_dir / "HOPE_STATE.md").exists(),
            },
            {
                "name": "runtime/task_theory_application_framework.md exists",
                "ok": (self.runtime_dir / "task_theory_application_framework.md").exists(),
            },
        ]

        passed = all(c["ok"] for c in checks)
        return {"passed": passed, "checks": checks}

    # ------------------------------------------------------------------
    # Combined scan
    # ------------------------------------------------------------------

    def scan(self) -> dict:
        """Run all three scans and return a combined report.

        Report keys:
          timestamp       — ISO 8601 string
          size_alerts     — list of size check dicts (all files checked)
          stale_alerts    — list of staleness check dicts (all files checked)
          self_alignment  — result of self_alignment_check()
          recommendations — list of human-readable recommendation strings
          overall         — "healthy" | "needs_attention" | "critical"
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        size_results = self.scan_file_sizes()
        stale_results = self.scan_stale_files()
        alignment = self.self_alignment_check()

        recommendations = []

        # Size recommendations
        for item in size_results:
            if item["exceeds"]:
                ratio = item["size_kb"] / item["threshold_kb"]
                severity = "CRITICAL" if ratio > 2.0 else "WARNING"
                recommendations.append(
                    f"[{severity}] {item['file']} is {item['size_kb']:.1f} KB "
                    f"(threshold {item['threshold_kb']} KB) — consider compressing or archiving."
                )

        # Staleness recommendations
        for item in stale_results:
            if item["stale"]:
                recommendations.append(
                    f"[WARNING] {item['file']} has not been updated in {item['age_days']:.1f} days "
                    f"(threshold {item['threshold_days']} days) — review if still current."
                )

        # Self-alignment recommendations
        if not alignment["passed"]:
            for check in alignment["checks"]:
                if not check["ok"]:
                    recommendations.append(
                        f"[CRITICAL] Structural check failed: '{check['name']}' — "
                        "self-alignment integrity compromised."
                    )

        # Determine overall status
        alignment_failed = not alignment["passed"]
        any_double_exceeded = any(
            item["size_kb"] > item["threshold_kb"] * 2 for item in size_results
        )
        any_alert = (
            any(item["exceeds"] for item in size_results)
            or any(item["stale"] for item in stale_results)
            or alignment_failed
        )

        if alignment_failed or any_double_exceeded:
            overall = "critical"
        elif any_alert:
            overall = "needs_attention"
        else:
            overall = "healthy"

        return {
            "timestamp": timestamp,
            "size_alerts": size_results,
            "stale_alerts": stale_results,
            "self_alignment": alignment,
            "recommendations": recommendations,
            "overall": overall,
        }

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_report(self, report: dict) -> str:
        """Return a human-readable string representation of a scan report."""
        lines = []
        lines.append("=" * 60)
        lines.append("Memory Metabolism Scan Report")
        lines.append(f"Timestamp : {report['timestamp']}")
        lines.append(f"Overall   : {report['overall'].upper()}")
        lines.append("=" * 60)

        # Size section
        lines.append("\n-- File Size Checks --")
        if report["size_alerts"]:
            for item in report["size_alerts"]:
                status = "EXCEEDS" if item["exceeds"] else "OK"
                lines.append(
                    f"  [{status}] {item['file']}: {item['size_kb']:.1f} KB "
                    f"/ threshold {item['threshold_kb']} KB"
                )
        else:
            lines.append("  (no tracked files found)")

        # Staleness section
        lines.append("\n-- Staleness Checks --")
        if report["stale_alerts"]:
            for item in report["stale_alerts"]:
                status = "STALE" if item["stale"] else "OK"
                lines.append(
                    f"  [{status}] {item['file']}: {item['age_days']:.1f} days old "
                    f"/ threshold {item['threshold_days']} days"
                )
        else:
            lines.append("  (no tracked files found)")

        # Self-alignment section
        lines.append("\n-- Self-Alignment Checks --")
        alignment = report["self_alignment"]
        for check in alignment["checks"]:
            ok_str = "PASS" if check["ok"] else "FAIL"
            lines.append(f"  [{ok_str}] {check['name']}")
        overall_align = "PASSED" if alignment["passed"] else "FAILED"
        lines.append(f"  => Self-alignment: {overall_align}")

        # Recommendations section
        lines.append("\n-- Recommendations --")
        if report["recommendations"]:
            for rec in report["recommendations"]:
                lines.append(f"  * {rec}")
        else:
            lines.append("  No issues found — system is healthy.")

        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Memory metabolism scanner — read-only health check."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also print the raw JSON report after the human-readable report.",
    )
    args = parser.parse_args()

    scanner = MemoryMetabolismScanner()
    report = scanner.scan()

    print(scanner.format_report(report))

    if args.json:
        print("\n-- JSON Report --")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
