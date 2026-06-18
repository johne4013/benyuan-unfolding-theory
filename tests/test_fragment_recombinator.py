#!/usr/bin/env python3
"""
test_fragment_recombinator.py — 碎片重组器测试

不依赖 ANTHROPIC_API_KEY：合成步骤通过注入假 recombine_fn 完成。
覆盖：碎片加载（含缺失文件）、张力评分形状、配对筛选、重组、
锚点筛选、产出候选、端到端流程。
"""

import json

import pytest

import fragment_recombinator as fr


# ──────────────────────────────────────────────────────────────────────
# 碎片加载
# ──────────────────────────────────────────────────────────────────────

def _write(runtime, name, text):
    (runtime / name).write_text(text, encoding="utf-8")


def test_load_fragments_missing_files_returns_empty(tmp_path):
    # 没有任何来源文件时返回空列表，不报错
    assert fr.load_fragments(runtime=tmp_path) == []


def test_load_fragments_splits_by_heading(tmp_path):
    _write(tmp_path, "memory.md",
           "# 顶层\n\n"
           "## 段落甲\n这是关于约束与结构稳定性的一段足够长的记忆内容。\n\n"
           "## 段落乙\n这是关于展开与生成面向的另一段足够长的记忆内容。\n")
    frags = fr.load_fragments(sources=("memory.md",), runtime=tmp_path)
    titles = {f["title"] for f in frags}
    assert "段落甲" in titles and "段落乙" in titles
    assert all(f["source"] == "memory.md" for f in frags)


def test_load_fragments_drops_too_short(tmp_path):
    _write(tmp_path, "memory.md", "## 短\n太短\n")
    assert fr.load_fragments(sources=("memory.md",), runtime=tmp_path) == []


def test_load_fragments_multiple_sources(tmp_path):
    _write(tmp_path, "memory.md", "## 记忆\n关于法则属性与结构约束在法则展开过程中如何显现的足够长的一段记忆内容。\n")
    _write(tmp_path, "reflection.md", "## 2026-06-16 反思\n关于展开属性与希望开放性在主体层面的足够长的一段反思内容。\n")
    frags = fr.load_fragments(runtime=tmp_path)
    sources = {f["source"] for f in frags}
    assert sources == {"memory.md", "reflection.md"}


# ──────────────────────────────────────────────────────────────────────
# 张力评分
# ──────────────────────────────────────────────────────────────────────

def test_tension_zero_for_identical_text():
    a = {"source": "memory.md", "text": "约束与结构稳定性的展开关系研究"}
    b = {"source": "memory.md", "text": "约束与结构稳定性的展开关系研究"}
    # 完全相同 → 冗余 → 张力趋于 0
    assert fr.tension_score(a, b) < 0.05


def test_tension_zero_for_unrelated_text():
    a = {"source": "memory.md", "text": "量子纠缠与黑洞视界的物理机制讨论"}
    b = {"source": "memory.md", "text": "烹饪牛肉面的火候与汤底配方心得"}
    # 完全无关 → 噪音 → 张力趋于 0
    assert fr.tension_score(a, b) < 0.1


def test_tension_peaks_for_partial_overlap():
    a = {"source": "memory.md", "text": "约束与结构稳定性在展开过程中的作用"}
    b = {"source": "memory.md", "text": "约束与希望开放性在主体层面的张力关系"}
    score = fr.tension_score(a, b)
    # 部分重叠 → 张力显著
    assert score > 0.2


def test_cross_source_bonus():
    text = "约束与结构稳定性在展开过程中的张力作用机制"
    text2 = "约束与希望开放性在主体反思中的张力关系机制"
    same = fr.tension_score(
        {"source": "memory.md", "text": text},
        {"source": "memory.md", "text": text2},
    )
    cross = fr.tension_score(
        {"source": "memory.md", "text": text},
        {"source": "reflection.md", "text": text2},
    )
    assert cross > same


# ──────────────────────────────────────────────────────────────────────
# 配对
# ──────────────────────────────────────────────────────────────────────

