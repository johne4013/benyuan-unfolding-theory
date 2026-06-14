#!/usr/bin/env python3
"""
paths.py — continuity 根目录统一解析

所有脚本的默认读写位置由本模块统一决定，解析顺序：

  1. 调用方显式传入的路径参数（各脚本自身处理，优先级最高）
  2. 环境变量 FAVA_CONTINUITY_ROOT
  3. 本仓库根目录（scripts/ 的上一级，需存在 runtime/ 目录）
  4. ~/.hermes/continuity（历史默认位置，兜底）

这样脚本无论在本机 Hermes 环境、仓库克隆位置还是 CI 中运行，
都会把数据写到正确的 continuity 根目录下。
"""

import os
from pathlib import Path

ENV_VAR = "FAVA_CONTINUITY_ROOT"
LEGACY_ROOT = "~/.hermes/continuity"


def continuity_root() -> Path:
    """返回 continuity 根目录（含 core/ runtime/ archive/ 的目录）。"""
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env).expanduser()

    repo = Path(__file__).resolve().parent.parent
    if (repo / "runtime").is_dir():
        return repo

    return Path(LEGACY_ROOT).expanduser()


def runtime_dir() -> Path:
    """返回 runtime/ 目录。"""
    return continuity_root() / "runtime"
