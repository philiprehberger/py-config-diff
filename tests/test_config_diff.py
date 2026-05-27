import json
import re
import tempfile
from pathlib import Path

from philiprehberger_config_diff import (
    ChangeType,
    diff_dicts,
    diff_files,
    unified_diff,
)


def test_no_changes():
    report = diff_dicts({"a": 1}, {"a": 1})
    assert not report.has_changes


def test_added():
    report = diff_dicts({"a": 1}, {"a": 1, "b": 2})
    assert len(report.added) == 1
    assert report.added[0].path == "b"


def test_removed():
    report = diff_dicts({"a": 1, "b": 2}, {"a": 1})
    assert len(report.removed) == 1
    assert report.removed[0].path == "b"


def test_modified():
    report = diff_dicts({"a": 1}, {"a": 2})
    assert len(report.modified) == 1
    assert report.modified[0].left == 1
    assert report.modified[0].right == 2


def test_nested_diff():
    left = {"db": {"host": "localhost", "port": 5432}}
    right = {"db": {"host": "localhost", "port": 3306}}
    report = diff_dicts(left, right)
    assert len(report.modified) == 1
    assert report.modified[0].path == "db.port"


def test_summary():
    report = diff_dicts({"a": 1, "b": 2}, {"a": 10, "c": 3})
    summary = report.summary()
    assert "Added: 1" in summary
    assert "Removed: 1" in summary
    assert "Modified: 1" in summary


def test_include_filter():
    report = diff_dicts(
        {"a": 1, "b": 2, "c": 3},
        {"a": 10, "b": 20, "c": 30},
        include=["a"],
    )
    assert len(report.changes) == 1
    assert report.changes[0].path == "a"


def test_exclude_filter():
    report = diff_dicts(
        {"a": 1, "b": 2},
        {"a": 10, "b": 20},
        exclude=["b"],
    )
    assert len(report.changes) == 1


def test_diff_json_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        left_path = str(Path(tmpdir) / "left.json")
        right_path = str(Path(tmpdir) / "right.json")
        Path(left_path).write_text(json.dumps({"a": 1}))
        Path(right_path).write_text(json.dumps({"a": 2}))
        report = diff_files(left_path, right_path)
        assert len(report.modified) == 1


def test_diff_env_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        left_path = str(Path(tmpdir) / "dev.env")
        right_path = str(Path(tmpdir) / "prod.env")
        Path(left_path).write_text("DB_HOST=localhost\nDB_PORT=5432\n")
        Path(right_path).write_text("DB_HOST=prod-server\nDB_PORT=5432\n")
        report = diff_files(left_path, right_path)
        assert len(report.modified) == 1
        assert report.modified[0].path == "DB_HOST"


def test_change_str():
    report = diff_dicts({"a": 1}, {"a": 2})
    text = str(report.changes[0])
    assert "a" in text


def test_empty_dicts():
    report = diff_dicts({}, {})
    assert not report.has_changes


def test_unified_diff_identical_returns_empty():
    assert unified_diff({"a": 1}, {"a": 1}) == ""


def test_unified_diff_renders_change():
    out = unified_diff({"a": 1, "b": 2}, {"a": 1, "b": 3})
    assert "--- left" in out
    assert "+++ right" in out
    assert "-b = 2" in out
    assert "+b = 3" in out


def test_unified_diff_nested():
    left = {"db": {"host": "localhost", "port": 5432}}
    right = {"db": {"host": "remote", "port": 5432}}
    out = unified_diff(left, right)
    assert "-db.host = 'localhost'" in out
    assert "+db.host = 'remote'" in out


def test_unified_diff_custom_labels():
    out = unified_diff({"a": 1}, {"a": 2}, left_label="dev", right_label="prod")
    assert "--- dev" in out
    assert "+++ prod" in out


def test_change_type_enum():
    assert ChangeType.ADDED.value == "added"
    assert ChangeType.REMOVED.value == "removed"
    assert ChangeType.MODIFIED.value == "modified"


def test_exclude_with_compiled_regex():
    left = {"db": {"host": "old", "password": "pw1"}, "api_token": "t1"}
    right = {"db": {"host": "new", "password": "pw2"}, "api_token": "t2"}

    report = diff_dicts(
        left,
        right,
        exclude=[re.compile(r"password$"), re.compile(r"_token$")],
    )

    assert [c.path for c in report.changes] == ["db.host"]


def test_include_with_compiled_regex():
    left = {"db_host": "a", "db_port": 1, "api_host": "x"}
    right = {"db_host": "b", "db_port": 2, "api_host": "y"}

    report = diff_dicts(left, right, include=[re.compile(r"^db_")])

    paths = sorted(c.path for c in report.changes)
    assert paths == ["db_host", "db_port"]


def test_glob_and_regex_can_mix():
    left = {"a": 1, "b": 2, "c_token": "x"}
    right = {"a": 10, "b": 20, "c_token": "y"}

    report = diff_dicts(left, right, exclude=["a", re.compile(r"_token$")])

    assert [c.path for c in report.changes] == ["b"]
