"""Integration tests for the installed whichowns command."""

import shutil
import subprocess

import pytest

pytestmark = pytest.mark.integration


def run_whichowns(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed whichowns command and capture its output."""
    path = shutil.which("whichowns")
    assert path is not None, "whichowns is not installed on PATH"
    return subprocess.run(  # noqa: S603
        [path, *args], capture_output=True, text=True, check=False
    )


def test_finds_ls() -> None:
    """The installed command finds ls and exits 0."""
    result = run_whichowns("ls")

    assert result.returncode == 0
    # Only the prefix is stable: detectors will change what follows it.
    assert result.stdout.startswith("ls: ")


def test_reports_missing_command() -> None:
    """The installed command reports a missing command and exits 1."""
    result = run_whichowns("whichowns-nonexistent-command")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "command not found" in result.stderr
