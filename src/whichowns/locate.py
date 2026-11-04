"""Find a command on PATH and resolve its symlinks."""

import shutil
from pathlib import Path

from whichowns.models import Location


def locate(command: str) -> Location | None:
    """Find a command by name on PATH, or check a path directly.

    Args:
        command: A command name, or a path to an executable (anything containing "/").

    Returns:
        The command's location, or None if it isn't found or isn't executable.

    """
    match = shutil.which(command)
    if match is None:
        return None
    # which() returns relative paths for relative arguments or PATH entries, but
    # detectors compare against absolute paths, such as those in dpkg's file lists.
    path = Path(match).absolute()
    return Location(command=command, path=path, resolved=path.resolve())
