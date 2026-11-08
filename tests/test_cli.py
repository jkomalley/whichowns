"""Tests for the command-line interface."""

from pathlib import Path

import pytest

from whichowns import cli
from whichowns.cli import main
from whichowns.models import Location, Owner


def make_executable(path: Path) -> Path:
    """Create an executable file at path, including its parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n")
    path.chmod(0o755)
    return path


@pytest.fixture
def tool(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put a "tool" symlink on PATH that points to an executable outside it."""
    real = make_executable(tmp_path / "real" / "tool-1.0")
    link = tmp_path / "bin" / "tool"
    link.parent.mkdir()
    link.symlink_to(real)
    monkeypatch.setenv("PATH", str(link.parent))
    return real


@pytest.fixture
def owned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every command owned by brew's ripgrep."""

    # Keeps output tests independent of any detector's rules, which have their own
    # tests. test_brew_end_to_end covers a real detector through the CLI.
    def fake_find_owner(_: Location) -> Owner:
        return Owner("brew", "ripgrep")

    monkeypatch.setattr(cli, "find_owner", fake_find_owner)


@pytest.mark.usefixtures("tool")
def test_unmanaged(capsys: pytest.CaptureFixture[str]) -> None:
    """A found command with no owner is reported as unmanaged."""
    assert main(["tool"]) == 0
    assert capsys.readouterr().out == "tool: unmanaged\n"


def test_unmanaged_verbose(tool: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """-v adds the resolved path for an unmanaged command."""
    assert main(["-v", "tool"]) == 0
    assert capsys.readouterr().out == f"tool: unmanaged\n{tool}\n"


@pytest.mark.usefixtures("tool", "owned")
def test_managed(capsys: pytest.CaptureFixture[str]) -> None:
    """A managed command reports its package and manager."""
    assert main(["tool"]) == 0
    assert capsys.readouterr().out == "tool: ripgrep (brew)\n"


@pytest.mark.usefixtures("owned")
def test_managed_verbose(tool: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """-v adds the resolved path for a managed command."""
    assert main(["-v", "tool"]) == 0
    assert capsys.readouterr().out == f"tool: ripgrep (brew)\n{tool}\n"


def test_brew_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A command linked from a keg is reported as brew's by the real detectors."""
    real = make_executable(tmp_path / "Cellar" / "ripgrep" / "15.1.0" / "bin" / "rg")
    link = tmp_path / "bin" / "rg"
    link.parent.mkdir()
    link.symlink_to(real)
    monkeypatch.setenv("PATH", str(link.parent))

    assert main(["rg"]) == 0
    assert capsys.readouterr().out == "rg: ripgrep (brew)\n"


def test_path_argument_is_echoed_as_given(
    tool: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A path argument is echoed exactly as given, not as the resolved path."""
    monkeypatch.chdir(tool.parent)

    assert main(["./tool-1.0"]) == 0
    assert capsys.readouterr().out == "./tool-1.0: unmanaged\n"


@pytest.mark.usefixtures("tool")
def test_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    """A missing command goes to stderr with exit code 1."""
    assert main(["nope"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "whichowns: nope: command not found\n"


@pytest.mark.parametrize("argv", [[], ["a", "b"], ["-x", "tool"]])
def test_usage_error(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    """Wrong arguments exit with code 2 and a usage message."""
    with pytest.raises(SystemExit) as exc_info:
        main(argv)

    assert exc_info.value.code == 2  # noqa: PLR2004
    assert capsys.readouterr().err.startswith("usage: whichowns")


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    """--help prints usage to stdout and exits with code 0."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.startswith("usage: whichowns")
