#!/usr/bin/env python3
"""
反馈格式转换工具
在 Markdown 和 JSON 格式之间自动转换反馈内容
消除格式转换的手动操作成本
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime


class FeedbackFormatConverter:
    """反馈格式转换器，支持 Markdown ↔ JSON 双向转换"""

    def __init__(self):
        self.required_fields = ['task_id', 'task_name', 'observation', 'limitation', 'suggestion']

    def markdown_to_json(self, markdown_content: str, output_file: str = None) -> Dict:
        """将 Markdown 格式的反馈转换为 JSON

        Args:
            markdown_content: Markdown 格式的反馈内容
            output_file: 可选，输出文件路径

        Returns:
            转换后的 JSON 字典
        """
        feedback_dict = {}

        # 提取 task_id（从文件名或内容中）
        task_id_match = re.search(r'task-\d+-w\d+-\d+', markdown_content)
        if task_id_match:
            feedback_dict['task_id'] = task_id_match.group()

        # 提取 task_name（从标题）
        title_match = re.search(r'#\s+(.+)', markdown_content)
        if title_match:
            feedback_dict['task_name'] = title_match.group(1).strip()

        # 提取各个观察维度
        observation_match = re.search(
            r'##\s+观察|\*\*观察：\*\*([^【]*?)(?=##|\*\*|$)',
            markdown_content,
            re.DOTALL
        )
        if observation_match:
            # 如果第一组匹配，使用第一组；否则查找整个内容
            text = observation_match.group(1) if observation_match.lastindex else markdown_content
            # 寻找"观察点 1" 或类似的内容
            obs_section = re.search(
                r'观察点\s+1.*?(?=观察点\s+2|###|$)',
                text,
                re.DOTALL
            )
            if obs_section:
                # 提取内容，去除标记符号
                obs_text = obs_section.group(0)
                obs_text = re.sub(r'^.*?：', '', obs_text, flags=re.MULTILINE)
                feedback_dict['observation'] = obs_text.strip()

        # 提取理论局限
        limitation_text = ""
        limitation_section = re.search(
            r'观察点\s+2.*?(?=观察点\s+3|###|$)',
            markdown_content,
            re.DOTALL
        )
        if limitation_section:
            limitation_text = limitation_section.group(0)
            limitation_text = re.sub(r'^.*?：', '', limitation_text, flags=re.MULTILINE)
            feedback_dict['limitation'] = limitation_text.strip()

        # 提取建议
        suggestion_text = ""
        suggestion_section = re.search(
            r'观察点\s+3.*?(?=##|$)',
            markdown_content,
            re.DOTALL
        )
        if suggestion_section:
            suggestion_text = suggestion_section.group(0)
            suggestion_text = re.sub(r'^.*?：', '', suggestion_text, flags=re.MULTILINE)
            feedback_dict['suggestion'] = suggestion_text.strip()

        # 如果上述方法未能提取，尝试更宽松的模式
        if 'observation' not in feedback_dict:
            # 查找 "观察：" 之后的内容
            obs = re.search(r'[观察].*?：(.*?)(?=[局限]|$)', markdown_content, re.DOTALL)
            if obs:
                feedback_dict['observation'] = obs.group(1).strip()[:200]

        if 'limitation' not in feedback_dict:
            lim = re.search(r'[局限].*?：(.*?)(?=[建议]|$)', markdown_content, re.DOTALL)
            if lim:
                feedback_dict['limitation'] = lim.group(1).strip()[:200]

        if 'suggestion' not in feedback_dict:
            sug = re.search(r'[建议].*?：(.*?)(?=$)', markdown_content, re.DOTALL)
            if sug:
                feedback_dict['suggestion'] = sug.group(1).strip()[:300]

        # 补充基本字段
        if 'task_id' not in feedback_dict:
            feedback_dict['task_id'] = 'unknown'
            print("警告：无法从内容中提取 task_id，使用 'unknown' 作为默认值", file=sys.stderr)
        if 'task_name' not in feedback_dict:
            feedback_dict['task_name'] = 'Unknown Task'

        # 验证和清理
        feedback_dict = self._validate_and_clean(feedback_dict)

        # 保存到文件（如指定）
        if output_file:
            self._save_json(feedback_dict, output_file)

        return feedback_dict

    def json_to_markdown(self, json_dict: Dict, output_file: str = None) -> str:
        """将 JSON 格式的反馈转换为 Markdown

        Args:
            json_dict: JSON 字典格式的反馈
            output_file: 可选，输出文件路径

        Returns:
            转换后的 Markdown 字符串
        """
        markdown_lines = []

        # 生成标题
        task_name = json_dict.get('task_name', 'Feedback')
        markdown_lines.append(f"# 执行反馈记录：{task_name}")
        markdown_lines.append("")

        # 生成基本信息
        task_id = json_dict.get('task_id', 'unknown')
        markdown_lines.append(f"**任务 ID：** {task_id}")
        markdown_lines.append(f"**任务名称：** {task_name}")
        markdown_lines.append(f"**执行日期：** {datetime.now().strftime('%Y-%m-%d')}")
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

        # 观察点 1
        markdown_lines.append("## 观察点 1：理论有效性")
        markdown_lines.append("")
        observation = json_dict.get('observation', '（未填写）')
        markdown_lines.append(observation)
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

        # 观察点 2
        markdown_lines.append("## 观察点 2：局限暴露")
        markdown_lines.append("")
        limitation = json_dict.get('limitation', '（未填写）')
        markdown_lines.append(limitation)
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

        # 建议
        markdown_lines.append("## 建议的改进方向")
        markdown_lines.append("")
        suggestion = json_dict.get('suggestion', '（未填写）')
        markdown_lines.append(suggestion)
        markdown_lines.append("")

        markdown_content = '\n'.join(markdown_lines)

        # 保存到文件（如指定）
        if output_file:
            self._save_markdown(markdown_content, output_file)

        return markdown_content

    def auto_convert(self, input_file: str, output_format: str = None) -> str:
        """自动检测输入格式并转换

        Args:
            input_file: 输入文件路径
            output_format: 输出格式（'json' 或 'markdown'），如未指定则自动选择

        Returns:
            输出文件的路径
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在：{input_file}")

        # 检测输入格式
        input_format = 'json' if input_file.endswith('.json') else 'markdown'

        # 确定输出格式
        if output_format is None:
            output_format = 'markdown' if input_format == 'json' else 'json'

        # 读取输入
        with open(input_file, 'r', encoding='utf-8') as f:
            if input_format == 'json':
                content = json.load(f)
            else:
                content = f.read()

        # 生成输出文件名
        stem = input_path.stem
        output_ext = '.json' if output_format == 'json' else '.md'
        output_file = str(input_path.parent / f"{stem}{output_ext}")

        # 转换
        if input_format == 'json' and output_format == 'markdown':
            self.json_to_markdown(content, output_file)
        elif input_format == 'markdown' and output_format == 'json':
            self.markdown_to_json(content, output_file)
        else:
            raise ValueError(f"不支持的转换：{input_format} → {output_format}")

        return output_file

    def _validate_and_clean(self, feedback_dict: Dict) -> Dict:
        """验证和清理反馈字典"""
        # 确保所有必需字段存在
        for field in self.required_fields:
            if field not in feedback_dict or not feedback_dict[field]:
                feedback_dict[field] = f"（{field} 未填写）"

        # 清理文本（去除多余空白）
        for key in self.required_fields:
            if isinstance(feedback_dict[key], str):
                feedback_dict[key] = ' '.join(feedback_dict[key].split())

        return feedback_dict

    def _save_json(self, feedback_dict: Dict, output_file: str) -> None:
        """保存为 JSON 文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_dict, f, indent=2, ensure_ascii=False)

        print(f"✓ 已保存 JSON：{output_file}")

    def _save_markdown(self, markdown_content: str, output_file: str) -> None:
        """保存为 Markdown 文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✓ 已保存 Markdown：{output_file}")

    def batch_convert(self, input_dir: str, input_format: str = 'markdown', output_format: str = 'json') -> list:
        """批量转换目录中的文件

        Args:
            input_dir: 输入目录
            input_format: 输入格式
            output_format: 输出格式

        Returns:
            转换成功的文件列表
        """
        input_path = Path(input_dir)
        ext = '.json' if input_format == 'json' else '.md'
        files = list(input_path.glob(f"*{ext}"))

        results = []
        failures = []
        for file in files:
            try:
                output = self.auto_convert(str(file), output_format)
                results.append(output)
            except Exception as e:
                print(f"✗ 转换失败 {file}：{str(e)}")
                failures.append(str(file))

        if failures:
            print(f"\n⚠ 批量转换完成，{len(failures)} 个文件失败，{len(results)} 个成功", file=sys.stderr)

        return results


