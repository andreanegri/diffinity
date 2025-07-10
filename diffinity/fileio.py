import json
import configparser
import difflib
import os
import re


def sanitize_paths(text):
    # Unix-like paths
    text = re.sub(r'(?<=["\'])/[^"\']+(?=["\'])', '__PATH__', text)   # tra virgolette
    text = re.sub(r'(?<![\w/])/(?:[\w.-]+/)*[\w.-]+', '__PATH__', text)  # path non quotati

    # Windows paths (con \\ o /)
    text = re.sub(r'(?<=["\'])[A-Za-z]:[\\/][^"\']+(?=["\'])', '__PATH__', text)
    text = re.sub(r'[A-Za-z]:[\\/](?:[\w.-]+[\\/])*[\w.-]+', '__PATH__', text)

    return text

def load_text(filepath):
    with open(filepath, encoding="utf-8") as f:
        return f.read()

def parse_ini(text):
    parser = configparser.ConfigParser()
    parser.read_string(text)
    return {s: dict(parser[s]) for s in parser.sections()}

def semantic_diff(obj1, obj2):
    if obj1 == obj2:
        return []
    return list(difflib.unified_diff(
        json.dumps(obj1, indent=2).splitlines(),
        json.dumps(obj2, indent=2).splitlines(),
        lineterm=""
    ))

def plain_diff(text1, text2):
    return list(difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        lineterm=""
    ))

def parse_file(path1, path2, ignore_paths=False):
    ext = os.path.splitext(path1)[1].lower()
    text1 = load_text(path1)
    text2 = load_text(path2)

    if ignore_paths:
        text1 = sanitize_paths(text1)
        text2 = sanitize_paths(text2)

    try:
        if ext == ".json":
            return semantic_diff(json.loads(text1), json.loads(text2))
        elif ext == ".ini":
            return semantic_diff(parse_ini(text1), parse_ini(text2))
        else:
            return plain_diff(text1, text2)
    except Exception as e:
        return [f"Errore nel parsing ({ext}): {e}"]
