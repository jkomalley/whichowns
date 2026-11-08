# whichowns

Find which package manager owns a command.

## Install

```sh
uv tool install whichowns
```

## Usage

```console
$ whichowns rg
rg: ripgrep (brew)

$ whichowns -v rg
rg: ripgrep (brew)
/opt/homebrew/Cellar/ripgrep/15.1.0/bin/rg

$ whichowns foo
foo: unmanaged

$ whichowns nope
whichowns: nope: command not found
```

Homebrew formulae are detected on macOS and Linux. Commands from other package managers are reported as unmanaged for now.
