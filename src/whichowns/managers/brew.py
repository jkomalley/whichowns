"""Detect commands installed by Homebrew."""

from whichowns.models import Location, Owner


def detect(location: Location) -> Owner | None:
    """Report the formula whose keg holds the command's resolved file.

    Args:
        location: Where the command was found.

    Returns:
        The formula that owns the command, or None if the file isn't in a keg.

    """
    parts = location.resolved.parts
    if "Cellar" not in parts:
        return None
    index = parts.index("Cellar")
    # A keg file needs a formula, a version and a name after Cellar. The version's
    # format isn't checked because HEAD installs use names like "HEAD-abc123".
    if len(parts) < index + 4:
        return None
    return Owner("brew", parts[index + 1])
