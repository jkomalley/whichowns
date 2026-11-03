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
- `just check`: format check, lint, type check and tests; must pass before committing

## Workflow

- The user makes the design decisions. Help with the step asked; don't implement ahead. When requirements or approach are ambiguous, ask before writing code.
- Every change gets its own branch and pull request; no direct commits to main.
- PRs are merged with a merge commit, never squashed or rebased.
- Commits are atomic: one logical change per commit.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, …).

## Code Style

- ruff with all rules enabled and pragmatic ignores (see `pyproject.toml`).
- Comments explain *why* code does something, not *what* it does.
