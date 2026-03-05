# Design: Side-by-Side Diff Display

**Date:** 2026-03-05
**Status:** Approved

## Overview

Add a side-by-side diff display mode to diffinity using `rich.Table`, making it the new default style. The existing `compact` and `verbose` styles are retained as fallback options.

## Architecture

### CLI Changes (`cli.py`)

- `--style` choices expand to `["sidebyside", "compact", "verbose"]`
- Default changes from `"compact"` to `"sidebyside"`

### Engine Changes (`engine.py`)

- Add `_print_sidebyside(diff_lines, relpath_display)` function
- `run_diff` calls `_print_sidebyside` when `style == "sidebyside"`, otherwise the existing per-line loop is unchanged

## Side-by-Side Renderer

`_print_sidebyside` parses unified diff lines and builds a `rich.Table` with two columns (OLD / NEW):

| Diff line type | Left column | Right column |
|---|---|---|
| `-` deletion | line text (red) | `~~~` placeholder (dim) |
| `+` addition | `~~~` placeholder (dim) | line text (green) |
| context | line text (dim) | line text (dim) |
| `@@` hunk header | full-width separator (magenta) | |
| `---` / `+++` | skipped | skipped |

- Table style: `rich.box.SIMPLE_HEAVY` (or similar clean box style)
- Column headers: `OLD` (red) and `NEW` (green)
- File header: `rich.Rule` or `Panel` showing the filename before the table
- Each cell is a `rich.Text` object with appropriate style

## Edge Cases

- **No differences**: prints `✓ filename (no differences)` in dim — no table rendered
- **Missing files**: yellow warning — no table rendered
- **Long lines**: `rich.Table` wraps within cells naturally
- **`--output` export**: unchanged — `results` list collects raw unified diff lines; exports remain as text/HTML

## Non-Goals

- Inline character-level highlighting (not in scope)
- Changes to the export/report format
