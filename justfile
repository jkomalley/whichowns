set positional-arguments

# Show available recipes
default:
    @just --list

# Install the project, dev tools and git hooks
setup:
    uv sync
    uv run pre-commit install

# Install the project and dev tools
sync *args:
    uv sync "$@"

# Run the CLI locally, passing any arguments through
run *args:
    uv run whichowns "$@"

# Run tests
test *args:
    uv run --locked pytest "$@"

# Run unit tests with the 100% coverage gate
cov:
    uv run --locked pytest --cov-fail-under=100

# pytest exits 5 when it collects no tests, which is expected until the first
# integration test exists.

# Run integration tests
integration *args:
    uv run --locked pytest -m integration --no-cov "$@" || [ $? -eq 5 ]

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
check:
    uv run --locked ruff format --check src/ tests/
    uv run --locked ruff check src/ tests/
    uv run --locked ty check src/ tests/
    uv run --locked pytest --cov-fail-under=100
