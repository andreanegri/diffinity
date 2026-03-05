import json
import pytest
from diffinity.fileio import (
    load_text,
    parse_ini,
    semantic_diff,
    plain_diff,
    sanitize_paths,
    parse_file,
)


# --- load_text ---

def test_load_text_reads_utf8_content(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world", encoding="utf-8")
    assert load_text(str(f)) == "hello world"


def test_load_text_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text(str(tmp_path / "missing.txt"))


# --- parse_ini ---

def test_parse_ini_returns_dict_of_sections():
    result = parse_ini("[section]\nkey = value\n")
    assert result == {"section": {"key": "value"}}


def test_parse_ini_multiple_sections():
    text = "[db]\nhost = localhost\n[cache]\nbackend = redis\n"
    result = parse_ini(text)
    assert result == {"db": {"host": "localhost"}, "cache": {"backend": "redis"}}


def test_parse_ini_empty_string():
    assert parse_ini("") == {}


# --- semantic_diff ---

def test_semantic_diff_identical_objects_returns_empty():
    assert semantic_diff({"a": 1}, {"a": 1}) == []


def test_semantic_diff_detects_changed_value():
    diff = semantic_diff({"a": 1}, {"a": 2})
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    assert added and removed


def test_semantic_diff_ignores_key_order():
    assert semantic_diff({"b": 2, "a": 1}, {"a": 1, "b": 2}) == []


def test_semantic_diff_nested_objects():
    obj1 = {"outer": {"inner": 1}}
    obj2 = {"outer": {"inner": 2}}
    diff = semantic_diff(obj1, obj2)
    assert any("+1" in l or "+2" in l for l in diff)


# --- plain_diff ---

def test_plain_diff_identical_text_returns_empty():
    assert plain_diff("same\n", "same\n") == []


def test_plain_diff_detects_changed_line():
    diff = plain_diff("line one\nline two\n", "line one\nLINE TWO\n")
    assert any(l.startswith("+LINE TWO") for l in diff)


def test_plain_diff_detects_added_line():
    diff = plain_diff("line one\n", "line one\nnew line\n")
    assert any(l.startswith("+new line") for l in diff)


# --- sanitize_paths ---

def test_sanitize_paths_replaces_unix_paths():
    text = '{"log": "/var/log/app.log"}'
    result = sanitize_paths(text)
    assert "/var/log/app.log" not in result
    assert "__PATH__" in result


def test_sanitize_paths_replaces_unquoted_unix_path():
    text = "config file: /etc/hosts"
    result = sanitize_paths(text)
    assert "/etc/hosts" not in result
    assert "__PATH__" in result


def test_sanitize_paths_replaces_windows_paths():
    text = '"config": "C:\\\\Users\\\\admin\\\\config.ini"'
    result = sanitize_paths(text)
    assert "C:\\\\Users" not in result
    assert "__PATH__" in result


def test_sanitize_paths_leaves_non_paths_unchanged():
    text = "just some plain text with numbers 123"
    assert sanitize_paths(text) == text


# --- parse_file ---

def test_parse_file_json_semantic_diff(tmp_path):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text('{"host": "localhost", "port": 8080}', encoding="utf-8")
    f2.write_text('{"host": "remotehost", "port": 8080}', encoding="utf-8")
    diff = parse_file(str(f1), str(f2))
    assert any(l.startswith("+") or l.startswith("-") for l in diff if not l.startswith(("+++", "---")))


def test_parse_file_json_no_diff(tmp_path):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text('{"b": 2, "a": 1}', encoding="utf-8")
    f2.write_text('{"a": 1, "b": 2}', encoding="utf-8")
    assert parse_file(str(f1), str(f2)) == []


def test_parse_file_ini_semantic_diff(tmp_path):
    f1 = tmp_path / "a.ini"
    f2 = tmp_path / "b.ini"
    f1.write_text("[db]\nhost = localhost\n", encoding="utf-8")
    f2.write_text("[db]\nhost = remotehost\n", encoding="utf-8")
    diff = parse_file(str(f1), str(f2))
    assert any(l.startswith("+") or l.startswith("-") for l in diff if not l.startswith(("+++", "---")))


def test_parse_file_txt_plain_diff(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("line one\nline two\n", encoding="utf-8")
    f2.write_text("line one\nline TWO\n", encoding="utf-8")
    diff = parse_file(str(f1), str(f2))
    assert any("+line TWO" in l for l in diff)


def test_parse_file_ignore_paths_sanitizes_before_diff(tmp_path):
    f1 = tmp_path / "a.json"
    f2 = tmp_path / "b.json"
    f1.write_text('{"log": "/var/log/app.log", "name": "myapp"}', encoding="utf-8")
    f2.write_text('{"log": "/var/log/other.log", "name": "myapp"}', encoding="utf-8")
    diff = parse_file(str(f1), str(f2), ignore_paths=True)
    assert diff == []


def test_parse_file_unknown_extension_uses_plain_diff(tmp_path):
    f1 = tmp_path / "a.yaml"
    f2 = tmp_path / "b.yaml"
    f1.write_text("key: value1\n", encoding="utf-8")
    f2.write_text("key: value2\n", encoding="utf-8")
    diff = parse_file(str(f1), str(f2))
    assert any("+key: value2" in l for l in diff)


def test_parse_file_malformed_json_returns_error_message(tmp_path):
    f1 = tmp_path / "bad.json"
    f2 = tmp_path / "ok.json"
    f1.write_text("{not valid json", encoding="utf-8")
    f2.write_text('{"key": "val"}', encoding="utf-8")
    result = parse_file(str(f1), str(f2))
    assert len(result) == 1
    assert result[0].startswith("Errore nel parsing")
