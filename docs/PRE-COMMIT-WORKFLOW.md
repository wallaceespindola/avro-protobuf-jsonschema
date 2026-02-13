# Pre-commit Hooks Workflow Guide

## Visual Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Developer Workflow                            │
└─────────────────────────────────────────────────────────────────┘

1. EDIT FILES
   ├─ Modify Python files
   ├─ Edit configuration (YAML, JSON, TOML)
   └─ Update documentation (Markdown)
       ↓
2. STAGE CHANGES
   └─ git add .
       ↓
3. COMMIT
   └─ git commit -m "message"
       ↓
4. PRE-COMMIT HOOKS TRIGGER (automatic)
   ├─ File Checks
   │  ├─ YAML syntax validation
   │  ├─ JSON syntax validation
   │  ├─ TOML syntax validation
   │  ├─ Line ending fixes (auto-fix)
   │  └─ Whitespace cleanup (auto-fix)
   │     ↓
   ├─ Security Checks
   │  ├─ Private key detection
   │  ├─ Bandit security scan
   │  └─ Large file detection
   │     ↓
   ├─ Python Formatting
   │  ├─ Black formatter (auto-fix)
   │  └─ isort import sorting (auto-fix)
   │     ↓
   ├─ Linting & Quality
   │  ├─ Flake8 style checking
   │  ├─ Pydocstyle docstring checking
   │  └─ MyPy type checking
   │     ↓
   └─ Markup Validation
      ├─ yamllint YAML checking
      └─ markdownlint Markdown checking
          ↓
5. RESULT
   ├─ IF ALL PASS
   │  └─ Commit accepted ✓
   │     └─ Code is pushed to repository
   │        ↓
   │     5a. GITHUB ACTIONS (CI/CD)
   │         ├─ Run pre-commit again
   │         ├─ Run pytest
   │         ├─ Upload coverage
   │         └─ Status reported on PR
   │
   └─ IF ANY FAIL
      ├─ Auto-fixed issues
      │  └─ Files modified by black, isort, etc.
      │     └─ Need: git add . && git commit
      │
      └─ Manual fix issues
         ├─ Read error messages
         ├─ Fix code/config manually
         ├─ git add .
         └─ git commit
            ↓ (hooks run again)
```

## Hook Categories and Sequence

```
SEQUENCE OF EXECUTION
─────────────────────

Phase 1: Basic File Validation (Fast)
  1. end-of-file-fixer (auto-fix)
  2. trailing-whitespace (auto-fix)
  3. check-yaml
  4. check-json
  5. check-toml
  6. check-xml
  7. forbid-crlf (auto-fix)
  8. forbid-tabs (auto-fix)

Phase 2: Security & Safety (Medium)
  9. detect-private-key
  10. check-merge-conflict
  11. check-large-files
  12. bandit (security scan)

Phase 3: Code Quality (Slower)
  13. black (formatter, auto-fix)
  14. isort (import sorter, auto-fix)
  15. flake8 (linter)
  16. pydocstyle (docstrings)
  17. mypy (type checking) - Slowest

Phase 4: Documentation (Medium)
  18. yamllint
  19. markdownlint

Total: ~19 hooks
Typical runtime: 5-30 seconds (first run)
```

## Decision Tree for Hook Failures

```
HOOK FAILED?
    ↓
    ├─── Can it auto-fix? (black, isort, etc.)
    │    ├─ YES → Review git diff → git add . → git commit
    │    └─ NO → Continue below
    │
    └─── Read the error message
         ↓
         ├─ Syntax error (YAML, JSON, etc.)?
         │  └─ Fix file syntax → git add . → git commit
         │
         ├─ Flake8 error (PEP 8)?
         │  └─ Read flake8 documentation → Fix code → git add . → git commit
         │
         ├─ MyPy error (type checking)?
         │  └─ Add type hints or # type: ignore → git add . → git commit
         │
         ├─ Bandit warning (security)?
         │  └─ Review security issue → Fix or suppress → git add . → git commit
         │
         ├─ Docstring issue (pydocstyle)?
         │  └─ Add/fix docstrings → git add . → git commit
         │
         └─ Other?
            └─ Check tool documentation
               └─ Fix issue → git add . → git commit
```

## Common Scenarios

### Scenario 1: Code Format Issue
```bash
$ git commit -m "Add new feature"
  → black reformats file
  → isort reorders imports
  
  Review changes:
$ git diff
  
  Stage and retry:
$ git add .
$ git commit -m "Add new feature"
  → All checks pass ✓
```

### Scenario 2: Type Error
```bash
$ git commit -m "Refactor function"
  → mypy detects type mismatch
  
  Fix the code:
$ vim app/main.py  # Add type hints
  
  Retry:
$ git add .
$ git commit -m "Refactor function"
  → All checks pass ✓
