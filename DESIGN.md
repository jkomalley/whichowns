# whichowns design spec

`whichowns` is a CLI that reports which package manager owns a command. It targets Linux and macOS.

## Versions

| Version | Contents |
|---|---|
| `0.0.1` | Working CLI that reports everything as unmanaged; claims the PyPI name |
| `0.1.0` | brew detector |
| `0.2.0` | dpkg detector |
| `0.3.0` | uv detector |
| `0.4.0` | pipx detector; this spec fully implemented |

Every detector is a `feat:`, so CI's version guard requires a minor bump for each one. A release is a version-bump PR, and the CD workflow publishes it to PyPI after it merges.

## Behavior

`whichowns` takes one argument, a command name or a path to an executable.

- A name is looked up on PATH, and the first match is used.
- A path (anything containing `/`) is checked directly, relative to the current directory if it isn't absolute. PATH isn't searched.

The match's symlinks are then resolved, and the owning manager and package are reported.

```text
$ whichowns rg
rg: ripgrep (brew)

$ whichowns -v rg
rg: ripgrep (brew)
/opt/homebrew/Cellar/ripgrep/15.1.0/bin/rg

$ whichowns /usr/bin/sed
/usr/bin/sed: sed (dpkg)

$ whichowns foo
foo: unmanaged

$ whichowns -v foo
foo: unmanaged
/home/me/bin/foo

$ whichowns nope
whichowns: nope: command not found    # stderr
```

The argument is echoed back exactly as given. A path that doesn't exist or isn't executable also gets "command not found".

`whichowns` only sees files. Shell builtins, aliases and functions aren't found, so `whichowns cd` may say "command not found" even though `type cd` finds it.

| Exit code | Meaning |
|---|---|
| `0` | Command found, managed or unmanaged |
| `1` | Command not found |
| `2` | Usage error |

## Layout

```text
src/whichowns/
├── __main__.py        # Calls cli.main()
├── cli.py             # Arguments, -v, output, exit codes
├── locate.py          # PATH lookup and symlink resolution
├── models.py          # Location, Owner
└── managers/
    ├── __init__.py    # Detector order and find_owner()
    ├── uv.py
    ├── pipx.py
    ├── brew.py
    └── dpkg.py
```

`cli.py` is the only module that prints or sets exit codes. There is no public library API.

`cli.main(argv: list[str] | None = None) -> int` returns the exit code, and `__main__.py` passes it to `sys.exit()`. Usage errors and `--help` are the exception: argparse exits directly (with 2 and 0), so tests check them with `pytest.raises(SystemExit)`. The `[project.scripts]` entry point changes to `whichowns.cli:main`.

## Flow

```text
whichowns rg
  → cli: parse arguments
  → locate("rg"): Location, or None (exit 1)
  → find_owner(location): Owner, or None (unmanaged)
  → cli: print result (exit 0)
```

## Core types

```python
@dataclass(frozen=True)
class Location:
    command: str    # Argument as given
    path: Path      # PATH match, or the given path
    resolved: Path  # Final symlink target

@dataclass(frozen=True)
class Owner:
    manager: str
    package: str

Detector = Callable[[Location], Owner | None]
```

## Design decisions

| Area | Decision |
|---|---|
| Arguments | Exactly one command name or path; `argparse`, with no runtime dependencies |
| PATH lookup | `shutil.which()`, first match only; it checks paths directly |
| Symlinks | `Path.resolve()`, keeping both `path` and `resolved` |
| Symlinked commands | Owner is the package of the resolved file; `path` is only checked when `resolved` matches nothing |
| Detectors | Plain functions, tried in the order uv, pipx, brew, dpkg |
| Detector order | uv, pipx and brew can't match the same path, so their order doesn't matter; dpkg is last because it's the only slow one |
| Multiple owners | First match wins |
| Detector errors | Missing, unreadable or malformed files count as no match |
| Output | One line by default; `-v` adds the resolved path, managed or not |

### Symlinked commands

A command on PATH is often a symlink into a different package. On Ubuntu, `/usr/bin/python3` (from `python3-minimal`) points to `/usr/bin/python3.12` (from `python3.12-minimal`), so `whichowns python3` reports `python3.12-minimal`. This keeps every manager answering the same question, "who owns the file that actually runs", because brew, uv and pipx can only match the resolved path. `-v` shows the resolved file, which explains the answer.

## Detectors