def test_find_high_tension_pairs_filters_and_sorts():
    frags = [
        {"id": "a", "source": "memory.md", "text": "约束与结构稳定性在展开过程中的作用机制"},
        {"id": "b", "source": "reflection.md", "text": "约束与希望开放性在主体层面的张力关系"},
        {"id": "c", "source": "memory.md", "text": "烹饪牛肉面的火候与汤底配方完全无关内容"},
    ]
    pairs = fr.find_high_tension_pairs(frags, min_tension=0.15)
    # a×b 应入选；与 c 的无关配对应被过滤
    ids = {(p[0]["id"], p[1]["id"]) for p in pairs}
    assert ("a", "b") in ids
    # 降序
    scores = [p[2] for p in pairs]
    assert scores == sorted(scores, reverse=True)


def test_find_high_tension_pairs_top_n():
    frags = [
        {"id": str(i), "source": "memory.md",
         "text": f"约束与展开张力关系的第{i}种结构稳定性分析内容"}
        for i in range(5)
    ]
    pairs = fr.find_high_tension_pairs(frags, min_tension=0.0, top_n=3)
    assert len(pairs) == 3


# ──────────────────────────────────────────────────────────────────────
# 重组（注入假 LLM）
# ──────────────────────────────────────────────────────────────────────

def _fake_fn(result_dict):
    """返回一个忽略输入、输出固定 JSON 的假合成函数。"""
    def fn(system, user):
        return json.dumps(result_dict, ensure_ascii=False)
    return fn


def test_recombine_pair_attaches_metadata():
    a = {"id": "memory.md:0", "source": "memory.md", "text": "约束面向"}
    b = {"id": "reflection.md:1", "source": "reflection.md", "text": "展开面向"}
    fn = _fake_fn({
        "is_meaningful": True, "tension_type": "互补",
        "new_structure_title": "本原张力的双面统一",
        "synthesis": "两者是同一张力的两面。", "anchor_concept": "本原张力",
        "opens_new_possibility": "可操作化张力监测", "hope_direction": "推进开放性",
    })
    out = fr.recombine_pair(a, b, tension=0.5, recombine_fn=fn)
    assert out["source_fragments"] == ["memory.md:0", "reflection.md:1"]
    assert out["tension"] == 0.5
    assert out["anchor_concept"] == "本原张力"


def test_recombine_pair_handles_markdown_wrapped_json():
    a = {"id": "x", "source": "memory.md", "text": "甲"}
    b = {"id": "y", "source": "memory.md", "text": "乙"}

    def fn(system, user):
        return "```json\n" + json.dumps({"is_meaningful": False}, ensure_ascii=False) + "\n```"

    out = fr.recombine_pair(a, b, recombine_fn=fn)
    assert out["is_meaningful"] is False


# ──────────────────────────────────────────────────────────────────────
# 锚点筛选
# ──────────────────────────────────────────────────────────────────────

def test_is_kept_requires_meaningful_and_anchor():
    assert fr.is_kept({"is_meaningful": True, "anchor_concept": "本原张力"})
    assert not fr.is_kept({"is_meaningful": False, "anchor_concept": "本原张力"})
    assert not fr.is_kept({"is_meaningful": True, "anchor_concept": ""})
    assert not fr.is_kept({"is_meaningful": True})


# ──────────────────────────────────────────────────────────────────────
# 产出候选
# ──────────────────────────────────────────────────────────────────────

def test_synthesis_to_candidate(tmp_path):
    from evolution_candidate_manager import EvolutionCandidateManager
    manager = EvolutionCandidateManager(candidates_dir=tmp_path / "cands")
    synthesis = {
        "is_meaningful": True, "tension_type": "矛盾",
        "new_structure_title": "矛盾中的更高结构",
        "synthesis": "更高结构容纳了两个碎片的冲突。",
        "anchor_concept": "层级桥接",
        "opens_new_possibility": "新的桥接路径",
        "hope_direction": "保持开放",
        "source_fragments": ["memory.md:0", "reflection.md:2"],
        "tension": 0.42,
    }
    cand = fr.synthesis_to_candidate(synthesis, manager=manager)
    assert cand["type"] == "ENHANCEMENT"
    assert cand["origin"] == "recombination"
    assert cand["source_fragments"] == ["memory.md:0", "reflection.md:2"]
    assert cand["anchor_concept"] == "层级桥接"
    assert cand["expansion_type"] == "展开属性型"
    assert "矛盾中的更高结构" in cand["title"]
    assert cand["hope_direction"].startswith("推进")


