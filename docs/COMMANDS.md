# Quick Command Reference

All `make` commands and development workflows in one place.

## 📋 Table of Contents

- [Setup & Installation](#setup--installation)
- [Development Server](#development-server)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Examples & Clients](#examples--clients)
- [Docker](#docker)
- [Cleanup](#cleanup)
- [Information](#information)

---

## Setup & Installation

### `make setup`
Full project setup (run this first)
- Creates virtual environment with uv
- Installs all dependencies
- Creates .env file if not exists

### `make install`
Install production dependencies only

### `make install-dev`
Install with development dependencies

### `make sync`
Sync dependencies from pyproject.toml

### `make update`
Update all dependencies to latest versions

---

## Development Server

### `make run` or `make dev`
Start FastAPI development server with auto-reload
- URL: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### `make run-prod`
Start production server (4 workers, no reload)

---

## Protobuf

### `make proto`
Generate Python code from Protobuf schema
- Input: `schemas/user.proto`
- Output: `schemas/user_pb2.py`, `schemas/user_pb2.pyi`

### `make proto-clean`
Remove generated Protobuf files

---

## Testing

### `make test`
Run all tests with pytest

### `make test-cov`
Run tests with coverage report
- Generates HTML report in `htmlcov/`
- Generates XML report for CI
- Shows terminal coverage summary

### `make test-watch`
Run tests in watch mode (auto-rerun on changes)

### `make test-fast`
Run tests, stop on first failure

### `make test-failed`
Re-run only failed tests from last run

### `make test-verbose`
Run tests with extra output

### `make test-json`
Run only JSON endpoint tests

### `make test-avro`
Run only Avro endpoint tests

### `make test-protobuf`
Run only Protobuf endpoint tests

---

## Code Quality

### `make lint`
Run all linters (flake8 + mypy)

### `make format`
Format code with black and isort

### `make format-check`
Check formatting without modifying files

### `make type-check`
Run type checking with mypy

### `make check`
Run all checks (format + lint + type)

### `make ci`
Run all CI checks (check + test with coverage)

---

## Examples & Clients

### `make examples`
Run all standalone examples
- Avro example
- JSON Schema example
- Protobuf example (if generated)

### `make example-avro`
Run Avro example only

### `make example-json`
Run JSON Schema example only

### `make example-protobuf`
Run Protobuf example only

### `make clients`
Test all API endpoints (requires server running)
- Tests JSON endpoint
- Tests Avro endpoint
- Tests Protobuf endpoint (if generated)

---

## Docker

### `make docker`
Build Docker image
- Image name: `schemas-demo:latest`

### `make docker-up`
Start containers with docker-compose
- Builds image
- Starts API service on port 8000

### `make docker-down`
Stop and remove containers

### `make docker-logs`
View container logs (follow mode)

### `make docker-shell`
Open bash shell in running container

---

## Cleanup

### `make clean`
Clean generated files and caches
- Removes `__pycache__`
- Removes `.pytest_cache`
- Removes `.mypy_cache`
- Removes coverage reports

### `make clean-proto`
Remove generated Protobuf files

### `make clean-all`
Clean everything including virtual environment

---

## Information

### `make help`
Show all available commands (this is the default target)

### `make info`
Show project information
- Python version
- uv version
- Virtual environment status
- .env file status
- Protobuf code status
- API endpoints

### `make deps`
Show installed dependencies with versions

### `make tree`
Show project tree structure (requires `tree` command)

---

## Common Workflows

### First Time Setup

```bash
make setup           # Setup project
make proto          # Generate Protobuf code
nano .env           # Edit your author info
make dev            # Start development server
```

### Daily Development

```bash
make dev            # Start server
# In another terminal:
make test-watch     # Auto-run tests on changes
```

### Before Committing

```bash
make format         # Format code
make ci             # Run all checks
```

### Testing Endpoints

```bash
make dev            # Start server
# In another terminal:
make clients        # Test all endpoints
```

### Running Examples

```bash
make examples       # Run all standalone examples
```

### Docker Development

```bash
make docker-up      # Start in Docker
make docker-logs    # View logs
make docker-down    # Stop containers
```

---

## Color Output

Commands use colors to make things easier to read:
- 🔵 **Blue**: Info messages
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warnings
- 🔴 **Red**: Errors

---

## Environment Variables

All commands respect `.env` file settings:
- Author information
- Application settings
- See `.env.example` for available options

---

## Tips

1. **Run `make help`** to see all commands with descriptions
2. **Use `make info`** to check project status
3. **Commands use `uv run`** to activate the virtual environment
4. **Most commands use colors** to make output easier to read
5. **Generated files are excluded** from linting and formatting

---

## Shell Completion

To enable tab completion for make commands:

```bash
# Add to ~/.bashrc or ~/.zshrc
complete -W "$(make -qp | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | sort -u)" make
```

---

## Need Help?

- Run `make help` for command list
- Check [README.md](README.md) for full documentation
- Check [TESTING.md](TESTING.md) for testing guide
- See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

---

**Last Updated**: 2026-02-10
**Total Commands**: 50+
