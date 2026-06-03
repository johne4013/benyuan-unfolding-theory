"""Tests for time-series functions in hope_tension_collector.py."""

import json
import os
import pytest
import hope_tension_collector as htc


def make_signals(ts="2024-01-01T10:00:00", overall="healthy"):
    return {
        "timestamp": ts,
        "law_side": {"core_age_days": 5.2, "memory_kb": 12.0},
        "expansion_side": {"reflection_entries_7d": 3, "reflection_size_kb": 22.0},
        "tension": {"law_alerts": 0, "expansion_alerts": 0},
        "alerts": [],
        "overall": overall,
    }


def test_save_snapshot_creates_file(tmp_path):
    history_file = str(tmp_path / "tension_history.jsonl")
    htc.save_snapshot(make_signals(), history_file=history_file)
    assert os.path.exists(history_file)


def test_load_history_empty_if_missing(tmp_path):
    missing = str(tmp_path / "nonexistent.jsonl")
    result = htc.load_history(10, history_file=missing)
    assert result == []


def test_save_and_load_roundtrip(tmp_path):
    history_file = str(tmp_path / "tension_history.jsonl")
    for i in range(5):
        htc.save_snapshot(make_signals(ts=f"2024-01-0{i+1}T10:00:00"), history_file=history_file)
    history = htc.load_history(5, history_file=history_file)
    assert len(history) == 5
    assert history[0]["timestamp"] == "2024-01-01T10:00:00"
    assert history[4]["timestamp"] == "2024-01-05T10:00:00"


def test_format_trend_report_has_arrows(tmp_path):
    history_file = str(tmp_path / "tension_history.jsonl")
    # Save two snapshots with different values so we get arrow changes
    snap1 = make_signals(ts="2024-01-01T10:00:00")
    snap2 = make_signals(ts="2024-01-02T10:00:00")
    snap2["law_side"]["core_age_days"] = 6.5  # higher → ↑
    snap2["expansion_side"]["reflection_entries_7d"] = 1  # lower → ↓
    htc.save_snapshot(snap1, history_file=history_file)
    htc.save_snapshot(snap2, history_file=history_file)

    history = htc.load_history(10, history_file=history_file)
    report = htc.format_trend_report(history)
    # Report must contain at least one kind of arrow
    assert any(arrow in report for arrow in ("↑", "↓", "→"))
