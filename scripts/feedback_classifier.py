#!/usr/bin/env python3
"""
反馈分类脚本
自动将反馈分类为：TEMPORARY / PATTERN / ANOMALY / ENHANCEMENT
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

class FeedbackClassifier:
    """分类反馈并标记为理论演化候选"""

    PATTERN_SIMILARITY_THRESHOLD = 0.15

    def __init__(self, candidate_manager=None):
        # 可选注入 EvolutionCandidateManager，用于跨任务 PATTERN 关联
        self._candidate_manager = candidate_manager

        # 关键词定义
        self.anomaly_indicators = [
            '理论失败', '预测失败', '违反', '出乎预料', '意外',
            '应该失败但成功', '应该成功但失败', '违反约束但工作',
            '论证不可能',
        ]

        self.pattern_indicators = [
            '多个任务', '重复', '总是', '每次', '经常', '多次', '多个场景',
        ]

        self.enhancement_indicators = [
            '可以', '建议', '改进', '优化', '更好', '扩展', '补充',
        ]

    def classify_feedback(self, feedback_dict):
        """分类一条反馈"""

        description = feedback_dict.get('observation', '').lower() + ' ' + \
                     feedback_dict.get('limitation', '').lower() + ' ' + \
                     feedback_dict.get('suggestion', '').lower()

        # 检查异常信号
        if self._contains_keywords(description, self.anomaly_indicators):
            return 'ANOMALY'

        # 检查模式信号
        if self._contains_keywords(description, self.pattern_indicators):
            # 检查这个问题是否重复出现
            if self._is_repeated_pattern(feedback_dict):
                return 'PATTERN'

        # 检查增强信号
        if self._contains_keywords(description, self.enhancement_indicators):
            # 只在以下情况排除：反馈表现出对框架本身的负面评价或框架失效
            # 而不是仅仅描述技术限制。"无法"通常是中性的技术描述，不代表框架失效。
            problem_phrases = [
                '存在问题',
                '发现问题',
                '框架失败',
                '理论失败',
                '不适用',
                '完全错误',
            ]
            has_actual_problem = any(phrase in description for phrase in problem_phrases)
            if not has_actual_problem:
                return 'ENHANCEMENT'

        # 默认为临时反馈
        return 'TEMPORARY'

    def _validate_feedback_structure(self, feedback_dict: dict) -> tuple:
        """验证反馈的数据结构完整性

        返回：(is_valid, error_message)
        """
        required_fields = ['task_id', 'task_name', 'observation', 'limitation', 'suggestion']
        missing_fields = [f for f in required_fields if f not in feedback_dict or not feedback_dict[f]]

        if missing_fields:
            return False, f"缺少必需字段：{', '.join(missing_fields)}"

        return True, None

    def _contains_keywords(self, text, keywords):
        """检查文本是否包含关键词"""
        return any(kw in text for kw in keywords)

    def _is_repeated_pattern(self, feedback_dict):
        """检查是否是重复出现的模式"""
        # 在实际应用中，这里应该查询历史反馈
        # 目前简单地检查描述中是否明确说了"重复"
        description = feedback_dict.get('observation', '').lower()
        repeat_keywords = ['多个任务', '重复', '总是', '每次', '经常', '多次']
        return any(kw in description for kw in repeat_keywords)

    def generate_candidate(self, feedback_dict, classification):
        """根据反馈生成理论演化候选"""

        if classification == 'TEMPORARY':
            return None  # 临时反馈不生成候选

        candidate = {
            'id': f"candidate-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'type': classification,
            'priority': self._determine_priority(classification),
            'source_feedback': feedback_dict.get('task_id', 'unknown'),
            'title': self._generate_title(feedback_dict, classification),
            'description': self._generate_description(feedback_dict),
            'status': 'CANDIDATE',
            'awaiting_review': True,
        }

        return candidate

    def _determine_priority(self, classification):
        """根据分类确定优先级"""
        priorities = {
            'ANOMALY': 'high',
            'PATTERN': 'medium',
            'ENHANCEMENT': 'low',
        }
        return priorities.get(classification, 'medium')

    def _generate_title(self, feedback_dict, classification):
        """生成候选标题"""
        observation = feedback_dict.get('observation', 'Feedback')
        if len(observation) > 50:
            return observation[:47] + '...'
        return observation

    def _generate_description(self, feedback_dict):
        """生成候选描述"""
        parts = []

        if feedback_dict.get('observation'):
            parts.append(f"观察：{feedback_dict['observation']}")

        if feedback_dict.get('limitation'):
            parts.append(f"理论局限：{feedback_dict['limitation']}")

        if feedback_dict.get('suggestion'):
            parts.append(f"建议改进：{feedback_dict['suggestion']}")

        return '\n'.join(parts)

    def save_candidate(self, candidate, output_dir=None):
        """保存理论演化候选"""

        if not candidate:
            return None

        if output_dir is None:
            from paths import runtime_dir
            output_dir = runtime_dir() / "evolution_candidates"
        output_path = Path(output_dir).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)

        candidate_file = output_path / f"{candidate['id']}-{candidate['type'].lower()}.json"
        with open(candidate_file, 'w', encoding='utf-8') as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)

        return str(candidate_file)

    def process_feedback_file(self, feedback_file_path):
        """处理一个反馈文件"""

        with open(feedback_file_path, 'r', encoding='utf-8') as f:
            feedback = json.load(f)

        is_valid, error_msg = self._validate_feedback_structure(feedback)
        if not is_valid:
            return {
                'feedback_file': str(feedback_file_path),
                'classification': 'INVALID',
                'priority': None,
                'candidate_generated': False,
                'candidate_file': None,
                'validation_error': error_msg,
            }

        classification = self.classify_feedback(feedback)

        # P1.2 跨任务 PATTERN 关联：若 PATTERN 且有候选管理器，优先合并到已有 PATTERN 候选
        existing_pattern_id = None
        if classification == 'PATTERN' and self._candidate_manager is not None:
            existing_pattern_id = self._find_similar_pattern(feedback)

        if existing_pattern_id:
            evidence_task = feedback.get('task_id', 'unknown')
            evidence_desc = (
                f"{feedback.get('observation', '')} | {feedback.get('limitation', '')}"
            )
            self._candidate_manager.add_evidence(existing_pattern_id, evidence_task, evidence_desc)
            return {
                'feedback_file': str(feedback_file_path),
                'classification': classification,
                'priority': self._determine_priority(classification),
                'candidate_generated': False,
                'candidate_file': None,
                'evidence_added_to': existing_pattern_id,
            }

        candidate = self.generate_candidate(feedback, classification)

        result = {
            'feedback_file': str(feedback_file_path),
            'classification': classification,
            'priority': self._determine_priority(classification) if classification != 'TEMPORARY' else None,
            'candidate_generated': candidate is not None,
            'candidate_file': None,
        }

        if candidate:
            candidate_file = self.save_candidate(candidate)
            result['candidate_file'] = candidate_file

        return result

    def _find_similar_pattern(self, feedback: dict) -> str:
        """
        在已有 PATTERN 候选中查找与当前反馈相似的候选。
        若相似度超过阈值，返回该候选 ID；否则返回 None。
        """
        try:
            existing = self._candidate_manager.list_candidates(
                candidate_type='PATTERN', status='CANDIDATE'
            )
        except Exception:
            return None

        feedback_text = (
            feedback.get('observation', '') + ' ' +
            feedback.get('limitation', '') + ' ' +
            feedback.get('suggestion', '')
        )

        best_id = None
        best_score = 0.0

        for cand in existing:
            cand_text = (
                cand.get('title', '') + ' ' +
                cand.get('description', '') + ' ' +
                cand.get('improvement_direction', '')
            )
            score = self._compute_similarity(feedback_text, cand_text)
            if score > best_score:
                best_score = score
                best_id = cand.get('id')

        if best_score >= self.PATTERN_SIMILARITY_THRESHOLD:
            return best_id
        return None

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的关键词相似度（字级二元组 Jaccard 系数）"""
        stopwords = {
            '的', '了', '在', '是', '有', '和', '也', '都', '不', '这', '对', '于',
            '与', '其', '为', '以', '及', '但', '从', '而', '中', '到', '被', '将',
            '能', '会', '应该', '没有', '可以', '一个', '进行',
        }

        def tokenize(text):
            tokens = set()
            words = re.findall(r'[一-鿿]+|[a-zA-Z]{2,}', text.lower())
            for word in words:
                if word not in stopwords and len(word) >= 2:
                    tokens.add(word)
                    # 汉字二元组，提高短语粒度匹配
                    for i in range(len(word) - 1):
                        bigram = word[i:i+2]
                        if bigram not in stopwords:
                            tokens.add(bigram)
            return tokens

        t1 = tokenize(text1)
        t2 = tokenize(text2)
        if not t1 or not t2:
            return 0.0
        intersection = len(t1 & t2)
        union = len(t1 | t2)
        return intersection / union if union > 0 else 0.0

    def print_result(self, result):
        """美化打印分类结果"""
        print(f"\n反馈分类结果")
        print(f"{'='*60}")
        print(f"反馈文件：{result['feedback_file'].split('/')[-1]}")
        print(f"分类：{result['classification']}")
        if result['priority']:
            print(f"优先级：{result['priority'].upper()}")
        print(f"生成候选：{'是' if result['candidate_generated'] else '否'}")
        if result['candidate_file']:
            print(f"候选文件：{result['candidate_file'].split('/')[-1]}")
        print(f"{'='*60}\n")


