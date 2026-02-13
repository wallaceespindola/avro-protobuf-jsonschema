# Pre-commit Hooks Setup Summary

## Files Created

### 1. `.pre-commit-config.yaml`
The main pre-commit configuration file that defines all hooks to run. Includes:
- **General file checks**: YAML, JSON, TOML, XML validation, line ending fixes, merge conflict detection
- **Python formatting**: Black (code formatter), isort (import sorter)
- **Python linting**: flake8 (with bugbear and comprehensions), bandit (security), pydocstyle (docstrings)
- **Type checking**: MyPy
- **Markup linting**: yamllint, markdownlint
- **Git checks**: Local hook for requirements verification

### 2. `.pre-commit-setup.sh`
Executable setup script that:
- Checks if pre-commit is installed
- Installs pre-commit if needed
- Installs all hooks
- Runs initial check on all files
- Provides usage instructions

### 3. `.pre-commit-validate.sh`
Executable validation script that:
- Validates the `.pre-commit-config.yaml` syntax
- Checks pre-commit installation
- Verifies configuration is valid

### 4. `PRE-COMMIT.md`
Full documentation including:
- Installation instructions
- Usage examples
- List of all configured hooks with descriptions
- Troubleshooting guide
- Configuration file references
- Common commands
- Best practices

### 5. `.github/workflows/pre-commit.yml`
GitHub Actions workflow that:
- Runs pre-commit checks on push and pull requests
- Runs additional code quality checks (mypy, pytest with coverage)
- Uploads coverage reports to codecov

### 6. `pyproject.toml` - Updated
Added missing dev dependencies:
- `bandit>=1.7.5` - Security linting
- `pydocstyle>=6.3.0` - Docstring style checking
- `pre-commit>=3.5.0` - Pre-commit framework
- `yamllint>=1.33.0` - YAML linting
- `markdownlint-cli>=0.37.0` - Markdown linting
- `flake8-bugbear>=23.12.0` - Additional flake8 checks
- `flake8-comprehensions>=3.14.0` - Comprehension checks

## Quick Start

### Initial Setup
```bash
# Option 1: Use the setup script
bash .pre-commit-setup.sh

# Option 2: Manual setup
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

### Validate Configuration
```bash
bash .pre-commit-validate.sh
```

### Run Hooks Manually
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run on changed files only
pre-commit run
```

## Hook Execution Flow

```
1. User runs: git commit
2. Pre-commit hooks run automatically:
   - File syntax validation (YAML, JSON, TOML, XML)
   - Line ending and whitespace fixes
   - Security checks (detect private keys, bandit)
   - Code formatting (black, isort) - auto-fixes
   - Linting (flake8, pydocstyle)
   - Type checking (mypy)
   - Markdown/YAML validation
3. If hooks fail:
   - Some issues are auto-fixed
   - Review changes and git add them
   - Re-run: git commit
4. If all pass: commit proceeds
```

## Available Commands

```bash
# Setup and validation
bash .pre-commit-setup.sh        # Setup all hooks
bash .pre-commit-validate.sh     # Validate configuration

# Running hooks
pre-commit run --all-files       # Run all hooks on all files
pre-commit run black --all-files # Run specific hook
pre-commit run                   # Run on staged changes

# Maintenance
pre-commit autoupdate            # Update all hooks to latest versions
pre-commit clean                 # Remove pre-commit cache
pre-commit uninstall             # Remove hooks

# Debugging
pre-commit run -v                # Verbose output
pre-commit validate-config       # Validate YAML syntax
```

## Hooks Explained

### Formatting Hooks (Auto-fix)
- **black**: Formats Python code
- **isort**: Sorts imports

### Validation Hooks (Check only)
- **check-yaml**: Validates YAML syntax
- **check-json**: Validates JSON syntax
- **check-toml**: Validates TOML syntax
- **check-xml**: Validates XML syntax

### Quality Hooks (Can fail)
- **flake8**: PEP 8 compliance and error detection
- **mypy**: Static type checking
- **bandit**: Security vulnerability detection
- **pydocstyle**: Docstring style checking
- **yamllint**: YAML style checking
- **markdownlint**: Markdown style checking

### Cleanup Hooks (Auto-fix)
- **end-of-file-fixer**: Ensures files end with newline
- **trailing-whitespace**: Removes trailing whitespace
- **forbid-crlf**: Converts CRLF to LF
- **forbid-tabs**: Replaces tabs with spaces

## Configuration Files

All tool configurations are in `pyproject.toml` except:
- `.flake8`: Flake8 configuration (doesn't support pyproject.toml)
- `.pre-commit-config.yaml`: Pre-commit hook definitions

## Tips and Tricks

### Auto-fix Issues
```bash
# Format and sort imports
black .
isort .

# Then commit
git add .
git commit
```

### Skip Hooks (Use with caution)
```bash
git commit --no-verify
```

### Run Only Specific Hooks
Edit `.pre-commit-config.yaml` and comment out unwanted hooks:
```yaml
# - repo: https://github.com/PyCQA/mypy
#   hooks:
#     - id: mypy
```

### Exclude Files from Hooks
Add `exclude:` pattern to hook configuration:
```yaml
- repo: https://github.com/psf/black
  hooks:
    - id: black
      exclude: ^migrations/
```

## Integration with IDEs

### VS Code
Install extensions:
- Python
- Pylance
- Black Formatter
- isort

Configure settings:
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm
- Enable "Run pre-commit hooks before commit"
- Settings → Tools → Python Integrated Tools → Default Test Runner (pytest)

## Troubleshooting

### Pre-commit fails with "command not found"
Install all dependencies:
```bash
pip install -e ".[dev]"
```

### MyPy is slow
Add `exclude:` pattern to skip large files:
```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  hooks:
    - id: mypy
      exclude: ^vendor/
```

### Hook modifies files and fails
This is expected. The fix the modified files and commit:
```bash
git add .
git commit
```

### Need to update specific hook
```bash
pre-commit autoupdate --repo https://github.com/psf/black
```

## CI/CD Integration

The `.github/workflows/pre-commit.yml` GitHub Actions workflow automatically:
- Runs pre-commit on all push and pull requests
- Uploads coverage reports
- Provides feedback on code quality

## Next Steps

1. **Install hooks**:
   ```bash
   bash .pre-commit-setup.sh
   ```

2. **Run on all files**:
   ```bash
   pre-commit run --all-files
   ```

3. **Fix any issues** - some hooks auto-fix, others require manual fixes

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "Fix pre-commit issues"
   ```

5. **Read the documentation**:
   ```bash
   cat PRE-COMMIT.md
   ```

## Resources

- [Pre-commit documentation](https://pre-commit.com/)
- [Black documentation](https://black.readthedocs.io/)
- [isort documentation](https://pycqa.github.io/isort/)
- [Flake8 documentation](https://flake8.pycqa.org/)
- [MyPy documentation](https://mypy.readthedocs.io/)
- [Bandit documentation](https://bandit.readthedocs.io/)
- [Yamllint documentation](https://yamllint.readthedocs.io/)

## Support

For issues or questions:
1. Check `PRE-COMMIT.md` for detailed documentation
2. Run `pre-commit --help` for command help
3. Check `.pre-commit-config.yaml` for hook configurations
4. Consult individual tool documentation
