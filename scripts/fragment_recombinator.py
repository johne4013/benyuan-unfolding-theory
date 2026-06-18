#!/usr/bin/env python3
"""
fragment_recombinator.py — 碎片重组器（记忆代谢的下一环）

记忆代谢（memory_metabolism.py）把经验压缩成碎片，沉淀在
runtime/memory.md（人工维护的长期记忆）与 runtime/reflection.md
（工具链自动写入的反思条目）中。本模块做的是代谢之后最关键的一环：

  把这些已沉淀的碎片，按"张力"两两配对，让 LLM 在张力中合成
  一个能同时容纳两者的更高结构，产出为理论演化候选。

这正是本原展开论意义上的"想象力"操作化：想象不是无中生有，而是
已有碎片在张力驱动下的非原始重组（原始关联已知，想象来自原始关联
之外的组合）。

设计要点（与理论对齐）：
  1) 张力驱动，不是随机：相关但从未被连接的碎片张力最高（中等语义
     重叠），完全相同（冗余）或完全无关（噪音）的配对都被过滤。
     跨来源（memory × reflection）配对额外加权。
  2) 锚点筛选（认同连续性检验）：重组结果必须能锚定到已有理论概念，
     否则视为幻觉而非想象，丢弃。这一层加上后续的候选审批流程，
     共同构成"重组结果是否有价值"的过滤。
  3) 产出复用现有管线：合成结果走 EvolutionCandidateManager，
     与其它候选一样进入 CANDIDATE → APPROVED → INTEGRATED 生命周期。

碎片加载、张力配对不需要 API key（纯本地、确定性、可测）；
只有实际合成（recombine）这一步调用 LLM，需要 ANTHROPIC_API_KEY。
合成函数可注入，便于测试与替换。

用法：
    # 看碎片加载情况（无需 LLM）
    python3 fragment_recombinator.py scan

    # 看高张力配对（无需 LLM）
    python3 fragment_recombinator.py pairs --top 10 --min-tension 0.3

    # 对高张力配对做重组（需要 ANTHROPIC_API_KEY）；--apply 写入候选
    python3 fragment_recombinator.py recombine --top 5
    python3 fragment_recombinator.py recombine --top 5 --apply
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from paths import runtime_dir


DEFAULT_SOURCES = ("memory.md", "reflection.md")
MIN_FRAGMENT_CHARS = 30   # 太短的片段不构成有意义单元
DEFAULT_MIN_TENSION = 0.3

# 与 feedback_classifier 一致的停用词，保证相似度口径统一
_STOPWORDS = {
    '的', '了', '在', '是', '有', '和', '也', '都', '不', '这', '对', '于',
    '与', '其', '为', '以', '及', '但', '从', '而', '中', '到', '被', '将',
    '能', '会', '应该', '没有', '可以', '一个', '进行',
}


# ──────────────────────────────────────────────────────────────────────
# 碎片加载
# ──────────────────────────────────────────────────────────────────────

def _split_into_fragments(text: str, source: str) -> List[Dict]:
    """把一个 markdown 文档切成碎片。

    切分规则：以 markdown 标题（# / ## / ###）为段落边界，每个标题段
    连同其正文为一个碎片；无标题的前导正文按空行段落切。过短的片段丢弃。
    """
    fragments: List[Dict] = []
    # 以标题行为锚点切块；标题本身保留在块首
    blocks = re.split(r'(?m)^(?=#{1,6}\s)', text)
    raw_chunks: List[str] = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith('#'):
            raw_chunks.append(block)
        else:
            # 无标题前导内容：按空行再切成段落
            for para in re.split(r'\n\s*\n', block):
                para = para.strip()
                if para:
                    raw_chunks.append(para)

    for idx, chunk in enumerate(raw_chunks):
        # 提取标题作为碎片标题（若有）
        first_line = chunk.splitlines()[0].strip()
        title = first_line.lstrip('#').strip() if first_line.startswith('#') else first_line[:40]
        if len(chunk) < MIN_FRAGMENT_CHARS:
            continue
        fragments.append({
            "id": f"{source}:{idx}",
            "source": source,
            "title": title,
            "text": chunk,
        })
    return fragments


def load_fragments(sources=DEFAULT_SOURCES, runtime=None) -> List[Dict]:
    """从 memory.md / reflection.md 等来源加载碎片。

    缺失的来源文件被静默跳过（不报错），与工具链其它脚本一致。
    返回碎片字典列表：{id, source, title, text}。
    """
    base = Path(runtime) if runtime is not None else runtime_dir()
    fragments: List[Dict] = []
    for source in sources:
        path = base / source
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        fragments.extend(_split_into_fragments(text, source))
    return fragments


# ──────────────────────────────────────────────────────────────────────
# 张力评分
# ──────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> set:
    """字级二元组 + 词，口径与 feedback_classifier 一致。"""
    tokens = set()
    words = re.findall(r'[一-鿿]+|[a-zA-Z]{2,}', text.lower())
    for word in words:
        if word not in _STOPWORDS and len(word) >= 2:
            tokens.add(word)
            for i in range(len(word) - 1):
                bigram = word[i:i + 2]
                if bigram not in _STOPWORDS:
                    tokens.add(bigram)
    return tokens


def _jaccard(t1: set, t2: set) -> float:
    if not t1 or not t2:
        return 0.0
    union = len(t1 | t2)
    return len(t1 & t2) / union if union else 0.0


def tension_score(frag_a: Dict, frag_b: Dict) -> float:
    """两个碎片之间的张力分数（0~1）。

    张力在"相关但不相同"处最高：语义重叠 j 在 0.5 附近时基础分最高，
    j→0（无关，噪音）或 j→1（冗余）时基础分趋于 0。跨来源配对
    （memory × reflection）再乘一个加权，鼓励把人工长期记忆与
    自动反思连接起来。
    """
    j = _jaccard(_tokenize(frag_a["text"]), _tokenize(frag_b["text"]))
    base = 4.0 * j * (1.0 - j)  # 在 j=0.5 处取最大值 1.0
    cross_source = 1.15 if frag_a["source"] != frag_b["source"] else 1.0
    return min(base * cross_source, 1.0)


def find_high_tension_pairs(
    fragments: List[Dict],
    min_tension: float = DEFAULT_MIN_TENSION,
    top_n: Optional[int] = None,
) -> List[Tuple[Dict, Dict, float]]:
    """返回按张力降序排列的高张力碎片对。

    复杂度 O(n^2)，适用于 runtime 碎片规模（数十到数百）。
    """
    pairs: List[Tuple[Dict, Dict, float]] = []
    n = len(fragments)
    for i in range(n):
        for k in range(i + 1, n):
            score = tension_score(fragments[i], fragments[k])
            if score >= min_tension:
                pairs.append((fragments[i], fragments[k], score))
    pairs.sort(key=lambda t: t[2], reverse=True)
    if top_n is not None:
        pairs = pairs[:top_n]
    return pairs


# ──────────────────────────────────────────────────────────────────────
# 重组（LLM 合成）
# ──────────────────────────────────────────────────────────────────────

_SYSTEM_RECOMBINE = """\
你是本原展开论（Benyuan Unfolding Theory）的碎片重组助手。

