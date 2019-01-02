"""Compare configuration files across environments."""

from __future__ import annotations

import configparser
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


__all__ = [
    "diff_files",
    "diff_dicts",
    "DiffReport",
    "Change",
    "ChangeType",
]


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass(frozen=True)
class Change:
    """A single difference between two configs."""

    type: ChangeType
    path: str
    left: Any = None
    right: Any = None

    def __str__(self) -> str:
        match self.type:
            case ChangeType.ADDED:
                return f"+ {self.path} = {self.right!r}"
            case ChangeType.REMOVED:
                return f"- {self.path} = {self.left!r}"
            case ChangeType.MODIFIED:
                return f"~ {self.path}: {self.left!r} -> {self.right!r}"


@dataclass
class DiffReport:
    """Result of comparing two configurations."""

    changes: list[Change] = field(default_factory=list)

    @property
    def added(self) -> list[Change]:
        return [c for c in self.changes if c.type == ChangeType.ADDED]

    @property
    def removed(self) -> list[Change]:
        return [c for c in self.changes if c.type == ChangeType.REMOVED]

    @property
    def modified(self) -> list[Change]:
        return [c for c in self.changes if c.type == ChangeType.MODIFIED]

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        return (
            f"Added: {len(self.added)}, "
            f"Removed: {len(self.removed)}, "
            f"Modified: {len(self.modified)}"
        )

    def __str__(self) -> str:
        if not self.changes:
            return "No differences"
        lines = [str(c) for c in self.changes]
        lines.append(f"\n{self.summary()}")
        return "\n".join(lines)


def diff_files(
    left_path: str,
    right_path: str,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> DiffReport:
    """Compare two configuration files.

    Supports JSON, TOML (Python 3.11+), INI, and .env files.

    Args:
        left_path: Path to the first config file.
        right_path: Path to the second config file.
        include: Glob patterns for keys to include.
        exclude: Glob patterns for keys to exclude.

    Returns:
        DiffReport with all changes.
    """
    left_data = _load_file(left_path)
    right_data = _load_file(right_path)
    return diff_dicts(left_data, right_data, include=include, exclude=exclude)


def diff_dicts(
    left: dict[str, Any],
    right: dict[str, Any],
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> DiffReport:
    """Compare two dictionaries and report differences.

    Args:
        left: First dict.
        right: Second dict.
        include: Glob patterns for keys to include.
        exclude: Glob patterns for keys to exclude.

    Returns:
        DiffReport with all changes.
    """
    changes: list[Change] = []
    _diff_recursive(left, right, "", changes)

    if include or exclude:
        changes = _filter_changes(changes, include, exclude)

    return DiffReport(changes=changes)


def _diff_recursive(
    left: Any,
    right: Any,
    prefix: str,
    changes: list[Change],
) -> None:
    if isinstance(left, dict) and isinstance(right, dict):
        all_keys = set(left) | set(right)
        for key in sorted(all_keys):
            path = f"{prefix}.{key}" if prefix else key
            if key not in left:
                changes.append(Change(ChangeType.ADDED, path, right=right[key]))
            elif key not in right:
                changes.append(Change(ChangeType.REMOVED, path, left=left[key]))
            else:
                _diff_recursive(left[key], right[key], path, changes)
    elif left != right:
        changes.append(Change(ChangeType.MODIFIED, prefix, left=left, right=right))


def _filter_changes(
    changes: list[Change],
    include: list[str] | None,
    exclude: list[str] | None,
) -> list[Change]:
    result = changes
    if include:
        result = [c for c in result if any(fnmatch(c.path, p) for p in include)]
    if exclude:
        result = [c for c in result if not any(fnmatch(c.path, p) for p in exclude)]
    return result


def _load_file(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    suffix = file_path.suffix.lower()
    text = file_path.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(text)

    if suffix == ".toml":
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError:
                msg = "TOML support requires Python 3.11+ or the 'tomli' package"
                raise ImportError(msg) from None
        return tomllib.loads(text)

    if suffix == ".ini" or suffix == ".cfg":
        return _parse_ini(text)

    if suffix == ".env" or file_path.name.startswith(".env"):
        return _parse_env(text)

    # Default: try JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _parse_env(text)


def _parse_ini(text: str) -> dict[str, Any]:
    parser = configparser.ConfigParser()
    parser.read_string(text)
    result: dict[str, Any] = {}
    for section in parser.sections():
        result[section] = dict(parser[section])
    if parser.defaults():
        result["DEFAULT"] = dict(parser.defaults())
    return result


_ENV_LINE_RE = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)')


def _parse_env(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _ENV_LINE_RE.match(line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            # Strip quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result[key] = value
    return result
