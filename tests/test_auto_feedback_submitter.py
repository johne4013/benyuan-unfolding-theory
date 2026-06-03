"""Tests for AutoFeedbackSubmitter (scripts/auto_feedback_submitter.py)."""

import json
import re
import pytest
from auto_feedback_submitter import AutoFeedbackSubmitter


def make_submitter(tmp_path):
    return AutoFeedbackSubmitter(feedbacks_dir=str(tmp_path / "feedbacks"))


def test_submit_creates_json_file(tmp_path):
    s = make_submitter(tmp_path)
    result = s.submit(
        task_name="Test Task",
        observation="Observed X",
        limitation="Limited by Y",
        suggestion="Suggest Z",
        auto_process=False,
    )
    assert result["feedback_file"] is not None
    import os
    assert os.path.exists(result["feedback_file"])


def test_submit_file_has_correct_fields(tmp_path):
    s = make_submitter(tmp_path)
    result = s.submit(
        task_name="My Task",
        observation="Something happened",
        limitation="Theory doesn't cover X",
        suggestion="Add coverage for X",
        auto_process=False,
    )
    with open(result["feedback_file"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["task_id"] == result["task_id"]
    assert data["task_name"] == "My Task"
    assert data["observation"] == "Something happened"
    assert "submitted_at" in data


def test_generate_task_id_format(tmp_path):
    s = make_submitter(tmp_path)
    task_id = s._generate_task_id()
    assert re.match(r"task-\d{8}-\d{3}", task_id), f"Bad format: {task_id}"


def test_generate_task_id_increments(tmp_path):
    s = make_submitter(tmp_path)
    id1 = s._generate_task_id()
    # Write a file so the next call sees it and increments
    s.submit(task_name="t1", observation="o", limitation="l", suggestion="s", auto_process=False)
    id2 = s._generate_task_id()
    assert id1 != id2


def test_submit_with_hope_tracking(tmp_path):
    s = make_submitter(tmp_path)
    hope = {
        "impact_on_hope": "推进",
        "new_possibility_found": "是",
        "possibility_description": "Opens new dimension",
    }
    result = s.submit(
        task_name="Hope Task",
        observation="Theory advanced",
        limitation="Minor gaps",
        suggestion="Expand section 2",
        hope_tracking=hope,
        auto_process=False,
    )
    with open(result["feedback_file"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "hope_tracking" in data
    assert data["hope_tracking"]["impact_on_hope"] == "推进"
