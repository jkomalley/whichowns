"""Data types shared by command lookup and the package manager detectors."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


@dataclass(frozen=True)
class Location:
    """Where a command was found.

    Attributes:
        command: The argument exactly as given.
        path: The PATH match, or the given path, in its real directory.
            Not followed if it's a symlink itself.
        resolved: The final target after following every symlink.

    """

    command: str
    path: Path
    resolved: Path


@dataclass(frozen=True)
class Owner:
    """The package manager and package that own a command."""

    manager: str
    package: str


# The `type` statement needs Python 3.12, and whichowns supports 3.11.
Detector: TypeAlias = Callable[[Location], Owner | None]
