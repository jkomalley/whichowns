set positional-arguments

# Show available recipes
default:
    @just --list

# Install the project and dev tools
sync *args:
    uv sync "$@"

# Run the CLI locally, passing any arguments through
run *args:
    uv run whichowns "$@"

# Run tests
test *args:
    uv run pytest "$@"

# Format code
fmt *args:
    uv run ruff format src/ tests/ "$@"

# Lint and auto-fix
lint *args:
    uv run ruff check --fix src/ tests/ "$@"

# Type check
type *args:
    uv run ty check src/ tests/ "$@"

# Run every check without changing files
check:
    uv run --locked ruff format --check src/ tests/
    uv run --locked ruff check src/ tests/
    uv run --locked ty check src/ tests/
    uv run --locked pytest
