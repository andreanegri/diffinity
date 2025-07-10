# DIFFINITY

![diffinity-logo](diffinity/resources/images/logo400.png)  
*A CLI tool for deep, nerd-grade diffing of configuration files.*

---

**Current version**: `0.1.0`

**Diffinity** is a command-line utility designed to compare configuration files across multiple application runs.  
It supports **semantic diff** for structured formats (like `JSON` and `INI`) and **textual diff** for custom text-based files.

> Designed for devs who obsess over clean diffs and meaningful config changes.

---

## ✨ Features

- ✅ Semantic comparison for `.json` (ignores key order)
- 🧠 Smart text diff fallback for any other readable format
- 🎨 Colored, compact terminal output (or verbose mode if you prefer)
- 🧾 Exportable reports in `.txt` or `.html`
- 📂 Include files via:
  - full paths (`--includelist`)
  - suffix-based patterns (`--includepatterns`)
- 🧽 Optional `--ignore-paths` to skip irrelevant path differences

---

## 📦 Installation

```bash
git clone https://github.com/andreanegri/diffinity.git
cd diffinity

python -m venv .venv
source .venv/bin/activate

pip install --upgrade setuptools pip

pip install -e .
```

---

## 🚀 Usage

```bash
diffinity run1/ run2/ --includelist files.txt
```

or:

```bash
diffinity run1/ run2/ --includepatterns patterns.txt --ignore-paths --output report.html
```

---

## 📄 Example

Given:

```
run1/config/pipeline1_settings.json
run2/config/pipeline2_settings.json
```

With `patterns.txt`:

```
config/_settings.json
```

Diffinity compares:

```
run1/config/pipeline1_settings.json
vs
run2/config/pipeline2_settings.json
```

And shows:

```
┌─ Diff: config/pipeline1_settings.json ↔ config/pipeline2_settings.json ───────
-     "debug": true,
+     "debug": false,
```

---

## 🛠 CLI Options

| Flag               | Description                              |
|--------------------|------------------------------------------|
| `--includelist`     | List of full relative file paths         |
| `--includepatterns` | List of suffix patterns (prefixed by dir name) |
| `--ignore-paths`    | Ignore filesystem paths in comparison    |
| `--style`           | Output style: `compact` (default) or `verbose` |
| `--output`          | Export report to `.txt` or `.html`       |


---

## 🤘 Contributing

Pull requests and feedback are welcome.  
Open issues, submit features, or fork away!

