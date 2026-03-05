import os
import pytest
from diffinity.engine import run_diff

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _setup_dirs(tmp_path, files1, files2):
    """Create two run dirs with the given {relpath: content} dicts."""
    dir1 = tmp_path / "run1"
    dir2 = tmp_path / "run2"
    for rel, content in files1.items():
        p = dir1 / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    for rel, content in files2.items():
        p = dir2 / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return str(dir1), str(dir2)


def _run(dir1, dir2, out, **kwargs):
    run_diff(dir1, dir2, output_file=out, **kwargs)
    return open(out, encoding="utf-8").read()


# --- includelist tests ---

def test_run_diff_includelist_identical_files(tmp_path):
    content = '{"key": "value"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": content}, {"a.json": content})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.json"])
    assert "no differences" in result or "✓" in result


def test_run_diff_includelist_different_files_compact(tmp_path):
    dir1, dir2 = _setup_dirs(tmp_path, {"a.txt": "line one\n"}, {"a.txt": "line TWO\n"})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"], style="compact")
    assert any(l.startswith("+") or l.startswith("-") for l in result.splitlines()
               if not l.startswith(("+++", "---")))
    assert "@@" not in result


def test_run_diff_includelist_different_files_verbose(tmp_path):
    dir1, dir2 = _setup_dirs(tmp_path, {"a.txt": "line one\n"}, {"a.txt": "line TWO\n"})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"], style="verbose")
    assert "@@" in result


def test_run_diff_includelist_missing_file_in_dir1(tmp_path):
    dir1, dir2 = _setup_dirs(tmp_path, {}, {"a.txt": "content\n"})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"])
    assert "[MISSING]" in result or "⚠" in result


def test_run_diff_includelist_missing_file_in_dir2(tmp_path):
    dir1, dir2 = _setup_dirs(tmp_path, {"a.txt": "content\n"}, {})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"])
    assert "[MISSING]" in result or "⚠" in result


# --- includepatterns tests ---

def test_run_diff_includepatterns_flat_files(tmp_path):
    # Pattern "_config.json" → run1_config.json in dir run1/, run2_config.json in run2/
    content = '{"key": "value"}'
    dir1 = tmp_path / "run1"
    dir2 = tmp_path / "run2"
    dir1.mkdir()
    dir2.mkdir()
    (dir1 / "run1_config.json").write_text(content, encoding="utf-8")
    (dir2 / "run2_config.json").write_text(content, encoding="utf-8")
    out = str(tmp_path / "out.txt")
    result = _run(str(dir1), str(dir2), out, includepatterns=["_config.json"])
    assert "no differences" in result or "✓" in result


def test_run_diff_includepatterns_with_subdir(tmp_path):
    # Pattern "subdir/_notes.txt" → subdir/run1_notes.txt in dir1, subdir/run2_notes.txt in dir2
    content = "notes content\n"
    dir1 = tmp_path / "run1"
    dir2 = tmp_path / "run2"
    (dir1 / "subdir").mkdir(parents=True)
    (dir2 / "subdir").mkdir(parents=True)
    (dir1 / "subdir" / "run1_notes.txt").write_text(content, encoding="utf-8")
    (dir2 / "subdir" / "run2_notes.txt").write_text(content, encoding="utf-8")
    out = str(tmp_path / "out.txt")
    result = _run(str(dir1), str(dir2), out, includepatterns=["subdir/_notes.txt"])
    assert "no differences" in result or "✓" in result


# --- error cases ---

def test_run_diff_no_includelist_or_patterns_raises(tmp_path):
    dir1, dir2 = _setup_dirs(tmp_path, {}, {})
    out = str(tmp_path / "out.txt")
    with pytest.raises(ValueError):
        run_diff(dir1, dir2, output_file=out)


# --- output file tests ---

def test_run_diff_output_txt_written(tmp_path):
    content = '{"key": "value"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": content}, {"a.json": content})
    out = str(tmp_path / "out.txt")
    run_diff(dir1, dir2, includelist=["a.json"], output_file=out)
    assert os.path.exists(out)


def test_run_diff_output_html_written(tmp_path):
    content = '{"key": "value"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": content}, {"a.json": content})
    out = str(tmp_path / "out.html")
    run_diff(dir1, dir2, includelist=["a.json"], output_file=out)
    assert os.path.exists(out)
    assert "<pre" in open(out, encoding="utf-8").read()


# --- ignore_paths flag ---

def test_run_diff_ignore_paths_flag(tmp_path):
    # Only difference is the path value — with ignore_paths it should be sanitized to no-diff
    f1 = '{"log": "/var/log/app.log", "name": "myapp"}'
    f2 = '{"log": "/var/log/other.log", "name": "myapp"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": f1}, {"a.json": f2})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.json"], ignore_paths=True)
    assert "no differences" in result or "✓" in result


# --- multiple files ---

def test_run_diff_multiple_files_in_includelist(tmp_path):
    same = '{"key": "value"}'
    diff1 = '{"key": "value1"}'
    diff2 = '{"key": "value2"}'
    dir1, dir2 = _setup_dirs(
        tmp_path,
        {"a.json": same, "b.json": same, "c.json": diff1},
        {"a.json": same, "b.json": same, "c.json": diff2},
    )
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.json", "b.json", "c.json"])
    lines = result.splitlines()
    no_diff_count = sum(1 for l in lines if "no differences" in l or (l.startswith("✓")))
    assert no_diff_count == 2
    assert any(l.startswith("+") or l.startswith("-") for l in lines if not l.startswith(("+++", "---")))


# --- sidebyside style tests ---

def test_run_diff_sidebyside_no_crash_identical(tmp_path):
    """Side-by-side mode must not raise for identical files."""
    content = '{"key": "value"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": content}, {"a.json": content})
    out = str(tmp_path / "out.txt")
    run_diff(dir1, dir2, includelist=["a.json"], output_file=out, style="sidebyside")


def test_run_diff_sidebyside_no_crash_different(tmp_path):
    """Side-by-side mode must not raise for different files."""
    dir1, dir2 = _setup_dirs(tmp_path, {"a.txt": "old line\n"}, {"a.txt": "new line\n"})
    out = str(tmp_path / "out.txt")
    run_diff(dir1, dir2, includelist=["a.txt"], output_file=out, style="sidebyside")


def test_run_diff_sidebyside_export_contains_diff_lines(tmp_path):
    """The txt export must still contain raw unified diff lines even in sidebyside mode."""
    dir1, dir2 = _setup_dirs(tmp_path, {"a.txt": "old line\n"}, {"a.txt": "new line\n"})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"], style="sidebyside")
    # Export captures raw unified diff lines regardless of terminal style
    assert any(l.startswith("+") or l.startswith("-") for l in result.splitlines()
               if not l.startswith(("+++", "---")))


def test_run_diff_sidebyside_missing_file(tmp_path):
    """Missing file warning must still appear in sidebyside mode."""
    dir1, dir2 = _setup_dirs(tmp_path, {}, {"a.txt": "content\n"})
    out = str(tmp_path / "out.txt")
    result = _run(dir1, dir2, out, includelist=["a.txt"], style="sidebyside")
    assert "[MISSING]" in result or "⚠" in result
