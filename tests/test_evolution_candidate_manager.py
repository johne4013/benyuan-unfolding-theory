"""Tests for EvolutionCandidateManager (scripts/evolution_candidate_manager.py)."""

import json
import pytest
from evolution_candidate_manager import EvolutionCandidateManager


def make_manager(tmp_path):
    return EvolutionCandidateManager(candidates_dir=str(tmp_path / "candidates"))


def test_create_save_load(tmp_path):
    mgr = make_manager(tmp_path)
    cand = mgr.create_candidate("PATTERN", "Test Pattern", "A description", "task-001")
    mgr.save_candidate(cand)
    loaded = mgr.load_candidate(cand["id"])
    assert loaded["id"] == cand["id"]
    assert loaded["type"] == "PATTERN"
    assert loaded["title"] == "Test Pattern"


def test_load_not_found(tmp_path):
    mgr = make_manager(tmp_path)
    with pytest.raises(FileNotFoundError):
        mgr.load_candidate("nonexistent-id")


def test_update_status(tmp_path):
    mgr = make_manager(tmp_path)
    cand = mgr.create_candidate("ANOMALY", "Test Anomaly", "Desc", "task-002")
    mgr.save_candidate(cand)
    updated = mgr.update_candidate_status(cand["id"], "APPROVED", "Looks good")
    assert updated["status"] == "APPROVED"
    # Verify persisted
    loaded = mgr.load_candidate(cand["id"])
    assert loaded["status"] == "APPROVED"


def test_add_evidence_increments_count(tmp_path):
    mgr = make_manager(tmp_path)
    cand = mgr.create_candidate("PATTERN", "Repeat Pattern", "Desc", "task-003")
    mgr.save_candidate(cand)
    updated = mgr.add_evidence(cand["id"], "task-004", "More evidence")
    assert updated["evidence_count"] == 2


def test_list_candidates_empty(tmp_path):
    mgr = make_manager(tmp_path)
    results = mgr.list_candidates()
    assert results == []


def test_list_candidates_filters_by_status(tmp_path):
    mgr = make_manager(tmp_path)
    cand1 = mgr.create_candidate("PATTERN", "Pattern 1", "Desc", "task-005")
    cand2 = mgr.create_candidate("ANOMALY", "Anomaly 1", "Desc", "task-006")
    mgr.save_candidate(cand1)
    mgr.save_candidate(cand2)
    mgr.update_candidate_status(cand2["id"], "APPROVED")

    candidates = mgr.list_candidates(status="CANDIDATE")
    assert len(candidates) == 1
    assert candidates[0]["id"] == cand1["id"]


def test_list_skips_corrupted_json(tmp_path):
    mgr = make_manager(tmp_path)
    cand = mgr.create_candidate("ENHANCEMENT", "Enhancement 1", "Desc", "task-007")
    mgr.save_candidate(cand)

    # Write a corrupt JSON file in the same directory
    corrupt_file = mgr.candidates_dir / "corrupt-enhancement.json"
    corrupt_file.write_text("{invalid json", encoding="utf-8")

    # list_candidates should skip the corrupt file and return the valid one
    results = mgr.list_candidates()
    assert len(results) == 1
    assert results[0]["id"] == cand["id"]
