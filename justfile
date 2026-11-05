set positional-arguments

# Show available recipes
default:
    @just --list

# Install the project, dev tools and git hooks
setup:
    uv sync --locked
    uv run --locked pre-commit install

# Install the project and dev tools
sync *args:
    uv sync "$@"

# Run the CLI locally, passing any arguments through
run *args:
    uv run --locked whichowns "$@"

# Run unit tests
test *args:
    uv run --locked pytest "$@"

# Run unit tests with the 100% coverage gate
cov:
    uv run --locked pytest --cov --cov-fail-under=100

# Run integration tests
# They run against a fresh non-editable build, as users install it, in a
# throwaway environment so .venv stays editable. --reinstall-package stops uv
# from reusing a cached build of older source.
integration *args:
    uv run --locked --isolated --no-editable --reinstall-package whichowns pytest -m integration tests/integration "$@"

# Format code
fmt *args:
    uv run --locked ruff format src/ tests/ "$@"

# Lint and auto-fix
lint *args:
    uv run --locked ruff check --fix src/ tests/ "$@"

# Type check
type *args:
    uv run --locked ty check src/ tests/ "$@"

# Run every check without changing files
check: (fmt "--check") (lint "--no-fix") type cov
