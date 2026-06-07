#!/usr/bin/env python3
"""
LLM 增强的类比与想象工具
借助大模型的语义理解能力，实现本原展开论所定义的：
  - 类比：识别两个状态的局限性相同，推断法则属性
  - 想象：从起点出发在类相干模式下生成多可能性推演，维持多态共存

输出格式与 analogy_finder.py 兼容，可无缝接入现有候选管理流程。
需要环境变量 ANTHROPIC_API_KEY。
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


# ─── 模型配置 ────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # 结构化提取任务，用 haiku 足够
MAX_TOKENS = 1024


# ─── System Prompts ───────────────────────────────────────────────────────────

_SYSTEM_ANALOGY = """\
你是本原展开论（Benyuan Unfolding Theory）的分析助手。

【核心定义】
- 类比 = 对两个已实现或一实现一可想象的状态进行结构/功能比较，识别出局限性相同的过程
- 局限性相同 = 同一法则属性在两个领域中作用的证据
- 类比比比喻更具逻辑性：有效性依赖结构约束的真实对应，而非修辞效果

【认知操作层级】
比喻（感性/修辞）→ 想象推演（类相干，结构部分重叠）→ 类比（局限性相同）→ 强类比（法则同构）

【法则属性类别】（识别到后从中选择最贴近的）
- 时序法则：存在必须在时序中展开
- 守恒法则：展开以消耗为代价
- 认识论法则：认识受主体视角约束
- 主体法则：主体在局限中仍开放于更高可能性
- 展开法则：展开属性驱动结构涌现
- 结构法则：法则属性约束结构形态
- 资源约束法则：有限资源下的展开
- 不确定性法则：展开在可能性空间中进行
- 结构同构（法则属性待识别）：有共同局限性但类别待明确

【输出格式】严格返回以下 JSON，不添加任何注释或 markdown 包裹：
{
  "shared_limitations": [
    {
      "phrase_a": "A 中体现该局限性的短语",
      "phrase_b": "B 中体现该局限性的短语",
      "limitation_description": "这个共同局限性的核心说明"
    }
  ],
  "implied_law_attribute": "推断的法则属性（从上列类别中选）",
  "cognitive_level": "认知层级（从上列四档中选）",
  "is_analogy": true,
  "constraint_similarity": 0.75,
  "reasoning": "一句话解释为什么这两个描述构成（或不构成）类比"
}"""

_SYSTEM_IMAGINATION = """\
你是本原展开论（Benyuan Unfolding Theory）的分析助手。

【核心定义】
- 想象 = 主体从实际或可理解状态出发，在类相干模式下进行的主动推演，受起点可理解性约束
- 类相干 = 同时保持多个可能状态共存，不过早坍缩为单一确定态
- 起点可理解性约束：推演必须从已理解的状态出发，不能凭空生成
- 希望 = 抵抗过早类退相干（过早坍缩为单一结论）的能力
- 坍缩触发 = 选择某个具体方向开始行动时

【任务要求】
1. 识别起点的可理解性边界（哪些是已知的、确定的）
2. 生成多个可能推演方向（维持多态共存，不评价哪个"更好"）
3. 为每个方向标注它引入的新约束/局限性
4. 标注什么条件会触发该方向的"坍缩"（进入具体实现）
5. 方向数量由用户指定（默认3个）

