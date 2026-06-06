"""
tests/test_theory_application_checker.py

单元测试：TheoryApplicationChecker
"""

import pytest
from theory_application_checker import TheoryApplicationChecker


@pytest.fixture
def checker():
    return TheoryApplicationChecker()


def test_detect_level_engineering(checker):
    """含 'Python脚本' 的描述应识别为 engineering 层级"""
    level = checker.detect_level("请编写一个 Python脚本 来处理数据文件")
    assert level == "engineering"


def test_detect_level_theory(checker):
    """含 '本原展开论' 的描述应识别为 theory 层级（因含'本原'关键词）"""
    level = checker.detect_level("请梳理本原展开论的展开属性与法则属性之间的关系")
    assert level == "theory"


def test_detect_level_core(checker):
    """含 'core/concepts.md' 的描述应识别为 core 层级"""
    level = checker.detect_level("请更新 core/concepts.md 中的定义")
    assert level == "core"


def test_detect_level_simple_default(checker):
    """不含任何层级关键词的普通描述应默认为 simple"""
    level = checker.detect_level("今天天气不错，去散步吧")
    assert level == "simple"


def test_checklist_has_correct_dimensions(checker):
    """engineering 层级应包含 D1/D2/D3，不包含 D4"""
    checklist = checker.generate_checklist("写一个 Python 脚本", level="engineering")
    dims = checklist["dimensions"]
    assert "D1" in dims
    assert "D2" in dims
    assert "D3" in dims
    assert "D4" not in dims
