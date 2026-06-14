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
    level = checker.detect_task_level("请编写一个 Python脚本 来处理数据文件")
    assert level == "engineering"


def test_detect_level_theory(checker):
    """含 '本原展开论' 的描述应识别为 theory 层级"""
    level = checker.detect_task_level("请梳理本原展开论的展开属性与法则属性之间的关系")
    assert level == "theory"


def test_detect_level_core(checker):
    """含 'core/concepts.md' 的描述应识别为 core 层级"""
    level = checker.detect_task_level("请更新 core/concepts.md 中的定义")
    assert level == "core"


def test_detect_level_simple_default(checker):
    """不含任何层级关键词的普通描述应默认为 simple"""
    level = checker.detect_task_level("今天天气不错，去散步吧")
    assert level == "simple"


def test_checklist_has_required_fields(checker):
    """生成的 checklist 应包含 task_id / task_level / checklist 字段"""
    result = checker.generate_checklist("task-001", "写一个 Python 脚本", "实现数据处理工具")
    assert result["task_id"] == "task-001"
    assert "task_level" in result
    assert "checklist" in result
