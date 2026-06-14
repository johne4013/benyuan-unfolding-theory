from pathlib import Path

import paths


def test_env_var_override(monkeypatch, tmp_path):
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    assert paths.continuity_root() == tmp_path
    assert paths.runtime_dir() == tmp_path / "runtime"


def test_repo_root_fallback(monkeypatch):
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    root = paths.continuity_root()
    # 仓库根目录必须包含 runtime/ 与 scripts/（或兜底到历史默认位置）
    assert (root / "runtime").is_dir() or str(root).endswith("continuity")


def test_repo_root_matches_this_repo(monkeypatch):
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    repo = Path(__file__).resolve().parent.parent
    if (repo / "runtime").is_dir():
        assert paths.continuity_root() == repo
