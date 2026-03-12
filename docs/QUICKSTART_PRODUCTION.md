# Quick Implementation Guide

> **Purpose:** Copy-paste templates to quickly implement production standards  
> **Time Estimate:** 2-4 hours for Phase 1  
> **Date:** March 12, 2026

---

## Phase 1: Quick Setup (Do This First) - 1-2 hours

### Step 1: Create `pyproject.toml`

Copy this file to your project root:

```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pisync"
version = "1.0.0"
description = "Automated media transfer to Raspberry Pi over SSH/SFTP"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "your.email@example.com"}]
repository = "https://github.com/yourusername/pisync"
keywords = ["raspberry-pi", "media", "sftp", "automation", "file-transfer"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: System :: File Systems",
    "Topic :: System :: Networking",
]

dependencies = [
    "paramiko>=3.5.1,<4.0",
    "pillow>=12.0.0,<13.0",
    "pydantic-settings>=2.5.2,<3.0",
    "pyside6>=6.10.0,<7.0",
    "send2trash>=1.8.3,<2.0",
    "watchdog>=5.0.3,<6.0",
    "python-dotenv>=1.0.1,<2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "black>=23.12.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "pylint>=3.0.0",
    "isort>=5.13.0",
    "bump2version>=1.0.1",
]

[project.scripts]
pisync = "src.main:main"

[tool.setuptools]
packages = ["src"]

[tool.setuptools.package-data]
src = ["../assets/**/*"]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
  | __pycache__
  | \.eggs
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
plugins = []

[tool.isort]
profile = "black"
line_length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=50",
    "-v",
]
markers = [
    "integration: marks tests as integration tests",
    "slow: marks tests as slow",
    "ui: marks tests that require UI",
]

[tool.coverage.run]
branch = true
omit = [
    "*/__init__.py",
    "*/tests/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Step 2: Create `setup.py`

Copy this to your project root (this is a wrapper that reads `pyproject.toml`):

```python
"""Setup configuration for PiSync."""
from setuptools import setup

setup()
```

### Step 3: Create `src/__version__.py`

Copy this to create a version file:

```python
"""Version information for PiSync."""

__title__ = "PiSync"
__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__copyright__ = "Copyright 2026 Your Name"
__url__ = "https://github.com/yourusername/pisync"
```

### Step 4: Update `main.py`

Replace the version string with your new version file:

```python
import sys

from PySide6.QtWidgets import QApplication

from src import __version__
from src.components.main_window import MainWindow
from src.components.splash_screen import SplashScreen
from src.utils.helper import get_path, rounded_icon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PiSync")
    app.setApplicationVersion(__version__)  # ← Use version file

    # ---- STYLESHEET ----
    stylesheet_path = get_path("assets/styles/modern_theme.qss")
    try:
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("No stylesheet found — using default theme.")

    # ---- SPLASH ----
    logo_path = get_path("assets/icons/pisync_logo.png")
    splash = SplashScreen(str(logo_path), duration=2500)
    splash.show()

    # ---- ICON (rounded) ----
    app.setWindowIcon(rounded_icon(str(logo_path), 15))

    # ---- MAIN WINDOW ----
    window = MainWindow()

    def start_main():
        splash.close()
        window.show()

    splash.show_and_wait(start_main, window)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### Step 5: Create `.flake8` Config

