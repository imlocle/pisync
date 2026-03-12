# PiSync Packaging & Distribution Guide

## Overview

This guide walks through building and distributing PiSync as both a PyPI package and standalone executable.

## Files Created

- **pyproject.toml** - Modern Python packaging configuration with metadata
- **MANIFEST.in** - Specifies non-Python files to include in distributions
- **Makefile** - Convenient build commands
- **scripts/build.sh** - Build wheel and source distributions
- **scripts/build_exe.sh** - Build standalone executable with PyInstaller
- **scripts/setup_dev.sh** - Setup development environment
- **.github/workflows/publish.yml** - CI/CD pipeline for automated publishing

## Quick Start

### 1. Setup Development Environment

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup development environment
./scripts/setup_dev.sh

# Or manually
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test,build]"
```

### 2. Build Distributions

#### Option A: Using Make

```bash
# Build both wheel and source distributions
make build

# Build and publish to PyPI
make publish

# Build and publish to TestPyPI (for testing)
make publish-test
```

#### Option B: Using Scripts

```bash
# Build wheel and source distributions
./scripts/build.sh

# Build standalone executable
./scripts/build_exe.sh
```

#### Option C: Manual Build

```bash
python -m build
twine check dist/*
```

## Distribution Types

### 1. Source Distribution (.tar.gz)

- Contains all source code
- Users must have Python installed
- Build: `python -m build --sdist`

### 2. Wheel (.whl)

- Binary distribution, faster to install
- Ready to use without compilation
- Build: `python -m build --wheel`

### 3. Standalone Executable (.exe/.app/.bin)

- No dependencies required
- Self-contained package
- Build: `./scripts/build_exe.sh`

## Testing Distributions

Before publishing, test locally:

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from local wheel
pip install dist/pisync-*.whl

# Run the application
pisync
```

## Publishing to PyPI

### Setup OneTime

1. Create account at https://pypi.org
2. Create ~/.pypirc:

```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi_...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi_...
```

3. Or set environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi_xxxx
```

### Publishing Steps

1. **Update version** in pyproject.toml
2. **Build distributions**:
   ```bash
   make build
   ```
3. **Test on TestPyPI** (optional but recommended):
   ```bash
   make publish-test
   ```
4. **Publish to PyPI**:
   ```bash
   make publish
   ```
5. **Create git tag**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Automated Publishing with GitHub Actions

The `.github/workflows/publish.yml` workflow automatically:

- Runs on version tags (v*.*.\*)
- Tests on multiple Python versions (3.9-3.13)
- Runs linting and type checks
- Builds distributions
- Publishes to PyPI
- Creates GitHub release with distribution files

**Setup required:**

1. Add PyPI API token as GitHub secret: `PYPI_API_TOKEN`
2. Update email/author in pyproject.toml
3. Push tag: `git push origin v1.0.0`

## Verifying Distributions

```bash
# Check distribution integrity
twine check dist/*

# List contents
# For wheel:
unzip -l dist/pisync-*.whl

# For source:
tar -tzf dist/pisync-*.tar.gz
```

## Configuration Update Checklist

Before each release:

- [ ] Update version in `pyproject.toml` and `main.py`
- [ ] Update `README.md` with new features
- [ ] Update `CHANGELOG.md` or add release notes
- [ ] Run all tests: `make test`
- [ ] Run linting: `make lint`
- [ ] Build and test locally: `make build && pip install dist/pisync-*.whl`
- [ ] Create git tag and push
- [ ] Verify PyPI release at https://pypi.org/project/pisync/

## Troubleshooting

### "ModuleNotFoundError" when installing

- Ensure `include-package-data = true` in pyproject.toml
- Check MANIFEST.in includes all necessary files
- Verify file paths in pyproject.toml match your structure

### PyPI upload fails with "Invalid distribution"

```bash
# Check distribution validity
twine check dist/*

# Common issues: missing files, version conflicts, encoding problems
```

### GitHub Actions workflow not running

- Verify PyPI API token is set as secret
- Check tag format: should be `v*.*.*` (e.g., `v1.0.0`)
- Ensure workflow file is in default branch

## Version Bumping

Use semantic versioning: MAJOR.MINOR.PATCH

```bash
# Patch release (bug fix)
# Update version: 1.0.0 → 1.0.1

# Minor release (new feature)
# Update version: 1.0.0 → 1.1.0

# Major release (breaking change)
# Update version: 1.0.0 → 2.0.0
```

## Installation Methods

Users can install PiSync via:

```bash
# From PyPI (recommended)
pip install pisync

# From wheel file
pip install pisync-1.0.0-py3-none-any.whl

# From source
pip install pisync-1.0.0.tar.gz

# From source (development)
pip install -e git+https://github.com/yourusername/pisync.git

# Standalone executable
# Download from GitHub releases or run: ./pisync
```

## Next Steps

1. Update author info in `pyproject.toml`
2. Create GitHub repository if not already done
3. Add PyPI authentication tokens to GitHub
4. Test build locally with `make build`
5. Create first release and push to PyPI

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [Build Tool Documentation](https://python-build.readthedocs.io/)
- [Twine Documentation](https://twine.readthedocs.io/)