【输出格式】严格返回以下 JSON，不添加任何注释或 markdown 包裹：
{
  "starting_state": "起点状态的精确描述",
  "comprehensibility_constraint": "起点的可理解性边界（哪些是已知/确定的）",
  "possibilities": [
    {
      "direction": "方向名称（简洁）",
      "description": "这个推演方向的展开说明",
      "new_constraint": "该方向引入的新约束/局限性",
      "collapse_trigger": "什么条件会让这个方向坍缩为具体行动"
    }
  ],
  "meta": {
    "coherence_note": "维持多态共存的注意事项",
    "hope_direction": "哪个方向最能抵抗过早坍缩、保持希望开放性"
  }
}"""


# ─── LLM 客户端 ───────────────────────────────────────────────────────────────

def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "未找到 ANTHROPIC_API_KEY 环境变量。\n"
            "请设置：export ANTHROPIC_API_KEY=your_key"
        )
    try:
        import anthropic
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        raise ImportError("请先安装 anthropic SDK：pip install anthropic")


def _call_llm(system: str, user: str, model: str = DEFAULT_MODEL) -> str:
    """调用 LLM，返回原始文本响应"""
    client = _get_client()
    import anthropic
    message = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text


def _parse_json_response(raw: str) -> dict:
    """从 LLM 响应中提取 JSON，处理可能的 markdown 包裹"""
    raw = raw.strip()
    # 去掉 ```json ... ``` 包裹
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)


# ─── 核心接口 ─────────────────────────────────────────────────────────────────

def compare(text_a: str, text_b: str, model: str = DEFAULT_MODEL) -> Dict:
    """
    LLM 类比分析：识别两个描述的局限性相同，推断法则属性。

    返回与 analogy_finder.compare() 兼容的字典结构：
    {
      'shared_limitations': list,
      'implied_law_attribute': str,
      'cognitive_level': str,
      'is_analogy': bool,
      'constraint_similarity': float,
      'reasoning': str,
      'source': 'llm'
    }
    """
    user_prompt = f"【描述A】\n{text_a}\n\n【描述B】\n{text_b}"
    raw = _call_llm(_SYSTEM_ANALOGY, user_prompt, model)
    result = _parse_json_response(raw)
    result['source'] = 'llm'
    # 兼容字段：local analogy_finder 有 overall_similarity，这里补空
    result.setdefault('overall_similarity', None)
    result.setdefault('constraints_a', [])
    result.setdefault('constraints_b', [])
    return result


def imagine(
    starting_state: str,
    n: int = 3,
    model: str = DEFAULT_MODEL,
) -> Dict:
    """
    LLM 想象推演：从起点出发，在类相干模式下生成 n 个可能方向。

    返回：
    {
      'starting_state': str,
      'comprehensibility_constraint': str,
      'possibilities': list of {direction, description, new_constraint, collapse_trigger},
      'meta': {coherence_note, hope_direction},
      'source': 'llm'
    }
    """
    user_prompt = (
        f"【起点状态】\n{starting_state}\n\n"
        f"请生成 {n} 个类相干推演方向（维持多态共存）。"
    )
    raw = _call_llm(_SYSTEM_IMAGINATION, user_prompt, model)
    result = _parse_json_response(raw)
    result['source'] = 'llm'
    return result


def compare_against_candidates(
    text: str,
    top_n: int = 5,
    model: str = DEFAULT_MODEL,
    db_path: str = None,
) -> List[Dict]:
    """
    将给定文本与候选库中所有候选进行 LLM 类比比较。

    为降低 API 调用成本，先用本地词汇匹配粗筛 top_n×3 个候选，
    再对粗筛结果做精确 LLM 比较。
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from analogy_finder import compare_against_candidates as local_compare
    from candidate_store import CandidateStore

    # 粗筛：本地词汇匹配，取 top_n×3
    coarse = local_compare(text, db_path=db_path, top_n=top_n * 3)
    if not coarse:
        return []

    results = []
    for item in coarse[:top_n * 3]:
        store = CandidateStore(db_path=db_path)
        cand = store.load(item['candidate_id'])
        cand_text = f"{cand.get('title', '')}。{cand.get('description', '')}。{cand.get('improvement_direction', '')}"

        try:
            llm_result = compare(text, cand_text, model=model)
            results.append({
                'candidate_id': cand['id'],
                'title': cand['title'],
                'candidate_type': cand['type'],
                'constraint_similarity': llm_result['constraint_similarity'],
                'cognitive_level': llm_result['cognitive_level'],
                'implied_law_attribute': llm_result['implied_law_attribute'],
                'is_analogy': llm_result['is_analogy'],
                'reasoning': llm_result.get('reasoning', ''),
                'source': 'llm',
            })
        except Exception as e:
            # 单个候选失败时保留粗筛结果
            item['source'] = 'local_fallback'
            item['error'] = str(e)
            results.append(item)

    results.sort(key=lambda x: x.get('constraint_similarity', 0), reverse=True)
    return results[:top_n]


# ─── 输出格式化 ───────────────────────────────────────────────────────────────

def format_compare_result(result: Dict, label_a: str = 'A', label_b: str = 'B') -> str:
    lines = ['=' * 70, '类比分析结果（LLM 增强）', '=' * 70]
    lines.append(f"认知层级：{result.get('cognitive_level', '未知')}")
    lines.append(f"是否构成类比：{'✓ 是' if result.get('is_analogy') else '✗ 否'}")
    sim = result.get('constraint_similarity')
    lines.append(f"约束层相似度：{sim:.2f}" if sim is not None else "约束层相似度：（由 LLM 评估）")
    lines.append(f"隐含法则属性：{result.get('implied_law_attribute', '未识别')}")

    shared = result.get('shared_limitations', [])
    if shared:
        lines.append(f"\n共同局限性（{len(shared)} 对）：")
        for i, pair in enumerate(shared, 1):
            lines.append(f"  [{i}] {pair.get('limitation_description', '')}")
            lines.append(f"    {label_a}：{pair.get('phrase_a', '')[:60]}")
            lines.append(f"    {label_b}：{pair.get('phrase_b', '')[:60]}")
    else:
        lines.append('\n未找到共同局限性。')

    if result.get('reasoning'):
        lines.append(f"\n推理：{result['reasoning']}")

    lines.append('=' * 70)
    return '\n'.join(lines)