Copy this to your project root:

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.venv,build,dist,.eggs/,*.egg-info
ignore = E203,E266,E501,W503
per-file-ignores =
    __init__.py: F401
    tests/*: F401,F811
```

### Step 6: Split Requirements Files

Your current `requirements.txt` becomes `requirements.txt` (production-only).

Create `requirements-dev.txt`:

```
-r requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
black==23.12.0
flake8==6.1.0
mypy==1.7.1
pylint==3.0.3
isort==5.13.2
bump2version==1.0.1
```

Create `.bumpversion.cfg` (for automatic versioning):

```ini
[bumpversion]
current_version = 1.0.0
commit = True
tag = True

[bumpversion:file:src/__version__.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"

[bumpversion:file:pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file:docs/PRODUCTION_STANDARDS.md]
search = > **Date:** March 12, 2026
replace = > **Date Updated:** {now:%B %d, %Y}
```

### Step 7: Create Initial Test Structure

Run these commands:

```bash
# Create test directories
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures

# Create __init__.py files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

### Step 8: Create `conftest.py` for Pytest

Copy to `tests/conftest.py`:

```python
"""Pytest configuration and shared fixtures."""
import os
import tempfile
from pathlib import Path

import pytest

from src.config.settings import SettingsConfig


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_settings(temp_dir):
    """Provide test settings with temporary directories."""
    return SettingsConfig(
        pi_user="testuser",
        pi_ip="192.168.1.100",
        ssh_key_path=str(temp_dir / "test_key"),
        local_watch_dir=str(temp_dir / "watch"),
        remote_base_dir="/mnt/external",
        auto_start_monitor=False,
        delete_after_transfer=False,
    )
```

---

## Phase 2: Add Basic Tests (1-2 hours)

### Step 1: Create Your First Test

Copy to `tests/unit/test_settings.py`:

```python
"""Unit tests for settings configuration."""
import pytest

from src.config.settings import SettingsConfig
from src.models.errors import IPAddressValidationError, PathValidationError


class TestSettingsValidation:
    """Test settings validation."""

    def test_valid_ip_address_accepted(self):
        """Valid IP addresses should be accepted."""
        config = SettingsConfig(pi_ip="192.168.1.100")
        assert config.pi_ip == "192.168.1.100"

    def test_invalid_ip_address_rejected(self):
        """Invalid IP addresses should raise error."""
        with pytest.raises(IPAddressValidationError):
            SettingsConfig(pi_ip="999.999.999.999")

    def test_default_ssh_port_is_22(self):
        """Default SSH port should be 22."""
        config = SettingsConfig()
        assert config.ssh_port == 22

    def test_custom_ssh_port_accepted(self):
        """Custom SSH port should be accepted."""
        config = SettingsConfig(ssh_port=2222)
        assert config.ssh_port == 2222

    def test_auto_start_monitor_defaults_false(self):
        """Auto-start monitor should default to False."""
        config = SettingsConfig()
        assert config.auto_start_monitor is False

    def test_delete_after_transfer_defaults_true(self):
        """Delete after transfer should default to True."""
        config = SettingsConfig()
        assert config.delete_after_transfer is True


class TestSettingsDefaults:
    """Test default settings."""

    def test_file_extensions_contains_common_formats(self):
        """Default file extensions should include common video formats."""
        config = SettingsConfig()
        assert ".mkv" in config.file_extensions
        assert ".mp4" in config.file_extensions
        assert ".avi" in config.file_extensions

    def test_skip_patterns_contains_common_files(self):
        """Default skip patterns should exclude system files."""
        config = SettingsConfig()
        assert ".DS_Store" in config.skip_patterns
        assert "Thumbs.db" in config.skip_patterns


class TestSettingsFromJson:
    """Test JSON loading."""

    def test_from_json_creates_config(self, test_settings):
        """from_json should create valid config."""
        data = {
            "pi_user": "pi",
            "pi_ip": "192.168.1.50",
            "ssh_port": 22,
        }
        config = SettingsConfig.from_json(data)
        assert config.pi_user == "pi"
        assert config.pi_ip == "192.168.1.50"

    def test_from_json_converts_lists_to_sets(self):
        """from_json should convert file extension lists to sets."""
        data = {
            "file_extensions": [".mkv", ".mp4"],
            "skip_patterns": [".DS_Store"],
        }
        config = SettingsConfig.from_json(data)
        assert isinstance(config.file_extensions, set)
        assert ".mkv" in config.file_extensions
```

Remember this makes an example test. This way people can understand good testing structure.

### Step 2: Run Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest tests/

# Run only unit tests
pytest tests/unit/ -v

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser to see coverage
```

---

## Phase 3: Add GitHub Actions CI/CD (45 minutes)

### Create `.github/workflows/test.yml`

Make directories and copy this file:

```bash
mkdir -p .github/workflows
```

Copy to `.github/workflows/test.yml`:

```yaml
name: Tests & Quality Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    name: Test on Python ${{ matrix.python-version }}
    runs-on: macos-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Format check with Black
        run: |
          black --check src tests

      - name: Sort imports with isort
        run: |
          isort --check-only src tests

      - name: Lint with Flake8
        run: |
          flake8 src tests

      - name: Type check with MyPy
        run: |
          mypy src

      - name: Run tests with Pytest
        run: |
          pytest tests/ --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false

  lint:
    name: Lint with Pylint
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run Pylint
        run: |
          pylint src --disable=C0111,R0913,R0914 --fail-under=8.0
        continue-on-error: true
```

### Create `.github/workflows/security.yml`

Copy to `.github/workflows/security.yml`:

```yaml
name: Security Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install bandit safety

      - name: Run Bandit security scan
        run: |
          bandit -r src -f json -o bandit-report.json
        continue-on-error: true

      - name: Check dependencies with Safety
        run: |
          safety check --json
        continue-on-error: true
```

---

## Phase 4: Add Development Tools (30 minutes)

### Create `Makefile` for Common Tasks

Copy to `Makefile`:

```makefile
.PHONY: help install install-dev format lint type-check test test-cov clean run

help:
	@echo "PiSync Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install all development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run              Run the application"
	@echo "  make format           Format code with Black and isort"
	@echo "  make lint             Run Flake8 linting"
	@echo "  make type-check       Run MyPy type checking"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Remove build artifacts"
	@echo "  make bump-patch       Bump patch version (1.0.0 -> 1.0.1)"
	@echo "  make bump-minor       Bump minor version (1.0.0 -> 1.1.0)"
	@echo "  make bump-major       Bump major version (1.0.0 -> 2.0.0)"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python main.py

format:
	black src tests
	isort src tests

lint:
	flake8 src tests
	pylint src --disable=C0111,R0913

type-check:
	mypy src

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .tox/ .mypy_cache/ .pytest_cache/ htmlcov/ dist/ build/ *.egg-info
	@echo "Cleaned build artifacts"

bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major
```

Now developers can run:

```bash
make install-dev    # Setup
make format         # Format code
make lint           # Check quality
make test           # Run tests
make run            # Run app
```

### Create `.pre-commit-config.yaml` (Optional - Advanced)

Copy to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

Install with:

```bash
pip install pre-commit
pre-commit install
# Now checks run automatically on every commit
```

---

## Phase 5: Update README with New Sections (15 minutes)

Add these sections to your existing `README.md`:

### Add Development Section

````markdown
## 🛠 Development

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/pisync.git
cd pisync

# Use Makefile for common tasks
make install-dev
make test
make run
```
````

### Running Tests

```bash
# Run all tests
make test-cov

# Run specific test file
pytest tests/unit/test_settings.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html to view
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Check type hints
make type-check

# Run everything
black . && isort . && flake8 src && mypy src
```

### Build & Package

```bash
# Install as package (development mode)
pip install -e .

# Build distribution
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for full details.

````

---

## Verification Checklist

Run through this after implementing Phase 1:

```bash
# ✅ Check pyproject.toml exists and is valid
cat pyproject.toml | head -20

# ✅ Check version file is in place
python -c "from src import __version__; print(__version__)"

# ✅ Run formatting without errors
make format

# ✅ Run linting without errors
make lint

# ✅ Run at least one test
make test

# ✅ Application still runs
python main.py
````

---

## FAQ for Implementation

**Q: Do I need to do all of this?**  
A: Start with Phase 1 (pyproject.toml, version file, requirements split). This takes 30 minutes and gives you the CI/CD foundation. Phases 2-4 are valuable but can be added incrementally.

**Q: Will this break my existing setup?**  
A: No! Your code doesn't change. You're just adding configuration files. The app works exactly the same.

**Q: How do I keep requirements updated?**  
A: Use `pip list --outdated` to check, then update manually in `requirements*.txt`. For automation, use Dependabot (GitHub) or tools like Poetry.

**Q: What if I'm not ready for CI/CD?**  
A: Skip Phase 3. You can add it later. But at minimum, do Phase 1.

**Q: Can I use this with my current virtual environment?**  
A: Yes! Just run `pip install -r requirements-dev.txt` in your existing `.venv`.

---

## Next Steps After Implementation

1. **Commit changes:** `git commit -am "Add production standards configuration"`
2. **Push to GitHub:** `git push origin main`
3. **Watch Actions tab** to see CI/CD pipeline running
4. **Start writing tests** as you develop new features

---

**Congratulations!** You now have production-grade Python project infrastructure. 🎉
