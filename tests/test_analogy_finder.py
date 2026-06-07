"""tests for analogy_finder"""
import pytest
from analogy_finder import (
    extract_constraints,
    find_shared_limitations,
    infer_law_attribute,
    compare,
    _tokenize,
    _jaccard,
)


# ─── 约束提取 ─────────────────────────────────────────────────────────────────

def test_extract_constraints_strong_signal():
    text = "梦境中感官隔离，法则约束松弛；主体认同不稳定，无法维持逻辑一致性。"
    result = extract_constraints(text)
    weights = [c['weight'] for c in result]
    assert any(w >= 1.0 for w in weights), "应提取到 strong 信号约束"


def test_extract_constraints_empty():
    assert extract_constraints("") == []


def test_extract_constraints_returns_phrases():
    text = "想象受起点可理解性约束；不能从完全未知的状态出发。类比需要两个可比较的状态。"
    result = extract_constraints(text)
    assert len(result) >= 2
    assert all('phrase' in c and 'weight' in c for c in result)


# ─── 共同局限性 ───────────────────────────────────────────────────────────────

def test_find_shared_limitations_identical():
    ca = [{'phrase': '受法则约束，不能任意展开', 'weight': 1.0, 'signal': '约束'}]
    cb = [{'phrase': '受法则约束，不能任意展开', 'weight': 1.0, 'signal': '约束'}]
    pairs = find_shared_limitations(ca, cb)
    assert len(pairs) == 1
    assert pairs[0]['similarity'] == 1.0


def test_find_shared_limitations_no_overlap():
    ca = [{'phrase': '需要阳光才能生长', 'weight': 0.6, 'signal': '需要'}]
    cb = [{'phrase': '网络延迟影响响应速度', 'weight': 0.3, 'signal': ''}]
    pairs = find_shared_limitations(ca, cb, threshold=0.15)
    # 两者语义差距大，应无匹配或极低匹配
    assert all(p['similarity'] < 0.3 for p in pairs)


def test_find_shared_limitations_partial():
    # 两个句子共享"时序"、"约束"、"顺序"等约束词，应能配对
    ca = [{'phrase': '主体认同受时序约束，不能脱离时间顺序', 'weight': 1.0, 'signal': '约束'}]
    cb = [{'phrase': '历史事件的时序不可逆，顺序约束记忆结构', 'weight': 0.6, 'signal': ''}]
    pairs = find_shared_limitations(ca, cb, threshold=0.10)
    assert len(pairs) >= 1


# ─── 法则属性推断 ─────────────────────────────────────────────────────────────

def test_infer_law_attribute_temporal():
    shared = [{'phrase_a': '时序约束', 'phrase_b': '历时顺序'}]
    result = infer_law_attribute(shared, '时间顺序不可改变', '历史事件的时序不可逆')
    assert '时序' in result


def test_infer_law_attribute_epistemic():
    shared = [{'phrase_a': '认知边界', 'phrase_b': '观测受限'}]
    result = infer_law_attribute(shared, '认知受信息限制', '观测改变被观测对象')
    assert '认识论' in result


def test_infer_law_attribute_fallback():
    # 使用不含任何路由关键词的纯中性文本
    result = infer_law_attribute([], '苹果放在桌子上', '书本放在架子上')
    assert '结构同构' in result or '未识别' in result


# ─── 完整类比比较 ─────────────────────────────────────────────────────────────

def test_compare_returns_required_keys():
    result = compare("梦境中感官隔离，无法维持逻辑一致性", "想象受可理解性约束，不能从未知出发")
    required = ['overall_similarity', 'constraint_similarity', 'shared_limitations',
                'implied_law_attribute', 'cognitive_level', 'is_analogy',
                'constraints_a', 'constraints_b']
    for key in required:
        assert key in result, f"缺少字段：{key}"


def test_compare_identical_texts():
    text = "法则约束限制了展开的方向，不能超出本原张力的范围。"
    result = compare(text, text)
    assert result['overall_similarity'] == 1.0
    assert result['constraint_similarity'] >= 0.5


def test_compare_unrelated_texts():
    result = compare("今天天气很好适合散步", "数据库查询需要建立索引")
    assert result['overall_similarity'] < 0.3


def test_compare_analogy_dream_imagination():
    """梦境与想象的类比：都受'约束松弛程度'影响"""
    text_a = "梦境中感官输入隔离，前额叶活动降低，法则约束大幅松弛，认同不稳定，无法维持逻辑一致性。"
    text_b = "想象受起点可理解性约束，不能从完全未知的状态出发，约束越少推演空间越大但越难控制。"
    result = compare(text_a, text_b)
    assert result['overall_similarity'] > 0.0
    assert 'cognitive_level' in result


def test_compare_cognitive_level_strong():
    """高度结构重叠应达到类比或强类比层级"""
    text_a = "主体在局限条件下仍能开放于更高可能性，局限性本身是展开的结构性条件。"
    text_b = "主体在约束边界内保持开放，局限不是纯负面，而是展开得以发生的前提条件。"
    result = compare(text_a, text_b)
    assert result['constraint_similarity'] >= 0.10
    assert result['is_analogy'] is True
