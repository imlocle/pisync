.PHONY: help install dev-install build test lint format clean publish

PYTHON = python3
PIP = pip3
VENV_DIR = .venv

help:
	@echo "PiSync Build and Distribution Targets"
	@echo "====================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       Install dependencies"
	@echo "  make dev-install   Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint          Run linting checks (flake8, pylint, mypy)"
	@echo "  make format        Format code (black, isort)"
	@echo "  make test          Run tests with coverage"
	@echo ""
	@echo "Building & Distribution:"
	@echo "  make build         Build wheel and source distributions"
	@echo "  make dist          Alias for 'make build'"
	@echo "  make publish       Upload to PyPI (requires twine config)"
	@echo "  make publish-test  Upload to Test PyPI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove build artifacts and cache"
	@echo "  make clean-build   Remove build directories"
	@echo "  make clean-test    Remove test and coverage reports"

install:
	$(PIP) install -e .

dev-install:
	$(PIP) install -e ".[dev,test]"

test:
	pytest

lint:
	flake8 src main.py
	mypy src main.py
	pylint src main.py

format:
	black src main.py
	isort src main.py

build: clean
	$(PYTHON) -m build

dist: build

publish: build
	twine upload dist/*

publish-test: build
	twine upload --repository testpypi dist/*

clean: clean-build clean-test

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.py[cod]' -delete

clean-test:
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Development server
run:
	$(PYTHON) main.py
