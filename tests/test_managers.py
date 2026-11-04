"""Tests for the detector registry and owner lookup."""

from pathlib import Path

from whichowns.managers import find_owner
from whichowns.models import Location, Owner

LOCATION = Location("tool", Path("/bin/tool"), Path("/opt/tool"))


def no_match(_: Location) -> None:
    """Match nothing."""


def test_no_detectors_returns_none() -> None:
    """None is returned when there are no detectors to ask."""
    assert find_owner(LOCATION, []) is None


def test_no_match_returns_none() -> None:
    """None is returned when every detector declines."""
    assert find_owner(LOCATION, [no_match, no_match]) is None


def test_first_match_wins_and_stops() -> None:
    """The first matching detector's owner is returned and later ones aren't called."""
    later_calls: list[Location] = []

    def first(_: Location) -> Owner:
        return Owner("first", "pkg")

    def later(location: Location) -> Owner:
        later_calls.append(location)
        return Owner("later", "pkg")

    assert find_owner(LOCATION, [no_match, first, later]) == Owner("first", "pkg")
    assert later_calls == []
