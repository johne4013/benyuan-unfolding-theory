#!/usr/bin/env python3
"""
类比识别工具
基于本原展开论中"类比=局限性相同"的定义：
  对两个已实现或一实现一可想象的状态进行结构/功能比较，
  识别出局限性相同的过程；相同局限性是同一法则属性作用的证据。

核心操作层级（认知操作层级）：
  比喻（感性/修辞）→ 想象（类相干推演）→ 类比（局限性相同）→ 理论（提炼法则属性）
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# ─── 约束词归一化本体（理论内部近义词 → 约束类别标签）─────────────────────────
# 使词汇层差异不影响约束层的相似度计算
CONSTRAINT_ONTOLOGY = {
    # 行动不能（inability）
    '无法': 'CAT:行动不能', '不能': 'CAT:行动不能', '不可以': 'CAT:行动不能',
    '不允许': 'CAT:行动不能', '禁止': 'CAT:行动不能', '做不到': 'CAT:行动不能',
    # 约束依赖（dependency/constraint）
    '约束': 'CAT:约束依赖', '限制': 'CAT:约束依赖', '边界': 'CAT:约束依赖',
    '局限': 'CAT:约束依赖', '前提': 'CAT:约束依赖', '条件': 'CAT:约束依赖',
    '依赖': 'CAT:约束依赖', '依托': 'CAT:约束依赖', '受制': 'CAT:约束依赖',
    # 约束强度变化（constraint relaxation/tightening）
    '松弛': 'CAT:约束强度↓', '越少': 'CAT:约束强度↓', '降低': 'CAT:约束强度↓',
    '减弱': 'CAT:约束强度↓', '宽松': 'CAT:约束强度↓', '弱化': 'CAT:约束强度↓',
    '增强': 'CAT:约束强度↑', '越强': 'CAT:约束强度↑', '收紧': 'CAT:约束强度↑',
    # 稳定性（stability）
    '不稳定': 'CAT:稳定性↓', '失稳': 'CAT:稳定性↓', '混乱': 'CAT:稳定性↓',
    '稳定': 'CAT:稳定性+', '一致性': 'CAT:稳定性+', '持续': 'CAT:稳定性+',
    # 可能性空间（possibility space）
    '可能性': 'CAT:可能空间', '空间': 'CAT:可能空间', '范围': 'CAT:可能空间',
    '越大': 'CAT:可能空间↑', '扩展': 'CAT:可能空间↑', '打开': 'CAT:可能空间↑',
    '越小': 'CAT:可能空间↓', '收缩': 'CAT:可能空间↓', '坍缩': 'CAT:可能空间↓',
    # 起点/可理解性（origin/comprehensibility）
    '起点': 'CAT:起点约束', '出发': 'CAT:起点约束', '前提': 'CAT:起点约束',
    '可理解': 'CAT:可理解性', '未知': 'CAT:可理解性↓', '已知': 'CAT:可理解性+',
    # 认同/主体（identity/subject）
    '认同': 'CAT:主体认同', '主体': 'CAT:主体认同', '自我': 'CAT:主体认同',
    # 法则属性（law attribute）
    '法则': 'CAT:法则属性', '展开': 'CAT:展开属性', '本原': 'CAT:本原',
}


# ─── 约束关键词分类 ────────────────────────────────────────────────────────────

# 局限性标志词（信号越强，提取的约束短语可靠性越高）
CONSTRAINT_SIGNALS = {
    'strong': [
        '局限', '约束', '边界', '限制', '前提', '条件', '依赖',
        '不能', '无法', '不可以', '不允许', '禁止', '排除',
        '只有.*才', '必须.*才能', '在.*下才',
    ],
    'medium': [
        '需要', '要求', '受.*制约', '取决于', '依托', '基于',
        '否则', '除非', '若.*则', '当.*时',
    ],
    'weak': [
        '仍然', '虽然', '尽管', '但', '然而', '不过',
    ],
}

# 法则属性推断路由（共同局限性 → 隐含法则属性）
LAW_ATTRIBUTE_ROUTES = [
    (['时间', '顺序', '先后', '序列', '时序', '历时', '持续'],     '时序法则：存在必须在时序中展开'),
    (['能量', '守恒', '损耗', '消耗', '熵', '不可逆'],             '守恒法则：展开以消耗为代价'),
    (['信息', '认知', '可知', '理解', '感知', '观测', '测量'],     '认识论法则：认识受主体视角约束'),
    (['主体', '认同', '自我', '意识', '主观'],                      '主体法则：主体在局限中仍开放'),
    (['生成', '涌现', '展开', '演化', '发展', '增长'],              '展开法则：展开属性驱动结构涌现'),
    (['结构', '功能', '形式', '关系', '层级', '组织'],              '结构法则：法则属性约束结构形态'),
    (['资源', '有限', '稀缺', '竞争', '分配'],                      '资源约束法则：有限资源下的展开'),
    (['可能', '概率', '不确定', '随机', '选择'],                    '不确定性法则：展开在可能性空间中进行'),
]


# ─── 核心函数 ──────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> set:
    """CJK 二元组 + 长词提取 + 约束本体类别标签注入"""
    stopwords = {
        '的', '了', '在', '是', '有', '和', '也', '都', '不', '这', '对', '于',
        '与', '其', '为', '以', '及', '但', '从', '而', '中', '到', '被', '将',
        '能', '会', '应该', '没有', '可以', '一个', '进行', '一种', '我们',
    }
    tokens = set()
    words = re.findall(r'[一-鿿]+|[a-zA-Z]{2,}', text.lower())
    for word in words:
        if word not in stopwords and len(word) >= 2:
            tokens.add(word)
            for i in range(len(word) - 1):
                bigram = word[i:i + 2]
                if bigram not in stopwords:
                    tokens.add(bigram)
    # 注入约束本体类别：将文本中出现的本体词替换为类别标签，增强跨词汇对比能力
    for term, category in CONSTRAINT_ONTOLOGY.items():
        if term in text:
            tokens.add(category)
    return tokens


def _jaccard(tokens_a: set, tokens_b: set) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union > 0 else 0.0


def extract_constraints(text: str) -> List[Dict]:
    """
    从文本中提取约束/局限性短语。

    返回列表，每项：{'phrase': str, 'weight': float, 'signal': str}
    weight: strong=1.0, medium=0.6, weak=0.3
    """
    constraints = []
    # 中文句号/感叹号/问号/分号切句；逗号切子句（提高短语粒度）
    sentences = re.split(r'[；;。！!？?\n，,]', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        weight = 0.0
        matched_signal = ''

        for signal in CONSTRAINT_SIGNALS['strong']:
            if re.search(signal, sentence):
                weight = max(weight, 1.0)
                matched_signal = signal
                break

        if weight < 1.0:
            for signal in CONSTRAINT_SIGNALS['medium']:
                if re.search(signal, sentence):
                    weight = max(weight, 0.6)
                    matched_signal = signal
                    break

        if weight < 0.6:
            for signal in CONSTRAINT_SIGNALS['weak']:
                if signal in sentence:
                    weight = max(weight, 0.3)
                    matched_signal = signal
                    break

        # 无信号词的短句也保留（低权重），用于整体相似度计算
        if weight == 0.0 and len(sentence) >= 4:
            weight = 0.2

        if weight > 0:
            constraints.append({
                'phrase': sentence,
                'weight': weight,
                'signal': matched_signal,
            })

    return constraints


def find_shared_limitations(
    constraints_a: List[Dict],
    constraints_b: List[Dict],
    threshold: float = 0.10,
) -> List[Dict]:
    """
    两组约束之间的配对匹配，返回局限性相同的对。

    每对包含：
      phrase_a, phrase_b, similarity, combined_weight, is_shared
    """
    pairs = []
    for ca in constraints_a:
        for cb in constraints_b:
            ta = _tokenize(ca['phrase'])
            tb = _tokenize(cb['phrase'])
            sim = _jaccard(ta, tb)
            if sim >= threshold:
                pairs.append({
                    'phrase_a': ca['phrase'],
                    'phrase_b': cb['phrase'],
                    'similarity': round(sim, 3),
                    'combined_weight': round((ca['weight'] + cb['weight']) / 2, 2),
                    'is_shared': True,
                })

    # 按 similarity × combined_weight 降序
    pairs.sort(key=lambda x: x['similarity'] * x['combined_weight'], reverse=True)
    return pairs


def infer_law_attribute(shared_pairs: List[Dict], text_a: str, text_b: str) -> str:
    """
    从共同局限性推断隐含的法则属性。
    先在匹配对文本中搜索，再回退到整体文本。
    """
    combined_text = text_a + text_b
    for pairs_dict in shared_pairs:
        combined_text += pairs_dict['phrase_a'] + pairs_dict['phrase_b']

    for keywords, law_attr in LAW_ATTRIBUTE_ROUTES:
        if any(kw in combined_text for kw in keywords):
            return law_attr

    return '结构同构（法则属性待识别）'


def _cognitive_level(similarity: float) -> str:
    """根据总相似度判断认知操作层级"""
    if similarity >= 0.45:
        return '强类比（法则同构）'
    elif similarity >= 0.25:
        return '类比（局限性相同）'
    elif similarity >= 0.10:
        return '想象推演（结构部分重叠）'
    else:
        return '比喻（修辞相似或无实质对应）'


# ─── 主接口 ───────────────────────────────────────────────────────────────────

def compare(text_a: str, text_b: str, threshold: float = 0.10) -> Dict:
    """
    完整类比分析：给定两段描述，识别局限性相同的结构。

    返回：
      {
        'overall_similarity': float,        # 整体文本相似度（二元组 Jaccard）
        'constraint_similarity': float,     # 约束层相似度（加权）
        'shared_limitations': list,         # 配对的共同局限性
        'implied_law_attribute': str,       # 推断的法则属性
        'cognitive_level': str,             # 认知操作层级
        'is_analogy': bool,                 # 是否构成类比（constraint_similarity > threshold）
        'constraints_a': list,              # 从 text_a 提取的约束
        'constraints_b': list,              # 从 text_b 提取的约束
      }
    """
    # 整体相似度（字面层）
    ta = _tokenize(text_a)
    tb = _tokenize(text_b)
    overall_sim = _jaccard(ta, tb)

    # 约束提取
    constraints_a = extract_constraints(text_a)
    constraints_b = extract_constraints(text_b)

    # 共同局限性配对
    shared = find_shared_limitations(constraints_a, constraints_b, threshold)

    # 约束层加权相似度
    if shared:
        # 用匹配对的 similarity × combined_weight 加权平均
        total_score = sum(p['similarity'] * p['combined_weight'] for p in shared)
        total_weight = sum(p['combined_weight'] for p in shared)
        constraint_sim = round(total_score / total_weight, 3) if total_weight > 0 else 0.0
    else:
        constraint_sim = 0.0

    # 法则属性推断（仅在有共同局限性时）
    law_attr = infer_law_attribute(shared, text_a, text_b) if shared else '无共同局限性，法则属性未识别'

    # 认知层级基于约束相似度（更严格）
    level = _cognitive_level(constraint_sim)
    is_analogy = constraint_sim >= threshold

    return {
        'overall_similarity': round(overall_sim, 3),
        'constraint_similarity': constraint_sim,
        'shared_limitations': shared,
        'implied_law_attribute': law_attr,
        'cognitive_level': level,
        'is_analogy': is_analogy,
        'constraints_a': constraints_a,
        'constraints_b': constraints_b,
    }


def compare_against_candidates(text: str, db_path: str = None, top_n: int = 5) -> List[Dict]:
    """
    将给定文本与候选库中所有候选进行类比比较，返回 top_n 最相似者。

    每项结果：{'candidate_id', 'title', 'similarity', 'cognitive_level', 'implied_law_attribute'}
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from candidate_store import CandidateStore

    store = CandidateStore(db_path=db_path)
    candidates = store.query()

    results = []
    for cand in candidates:
        cand_text = f"{cand.get('title', '')} {cand.get('description', '')} {cand.get('improvement_direction', '')}"
        result = compare(text, cand_text)
        results.append({
            'candidate_id': cand['id'],
            'title': cand['title'],
            'candidate_type': cand['type'],
            'constraint_similarity': result['constraint_similarity'],
            'overall_similarity': result['overall_similarity'],
            'cognitive_level': result['cognitive_level'],
            'implied_law_attribute': result['implied_law_attribute'],
            'is_analogy': result['is_analogy'],
        })

    results.sort(key=lambda x: x['constraint_similarity'], reverse=True)
    return results[:top_n]