# 使用示例
if __name__ == '__main__':
    import sys

    classifier = FeedbackClassifier()

    if len(sys.argv) > 1:
        # 如果提供了文件路径，处理该文件
        feedback_file = sys.argv[1]
        result = classifier.process_feedback_file(feedback_file)
        classifier.print_result(result)
    else:
        # 演示用法
        print("反馈分类脚本演示")
        print("="*60)

        # 演示 1：ANOMALY
        feedback1 = {
            'task_id': 'task-001',
            'observation': '理论预期约束满足就可以执行，但违反约束后仍然成功执行',
            'limitation': '理论无法解释这种现象',
            'suggestion': '需要补充关于动态约束的理论'
        }
        result1 = classifier.process_feedback_file.__self__ if hasattr(
            classifier.process_feedback_file, '__self__') else None

        classification1 = classifier.classify_feedback(feedback1)
        print(f"\n例 1 分类结果：{classification1}")
        if classification1 != 'TEMPORARY':
            candidate1 = classifier.generate_candidate(feedback1, classification1)
            print(f"  → 生成候选：{candidate1['type']}")
            print(f"  → 优先级：{candidate1['priority']}")

        # 演示 2：PATTERN
        feedback2 = {
            'task_id': 'task-002',
            'observation': '在多个任务中都出现了展开和能量的混淆',
            'limitation': '防漂移规则不够清晰',
            'suggestion': '需要补充常见混淆的明确示例'
        }

        classification2 = classifier.classify_feedback(feedback2)
        print(f"\n例 2 分类结果：{classification2}")
        if classification2 != 'TEMPORARY':
            candidate2 = classifier.generate_candidate(feedback2, classification2)
            print(f"  → 生成候选：{candidate2['type']}")
            print(f"  → 优先级：{candidate2['priority']}")

        # 演示 3：TEMPORARY
        feedback3 = {
            'task_id': 'task-003',
            'observation': '今天网络不好，导致执行失败',
            'limitation': '这是环境问题，不是理论问题',
            'suggestion': '无需改理论'
        }

        classification3 = classifier.classify_feedback(feedback3)
        print(f"\n例 3 分类结果：{classification3}")

        print("\n" + "="*60)
