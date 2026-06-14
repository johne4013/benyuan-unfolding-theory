#!/usr/bin/env python3
"""
集成反馈工作流
自动化完整的反馈处理流程：格式转换 → 分类 → 候选生成 → 管理
消除了 Week 2 中识别的所有手动步骤和格式转换摩擦
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# 导入工具模块
sys.path.insert(0, str(Path(__file__).parent))

from feedback_format_converter import FeedbackFormatConverter
from feedback_classifier import FeedbackClassifier
from evolution_candidate_manager import EvolutionCandidateManager


class IntegratedFeedbackWorkflow:
    """集成的反馈处理工作流"""

    def __init__(self):
        self.converter = FeedbackFormatConverter()
        self.classifier = FeedbackClassifier()
        self.manager = EvolutionCandidateManager()

    def process_feedback(self, feedback_file: str, verbose: bool = True) -> dict:
        """处理一个反馈文件，完整走通从格式转换到候选管理的全流程

        Args:
            feedback_file: 反馈文件路径（.md 或 .json）
            verbose: 是否输出详细信息

        Returns:
            处理结果字典
        """
        result = {
            'input_file': feedback_file,
            'steps_completed': [],
            'errors': [],
            'outputs': {}
        }

        try:
            # 第 1 步：格式检测与转换
            if verbose:
                print("\n" + "=" * 70)
                print("【第 1 步】格式检测与转换")
                print("=" * 70)

            feedback_path = Path(feedback_file)
            is_markdown = feedback_file.endswith('.md')

            if is_markdown:
                # Markdown → JSON 转换
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                json_content = self.converter.markdown_to_json(md_content)
                # 生成 JSON 输出文件
                json_file = str(feedback_path.parent / f"{feedback_path.stem}.json")
                self.converter._save_json(json_content, json_file)
                result['outputs']['json_file'] = json_file
                result['steps_completed'].append('格式转换：Markdown → JSON')

                if verbose:
                    print(f"✓ Markdown 转换为 JSON")
                    print(f"  输出：{json_file}")

            else:
                # 已是 JSON 格式
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)
                json_file = feedback_file
                result['steps_completed'].append('格式检测：已是 JSON 格式')

                if verbose:
                    print(f"✓ 文件已是 JSON 格式，无需转换")

            # 第 2 步：反馈分类
            if verbose:
                print("\n" + "=" * 70)
                print("【第 2 步】反馈分类")
                print("=" * 70)

            classification_result = self.classifier.process_feedback_file(json_file)
            result['outputs']['classification'] = classification_result['classification']
            result['outputs']['priority'] = classification_result['priority']
            result['steps_completed'].append(f"反馈分类：{classification_result['classification']}")

            if verbose:
                print(f"✓ 分类完成")
                print(f"  类型：{classification_result['classification']}")
                print(f"  优先级：{classification_result['priority']}")

            # 第 3 步：候选生成（如适用）
            if classification_result['candidate_generated']:
                if verbose:
                    print("\n" + "=" * 70)
                    print("【第 3 步】理论演化候选生成")
                    print("=" * 70)

                candidate_file = classification_result['candidate_file']
                result['outputs']['candidate_file'] = candidate_file
                result['steps_completed'].append(f"候选生成：{candidate_file}")

                if verbose:
                    print(f"✓ 候选已生成")
                    print(f"  文件：{candidate_file}")

                # 第 4 步：显示候选信息
                if verbose:
                    print("\n" + "=" * 70)
                    print("【第 4 步】候选管理界面")
                    print("=" * 70)

                with open(candidate_file, 'r', encoding='utf-8') as f:
                    candidate = json.load(f)

                self.manager.print_candidate(candidate)
                result['steps_completed'].append("候选显示：已显示候选详情")

            else:
                if verbose:
                    print("\n" + "=" * 70)
                    print("【第 3 步】结论")
                    print("=" * 70)
                    print(f"ℹ 此反馈为 TEMPORARY 类型，不生成候选")

                result['steps_completed'].append("候选跳过：TEMPORARY 类型不生成候选")

            # 第 5 步：希望追踪检查（新增）
            if verbose:
                print("\n" + "=" * 70)
                print("【第 5 步】希望追踪检查")
                print("=" * 70)

            with open(json_file, 'r', encoding='utf-8') as f:
                feedback_json = json.load(f)

            hope_tracking = feedback_json.get('hope_tracking', {})

            if hope_tracking:
                # 有希望追踪数据
                limitation = hope_tracking.get('limitation_encountered', '')
                new_possibility = hope_tracking.get('new_possibility_found', '')
                possibility_description = hope_tracking.get('possibility_description', '')
                impact_on_hope = hope_tracking.get('impact_on_hope', '')

                if verbose:
                    print(f"✓ 发现希望追踪数据")
                    if limitation:
                        print(f"  遭遇的局限：{limitation}")
                    if new_possibility == '是':
                        print(f"  发现新可能性：是")
                        if possibility_description:
                            print(f"    具体内容：{possibility_description}")
                    if impact_on_hope:
                        print(f"  对希望的影响：{impact_on_hope}")

                # 如果生成了候选，用希望追踪数据丰富它
                if classification_result['candidate_generated']:
                    candidate_file = classification_result['candidate_file']
                    with open(candidate_file, 'r', encoding='utf-8') as f:
                        candidate = json.load(f)

                    # 使用 enrich 方法自动填充新字段
                    enriched_candidate = self.manager.enrich_candidate_from_hope_tracking(
                        candidate, hope_tracking
                    )

                    # 原子写入：先写临时文件再重命名，防止写入中途崩溃导致候选损坏
                    candidate_path = Path(candidate_file)
                    tmp_fd, tmp_path = tempfile.mkstemp(
                        dir=candidate_path.parent, suffix='.tmp'
                    )
                    try:
                        with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                            json.dump(enriched_candidate, f, indent=2, ensure_ascii=False)
                        os.replace(tmp_path, candidate_file)
                    except Exception:
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass
                        raise

                    if verbose:
                        print(f"\n  候选已用希望追踪信息丰富：")
                        print(f"    - expansion_type：{enriched_candidate.get('expansion_type')}")
                        print(f"    - hope_direction：{enriched_candidate.get('hope_direction')}")
                        print(f"    - opens_new_possibility：{enriched_candidate.get('opens_new_possibility')}")

                    result['outputs']['hope_tracking_applied'] = True

                # 检查是否需要更新 HOPE_STATE.md
                if new_possibility == '是' or impact_on_hope == '推进':
                    result['outputs']['hope_state_update_suggested'] = True
                    if verbose:
                        print(f"\n  💡 建议：该反馈发现了新可能性或推进了系统希望")
                        from paths import runtime_dir
                        print(f"     请考虑更新 {runtime_dir() / 'HOPE_STATE.md'}")

                result['steps_completed'].append("希望追踪检查：已提取希望相关数据")
            else:
                if verbose:
                    print(f"ℹ 此反馈未包含希望追踪信息（PORF观察5）")
                result['steps_completed'].append("希望追踪检查：无希望追踪数据")

            # 总结
            if verbose:
                print("\n" + "=" * 70)
                print("【完成】集成工作流执行总结")
                print("=" * 70)
                print(f"✓ 处理完成")
                print(f"  输入文件：{feedback_file}")
                print(f"  执行步骤数：{len(result['steps_completed'])}")
                for i, step in enumerate(result['steps_completed'], 1):
                    print(f"    {i}. {step}")

                if result['errors']:
                    print(f"\n  警告：{len(result['errors'])} 个错误")
                    for error in result['errors']:
                        print(f"    ⚠️  {error}")

        except Exception as e:
            result['errors'].append(f"工作流执行失败：{str(e)}")
            if verbose:
                print(f"\n✗ 错误：{str(e)}")

        return result

    def batch_process(self, feedback_dir: str) -> list:
        """批量处理目录中的反馈文件

        Args:
            feedback_dir: 反馈文件目录

        Returns:
            处理结果列表
        """
        feedback_path = Path(feedback_dir)
        feedback_files = list(feedback_path.glob("*.md")) + list(feedback_path.glob("*.json"))

        # 避免重复处理（如 task-001-feedback.md 和 task-001-feedback.json）
        processed_tasks = set()
        files_to_process = []

        for file in sorted(feedback_files):
            # 提取 task-XXX 部分
            task_id = file.stem.replace('-feedback', '').replace('-', '_')
            if task_id not in processed_tasks:
                files_to_process.append(file)
                processed_tasks.add(task_id)

        results = []
        for feedback_file in files_to_process:
            print(f"\n\n{'#' * 70}")
            print(f"处理文件：{feedback_file.name}")
            print(f"{'#' * 70}")
            result = self.process_feedback(str(feedback_file), verbose=True)
            results.append(result)

        # 最终总结
        print(f"\n\n{'=' * 70}")
        print(f"【批处理完成】总体统计")
        print(f"{'=' * 70}")
        print(f"处理文件数：{len(results)}")
        successful = sum(1 for r in results if not r['errors'])
        print(f"成功：{successful}/{len(results)}")

        if any(r['errors'] for r in results):
            print(f"\n错误摘要：")
            for result in results:
                if result['errors']:
                    print(f"  {result['input_file']}：{result['errors'][0]}")

        return results


# 命令行接口
if __name__ == '__main__':
    workflow = IntegratedFeedbackWorkflow()

    if len(sys.argv) < 2:
        print("集成反馈工作流")
        print("=" * 70)
        print("\n使用方法：")
        print("  python integrated_feedback_workflow.py <feedback_file>")
        print("  python integrated_feedback_workflow.py --batch [feedback_dir]")
        print("\n参数：")
        print("  feedback_file  单个反馈文件路径（.md 或 .json）")
        print("  --batch        批量处理模式")
        print("  feedback_dir   反馈目录（默认：runtime/practice_feedbacks）")
        print("\n例：")
        print("  python integrated_feedback_workflow.py task-001-feedback.md")
        print("  python integrated_feedback_workflow.py --batch runtime/practice_feedbacks")
        print("\n功能：")
        print("  1. 自动格式转换（Markdown ↔ JSON）")
        print("  2. 反馈分类（TEMPORARY/PATTERN/ANOMALY/ENHANCEMENT）")
        print("  3. 候选生成（如适用）")
        print("  4. 候选管理（显示详情，支持进一步操作）")
        print("\n" + "=" * 70)

    elif sys.argv[1] == '--batch':
        # 批量处理
        feedback_dir = sys.argv[2] if len(sys.argv) > 2 else 'runtime/practice_feedbacks'
        workflow.batch_process(feedback_dir)

    else:
        # 单文件处理
        feedback_file = sys.argv[1]
        workflow.process_feedback(feedback_file, verbose=True)