| Manager | Method | Package name source |
|---|---|---|
| uv | `uv-receipt.toml` in the environment root (`resolved.parent.parent`) | Tool directory name |
| pipx | `pipx_metadata.json` in the environment root (`resolved.parent.parent`) | `main_package.package` in the metadata |
| brew | Match `Cellar/<formula>/<version>` in `resolved` | Path |
| dpkg | Scan `/var/lib/dpkg/info/*.list` for an exact path match | `.list` filename |

### pipx notes

- The environment directory name isn't the package name when `--suffix` is used (`venvs/cowsay@2` holds `cowsay`), so the name comes from the metadata.
- Commands exposed with `pipx inject --include-apps` report the main package.

### brew notes

- The pattern covers `/opt/homebrew`, `/usr/local` and Linuxbrew.
- Casks (`Caskroom`) aren't detected.

### dpkg rules

- The manager is reported as `dpkg`. Every Debian install method (apt, aptitude, nala, `dpkg -i`, …) writes to the same database, and none of them records which tool was used.
- Check `resolved`, then `path`.
- Merged `/usr`: for a candidate under `/usr/bin`, `/usr/sbin` or `/usr/lib*`, also try the same path without the `/usr` prefix when that top-level directory (such as `/bin`) is a symlink to its `/usr` counterpart. Some packages still list the old spelling. For example, `netcat-openbsd` lists `/bin/nc.openbsd`, but the file resolves to `/usr/bin/nc.openbsd`.
- Strip any `:arch` suffix from the filename, such as `clang-format:amd64.list`.
- Don't call `dpkg-query` at runtime.
- Skip diversions for now, so a diverted command may show as unmanaged or get the wrong owner.

## Testing

Unit tests must reach 100% line and branch coverage of `src/whichowns`.

### Unit tests

| Target | Approach |
|---|---|
| `locate` | Temporary directories with a fake `PATH` and symlinks; absolute and relative path arguments |
| `find_owner` | Detector lists passed as an argument: none, first match wins, order respected |
| uv, pipx, brew | Fake directory trees in `tmp_path`; pipx with a suffixed directory; malformed metadata |
| dpkg | Fake `.list` files through a monkeypatched info-directory constant; merged-`/usr` alias through a monkeypatchable helper |
| `cli` | Output and exit code for found, unmanaged, not found, path argument, `-v`, and usage error; managed cases use a fake `Cellar` tree on `PATH`, so no mocks are needed |

### Integration tests

Integration tests live in `tests/integration/`, carry the `integration` marker, and are deselected by default. They run the installed `whichowns` command as a subprocess against real package managers, and each test skips when its manager isn't installed. CI runs them on Linux and macOS against the built wheel.

| Manager | Approach |
|---|---|
| uv | `uv tool install` into temporary `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR` |
| pipx | `pipx install` into temporary `PIPX_HOME` and `PIPX_BIN_DIR`, including a `--suffix` install |
| brew | Commands already installed under `$(brew --prefix)/bin`, compared against `brew`'s own answer |
| dpkg | Commands on `PATH`, compared against `dpkg-query -S` on each command's resolved path, skipping any it doesn't find; plus `nc` → `netcat-openbsd` for merged `/usr` |

uv and pipx install into temporary directories, so these tests never change a developer's real setup. The `dpkg-query` comparison can't catch merged-`/usr` misses, because `dpkg-query -S` has the same gap; the `nc` test covers them.

## Build order

1. `models.py` and `locate.py`
2. `managers/__init__.py`, with no detectors yet
3. `cli.py`, which makes everything found show as unmanaged
4. Release `0.0.1`
5. `brew.py`, then release `0.1.0`
6. `dpkg.py`, then release `0.2.0`
7. `uv.py`, then release `0.3.0`
8. `pipx.py`, then release `0.4.0`

Each detector PR adds its unit tests, its integration tests, and a changelog entry.

## To verify

- uv and pipx symlink commands into their tool environments on macOS. (Verified on Ubuntu 24.04 with uv 0.11 and pipx 1.18; the macOS integration tests will confirm it.)
- The `uv-receipt.toml` and `pipx_metadata.json` locations match real installs on macOS. (Verified on Ubuntu; the macOS integration tests will confirm it.)
- PyPI accepts `whichowns` on the first upload. (The name was unregistered on 2026-11-03.)

## Out of scope

- Public library API
- Multiple command arguments
- Package versions
- Showing all PATH matches or `-a`
- dpkg diversions
- Telling apt installs from other dpkg installs
- Homebrew casks
- `--json`
- snap and cargo
- pyenv and asdf shims
- Showing the full symlink chain
- Auditing everything on PATH
