import pytest
from diffinity.cli import parse_args


def test_parse_args_positional_dirs(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt"])
    args = parse_args()
    assert args.dir1 == "dir1"
    assert args.dir2 == "dir2"


def test_parse_args_includelist(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt"])
    args = parse_args()
    assert args.includelist == "list.txt"
    assert args.includepatterns is None


def test_parse_args_includepatterns(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2", "--includepatterns", "patterns.txt"])
    args = parse_args()
    assert args.includepatterns == "patterns.txt"
    assert args.includelist is None


def test_parse_args_mutually_exclusive_fails(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["diffinity", "dir1", "dir2", "--includelist", "list.txt", "--includepatterns", "patterns.txt"],
    )
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_neither_fails(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2"])
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_defaults(monkeypatch):
    monkeypatch.setattr("sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt"])
    args = parse_args()
    assert args.output is None
    assert args.style == "compact"
    assert args.ignore_paths is False


def test_parse_args_output_flag(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt", "--output", "report.html"]
    )
    args = parse_args()
    assert args.output == "report.html"


def test_parse_args_style_verbose(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt", "--style", "verbose"]
    )
    args = parse_args()
    assert args.style == "verbose"


def test_parse_args_style_invalid_fails(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt", "--style", "fancy"]
    )
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_ignore_paths_flag(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["diffinity", "dir1", "dir2", "--includelist", "list.txt", "--ignore-paths"]
    )
    args = parse_args()
    assert args.ignore_paths is True
