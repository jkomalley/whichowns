# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`whichowns` is a CLI that finds which package manager owns a command. Python 3.11+ (developed on 3.15), src layout, managed with `uv`.

## Commands

Tasks run through `just`. Apart from `default`, each recipe wraps a plain `uv` command; see `justfile`.

- `just sync [args]`: install the project and dev tools
- `just run [args]`: run the CLI
- `just test [args]`: run tests
- `just fmt [args]`: format code
- `just lint [args]`: lint and auto-fix
- `just type [args]`: type check
- `just check`: format check, lint, type check and tests with the 100% coverage gate; must pass before committing

## Workflow

- The user makes the design decisions. Help with the step asked; don't implement ahead. When requirements or approach are ambiguous, ask before writing code.
- Every change gets its own branch and pull request; no direct commits to main.
- PRs are merged with a merge commit, never squashed or rebased.
- Commits are atomic: one logical change per commit.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, …).

## Issues

- Titles are imperative and sentence case, with no type prefix ("Detect dpkg packages", not "feat: dpkg").
- Each issue has exactly one kind label: `enhancement` when its PR has `feat:` commits, `bug` for defects, `maintenance` for everything else.
- Each issue also has exactly one area label: `core`, `manager: <name>`, `ci`, `tooling`, `release` or `documentation`. An issue that spans two areas should be split.
- Each issue goes in the milestone of the release that ships it (`v0.0.1`, `v0.1.0`, …).
- PRs say `Closes #N`; release PRs say `Part of #N`.

## Code Style

- ruff with all rules enabled and pragmatic ignores (see `pyproject.toml`).
- Comments explain *why* code does something, not *what* it does.
