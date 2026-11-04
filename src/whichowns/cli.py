"""Command-line interface: arguments, output and exit codes."""

import argparse
import sys

from whichowns.locate import locate
from whichowns.managers import find_owner

PROG = "whichowns"


def main(argv: list[str] | None = None) -> int:
    """Report which package manager owns a command.

    Args:
        argv: Arguments without the program name, or None to use sys.argv.

    Returns:
        0 if the command was found, 1 if not. Usage errors and --help exit
        directly through argparse.

    """
    # Without an explicit prog, `python -m whichowns` shows "__main__.py".
    parser = argparse.ArgumentParser(
        prog=PROG, description="Find which package manager owns a command."
    )
    parser.add_argument("command", help="command name, or path to an executable")
    parser.add_argument("-v", action="store_true", help="also show the resolved path")
    args = parser.parse_args(argv)

    location = locate(args.command)
    if location is None:
        sys.stderr.write(f"{PROG}: {args.command}: command not found\n")
        return 1

    owner = find_owner(location)
    if owner is None:
        sys.stdout.write(f"{args.command}: unmanaged\n")
    else:
        sys.stdout.write(f"{args.command}: {owner.package} ({owner.manager})\n")
    if args.v:
        sys.stdout.write(f"{location.resolved}\n")
    return 0
