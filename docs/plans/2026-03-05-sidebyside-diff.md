# Side-by-Side Diff Display Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a side-by-side diff display mode using `rich.Table` as the new default style in diffinity.

**Architecture:** A new `_print_sidebyside(diff_lines, relpath_display)` function in `engine.py` parses unified diff lines and renders them as a two-column `rich.Table` (OLD / NEW). The `run_diff` orchestrator calls it when `style == "sidebyside"`. The CLI default changes from `"compact"` to `"sidebyside"`.

**Tech Stack:** Python stdlib, `rich` (already a dependency) — `rich.table.Table`, `rich.text.Text`, `rich.rule.Rule`, `rich.box`.

---

### Task 1: Update CLI to add `sidebyside` style

**Files:**
- Modify: `diffinity/cli.py:14`
- Test: `tests/test_cli.py:45` (existing test must be updated), `tests/test_cli.py` (new test)

**Step 1: Update the failing test for the new default**

In `tests/test_cli.py`, find `test_parse_args_defaults` and change the assertion:

```python
def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "a.json"])
    args = parse_args()
    assert args.output is None
    assert args.style == "sidebyside"   # was "compact"
    assert args.ignore_paths is False
```

Also add a new test for the `sidebyside` style:

```python
def test_parse_args_style_sidebyside(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "a.json", "--style", "sidebyside"]
    )
    args = parse_args()
    assert args.style == "sidebyside"
```

**Step 2: Run the tests to verify they fail**

```bash
pytest tests/test_cli.py::test_parse_args_defaults tests/test_cli.py::test_parse_args_style_sidebyside -v
```

Expected: `test_parse_args_defaults` FAILS (got `"compact"`), `test_parse_args_style_sidebyside` FAILS (invalid choice).

**Step 3: Update `cli.py`**

Change line 14 in `diffinity/cli.py`:

```python
parser.add_argument("--style", choices=["sidebyside", "compact", "verbose"], default="sidebyside", help="Output verbosity")
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cli.py -v
```

Expected: all PASS.

**Step 5: Commit**

```bash
git add diffinity/cli.py tests/test_cli.py
git commit -m "feat: add sidebyside as default style option"
```

---

### Task 2: Implement `_print_sidebyside` in `engine.py`

**Files:**
- Modify: `diffinity/engine.py`
- Test: `tests/test_engine.py` (new tests)

**Step 1: Write failing tests**

Add to `tests/test_engine.py`:

```python
def test_run_diff_sidebyside_no_crash_identical(tmp_path):
    """Side-by-side mode must not raise for identical files."""
    content = '{"key": "value"}'
    dir1, dir2 = _setup_dirs(tmp_path, {"a.json": content}, {"a.json": content})
    out = str(tmp_path / "out.txt")
    # Should not raise; identical files produce no table
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
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_engine.py::test_run_diff_sidebyside_no_crash_identical tests/test_engine.py::test_run_diff_sidebyside_no_crash_different tests/test_engine.py::test_run_diff_sidebyside_export_contains_diff_lines tests/test_engine.py::test_run_diff_sidebyside_missing_file -v
```

Expected: all FAIL (ValueError or TypeError — `sidebyside` not handled).

**Step 3: Implement `_print_sidebyside` in `engine.py`**

Add these imports at the top of `diffinity/engine.py`:

```python
from rich.table import Table
from rich.rule import Rule
import rich.box
```

Add the function after `_print_missing`:

```python
def _print_sidebyside(diff_lines, relpath_display):
    console.print(Rule(title=f"[bold cyan]{relpath_display}[/bold cyan]", style="cyan"))

    table = Table(
        box=rich.box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("OLD", header_style="bold red", ratio=1)
    table.add_column("NEW", header_style="bold green", ratio=1)

    PLACEHOLDER = Text("~~~", style="dim")

    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            continue
        elif line.startswith("@@"):
            # Hunk header: span-like separator using a dim full-width label
            hunk_text = Text(line, style="magenta")
            table.add_row(hunk_text, hunk_text)
        elif line.startswith("-"):
            table.add_row(Text(line, style="red"), PLACEHOLDER)
        elif line.startswith("+"):
            table.add_row(PLACEHOLDER, Text(line, style="green"))
        else:
            ctx = Text(line, style="dim")
            table.add_row(ctx, ctx)

    console.print(table)
    console.print()
```

**Step 4: Wire up `_print_sidebyside` in `run_diff`**

In `run_diff`, find the block starting at line 58 that calls `_print_header` and `_print_line`. Replace it so `sidebyside` is handled:

```python
        if any(line.startswith(("+", "-")) for line in diff_lines):
            results.append(f"▶ {relpath_display}")
            for line in diff_lines:
                results.append(line)

            if style == "sidebyside":
                _print_sidebyside(diff_lines, relpath_display)
            else:
                _print_header(relpath_display, style)
                for line in diff_lines:
                    if style == "compact" and not line.startswith(("+", "-")):
                        continue
                    _print_line(line, style)
                if style == "compact":
                    console.print()
                    results.append("")
        else:
            msg = f"✓ {relpath_display} (no differences)"
            console.print(Text(msg, style="dim"))
            results.append(msg)
```

Note: the `results.append` calls are moved before the style branch so exports always get raw unified diff lines regardless of terminal style.

**Step 5: Run all tests**

```bash
pytest tests/ -v
```

Expected: all PASS.

**Step 6: Commit**

```bash
git add diffinity/engine.py tests/test_engine.py
git commit -m "feat: add side-by-side diff display as default style"
```

---

### Task 3: Smoke test the full CLI end-to-end

**Step 1: Create two sample files and run diffinity**

```bash
mkdir -p /tmp/d1 /tmp/d2
echo '{"name": "alice", "role": "admin"}' > /tmp/d1/config.json
echo '{"name": "bob",   "role": "admin"}' > /tmp/d2/config.json
diffinity /tmp/d1 /tmp/d2 --includelist config.json
```

Expected: a two-column rich table with OLD on the left (red `-name: alice` row) and NEW on the right (green `+name: bob` row), `~~~` placeholder in the opposite column.

**Step 2: Verify compact still works**

```bash
diffinity /tmp/d1 /tmp/d2 --includelist config.json --style compact
```

Expected: the original compact output (no table, just colored `+`/`-` lines).

**Step 3: Clean up**

```bash
rm -rf /tmp/d1 /tmp/d2
```
