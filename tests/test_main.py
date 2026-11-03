"""Tests for the whichowns entry point."""

import pytest

from whichowns.__main__ import main


def test_main_prints_hello(capsys: pytest.CaptureFixture[str]) -> None:
    """main() writes the hello message to stdout."""
    main()
    assert capsys.readouterr().out == "Hello from whichowns!\n"
