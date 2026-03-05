# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Diffinity is a CLI tool for semantic and textual diffing of configuration files across multiple application runs. It compares files in two directories, using semantic diff for structured formats (JSON, INI) and text diff for others.

## Installation & Running

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
diffinity <dir1> <dir2> [options]
```

## CLI Usage

```bash
# Compare specific files
diffinity dir1/ dir2/ --includelist file1.json file2.ini

# Compare by file suffix patterns (replaces dir basenames in paths)
diffinity dir1/ dir2/ --includepatterns .json .ini

# Options
--output report.html     # Export to HTML or TXT
--style compact|verbose  # Output verbosity
--ignore-paths           # Obfuscate filesystem paths in output
```

## Architecture

Four core modules with clean separation of concerns:

- **`cli.py`** — Argument parsing (`parse_args()`) and `main()` entry point
- **`engine.py`** — Main orchestrator (`run_diff()`): constructs file pairs, invokes parsing, formats/prints output via `rich`
- **`fileio.py`** — File I/O and diff strategy routing: `.json`/`.ini` → semantic diff (order-independent); others → plain unified diff; `sanitize_paths()` for path obfuscation
- **`report.py`** — Export to `.txt` or `.html`

### Key Design Decisions

- **Semantic diff for JSON/INI**: Files are parsed into dicts and compared as sorted text, so key order differences are ignored.
- **Pattern-based file matching** (`--includepatterns`): The basename of each input directory is substituted for the suffix pattern to locate matching files across both dirs.
- `rich` is the only non-stdlib dependency, used for all terminal output coloring.

## Versioning

Uses `bumpversion` to update version across `pyproject.toml`, `diffinity/__init__.py`, and `README.md`:

```bash
bumpversion patch  # or minor, major
```

## No Tests or Linting Configured

There is currently no test suite, CI, or linting tooling set up. The `.gitignore` includes entries for `pytest`, `ruff`, and `mypy`, suggesting these may be added in the future.
