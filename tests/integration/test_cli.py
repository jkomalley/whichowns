"""Integration tests for the installed whichowns command."""

import os
import shutil
import subprocess
import sysconfig
from pathlib import Path
from typing import NoReturn

import pytest

pytestmark = pytest.mark.integration


def run_whichowns(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed whichowns command and capture its output."""
    # Not shutil.which: PATH may hold another whichowns, or none at all when
    # pytest isn't started through uv run.
    path = Path(sysconfig.get_path("scripts")) / "whichowns"
    # A blocked package manager should fail the test, not hang CI for hours.
    return subprocess.run(  # noqa: S603
        [path, *args], capture_output=True, text=True, check=False, timeout=30
    )


def skip_or_fail(reason: str) -> NoReturn:
    """Skip the test locally, or fail it in CI."""
    # CI installs every package manager, so anything missing there is a setup error.
    if os.environ.get("CI"):
        pytest.fail(reason)
    pytest.skip(reason)


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


def test_brew_formula() -> None:
    """A command installed by a brew formula is reported as that formula's."""
    brew = shutil.which("brew")
    if brew is None:
        skip_or_fail("brew isn't installed")
    prefix = subprocess.run(  # noqa: S603
        [brew, "--prefix"], capture_output=True, text=True, check=True, timeout=60
    ).stdout.strip()
    hello = Path(prefix) / "bin" / "hello"
    if not hello.exists():
        skip_or_fail("brew's hello formula isn't installed")

    assert run_whichowns(str(hello)).stdout == f"{hello}: hello (brew)\n"
