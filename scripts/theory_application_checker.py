#!/usr/bin/env python3
"""
任务理论适配检查脚本（TTAF）
在任务开始前，根据任务描述生成理论检视清单。

用法：
    python3 theory_application_checker.py "任务描述"
    python3 theory_application_checker.py "任务描述" --save
    python3 theory_application_checker.py "任务描述" --level engineering
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class TheoryApplicationChecker:
    """根据任务描述生成 TTAF（Task Theory Application Framework）检视清单"""

    # 任务层级关键词（检查顺序：从高优先级到低优先级，首次匹配即用）
    LEVEL_KEYWORDS = {
        "core": [
            "core/", "核心", "bootstrap", "soul", "identity",
            "theory.md", "concepts.md",
        ],
        "theory": [
            "理论", "概念", "本原", "展开属性", "法则属性",
            "连续性", "局限性", "希望", "主体", "认同",
        ],
        "subject": [
            "主体", "认同", "协同", "Hermes", "Fava",
            "判断", "价值", "信任",
        ],
        "engineering": [
            "脚本", "代码", "Python", "script", "函数",
            "数据库", "SQL", "测试", "API",
        ],
    }

    # TTAF 维度定义
    DIMENSIONS = {
        "D1": {"question": "这是什么类型的任务？", "depth": "简单确认"},
        "D2": {
            "question": "法则约束面：什么边界/规律使这个任务的结构成为可能？",
            "depth": "约束识别",
        },
        "D3": {
            "question": "展开面：在约束中可以生成哪些候选方案？",
            "depth": "方案生成",
        },
        "D4": {
            "question": "失败条件：哪些条件会导致执行失败？",
            "depth": "失败条件定义",
        },
        "D5": {
            "question": "理论对齐：当前任务与本原展开论哪个概念最相关？",
            "depth": "理论对齐检查",
        },
        "D6": {
            "question": "希望生成：任务完成后会打开什么新的可能性空间？",
            "depth": "希望生成",
        },
    }

    # 每个层级启用的维度
    LEVEL_DIMENSIONS = {
        "simple": ["D1"],
        "engineering": ["D1", "D2", "D3"],
        "subject": ["D1", "D2", "D3", "D4"],
        "theory": ["D1", "D2", "D3", "D4", "D5"],
        "core": ["D1", "D2", "D3", "D4", "D5", "D6"],
    }

    def detect_level(self, description: str) -> str:
        """根据任务描述关键词检测任务层级（首次匹配优先）"""
        for level in ("core", "theory", "subject", "engineering"):
            keywords = self.LEVEL_KEYWORDS[level]
            if any(kw in description for kw in keywords):
                return level
        return "simple"

    def generate_checklist(self, description: str, level: str = None) -> dict:
        """生成 TTAF 检视清单"""
        if level is None:
            level = self.detect_level(description)

        active_dims = self.LEVEL_DIMENSIONS.get(level, ["D1"])

        dimensions = {}
        for dim_key in active_dims:
            dim_def = self.DIMENSIONS[dim_key]
            # engineering 级别的 D1 使用"类型识别"而不是"简单确认"
            depth = dim_def["depth"]
            if dim_key == "D1" and level != "simple":
                depth = "类型识别"
            dimensions[dim_key] = {
                "question": dim_def["question"],
                "depth": depth,
                "answer": "",
            }

        checklist = {
            "task_description": description,
            "detected_level": level,
            "timestamp": datetime.now().isoformat(),
            "warning": None,
            "dimensions": dimensions,
            "notes": "根据关键词自动识别任务层级，请确认后填写各维度答案",
        }

        if level == "core":
            checklist["warning"] = (
                "⚠️ 涉及 core 层操作，需要personal显式批准后才可执行"
            )

        return checklist

    def format_checklist(self, checklist: dict) -> str:
        """将检视清单格式化为人类可读的文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("TTAF 任务理论适配检视清单")
        lines.append("=" * 60)

        if checklist.get("warning"):
            lines.append(f"\n{checklist['warning']}\n")

        lines.append(f"任务描述：{checklist['task_description']}")
        lines.append(f"检测层级：{checklist['detected_level'].upper()}")
        lines.append(f"生成时间：{checklist['timestamp']}")
        lines.append("")
        lines.append("--- 检视维度 ---")

        for dim_key, dim_val in checklist["dimensions"].items():
            lines.append(f"\n[{dim_key}] {dim_val['question']}")
            lines.append(f"  深度：{dim_val['depth']}")
            answer = dim_val.get("answer", "")
            lines.append(f"  答案：{answer if answer else '（待填写）'}")

        lines.append("")
        lines.append(f"注：{checklist['notes']}")
        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="TTAF 任务理论适配检视清单生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  python3 theory_application_checker.py "编写 Python 脚本处理数据"
  python3 theory_application_checker.py "修改 core/concepts.md" --save
  python3 theory_application_checker.py "优化 API 接口" --level engineering
""",
    )
    parser.add_argument("task_description", help="任务描述文本")
    parser.add_argument(
        "--save",
        action="store_true",
        help="将结果同时保存到 runtime/TTAF_latest.json",
    )
    parser.add_argument(
        "--level",
        choices=["simple", "engineering", "subject", "theory", "core"],
        default=None,
        help="手动指定任务层级（覆盖自动检测）",
    )

    args = parser.parse_args()

    checker = TheoryApplicationChecker()
    checklist = checker.generate_checklist(args.task_description, level=args.level)

    # 输出 JSON 到 stdout
    print(json.dumps(checklist, indent=2, ensure_ascii=False))

    if args.save:
        repo_root = Path(__file__).parent.parent
        runtime_dir = repo_root / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        output_path = runtime_dir / "TTAF_latest.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(checklist, f, indent=2, ensure_ascii=False)
        print(f"\n已保存到：{output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
