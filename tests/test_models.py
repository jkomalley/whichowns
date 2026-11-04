"""Tests for the shared data types."""

from pathlib import Path

from whichowns.models import Location, Owner


def test_models_compare_by_value() -> None:
    """Location and Owner built from equal fields are equal."""
    assert Location("rg", Path("/bin/rg"), Path("/opt/rg")) == Location(
        "rg", Path("/bin/rg"), Path("/opt/rg")
    )
    assert Owner("brew", "ripgrep") == Owner("brew", "ripgrep")