# ─── 输出格式化 ───────────────────────────────────────────────────────────────

def format_result(result: Dict, label_a: str = 'A', label_b: str = 'B') -> str:
    lines = []
    lines.append('=' * 70)
    lines.append('类比分析结果')
    lines.append('=' * 70)
    lines.append(f"认知层级：{result['cognitive_level']}")
    lines.append(f"是否构成类比：{'✓ 是' if result['is_analogy'] else '✗ 否'}")
    lines.append(f"约束层相似度：{result['constraint_similarity']:.3f}  （整体字面相似度：{result['overall_similarity']:.3f}）")
    lines.append(f"隐含法则属性：{result['implied_law_attribute']}")

    if result['shared_limitations']:
        lines.append(f"\n共同局限性（{len(result['shared_limitations'])} 对，仅显示前 5）：")
        for i, pair in enumerate(result['shared_limitations'][:5], 1):
            lines.append(f"  [{i}] 相似度 {pair['similarity']:.3f}  权重 {pair['combined_weight']:.2f}")
            lines.append(f"    {label_a}：{pair['phrase_a'][:60]}")
            lines.append(f"    {label_b}：{pair['phrase_b'][:60]}")
    else:
        lines.append('\n未找到共同局限性。')

    lines.append(f"\n提取的约束数：{label_a}={len(result['constraints_a'])}，{label_b}={len(result['constraints_b'])}")
    lines.append('=' * 70)
    return '\n'.join(lines)