# ──────────────────────────────────────────────────────────────────────
# 摘要生成
# ──────────────────────────────────────────────────────────────────────

def test_format_digest_with_kept_results():
    result = {
        "fragments": 4,
        "pairs": 3,
        "syntheses": [{"is_meaningful": True}],
        "kept": [
            {
                "tension_type": "矛盾",
                "new_structure_title": "约束与生成的更高统一",
                "synthesis": "两者在本原张力中互相成就。",
                "anchor_concept": "本原张力",
                "opens_new_possibility": "张力可操作化",
                "hope_direction": "推进开放性",
                "source_fragments": ["memory.md:0", "reflection.md:1"],
                "tension": 0.55,
            }
        ],
        "candidates_saved": [],
        "errors": [],
    }
    md = fr._format_digest(result, "2026-06-18")
    assert "约束与生成的更高统一" in md
    assert "本原张力" in md
    assert "矛盾" in md
    assert "2026-06-18" in md


def test_format_digest_empty_results():
    result = {
        "fragments": 2, "pairs": 1, "syntheses": [],
        "kept": [], "candidates_saved": [], "errors": [],
    }
    md = fr._format_digest(result, "2026-06-18")
    assert "无通过筛选" in md


def test_write_digest_creates_file(tmp_path):
    path = fr.write_digest("# 测试摘要内容", runtime=tmp_path)
    assert path.exists()
    assert "recombination_digest_" in path.name
    assert path.read_text(encoding="utf-8") == "# 测试摘要内容"


def test_write_digest_overwrites_same_day(tmp_path):
    fr.write_digest("# 第一次", runtime=tmp_path)
    fr.write_digest("# 第二次", runtime=tmp_path)
    files = list(tmp_path.glob("recombination_digest_*.md"))
    assert len(files) == 1
    assert "第二次" in files[0].read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────
# 端到端
# ──────────────────────────────────────────────────────────────────────

def test_run_recombination_end_to_end(tmp_path):
    from evolution_candidate_manager import EvolutionCandidateManager

    runtime = tmp_path / "runtime"
    runtime.mkdir()
    _write(runtime, "memory.md",
           "## 约束记忆\n约束与结构稳定性在展开过程中的作用机制是长期记忆要点。\n")
    _write(runtime, "reflection.md",
           "## 2026-06-16 反思\n约束与希望开放性在主体层面的张力关系是反思要点。\n")

    manager = EvolutionCandidateManager(candidates_dir=tmp_path / "cands")
    fn = _fake_fn({
        "is_meaningful": True, "tension_type": "互补",
        "new_structure_title": "约束—希望的张力统一",
        "synthesis": "约束既限制又生成希望的开放性。",
        "anchor_concept": "本原张力",
        "opens_new_possibility": "张力可作为希望的结构前提",
        "hope_direction": "推进开放性",
    })

    result = fr.run_recombination(
        min_tension=0.1, top_n=5,
        recombine_fn=fn, apply=True,
        runtime=runtime, manager=manager,
    )

    assert result["fragments"] == 2
    assert result["pairs"] >= 1
    assert len(result["kept"]) >= 1
    assert len(result["candidates_saved"]) >= 1
    # 候选确实落盘，可被列出
    saved = manager.list_candidates()
    assert any(c.get("origin") == "recombination" for c in saved)


def test_run_recombination_drops_unmeaningful(tmp_path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    _write(runtime, "memory.md",
           "## 甲\n约束与结构稳定性在展开过程中的作用机制内容片段。\n")
    _write(runtime, "reflection.md",
           "## 乙\n约束与希望开放性在主体层面的张力关系内容片段。\n")

    fn = _fake_fn({"is_meaningful": False})
    result = fr.run_recombination(
        min_tension=0.1, top_n=5, recombine_fn=fn, apply=False, runtime=runtime,
    )
    assert result["kept"] == []
    assert result["candidates_saved"] == []