【任务】给你两个来自记忆/反思的碎片，它们之间存在张力（相关但未被显式
连接，或彼此张力性地并存）。请不要简单拼接，而是寻找一个能同时容纳两者
的更高结构、新观点或新连接——这就是"在张力中重组生成新结构"。

【关键约束：认同连续性检验】
重组结果必须能锚定到本原展开论已有的概念或结构（如：本原张力、法则属性、
展开属性、层级桥接、连续性、局限性、希望、认同、协同展开等），否则它就是
悬空的幻觉而非想象。若两个碎片之间并不存在可被有意义重组的张力，请如实
判定 is_meaningful 为 false。

【张力类型】
- 互补：两者从不同侧面指向同一更高结构
- 矛盾：两者表面冲突，更高结构能消解或容纳该冲突（矛盾往往是最强生成源）
- 跨层：两者处于不同层级，共享可桥接的结构

【输出格式】严格返回以下 JSON，不要任何注释或 markdown 包裹：
{
  "is_meaningful": true,
  "tension_type": "互补 | 矛盾 | 跨层",
  "new_structure_title": "重组出的新结构/新观点（简洁标题）",
  "synthesis": "这个更高结构如何同时容纳两个碎片（2-4 句）",
  "anchor_concept": "锚定到的本原展开论已有概念（若无则留空字符串）",
  "opens_new_possibility": "这个重组打开了什么此前未显式存在的新方向",
  "hope_direction": "一句话：它如何推进系统在局限中的开放性"
}"""


def _default_recombine_fn(system: str, user: str) -> str:
    """默认合成函数：复用 llm_analogizer 的 LLM 客户端（延迟导入，
    仅在真正调用时才需要 ANTHROPIC_API_KEY）。"""
    from llm_analogizer import _call_llm, DEFAULT_MODEL
    return _call_llm(system, user, model=DEFAULT_MODEL)


def _parse_json_response(raw: str) -> dict:
    """从 LLM 响应提取 JSON，处理可能的 markdown 包裹。"""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)


def recombine_pair(
    frag_a: Dict,
    frag_b: Dict,
    tension: float = None,
    recombine_fn: Callable[[str, str], str] = None,
) -> Dict:
    """对一个碎片对做重组合成。

    Args:
        frag_a, frag_b: 碎片字典。
        tension:        张力分数（仅记录用）。
        recombine_fn:   接收 (system, user) 返回原始文本的可调用对象；
                        默认走 llm_analogizer 的 LLM。注入可用于测试。

    Returns:
        合成结果字典（含 is_meaningful / anchor_concept 等字段），并附带
        source_fragments 与 tension 元信息。
    """
    fn = recombine_fn if recombine_fn is not None else _default_recombine_fn
    user = (
        f"【碎片 A】（来源 {frag_a['source']}）\n{frag_a['text']}\n\n"
        f"【碎片 B】（来源 {frag_b['source']}）\n{frag_b['text']}"
    )
    raw = fn(_SYSTEM_RECOMBINE, user)
    result = _parse_json_response(raw)
    result["source_fragments"] = [frag_a["id"], frag_b["id"]]
    result["tension"] = round(tension, 3) if tension is not None else None
    return result


def is_kept(synthesis: Dict) -> bool:
    """锚点筛选：保留 is_meaningful 为真且锚定到已有概念的重组结果。"""
    if not synthesis.get("is_meaningful"):
        return False
    return bool((synthesis.get("anchor_concept") or "").strip())


# ──────────────────────────────────────────────────────────────────────
# 产出为候选
# ──────────────────────────────────────────────────────────────────────

def synthesis_to_candidate(synthesis: Dict, manager=None) -> Dict:
    """把一个（已通过筛选的）重组结果转换为理论演化候选。

    候选类型为 ENHANCEMENT（重组 = 理论增强），source_task 标记为
    fragment_recombination，并保留来源碎片与张力，便于追溯。
    """
    if manager is None:
        from evolution_candidate_manager import EvolutionCandidateManager
        manager = EvolutionCandidateManager()

    title = synthesis.get("new_structure_title", "（无标题重组）")
    tension_type = synthesis.get("tension_type", "")
    src = synthesis.get("source_fragments", [])
    description = (
        f"{synthesis.get('synthesis', '')}\n\n"
        f"张力类型：{tension_type}\n"
        f"来源碎片：{', '.join(src)}\n"
        f"锚定概念：{synthesis.get('anchor_concept', '')}"
    )
    candidate = manager.create_candidate(
        candidate_type="ENHANCEMENT",
        title=title,
        description=description,
        source_task="fragment_recombination",
        improvement_direction=synthesis.get("opens_new_possibility", "待定"),
    )
    # 重组专属元信息
    candidate["origin"] = "recombination"
    candidate["source_fragments"] = src
    candidate["tension"] = synthesis.get("tension")
    candidate["tension_type"] = tension_type
    candidate["anchor_concept"] = synthesis.get("anchor_concept", "")
    candidate["expansion_type"] = "展开属性型"  # 重组生成新结构，属展开侧
    hope_dir = synthesis.get("hope_direction", "")
    if hope_dir:
        candidate["hope_direction"] = f"推进：{hope_dir}"
    opens = synthesis.get("opens_new_possibility", "")
    if opens:
        candidate["opens_new_possibility"] = f"是——{opens}"
    return candidate


def run_recombination(
    sources=DEFAULT_SOURCES,
    min_tension: float = DEFAULT_MIN_TENSION,
    top_n: int = 5,
    recombine_fn: Callable[[str, str], str] = None,
    apply: bool = False,
    runtime=None,
    manager=None,
) -> Dict:
    """端到端：加载碎片 → 找高张力对 → 重组 → 筛选 →（可选）写入候选。

    Returns:
        {fragments, pairs, syntheses, kept, candidates_saved, errors}
    """
    fragments = load_fragments(sources=sources, runtime=runtime)
    pairs = find_high_tension_pairs(fragments, min_tension=min_tension, top_n=top_n)

    syntheses: List[Dict] = []
    kept: List[Dict] = []
    candidates_saved: List[str] = []
    errors: List[str] = []

    if apply and manager is None:
        from evolution_candidate_manager import EvolutionCandidateManager
        manager = EvolutionCandidateManager()

    for frag_a, frag_b, score in pairs:
        try:
            synthesis = recombine_pair(frag_a, frag_b, tension=score, recombine_fn=recombine_fn)
        except Exception as e:
            errors.append(f"重组 {frag_a['id']} × {frag_b['id']} 失败：{e}")
            continue
        syntheses.append(synthesis)
        if not is_kept(synthesis):
            continue
        kept.append(synthesis)
        if apply:
            candidate = synthesis_to_candidate(synthesis, manager=manager)
            path = manager.save_candidate(candidate)
            candidates_saved.append(candidate["id"])

    return {
        "fragments": len(fragments),
        "pairs": len(pairs),
        "syntheses": syntheses,
        "kept": kept,
        "candidates_saved": candidates_saved,
        "errors": errors,
    }


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def _cmd_scan(args):
    fragments = load_fragments()
    by_source: Dict[str, int] = {}
    for f in fragments:
        by_source[f["source"]] = by_source.get(f["source"], 0) + 1
    print(f"碎片总数：{len(fragments)}")
    for src, cnt in by_source.items():
        print(f"  {src}: {cnt}")
    if args.verbose:
        for f in fragments:
            print(f"  [{f['id']}] {f['title'][:50]}")


def _cmd_pairs(args):
    fragments = load_fragments()
    pairs = find_high_tension_pairs(
        fragments, min_tension=args.min_tension, top_n=args.top
    )
    if not pairs:
        print("未找到高张力配对（可降低 --min-tension 重试）。")
        return
    print(f"高张力配对（{len(pairs)} 对，min_tension={args.min_tension}）：")
    for a, b, score in pairs:
        cross = "↔跨源" if a["source"] != b["source"] else "  同源"
        print(f"  {score:.3f} {cross}  [{a['id']}] {a['title'][:24]}  ×  [{b['id']}] {b['title'][:24]}")


def _cmd_recombine(args):
    result = run_recombination(
        min_tension=args.min_tension,
        top_n=args.top,
        apply=args.apply,
    )
    if args.output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"碎片 {result['fragments']} 个，高张力配对 {result['pairs']} 对，"
          f"重组 {len(result['syntheses'])} 次，通过筛选 {len(result['kept'])} 个。")
    for s in result["kept"]:
        print(f"\n  【{s.get('tension_type', '')}】{s.get('new_structure_title', '')}")
        print(f"    合成：{s.get('synthesis', '')}")
        print(f"    锚定：{s.get('anchor_concept', '')}")
        print(f"    新可能性：{s.get('opens_new_possibility', '')}")
        print(f"    来源碎片：{', '.join(s.get('source_fragments', []))}（张力 {s.get('tension')}）")
    if result["candidates_saved"]:
        print(f"\n✓ 已写入候选 {len(result['candidates_saved'])} 个：")
        for cid in result["candidates_saved"]:
            print(f"    {cid}")
        print("  用 evolution_candidate_manager.py list 查看，approve 后可 integrate。")
    elif args.apply:
        print("\n（无通过筛选的重组，未写入候选）")
    else:
        print("\n（预览模式，未写入。加 --apply 写入候选库）")
    if result["errors"]:
        print("\n告警：")
        for e in result["errors"]:
            print(f"  {e}")


def main():
    parser = argparse.ArgumentParser(
        description="碎片重组器——记忆代谢之后的想象力环节（本原展开论）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="加载并统计碎片（无需 LLM）")
    p_scan.add_argument("-v", "--verbose", action="store_true", help="列出每个碎片")

    p_pairs = sub.add_parser("pairs", help="显示高张力配对（无需 LLM）")
    p_pairs.add_argument("--top", type=int, default=10)
    p_pairs.add_argument("--min-tension", type=float, default=DEFAULT_MIN_TENSION)

    p_rec = sub.add_parser("recombine", help="对高张力配对做 LLM 重组（需要 ANTHROPIC_API_KEY）")
    p_rec.add_argument("--top", type=int, default=5)
    p_rec.add_argument("--min-tension", type=float, default=DEFAULT_MIN_TENSION)
    p_rec.add_argument("--apply", action="store_true", help="把通过筛选的重组写入候选库")
    p_rec.add_argument("--json", action="store_true", dest="output_json")

    args = parser.parse_args()

    if args.cmd == "scan":
        _cmd_scan(args)
    elif args.cmd == "pairs":
        _cmd_pairs(args)
    elif args.cmd == "recombine":
        _cmd_recombine(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
