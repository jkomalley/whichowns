"""Tests for command lookup."""

from pathlib import Path

import pytest

from whichowns.locate import locate


def make_executable(path: Path) -> Path:
    """Create an executable file at path, including its parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n")
    path.chmod(0o755)
    return path


def set_path(monkeypatch: pytest.MonkeyPatch, *dirs: Path) -> None:
    """Replace PATH with the given directories."""
    monkeypatch.setenv("PATH", ":".join(str(d) for d in dirs))


def test_name_returns_first_path_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A name resolves to the match in the earliest PATH directory."""
    first = make_executable(tmp_path / "a" / "tool")
    make_executable(tmp_path / "b" / "tool")
    set_path(monkeypatch, tmp_path / "a", tmp_path / "b")

    location = locate("tool")

    assert location is not None
    assert location.command == "tool"
    assert location.path == first
    assert location.resolved == first


def test_absolute_path_is_checked_directly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An absolute path outside PATH is found as given."""
    tool = make_executable(tmp_path / "opt" / "tool")
    set_path(monkeypatch, tmp_path / "empty")

    location = locate(str(tool))

    assert location is not None
    assert location.path == tool


def test_relative_path_is_made_absolute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A relative path is found from the current directory and made absolute."""
    tool = make_executable(tmp_path / "bin" / "tool")
    set_path(monkeypatch, tmp_path / "empty")
    monkeypatch.chdir(tmp_path)

    location = locate("bin/tool")

    assert location is not None
    assert location.command == "bin/tool"
    assert location.path == tool


def test_relative_path_entry_is_made_absolute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A match from a relative PATH entry is made absolute."""
    tool = make_executable(tmp_path / "bin" / "tool")
    monkeypatch.setenv("PATH", "bin")
    monkeypatch.chdir(tmp_path)

    location = locate("tool")

    assert location is not None
    assert location.path == tool


def test_path_argument_does_not_search_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A path that doesn't exist isn't looked up by its name on PATH."""
    make_executable(tmp_path / "bin" / "tool")
    set_path(monkeypatch, tmp_path / "bin")
    monkeypatch.chdir(tmp_path)

    assert locate("sub/tool") is None


def test_symlinks_are_resolved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The PATH match is kept, and every symlink is followed to the target."""
    real = make_executable(tmp_path / "real" / "tool-1.0")
    middle = tmp_path / "middle" / "tool"
    middle.parent.mkdir()
    middle.symlink_to(real)
    link = tmp_path / "bin" / "tool"
    link.parent.mkdir()
    link.symlink_to(middle)
    set_path(monkeypatch, tmp_path / "bin")

    location = locate("tool")

    assert location is not None
    assert location.path == link
    assert location.resolved == real


def test_missing_command_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A name that isn't on PATH isn't found."""
    set_path(monkeypatch, tmp_path)

    assert locate("nope") is None


def test_non_executable_file_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file on PATH without execute permission isn't found."""
    (tmp_path / "tool").write_text("")
    set_path(monkeypatch, tmp_path)

    assert locate("tool") is None
