#!/usr/bin/env python3
"""
rename_agent.py — 一键替换协同节点 / 运行环境名称

本仓库默认使用 "Fava / fava / 小蚕豆" 作为 AI 协同节点名称，
"Hermes / hermes" 作为运行环境名称。克隆后你可以一条命令把它们
替换为你自己的 agent 名称，让这套理论核心 + 治理框架 + 任务技能
直接服务于你自己的 agent。

替换范围：仓库内所有 .md / .py 文本（跳过 .git、__pycache__、本脚本自身），
以及文件名中含 fava / hermes 的文件。

用法：
  # 仅预览将发生的改动（不写文件，默认）
  python3 scripts/rename_agent.py --node 小智

  # 实际执行替换
  python3 scripts/rename_agent.py --node 小智 --apply

  # 同时替换运行环境名 Hermes
  python3 scripts/rename_agent.py --node 小智 --runtime 小智运行时 --apply

说明：
- --node    替换协同节点名（Fava / fava / 小蚕豆）→ 你的名称
- --runtime 可选，替换运行环境名（Hermes / hermes）→ 你的名称
- 环境变量 FAVA_CONTINUITY_ROOT（paths.py 使用）不会被改动，保持脚本可用。
- 替换后请运行 `python3 -m pytest tests/ -q` 确认工具链正常。
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".py"}


def build_rules(node, runtime):
    """返回 (文本替换规则, 文件名替换规则)。顺序：先长后短，先中文后英文大小写。"""
    text_rules = []
    name_rules = []
    if node:
        # 中文昵称优先，再大写、小写
        text_rules += [("小蚕豆", node), ("Fava", node), ("fava", node)]
        name_rules += [("fava", node)]
    if runtime:
        text_rules += [("Hermes", runtime), ("hermes", runtime)]
        name_rules += [("hermes", runtime)]
    return text_rules, name_rules


def iter_text_files():
    for p in REPO_ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix in TEXT_SUFFIXES and p.resolve() != SELF:
            yield p


def main():
    ap = argparse.ArgumentParser(description="替换仓库中的协同节点 / 运行环境名称")
    ap.add_argument("--node", required=True, help="新的协同节点名称（替换 Fava/fava/小蚕豆）")
    ap.add_argument("--runtime", default=None, help="可选：新的运行环境名称（替换 Hermes/hermes）")
    ap.add_argument("--apply", action="store_true", help="实际写入改动；不加则仅预览")
    args = ap.parse_args()

    text_rules, name_rules = build_rules(args.node, args.runtime)

    files_changed = 0
    total_replacements = 0
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        new = text
        for old, rep in text_rules:
            new = new.replace(old, rep)
        if new != text:
            n = sum(text.count(old) for old, _ in text_rules)
            total_replacements += n
            files_changed += 1
            print(f"  [文本] {path.relative_to(REPO_ROOT)} : {n} 处")
            if args.apply:
                path.write_text(new, encoding="utf-8")

    renames = []
    for path in REPO_ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts) or not path.is_file():
            continue
        new_name = path.name
        for old, rep in name_rules:
            new_name = new_name.replace(old, rep)
        if new_name != path.name:
            renames.append((path, path.with_name(new_name)))

    for src, dst in renames:
        print(f"  [重命名] {src.relative_to(REPO_ROOT)} -> {dst.name}")
        if args.apply:
            src.rename(dst)

    mode = "已执行" if args.apply else "预览（未写入）"
    print(f"\n{mode}：{files_changed} 个文件文本改动，共 {total_replacements} 处；{len(renames)} 个文件重命名。")
    if not args.apply:
        print("加 --apply 实际执行。执行后请运行：python3 -m pytest tests/ -q")
    else:
        print("完成。请运行：python3 -m pytest tests/ -q 确认工具链正常。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