def format_candidates_result(results: List[Dict]) -> str:
    lines = []
    lines.append('=' * 70)
    lines.append('与候选库的类比比较结果')
    lines.append('=' * 70)
    if not results:
        lines.append('候选库为空或无匹配。')
    else:
        for i, r in enumerate(results, 1):
            mark = '✓' if r['is_analogy'] else '·'
            lines.append(
                f"  {mark} [{i}] {r['candidate_id'][:28]}  "
                f"约束相似度={r['constraint_similarity']:.3f}  {r['cognitive_level']}"
            )
            lines.append(f"      标题：{r['title'][:55]}")
            lines.append(f"      法则：{r['implied_law_attribute'][:55]}")
    lines.append('=' * 70)
    return '\n'.join(lines)


# ─── 命令行接口 ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='类比识别工具（本原展开论：局限性相同 = 类比）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 比较两段描述
  python3 analogy_finder.py "梦境中感官隔离，法则约束松弛，认同不稳定" \\
                             "想象中起点可理解性约束推演范围，法则未完全松弛"

  # 查看提取的约束（详细模式）
  python3 analogy_finder.py --verbose "描述A" "描述B"

  # 与候选库比较
  python3 analogy_finder.py --against-candidates "新观察：类比是局限性相同的识别过程"

  # 输出 JSON
  python3 analogy_finder.py --json "描述A" "描述B"
        """,
    )
    parser.add_argument('texts', nargs='*', help='待比较的两段描述（位置参数）')
    parser.add_argument('--against-candidates', metavar='TEXT', help='与候选库中所有候选进行类比比较')
    parser.add_argument('--top', type=int, default=5, help='候选库比较时返回前 N 个（默认 5）')
    parser.add_argument('--threshold', type=float, default=0.10, help='类比判定阈值（默认 0.10）')
    parser.add_argument('--verbose', action='store_true', help='显示全部提取的约束短语')
    parser.add_argument('--json', action='store_true', dest='output_json', help='输出 JSON 格式')
    parser.add_argument('--llm', action='store_true',
                        help='使用 LLM 增强（需要 ANTHROPIC_API_KEY；失败时自动回退到本地词汇匹配）')

    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).parent))

    def _do_compare(text_a, text_b):
        if args.llm:
            try:
                from llm_analogizer import compare as llm_compare
                result = llm_compare(text_a, text_b)
                result['_mode'] = 'llm'
                return result
            except Exception as e:
                print(f"[警告] LLM 调用失败（{e}），回退到本地词汇匹配", file=sys.stderr)
        return compare(text_a, text_b, threshold=args.threshold)

    if args.against_candidates:
        if args.llm:
            try:
                from llm_analogizer import compare_against_candidates as llm_cac
                results = llm_cac(args.against_candidates, top_n=args.top)
            except Exception as e:
                print(f"[警告] LLM 调用失败（{e}），回退到本地词汇匹配", file=sys.stderr)
                results = compare_against_candidates(args.against_candidates, top_n=args.top)
        else:
            results = compare_against_candidates(args.against_candidates, top_n=args.top)

        if args.output_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_candidates_result(results))

    elif len(args.texts) >= 2:
        text_a, text_b = args.texts[0], args.texts[1]
        result = _do_compare(text_a, text_b)

        if args.output_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result.get('_mode') == 'llm':
                from llm_analogizer import format_compare_result
                print(format_compare_result(result))
            else:
                print(format_result(result, label_a='A', label_b='B'))
                if args.verbose:
                    print('\n── A 的全部约束 ──')
                    for c in result['constraints_a']:
                        print(f"  [{c['weight']:.1f}] {c['phrase'][:70]}")
                    print('\n── B 的全部约束 ──')
                    for c in result['constraints_b']:
                        print(f"  [{c['weight']:.1f}] {c['phrase'][:70]}")

    else:
        parser.print_help()
