"""Tests for `python -m whichowns`."""

import runpy

import pytest


def test_module_exits_with_main_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Running the package as a module exits with cli.main()'s return code."""
    monkeypatch.setattr("sys.argv", ["whichowns", "whichowns-nonexistent-command"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("whichowns", run_name="__main__")

    assert exc_info.value.code == 1