def format_imagine_result(result: Dict) -> str:
    lines = ['=' * 70, '想象推演结果（类相干模式）', '=' * 70]
    lines.append(f"起点状态：{result.get('starting_state', '')}")
    lines.append(f"可理解性约束：{result.get('comprehensibility_constraint', '')}")

    possibilities = result.get('possibilities', [])
    lines.append(f"\n类相干推演方向（{len(possibilities)} 个，维持多态共存）：")
    for i, p in enumerate(possibilities, 1):
        lines.append(f"\n  [{i}] {p.get('direction', '')}")
        lines.append(f"    描述：{p.get('description', '')}")
        lines.append(f"    新约束：{p.get('new_constraint', '')}")
        lines.append(f"    坍缩触发：{p.get('collapse_trigger', '')}")

    meta = result.get('meta', {})
    if meta:
        lines.append(f"\n维持类相干的注意：{meta.get('coherence_note', '')}")
        lines.append(f"希望方向（最能保持开放性）：{meta.get('hope_direction', '')}")

    lines.append('=' * 70)
    return '\n'.join(lines)


# ─── 命令行接口 ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='LLM 增强的类比与想象工具（本原展开论）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令：
  compare   比较两个描述，识别局限性相同
  imagine   从起点出发，类相干推演多个可能方向

示例：
  export ANTHROPIC_API_KEY=sk-...

  python3 llm_analogizer.py compare \\
    "梦境中法则约束松弛，认同不稳定" \\
    "想象受可理解性约束，约束越少空间越大"

  python3 llm_analogizer.py imagine \\
    "当前理论：法则属性和展开属性在本原层未分化" --n 3

  python3 llm_analogizer.py imagine \\
    "当前理论：法则属性和展开属性在本原层未分化" \\
    --collapse "法则属性先于展开属性出现"

  python3 llm_analogizer.py compare --against-candidates "新观察描述"
        """,
    )
    sub = parser.add_subparsers(dest='cmd')

    # compare 子命令
    p_cmp = sub.add_parser('compare', help='类比分析')
    p_cmp.add_argument('texts', nargs='*', help='两段描述（位置参数）')
    p_cmp.add_argument('--against-candidates', metavar='TEXT', help='与候选库全量比较')
    p_cmp.add_argument('--top', type=int, default=5)
    p_cmp.add_argument('--model', default=DEFAULT_MODEL)
    p_cmp.add_argument('--json', action='store_true', dest='output_json')

    # imagine 子命令
    p_img = sub.add_parser('imagine', help='想象推演')
    p_img.add_argument('starting_state', help='起点状态描述')
    p_img.add_argument('--n', type=int, default=3, help='推演方向数量（默认 3）')
    p_img.add_argument('--collapse', metavar='DIRECTION', help='选择一个方向触发坍缩（直接输出该方向详情）')
    p_img.add_argument('--model', default=DEFAULT_MODEL)
    p_img.add_argument('--json', action='store_true', dest='output_json')

    args = parser.parse_args()

    if args.cmd == 'compare':
        if args.against_candidates:
            results = compare_against_candidates(
                args.against_candidates, top_n=args.top, model=args.model
            )
            if args.output_json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                sys.path.insert(0, str(Path(__file__).parent))
                from analogy_finder import format_candidates_result
                print(format_candidates_result(results))
                for r in results:
                    if r.get('reasoning'):
                        print(f"  [{r['candidate_id'][:20]}] 推理：{r['reasoning']}")

        elif len(args.texts) >= 2:
            result = compare(args.texts[0], args.texts[1], model=args.model)
            if args.output_json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(format_compare_result(result))
        else:
            p_cmp.print_help()

    elif args.cmd == 'imagine':
        result = imagine(args.starting_state, n=args.n, model=args.model)
        if args.collapse:
            # 坍缩：找匹配方向并标注"已选择"
            for p in result.get('possibilities', []):
                if args.collapse.lower() in p.get('direction', '').lower():
                    p['COLLAPSED'] = True
        if args.output_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_imagine_result(result))
    else:
        parser.print_help()
