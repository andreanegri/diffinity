import os
from .fileio import load_text, parse_file
from .report import export_report
from rich.console import Console
from rich.text import Text

console = Console()

def run_diff(
    dir1, dir2,
    includelist_path=None,
    output_file=None,
    style="compact",
    ignore_paths=False,
    includepatterns_path=None
):
    # Costruzione lista (relpath1, relpath2) da confrontare
    if includelist_path:
        files = [(line.strip(), line.strip()) for line in load_text(includelist_path).splitlines() if line.strip()]
    elif includepatterns_path:
        suffixes = []
        for line in load_text(includepatterns_path).splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.split("#", 1)[0].strip()  # remove inline comment
            if line:
                suffixes.append(line)
        base1 = os.path.basename(os.path.normpath(dir1))
        base2 = os.path.basename(os.path.normpath(dir2))
        files = []

        for raw in suffixes:
            subdir, _, suffix = raw.rpartition("/")
            file1 = f"{base1}{suffix}"
            file2 = f"{base2}{suffix}"
            relpath1 = os.path.join(subdir, file1) if subdir else file1
            relpath2 = os.path.join(subdir, file2) if subdir else file2
            files.append((relpath1, relpath2))
    else:
        raise ValueError("È necessario specificare --includelist o --includepatterns")

    results = []

    for relpath1, relpath2 in files:
        path1 = os.path.join(dir1, relpath1)
        path2 = os.path.join(dir2, relpath2)

        relpath_display = relpath1 if relpath1 == relpath2 else f"{relpath1} ↔ {relpath2}"

        if not os.path.exists(path1):
            msg = f"[MISSING] {relpath1} non trovato in {dir1}/"
            _print_missing(msg, style)
            results.append(msg)
            continue
        if not os.path.exists(path2):
            msg = f"[MISSING] {relpath2} non trovato in {dir2}/"
            _print_missing(msg, style)
            results.append(msg)
            continue

        diff_lines = list(parse_file(path1, path2, ignore_paths))

        if any(line.startswith(("+", "-")) for line in diff_lines):
            _print_header(relpath_display, style)
            results.append(f"=== {relpath_display} ===" if style == "verbose" else f"▶ {relpath_display}")
            for line in diff_lines:
                if style == "compact" and not line.startswith(("+", "-")):
                    continue
                _print_line(line, style)
                results.append(line)
            if style == "compact":
                console.print()
                results.append("")
        else:
            msg = f"✓ {relpath_display} (nessuna differenza)"
            console.print(Text(msg, style="dim"))
            results.append(msg)

    if output_file:
        export_report(results, output_file)

# === Stampa CLI ===

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
