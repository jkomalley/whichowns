"""Detector order and owner lookup."""

from collections.abc import Iterable

from whichowns.managers import brew
from whichowns.models import Detector, Location, Owner

DETECTORS: tuple[Detector, ...] = (brew.detect,)


def find_owner(
    location: Location, detectors: Iterable[Detector] = DETECTORS
) -> Owner | None:
    """Ask each detector in turn which package manager owns a command.

    Args:
        location: Where the command was found.
        detectors: Detectors to try, in order.

    Returns:
        The first owner a detector reports, or None if none match.

    """
    for detect in detectors:
        owner = detect(location)
        if owner is not None:
            return owner
    return None
