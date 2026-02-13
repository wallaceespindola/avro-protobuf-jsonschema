# Pre-commit Quick Reference

## One-liner Setup
```bash
pip install pre-commit && pre-commit install && pre-commit run --all-files
```

## Most Common Commands

```bash
# Setup
bash .pre-commit-setup.sh

# Run on all files
pre-commit run --all-files

# Run on changes only (staged)
pre-commit run

# Run specific hook
pre-commit run black --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks
git commit --no-verify
```

## What Each Hook Does

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| black | Format Python code | ✅ |
| isort | Sort imports | ✅ |
| flake8 | PEP 8 linting | ❌ |
| mypy | Type checking | ❌ |
| bandit | Security checks | ❌ |
| pydocstyle | Docstring style | ❌ |
| yamllint | YAML validation | ✅ |
| markdownlint | Markdown validation | ✅ |
| end-of-file-fixer | Fix line endings | ✅ |
| trailing-whitespace | Remove trailing spaces | ✅ |
| check-yaml | Validate YAML | ❌ |
| check-json | Validate JSON | ❌ |
| check-toml | Validate TOML | ❌ |
| detect-private-key | Find secrets | ❌ |

## When Hooks Fail

1. **Auto-fix hooks** (black, isort, etc.):
   - Review changes: `git diff`
   - Stage changes: `git add .`
   - Retry commit: `git commit`

2. **Check-only hooks** (flake8, mypy, etc.):
   - Read error messages carefully
   - Fix issues manually
   - Stage changes: `git add .`
   - Retry commit: `git commit`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "command not found" | Run `pip install -e ".[dev]"` |
| Hook is slow | Add file patterns to `exclude:` in config |
| Need to skip hook | Use `git commit --no-verify` (discouraged) |
| Update specific hook | Run `pre-commit autoupdate --repo <url>` |

## Files Created

- `.pre-commit-config.yaml` - Main configuration
- `.pre-commit-setup.sh` - Automated setup script
- `.pre-commit-validate.sh` - Configuration validator
- `PRE-COMMIT.md` - Full documentation
- `PRE-COMMIT-SETUP.md` - Detailed setup guide
- `.github/workflows/pre-commit.yml` - GitHub Actions workflow

## IDE Integration

### VS Code
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm
Settings → Tools → Python Integrated Tools → Enable "Run pre-commit hooks before commit"

## Performance Tips

```bash
# Cache results
pre-commit run --all-files

# Only changed files
pre-commit run

# Skip slow hooks
pre-commit run --hook-stage manual

# Run in parallel
pre-commit run -j 4
```

## Documentation

- Full guide: `cat PRE-COMMIT.md`
- Setup details: `cat PRE-COMMIT-SETUP.md`
- Config validation: `bash .pre-commit-validate.sh`
- Help: `pre-commit --help`

## Requirements

- Python 3.11+
- pip install pre-commit
- Run: `bash .pre-commit-setup.sh`

That's it! Pre-commit hooks are now active on every commit.
