"""Tests for the Homebrew detector."""

from pathlib import Path

import pytest

from whichowns.managers import brew
from whichowns.models import Location, Owner


def location_of(resolved: str) -> Location:
    """Build a location for a command that resolves to the given path."""
    # The detector only reads the resolved path, so the other fields are fillers.
    return Location("tool", Path("/bin/tool"), Path(resolved))


@pytest.mark.parametrize(
    ("resolved", "formula"),
    [
        pytest.param(
            "/opt/homebrew/Cellar/ripgrep/15.1.0/bin/rg", "ripgrep", id="apple-silicon"
        ),
        pytest.param("/usr/local/Cellar/ripgrep/15.1.0/bin/rg", "ripgrep", id="intel"),
        pytest.param(
            "/home/linuxbrew/.linuxbrew/Cellar/ripgrep/15.1.0/bin/rg",
            "ripgrep",
            id="linuxbrew",
        ),
        pytest.param(
            "/opt/homebrew/Cellar/python@3.13/3.13.1"
            "/Frameworks/Python.framework/Versions/3.13/bin/python3.13",
            "python@3.13",
            id="nested",
        ),
        pytest.param(
            "/opt/homebrew/Cellar/foo/HEAD-abc123/bin/foo", "foo", id="head-install"
        ),
        pytest.param(
            "/opt/homebrew/Cellar/foo/1.0/libexec/Cellar/bar/2.0/bin/bar",
            "foo",
            id="first-cellar-wins",
        ),
    ],
)
def test_keg_file_is_owned_by_its_formula(resolved: str, formula: str) -> None:
    """A file inside a keg is owned by the formula named after Cellar."""
    assert brew.detect(location_of(resolved)) == Owner("brew", formula)


@pytest.mark.parametrize(
    "resolved",
    [
        pytest.param("/usr/bin/rg", id="no-cellar"),
        pytest.param("/opt/homebrew/Cellar/ripgrep/15.1.0", id="keg-itself"),
        pytest.param("/opt/homebrew/Caskroom/foo/1.0/foo", id="cask"),
        pytest.param("/opt/MyCellar/foo/1.0/bin/foo", id="partial-name"),
    ],
)
def test_file_outside_a_keg_is_not_owned(resolved: str) -> None:
    """A file that isn't inside a keg isn't owned by brew."""
    assert brew.detect(location_of(resolved)) is None
