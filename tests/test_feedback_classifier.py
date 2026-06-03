"""Tests for FeedbackClassifier (scripts/feedback_classifier.py)."""

import json
import pytest
from feedback_classifier import FeedbackClassifier


@pytest.fixture
def clf():
    return FeedbackClassifier()


def make_feedback(obs="", lim="", sug="", task_id="task-001", task_name="Test"):
    return {
        "task_id": task_id,
        "task_name": task_name,
        "observation": obs,
        "limitation": lim,
        "suggestion": sug,
    }


def test_classify_anomaly(clf):
    fb = make_feedback(obs="理论预测失败，违反了所有约束但仍然成功")
    result = clf.classify_feedback(fb)
    assert result == "ANOMALY"


def test_classify_pattern(clf):
    # Use a keyword that _is_repeated_pattern also checks for
    fb = make_feedback(obs="在多个任务中重复出现了相同的问题")
    result = clf.classify_feedback(fb)
    assert result == "PATTERN"


def test_classify_enhancement(clf):
    fb = make_feedback(obs="可以改进这里", sug="建议优化算法逻辑")
    result = clf.classify_feedback(fb)
    assert result == "ENHANCEMENT"


def test_classify_temporary(clf):
    fb = make_feedback(obs="网络超时", lim="环境问题", sug="重试即可")
    result = clf.classify_feedback(fb)
    assert result == "TEMPORARY"


def test_validate_structure_ok(clf):
    fb = make_feedback(obs="观察", lim="局限", sug="建议")
    is_valid, err = clf._validate_feedback_structure(fb)
    assert is_valid is True
    assert err is None


def test_validate_structure_missing_field(clf):
    fb = {"task_id": "t1", "task_name": "name", "observation": "obs"}
    # Missing limitation and suggestion
    is_valid, err = clf._validate_feedback_structure(fb)
    assert is_valid is False
    assert err is not None


def test_compute_similarity_high(clf):
    text1 = "展开属性 法则约束 理论演化候选 多个任务重复出现"
    text2 = "展开属性 法则约束 理论演化候选 多次观察到相同模式"
    score = clf._compute_similarity(text1, text2)
    assert score >= 0.15


def test_compute_similarity_low(clf):
    text1 = "天气晴朗阳光明媚"
    text2 = "数据库连接失败重试"
    score = clf._compute_similarity(text1, text2)
    assert score < 0.15


def test_process_file_invalid_structure(clf, tmp_path):
    # Write a feedback file that is missing required fields
    bad_fb = {"task_id": "t1"}  # missing task_name, observation, limitation, suggestion
    fb_file = tmp_path / "bad.json"
    fb_file.write_text(json.dumps(bad_fb), encoding="utf-8")

    result = clf.process_feedback_file(str(fb_file))
    assert result["classification"] == "INVALID"
