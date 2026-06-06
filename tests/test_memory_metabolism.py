"""Tests for MemoryMetabolismScanner (scripts/memory_metabolism.py)."""

from memory_metabolism import MemoryMetabolismScanner


def make_scanner(tmp_path):
    # Create a fake runtime dir with some .md files
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "reflection.md").write_text("x" * 1024 * 50, encoding="utf-8")  # 50KB
    (runtime / "memory.md").write_text("small content", encoding="utf-8")
    (runtime / "HOPE_STATE.md").write_text("# Hope", encoding="utf-8")
    (runtime / "index.md").write_text("# Index", encoding="utf-8")
    return MemoryMetabolismScanner(runtime_dir=str(runtime))


def test_scan_file_sizes_returns_list(tmp_path):
    scanner = make_scanner(tmp_path)
    results = scanner.scan_file_sizes()
    assert isinstance(results, list)


def test_scan_stale_files_returns_list(tmp_path):
    scanner = make_scanner(tmp_path)
    results = scanner.scan_stale_files()
    assert isinstance(results, list)


def test_self_alignment_passes_with_hope_and_index(tmp_path):
    scanner = make_scanner(tmp_path)
    result = scanner.self_alignment_check()
    # HOPE_STATE.md and index.md exist, so those checks pass
    checks_by_name = {c["name"]: c["ok"] for c in result["checks"]}
    assert checks_by_name.get("index.md exists") is True
    assert checks_by_name.get("HOPE_STATE.md exists") is True


def test_scan_returns_overall(tmp_path):
    scanner = make_scanner(tmp_path)
    report = scanner.scan()
    assert report["overall"] in ("healthy", "needs_attention", "critical")


def test_format_report_is_string(tmp_path):
    scanner = make_scanner(tmp_path)
    report = scanner.scan()
    text = scanner.format_report(report)
    assert isinstance(text, str) and len(text) > 0
