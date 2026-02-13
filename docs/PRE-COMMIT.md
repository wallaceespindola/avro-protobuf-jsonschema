# Pre-commit Hooks Documentation

This project uses [pre-commit](https://pre-commit.com/) to automatically check and fix code quality issues before commits are made.

## Installation

### 1. Install pre-commit

```bash
pip install pre-commit
```

Or using your package manager:
```bash
# macOS with Homebrew
brew install pre-commit

# Ubuntu/Debian
apt-get install pre-commit
```

### 2. Initialize hooks

Run the setup script:
```bash
bash .pre-commit-setup.sh
```

Or manually:
```bash
pre-commit install
pre-commit install --hook-type pre-push
```

## Usage

### Automatic Checking

Pre-commit hooks run automatically on `git commit`. If any checks fail, the commit is aborted and you need to fix the issues.

### Manual Checks

Run pre-commit on all files:
```bash
pre-commit run --all-files
```

Run a specific hook:
```bash
pre-commit run black --all-files
pre-commit run isort --all-files
pre-commit run mypy --all-files
```

### Skip Hooks

If you need to bypass pre-commit checks (not recommended):
```bash
git commit --no-verify
```

### Update Hooks

Update all hooks to their latest versions:
```bash
pre-commit autoupdate
```

## Configured Hooks

### File Checks
- **check-ast**: Verify Python files have valid syntax
- **check-yaml**: Check YAML files for syntax errors
- **check-json**: Check JSON files for syntax errors
- **check-toml**: Check TOML files for syntax errors
- **check-xml**: Check XML files for syntax errors
- **end-of-file-fixer**: Ensure files end with a newline
- **trailing-whitespace**: Remove trailing whitespace
- **detect-private-key**: Prevent committing private keys
- **check-large-files**: Prevent committing files larger than 1MB
- **check-merge-conflict**: Check for merge conflict markers
- **check-executables-have-shebangs**: Ensure scripts have shebangs
- **forbid-crlf**: Ensure Unix line endings (LF)
- **forbid-tabs**: Ensure no tabs are used

### Python Code Formatting
- **black**: Format code according to Black style guide
- **isort**: Sort imports alphabetically and by section

### Python Linting
- **flake8**: Check for PEP 8 compliance and common errors
  - Includes: flake8-bugbear, flake8-comprehensions
- **bandit**: Security linting to detect common vulnerabilities
- **pydocstyle**: Check docstring conventions (Google style)

### Type Checking
- **mypy**: Static type checker for Python

### YAML/Markdown
- **yamllint**: Check YAML files for style issues
- **markdownlint**: Check Markdown files for style issues

## Troubleshooting

### Hook fails with "command not found"

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Hook takes too long

Some hooks (like mypy) can be slow. You can modify `.pre-commit-config.yaml` to:
- Skip certain hooks: Remove or comment out the hook entry
- Run on fewer files: Add `files:` pattern to the hook
- Run only on changed files: Modify the hook to exclude `--all-files`

### Fix files automatically

Some hooks can auto-fix issues:
```bash
# Format with Black and isort
black .
isort .
```

Then commit the changes.

### Exclude files from hooks

You can exclude files in `.pre-commit-config.yaml` using the `exclude:` field:
```yaml
- repo: https://github.com/psf/black
  hooks:
    - id: black
      exclude: ^migrations/
```

## Configuration Files

- `.pre-commit-config.yaml`: Main configuration for pre-commit hooks
- `.flake8`: Flake8 linter configuration
- `.black`: Black formatter configuration (in `pyproject.toml`)
- `.mypy`: MyPy type checker configuration (in `pyproject.toml`)
- `.isort`: Isort import sorter configuration (in `pyproject.toml`)

## CI/CD Integration

Pre-commit hooks are also integrated with GitHub Actions. See `.github/workflows/` for more details.

## Resources

- [pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## Common Commands

```bash
# Setup hooks
bash .pre-commit-setup.sh

# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run mypy --all-files

# Update hooks to latest versions
pre-commit autoupdate

# Remove pre-commit hooks
pre-commit uninstall
pre-commit uninstall --hook-type pre-push

# Debug a specific hook
pre-commit run black --all-files -v
```

## Best Practices

1. **Always commit changes**: If a hook modifies files, commit the changes before retrying
2. **Review auto-fixes**: Check that auto-fixes are correct before committing
3. **Keep hooks updated**: Run `pre-commit autoupdate` periodically
4. **Use consistent style**: Follow the configured style guides in your IDE
5. **Test locally**: Run hooks locally before pushing to avoid CI failures
