"""Integration tests for the installed whichowns command."""

import subprocess
import sysconfig
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def run_whichowns(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed whichowns command and capture its output."""
    # Not shutil.which: PATH may hold another whichowns, or none at all when
    # pytest isn't started through uv run.
    path = Path(sysconfig.get_path("scripts")) / "whichowns"
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
