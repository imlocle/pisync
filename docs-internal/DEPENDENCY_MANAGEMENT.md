# Dependency Management Guide

## Overview

PiSync uses **pip-tools** for professional dependency management. This provides:

- ✅ **Reproducible builds** - Exact versions locked in `.txt` files
- ✅ **Separated concerns** - Production vs development dependencies
- ✅ **Easy updates** - Update-friendly `.in` files + compiled `.txt` lock files
- ✅ **Security** - Easy to audit and patch specific packages
- ✅ **Transitive dependency tracking** - All sub-dependencies documented

## File Structure

```
requirements.in          # Top-level production deps (no versions)
requirements.txt        # Locked production deps (auto-generated)
requirements-dev.in     # Development deps with production inherited
requirements-dev.txt    # Locked dev deps (auto-generated)
```

## Installation

### First Time Setup

```bash
# Install all development dependencies
pip install -r requirements-dev.txt

# Or just production dependencies
pip install -r requirements.txt
```

### Using in Virtual Environment

```bash
# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install all development deps
pip install -r requirements-dev.txt
```

## Updating Dependencies

### Update a Specific Package

Only available production packages are automatically locked. To update:

```bash
# 1. Edit requirements.in with new version
# Example: change `paramiko>=3.5.1` to `paramiko>=4.0.0`

# 2. Recompile lock files
pip-compile requirements.in -o requirements.txt
pip-compile requirements-dev.in -o requirements-dev.txt

# 3. Verify and commit
pip install -r requirements.txt
git add requirements.txt requirements-dev.txt
git commit -m "Update dependencies: paramiko to 4.0.0"
```

### Update All Dependencies to Latest Compatible

```bash
# Upgrade to latest compatible versions
pip-compile requirements.in -o requirements.txt --upgrade
pip-compile requirements-dev.in -o requirements-dev.txt --upgrade

# Test that everything still works
pytest

# Commit changes
git add requirements*.txt
git commit -m "Update all dependencies to latest compatible versions"
```

### Batch Update with Version Constraints

```bash
# Update all packages matching pattern
pip-compile requirements.in -o requirements.txt --upgrade-package "pyside6" --upgrade-package "paramiko"
pip-compile requirements-dev.in -o requirements-dev.txt --upgrade-package "pytest"
```

## Adding New Dependencies

### Adding to Production Dependencies

```bash
# 1. Edit requirements.in
# Add new package (e.g., `requests>=2.28.0`)

# 2. Recompile
pip-compile requirements.in -o requirements.txt

# 3. Install and test
pip install -r requirements.txt
python -c "import requests; print(requests.__version__)"

# 4. Commit
git add requirements.in requirements.txt
git commit -m "Add requests library for API calls"
```

### Adding to Development Dependencies

```bash
# 1. Edit requirements-dev.in
# Add under appropriate group (Testing, Code quality, Build & distribution)

# 2. Recompile (remember it includes requirements.in)
pip-compile requirements-dev.in -o requirements-dev.txt

# 3. Install
pip install -r requirements-dev.txt

# 4. Test
black --version  # or whatever tool you added

# 5. Commit
git add requirements-dev.in requirements-dev.txt
git commit -m "Add black code formatter to dev dependencies"
```

## CI/CD Integration

GitHub Actions automatically uses these files:

```yaml
# .github/workflows/publish.yml
- name: Install dependencies
  run: |
    pip install --upgrade pip
    pip install -r requirements-dev.txt
```

## Comparison: pip-tools vs Alternatives

### pip-tools (Current)

**Pros:**

- ✅ Simple, lightweight
- ✅ Pure pip-compatible
- ✅ Fast compilation
- ✅ Human-readable lock files

**Cons:**

- No virtual environment management

### Poetry (Alternative)

**Pros:**

- Integrated virtual environment management
- More comprehensive

**Cons:**

- Different tool ecosystem (not pure pip)

### Pipenv (Legacy)

Not recommended - slower and less maintained

## Troubleshooting

### "pip-compile command not found"

```bash
# Install pip-tools
pip install pip-tools
```

### Compilation fails with conflicts

```bash
# Check for incompatible version constraints
pip-compile --verbose requirements.in

# May need to relax version constraints in requirements.in
# Example: `pyside6>=6.10.0` instead of `pyside6==6.10.0`
```

### Package versions too old/new

Edit `requirements.in`:

```ini
# Tighter constraint
paramiko>=3.5.1,<4.0.0

# Or very specific
pyside6==6.10.0
```

Then recompile:

```bash
pip-compile requirements.in -o requirements.txt
```

## Security Updates

When security patches are released:

```bash
# Update specific package
pip-compile requirements.in --upgrade-package paramiko -o requirements.txt

# Install and test
pip install -r requirements.txt
python -m pytest

# Commit
git commit -m "Security: Update paramiko to 3.5.2 (fixes CVE-XXXX)"
```

## Workflow Diagram

```
requirements.in --> pip-compile --> requirements.txt
(human)              (tool)         (machine, git)
                                    pip install -r

requirements-dev.in --> pip-compile --> requirements-dev.txt
(human)                 (tool)        (machine, git)
                                      pip install -r
```

## FAQ

**Q: Should I commit .txt files to git?**
A: Yes! Lock files should be committed so everyone has reproducible installs.

**Q: Can I install from requirements.in directly?**
A: No, use `.txt` files for reproducibility. Keep `.in` files for editing.

**Q: How often should I update?**
A: Monthly for security patches, quarterly for feature updates.

**Q: What if someone adds a dependency wrong?**
A: Code review catches it. `pip-compile` will fail if there are conflicts.

## Next Steps

- Review `requirements.txt` and `requirements-dev.txt` periodically
- Set up Dependabot for automated security alerts
- Monitor for deprecated packages
- Test after any dependency updates
