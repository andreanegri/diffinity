import os
from .fileio import parse_file
from .report import export_report
from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.rule import Rule
import rich.box

console = Console()

def run_diff(
    dir1, dir2,
    includelist=None,
    output_file=None,
    style="sidebyside",
    ignore_paths=False,
    includepatterns=None
):
    # Build list of (relpath1, relpath2) pairs to compare
    if includelist:
        files = [(entry.strip(), entry.strip()) for entry in includelist if entry.strip()]
    elif includepatterns:
        base1 = os.path.basename(os.path.normpath(dir1))
        base2 = os.path.basename(os.path.normpath(dir2))
        files = []
        for raw in includepatterns:
            raw = raw.strip()
            if not raw:
                continue
            subdir, _, suffix = raw.rpartition("/")
            file1 = f"{base1}{suffix}"
            file2 = f"{base2}{suffix}"
            relpath1 = os.path.join(subdir, file1) if subdir else file1
            relpath2 = os.path.join(subdir, file2) if subdir else file2
            files.append((relpath1, relpath2))
    else:
        raise ValueError("Either --includelist or --includepatterns must be specified")

    results = []

    for relpath1, relpath2 in files:
        path1 = os.path.join(dir1, relpath1)
        path2 = os.path.join(dir2, relpath2)

        relpath_display = relpath1 if relpath1 == relpath2 else f"{relpath1} ↔ {relpath2}"

        if not os.path.exists(path1):
            msg = f"[MISSING] {relpath1} not found in {dir1}/"
            _print_missing(msg, style)
            results.append(msg)
            continue
        if not os.path.exists(path2):
            msg = f"[MISSING] {relpath2} not found in {dir2}/"
            _print_missing(msg, style)
            results.append(msg)
            continue

        diff_lines = list(parse_file(path1, path2, ignore_paths))

        if any(line.startswith(("+", "-")) for line in diff_lines):
            results.append(f"▶ {relpath_display}" if style != "verbose" else f"=== {relpath_display} ===")

            if style == "sidebyside":
                for line in diff_lines:
                    results.append(line)
                _print_sidebyside(diff_lines, relpath_display)
            else:
                _print_header(relpath_display, style)
                for line in diff_lines:
                    if style == "compact" and not line.startswith(("+", "-")):
                        continue
                    _print_line(line, style)
                    results.append(line)
                if style == "compact":
                    console.print()
                    results.append("")
        else:
            msg = f"✓ {relpath_display} (no differences)"
            console.print(Text(msg, style="dim"))
            results.append(msg)

    if output_file:
        export_report(results, output_file)

# === CLI output ===

def _print_header(relpath, style):
    if style == "compact":
        bar = f"┌─ Diff: {relpath} " + "─" * max(10, 60 - len(relpath))
        console.print(Text(bar, style="bold cyan"))
    else:
        console.print(Text("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="cyan"))
        console.print(Text(f"≡ FILE: {relpath}", style="bold cyan"))
        console.print(Text("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", style="cyan"))

def _print_line(line, style):
    if line.startswith("+"):
        console.print(Text(line, style="green"))
    elif line.startswith("-"):
        console.print(Text(line, style="red"))
    elif line.startswith("@@"):
        console.print(Text(line, style="magenta"))
    elif line.startswith(("---", "+++")):
        if style == "verbose":
            console.print(Text(line, style="dim"))
    else:
        if style == "verbose":
            console.print(line)

def _print_missing(msg, style):
    if style == "compact":
        msg = msg.replace("[MISSING]", "⚠")
    console.print(Text(msg, style="bold yellow"))

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