# 命令行接口
if __name__ == '__main__':
    import sys

    converter = FeedbackFormatConverter()

    if len(sys.argv) < 2:
        print("反馈格式转换工具")
        print("=" * 70)
        print("\n使用方法：")
        print("  python feedback_format_converter.py <input_file> [output_format]")
        print("\n参数：")
        print("  input_file     输入文件路径（.json 或 .md）")
        print("  output_format  输出格式（可选，'json' 或 'markdown'）")
        print("\n例：")
        print("  python feedback_format_converter.py task-001-feedback.md")
        print("  python feedback_format_converter.py task-001-feedback.json markdown")
        print("\n" + "=" * 70)

    elif sys.argv[1] == '--batch':
        # 批量转换
        input_dir = sys.argv[2] if len(sys.argv) > 2 else 'runtime/practice_feedbacks'
        input_fmt = sys.argv[3] if len(sys.argv) > 3 else 'markdown'
        output_fmt = sys.argv[4] if len(sys.argv) > 4 else 'json'

        print(f"批量转换 {input_dir} 中的 {input_fmt} 文件为 {output_fmt}...")
        results = converter.batch_convert(input_dir, input_fmt, output_fmt)
        print(f"✓ 完成：{len(results)} 个文件")

    else:
        # 单文件转换
        input_file = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"正在转换：{input_file}")
        output_file = converter.auto_convert(input_file, output_format)
        print(f"✓ 成功！输出：{output_file}")