```

### Scenario 3: YAML Syntax Error
```bash
$ git commit -m "Update config"
  → yamllint detects bad syntax
  
  Fix the YAML:
$ vim .github/workflows/ci.yml
  
  Retry:
$ git add .
$ git commit -m "Update config"
  → All checks pass ✓
```

## Manual Hook Execution

```bash
# Run all hooks (required before commit)
$ pre-commit run --all-files

# Run only Python-related hooks
$ pre-commit run black mypy flake8 --all-files

# Run only on changed files (what happens on commit)
$ pre-commit run

# Run with verbose output for debugging
$ pre-commit run -v --all-files

# Clean cache and rerun
$ pre-commit clean
$ pre-commit run --all-files
```

## GitHub Actions Integration

```
PUSH TO GITHUB
    ↓
.github/workflows/pre-commit.yml TRIGGERED
    ├─ Run pre-commit on all files
    ├─ Run mypy type checking
    ├─ Run pytest with coverage
    ├─ Upload coverage to codecov
    └─ Report status on PR/commit
       ↓
       ├─ ALL PASS ✓
       │  └─ PR shows green checkmark
       │
       └─ FAIL ✗
          └─ PR shows red X
             └─ Developer must fix locally
                └─ Push fixes
                   └─ GitHub Actions runs again
```

## Setup Timeline

```
TIME    ACTION
────    ──────
0m      Run: bash .pre-commit-setup.sh
        ├─ Install pre-commit (if needed)
        ├─ Install git hooks
        └─ Run initial full scan

5-10m   First pre-commit run complete
        └─ May find and fix many issues
           └─ Review changes carefully

        Developer fixes remaining issues manually
        └─ Push fixes to repository

        Ready for development
        └─ Hooks run on every commit automatically
```

## Performance Expectations

```
SCENARIO                          TIME      NOTES
────────                          ────      ─────
First run (all files)             30-60s    Downloads packages, caches deps
Typical commit (changed files)    5-15s     Cached, faster
Black/isort only                  2-5s      Very fast
Full suite on large project       20-30s    MyPy can be slow
After pre-commit autoupdate       Variable  May need new downloads

TIP: Use 'pre-commit run' for changed files only during development
     Use 'pre-commit run --all-files' in CI/CD and before pushing
```

## Troubleshooting Flowchart

```
PRE-COMMIT NOT WORKING?
    ↓
    ├─ Is pre-commit installed?
    │  └─ NO → pip install pre-commit
    │
    ├─ Are hooks installed?
    │  └─ NO → pre-commit install
    │
    ├─ Is .pre-commit-config.yaml valid?
    │  └─ INVALID → bash .pre-commit-validate.sh
    │
    ├─ Are dependencies installed?
    │  └─ NO → pip install -e ".[dev]"
    │
    ├─ Is PATH correct?
    │  └─ NO → source venv/bin/activate
    │
    └─ Something else?
       └─ Run: pre-commit run -v --all-files
          └─ Check error messages
             └─ Consult documentation
```

## Integration Checklist

- [ ] Install pre-commit: `pip install pre-commit`
- [ ] Run setup script: `bash .pre-commit-setup.sh`
- [ ] Validate config: `bash .pre-commit-validate.sh`
- [ ] Test hooks: `pre-commit run --all-files`
- [ ] Fix any issues found
- [ ] Read `PRE-COMMIT.md` for full documentation
- [ ] Configure IDE integration (optional)
- [ ] Enable GitHub Actions workflow
- [ ] Commit all changes
- [ ] Share with team
- [ ] Periodically update hooks: `pre-commit autoupdate`

## Key Concepts

### Hook Stages
- **commit**: Run on `git commit` (default)
- **push**: Run on `git push` (configured)
- **manual**: Run only with `pre-commit run --hook-stage manual`

### Skip a Hook
```bash
# Temporarily
git commit --no-verify

# Permanently (edit config)
# Comment out hook in .pre-commit-config.yaml
```

### Auto-fix vs Manual
- **Auto-fix**: black, isort, end-of-file-fixer, trailing-whitespace
  - Files are modified automatically
  - Requires: `git add . && git commit`
  
- **Manual fix**: flake8, mypy, bandit
  - Developer must read and fix errors
  - Then: `git add . && git commit`

### Local vs CI/CD
- **Local**: Runs on developer machine before push
- **CI/CD**: Runs on GitHub Actions after push
  - Provides additional feedback
  - Can block merge if fails

---

## Questions?

See other docs:
- `PRE-COMMIT.md` - Main documentation
- `PRE-COMMIT-SETUP.md` - Setup guide
- `PRE-COMMIT-QUICKREF.md` - Quick reference
- `.pre-commit-config.yaml` - Configuration details
