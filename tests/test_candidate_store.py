"""Tests for CandidateStore (scripts/candidate_store.py)."""

import json
import pytest
from candidate_store import CandidateStore


def make_candidate(cid="cand-001", ctype="PATTERN", status="CANDIDATE", title="Test Candidate"):
    return {
        "id": cid,
        "type": ctype,
        "priority": "medium",
        "title": title,
        "status": status,
        "evidence_count": 1,
        "created_at": "2024-01-01T00:00:00",
        "description": "A test candidate",
    }


def test_save_and_load_roundtrip(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    cand = make_candidate()
    store.save(cand)
    loaded = store.load("cand-001")
    assert loaded["id"] == "cand-001"
    assert loaded["type"] == "PATTERN"
    assert loaded["title"] == "Test Candidate"
    assert loaded["status"] == "CANDIDATE"


def test_load_missing_raises(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    with pytest.raises(FileNotFoundError):
        store.load("nonexistent-id")


def test_query_by_status(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    store.save(make_candidate("id-1", status="CANDIDATE"))
    store.save(make_candidate("id-2", status="APPROVED"))
    store.save(make_candidate("id-3", status="INTEGRATED"))

    results = store.query(status="APPROVED")
    assert len(results) == 1
    assert results[0]["id"] == "id-2"


def test_query_by_type(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    store.save(make_candidate("id-1", ctype="PATTERN"))
    store.save(make_candidate("id-2", ctype="ANOMALY"))
    store.save(make_candidate("id-3", ctype="ENHANCEMENT"))

    results = store.query(candidate_type="ANOMALY")
    assert len(results) == 1
    assert results[0]["type"] == "ANOMALY"


def test_get_stats_counts_correctly(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    for i in range(3):
        store.save(make_candidate(f"cand-{i}", ctype="PATTERN"))
    store.save(make_candidate("cand-a", ctype="ANOMALY"))

    stats = store.get_stats()
    assert stats["total"] == 4
    assert stats["by_type"].get("PATTERN") == 3
    assert stats["by_type"].get("ANOMALY") == 1
    assert stats["by_status"].get("CANDIDATE") == 4


def test_import_from_json_dir(tmp_path):
    # Write 3 JSON files into tmp_path
    for i in range(3):
        cand = make_candidate(f"cand-{i}", title=f"Candidate {i}")
        (tmp_path / f"cand-{i}-pattern.json").write_text(
            json.dumps(cand), encoding="utf-8"
        )

    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    result = store.import_from_json_dir(str(tmp_path))
    assert result["imported"] == 3
    assert result["failed"] == 0
    assert store.get_stats()["total"] == 3


def test_export_and_reimport(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    for i in range(5):
        store.save(make_candidate(f"cand-{i}", title=f"Candidate {i}"))

    export_dir = tmp_path / "export"
    count = store.export_to_json_dir(str(export_dir))
    assert count == 5

    store2 = CandidateStore(db_path=str(tmp_path / "c2.db"))
    result = store2.import_from_json_dir(str(export_dir))
    assert result["imported"] == 5
    assert store2.get_stats()["total"] == 5


def test_upsert_updates_fields(tmp_path):
    store = CandidateStore(db_path=str(tmp_path / "c.db"))
    cand = make_candidate("cand-001", status="CANDIDATE", title="Original Title")
    store.save(cand)

    cand2 = dict(cand)
    cand2["status"] = "APPROVED"
    cand2["title"] = "Updated Title"
    store.save(cand2)

    loaded = store.load("cand-001")
    assert loaded["status"] == "APPROVED"
    assert loaded["title"] == "Updated Title"
    # Should still be only one record
    assert store.get_stats()["total"] == 1
