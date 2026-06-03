"""Tests for TheoryIntegrationWriter (scripts/theory_integration_writer.py)."""

import pytest
from pathlib import Path
from theory_integration_writer import TheoryIntegrationWriter


def make_runtime(tmp_path):
    """Create a fake continuity/runtime structure with minimal files."""
    runtime = tmp_path / "continuity" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "reflection.md").write_text("# Reflection\n", encoding="utf-8")
    (runtime / "concepts_v2_draft.md").write_text("# Concepts Draft\n", encoding="utf-8")
    (runtime / "failure_conditions_draft.md").write_text("# Failure Conditions\n", encoding="utf-8")
    (runtime / "HOPE_STATE.md").write_text("# Hope State\n", encoding="utf-8")
    (runtime / "theory_v2_draft.md").write_text("# Theory v2 Draft\n", encoding="utf-8")
    return runtime


def make_writer(tmp_path):
    make_runtime(tmp_path)
    return TheoryIntegrationWriter(continuity_dir=str(tmp_path / "continuity"))


def base_candidate(ctype="ENHANCEMENT", expansion="法则属性型", hope="推进：expand"):
    return {
        "id": "cand-test-001",
        "type": ctype,
        "priority": "medium",
        "title": "Test Integration Candidate",
        "status": "APPROVED",
        "description": "Description of the candidate",
        "improvement_direction": "Add more detail",
        "expansion_type": expansion,
        "hope_direction": hope,
        "opens_new_possibility": "是——opens new dimension",
        "evidence_count": 1,
    }


def test_integrate_writes_to_reflection(tmp_path):
    writer = make_writer(tmp_path)
    cand = base_candidate()
    result = writer.integrate(cand, dry_run=False)
    assert "reflection.md" in result["files_written"]
    assert result["errors"] == []
    content = (tmp_path / "continuity" / "runtime" / "reflection.md").read_text(encoding="utf-8")
    assert "Test Integration Candidate" in content


def test_integrate_enhancement_law_writes_concepts_draft(tmp_path):
    writer = make_writer(tmp_path)
    cand = base_candidate(ctype="ENHANCEMENT", expansion="法则属性型")
    result = writer.integrate(cand, dry_run=False)
    assert "concepts_v2_draft.md" in result["files_written"]
    content = (tmp_path / "continuity" / "runtime" / "concepts_v2_draft.md").read_text(encoding="utf-8")
    assert "Test Integration Candidate" in content


def test_integrate_anomaly_writes_failure_conditions(tmp_path):
    writer = make_writer(tmp_path)
    cand = base_candidate(ctype="ANOMALY", expansion="pending", hope="")
    result = writer.integrate(cand, dry_run=False)
    assert "failure_conditions_draft.md" in result["files_written"]
    content = (tmp_path / "continuity" / "runtime" / "failure_conditions_draft.md").read_text(encoding="utf-8")
    assert "Test Integration Candidate" in content


def test_integrate_dry_run_no_modification(tmp_path):
    writer = make_writer(tmp_path)
    cand = base_candidate()
    reflection_before = (tmp_path / "continuity" / "runtime" / "reflection.md").read_text(encoding="utf-8")
    result = writer.integrate(cand, dry_run=True)
    assert result["dry_run"] is True
    reflection_after = (tmp_path / "continuity" / "runtime" / "reflection.md").read_text(encoding="utf-8")
    assert reflection_before == reflection_after


def test_integrate_hope_direction_updates_hope_state(tmp_path):
    writer = make_writer(tmp_path)
    cand = base_candidate(hope="推进：opens new possibilities")
    result = writer.integrate(cand, dry_run=False)
    assert "HOPE_STATE.md" in result["files_written"]
    content = (tmp_path / "continuity" / "runtime" / "HOPE_STATE.md").read_text(encoding="utf-8")
    assert "推进：opens new possibilities" in content
