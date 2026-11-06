# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`whichowns` is a CLI that finds which package manager owns a command. Python 3.11+ (developed on 3.15), src layout, managed with `uv`.

## Commands

Tasks run through `just`. Apart from `default` and `check`, recipes are thin wrappers around `uv` commands; see `justfile`.

- `just setup`: install the project, dev tools and git hooks
- `just sync [args]`: install the project and dev tools
- `just run [args]`: run the CLI
- `just test [args]`: run unit tests
- `just integration [args]`: run integration tests
- `just cov`: run unit tests with the 100% coverage gate
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

## Releasing

1. In a PR, bump the version with `uv version`, rename `[Unreleased]` in `CHANGELOG.md` to `[x.y.z] - YYYY-MM-DD`, add a new empty `[Unreleased]`, and update the compare links. CD stops if the new section has no entries.
2. After it merges, tag `main`: `git fetch origin && git tag vx.y.z origin/main && git push origin vx.y.z`
3. The CD workflow checks the tag, runs CI, publishes to PyPI and creates the GitHub release.

If CD fails:

- **No code fix needed:** re-run the failed jobs.
- **Fix needed, and nothing is on PyPI yet:** fix it in a PR, delete the tag (`git push --delete origin vx.y.z` and `git tag -d vx.y.z`), and tag `main` again.
- **The published version has a bug:** bump the version. A published version can't be reused, so never move its tag.

## Code Style

- ruff with all rules enabled and pragmatic ignores (see `pyproject.toml`).
- Comments explain *why* code does something, not *what* it does.
