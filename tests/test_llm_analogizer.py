"""tests for llm_analogizer — 使用 mock 避免真实 API 调用"""
import json
import pytest
from unittest.mock import MagicMock, patch


# ─── Mock 工厂 ────────────────────────────────────────────────────────────────

def _mock_compare_response():
    return json.dumps({
        "shared_limitations": [
            {
                "phrase_a": "法则约束大幅松弛",
                "phrase_b": "约束越少推演空间越大",
                "limitation_description": "约束强度变化决定可能空间的大小"
            }
        ],
        "implied_law_attribute": "不确定性法则：展开在可能性空间中进行",
        "cognitive_level": "类比（局限性相同）",
        "is_analogy": True,
        "constraint_similarity": 0.72,
        "reasoning": "两者都描述了约束松弛时可能空间扩大的结构"
    })


def _mock_imagine_response():
    return json.dumps({
        "starting_state": "法则属性和展开属性在本原层未分化",
        "comprehensibility_constraint": "必须从'分化'这一可理解概念出发；时序是已知前提",
        "possibilities": [
            {
                "direction": "时序分化",
                "description": "法则属性和展开属性在法则展开的第一步中分化",
                "new_constraint": "需要时序作为分化的前提条件",
                "collapse_trigger": "选择特定时间点作为研究焦点"
            },
            {
                "direction": "层级分化",
                "description": "分化发生在层级跨越时：从本原层到结构层",
                "new_constraint": "需要层级概念作为分化的结构条件",
                "collapse_trigger": "确定某个具体层级的边界"
            },
            {
                "direction": "观测分化",
                "description": "分化是主体观测行为的产物，非本原内在结构",
                "new_constraint": "依赖主体存在，循环依赖风险",
                "collapse_trigger": "接受主体先于本原属性"
            }
        ],
        "meta": {
            "coherence_note": "不要急于选择哪个方向'正确'，三个方向同时有效",
            "hope_direction": "时序分化——最不依赖循环预设"
        }
    })


def _make_mock_client(response_text: str):
    """构造返回指定文本的 mock anthropic client"""
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


# ─── compare() 测试 ───────────────────────────────────────────────────────────

@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_compare_returns_required_keys(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_compare_response())
    from llm_analogizer import compare
    result = compare("梦境中法则约束松弛", "想象受约束越少空间越大")
    for key in ['shared_limitations', 'implied_law_attribute', 'cognitive_level',
                'is_analogy', 'constraint_similarity', 'source']:
        assert key in result, f"缺少字段：{key}"


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_compare_source_is_llm(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_compare_response())
    from llm_analogizer import compare
    result = compare("A", "B")
    assert result['source'] == 'llm'


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_compare_shared_limitations_structure(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_compare_response())
    from llm_analogizer import compare
    result = compare("A", "B")
    assert isinstance(result['shared_limitations'], list)
    assert len(result['shared_limitations']) >= 1
    pair = result['shared_limitations'][0]
    assert 'phrase_a' in pair and 'phrase_b' in pair and 'limitation_description' in pair


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_compare_similarity_range(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_compare_response())
    from llm_analogizer import compare
    result = compare("A", "B")
    assert 0.0 <= result['constraint_similarity'] <= 1.0


# ─── imagine() 测试 ───────────────────────────────────────────────────────────

@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_imagine_returns_required_keys(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_imagine_response())
    from llm_analogizer import imagine
    result = imagine("法则属性和展开属性在本原层未分化", n=3)
    for key in ['starting_state', 'comprehensibility_constraint', 'possibilities', 'source']:
        assert key in result, f"缺少字段：{key}"


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_imagine_possibilities_structure(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_imagine_response())
    from llm_analogizer import imagine
    result = imagine("起点描述", n=3)
    assert isinstance(result['possibilities'], list)
    assert len(result['possibilities']) >= 1
    p = result['possibilities'][0]
    for key in ['direction', 'description', 'new_constraint', 'collapse_trigger']:
        assert key in p, f"possibility 缺少字段：{key}"


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
@patch('llm_analogizer._get_client')
def test_imagine_meta_fields(mock_get_client):
    mock_get_client.return_value = _make_mock_client(_mock_imagine_response())
    from llm_analogizer import imagine
    result = imagine("起点描述")
    meta = result.get('meta', {})
    assert 'coherence_note' in meta
    assert 'hope_direction' in meta


# ─── 无 API Key 测试 ─────────────────────────────────────────────────────────

@patch.dict('os.environ', {}, clear=True)
def test_compare_no_api_key_raises():
    import importlib
    import llm_analogizer
    importlib.reload(llm_analogizer)
    with pytest.raises(EnvironmentError, match='ANTHROPIC_API_KEY'):
        llm_analogizer._get_client()


# ─── JSON 解析容错 ────────────────────────────────────────────────────────────

def test_parse_json_strips_markdown():
    from llm_analogizer import _parse_json_response
    raw = '```json\n{"key": "value"}\n```'
    result = _parse_json_response(raw)
    assert result == {"key": "value"}


def test_parse_json_plain():
    from llm_analogizer import _parse_json_response
    raw = '{"is_analogy": true, "constraint_similarity": 0.5}'
    result = _parse_json_response(raw)
    assert result['is_analogy'] is True
