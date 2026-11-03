set positional-arguments

# Show available recipes
default:
    @just --list

# Install the project and dev tools
sync:
    uv sync

# Run the CLI locally, passing any arguments through
run *args:
    uv run whichowns "$@"

# Run tests
test:
    uv run pytest

# Format code
fmt:
    uv run ruff format src/ tests/

# Lint and auto-fix
lint:
    uv run ruff check --fix src/ tests/

# Type check
type:
    uv run ty check src/

# Run every check without changing files
check:
    uv run ruff format --check src/ tests/
    uv run ruff check src/ tests/
    uv run ty check src/
    uv run pytest
