from html import escape

def export_report(lines, path):
    if path.endswith(".txt"):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    elif path.endswith(".html"):
        with open(path, "w", encoding="utf-8") as f:
            f.write("<pre style='font-family: monospace;'>\n")
            for line in lines:
                f.write(escape(line) + "\n")
            f.write("</pre>")
    else:
        print(f"Formato output non supportato: {path}")
