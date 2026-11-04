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
    # which() can return relative paths, "..", and symlinked directories, but
    # detectors compare against canonical paths, such as those in dpkg's file
    # lists. Only the directory is resolved: the command itself may be a symlink
    # that a package owns. Removing ".." as text would be wrong after a
    # symlinked directory.
    found = Path(match)
    path = found.parent.resolve() / found.name
    return Location(command=command, path=path, resolved=path.resolve())
