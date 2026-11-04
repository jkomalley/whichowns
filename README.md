# whichowns

Find which package manager owns a command.

## Install

```sh
uv tool install whichowns
```

## Usage

```text
$ whichowns rg
rg: ripgrep (brew)

$ whichowns -v rg
rg: ripgrep (brew)
/opt/homebrew/Cellar/ripgrep/15.1.0/bin/rg

$ whichowns ./bin/foo
./bin/foo: unmanaged
```

A name is looked up on `PATH`. A path (anything containing `/`) is checked directly. `-v` adds the resolved path.
