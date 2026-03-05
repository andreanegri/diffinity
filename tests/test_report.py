import pytest
from diffinity.report import export_report


def test_export_report_txt_writes_lines_joined_by_newlines(tmp_path):
    out = tmp_path / "report.txt"
    export_report(["line one", "line two", "line three"], str(out))
    assert out.read_text(encoding="utf-8") == "line one\nline two\nline three"


def test_export_report_txt_empty_list(tmp_path):
    out = tmp_path / "report.txt"
    export_report([], str(out))
    assert out.read_text(encoding="utf-8") == ""


def test_export_report_html_wraps_in_pre_tag(tmp_path):
    out = tmp_path / "report.html"
    export_report(["some diff"], str(out))
    content = out.read_text(encoding="utf-8")
    assert "<pre" in content
    assert "some diff" in content


def test_export_report_html_escapes_special_chars(tmp_path):
    out = tmp_path / "report.html"
    export_report(["<diff> & 'test'"], str(out))
    content = out.read_text(encoding="utf-8")
    assert "&lt;" in content
    assert "&amp;" in content
    assert "<diff>" not in content


def test_export_report_unsupported_extension_prints_message(tmp_path, capsys):
    out = tmp_path / "report.csv"
    export_report(["data"], str(out))
    captured = capsys.readouterr()
    assert "non supportato" in captured.out
    assert not out.exists()
