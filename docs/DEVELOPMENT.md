# PiSync Development Guide

> **Last Updated:** March 11, 2026  
> **Version:** 1.0.0

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Architecture Overview](#architecture-overview)
5. [Key Concepts](#key-concepts)
6. [Common Tasks](#common-tasks)
7. [Testing](#testing)
8. [Debugging](#debugging)
9. [Code Standards](#code-standards)
10. [Build & Packaging](#build--packaging)

## Getting Started

### Prerequisites

- Python 3.9+
- macOS 10.15+ (currently macOS only)
- Git
- SSH key for GitHub access

### Initial Setup

```bash
# Clone repository
git clone https://github.com/imlocle/pisync.git
cd pisync

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### IDE Setup

**Recommended: VS Code with Python extension**

```bash
# Install Pylance, Python, and Debugger for Chrome extensions
code .

# Select interpreter: .venv/bin/python
```

## Project Structure

```
pisync/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # User-facing overview
│
├── src/
│   ├── __init__.py
│   │
│   ├── application/                 # Business logic & controllers
│   │   ├── auto_sync_controller.py     # Automatic monitoring controller
│   │   ├── manual_transfer_controller.py # Manual transfer handler
│   │   ├── path_mapper.py              # Local-to-remote path mapping
│   │   └── transfer_engine.py          # Core transfer logic (interface)
│   │
│   ├── components/                  # UI (PySide6 widgets)
│   │   ├── main_window.py              # Main application window
│   │   ├── settings_window.py          # Settings/configuration dialog
│   │   ├── server_selection_dialog.py  # Multi-server selector
│   │   └── splash_screen.py            # Splash screen
│   │
│   ├── controllers/                 # Thread controllers
│   │   ├── main_window_controller.py   # UI event coordination
│   │   ├── monitor_thread.py           # File monitoring thread
│   │   ├── transfer_controller.py      # Transfer request handler
│   │   └── transfer_worker.py          # SFTP transfer worker
│   │
│   ├── domain/                      # Pure domain models
│   │   ├── models.py                   # Data classes (no dependencies)
│   │   └── protocols.py                # Abstract interfaces
│   │
│   ├── infrastructure/              # External system integration
│   │   └── filesystem/
│   │       ├── local.py                # Local filesystem operations
│   │       └── remote.py               # SFTP filesystem operations
│   │
│   ├── models/                      # Application models
│   │   └── errors.py                   # Custom exception hierarchy
│   │
│   ├── repositories/                # Data access patterns
│   │   └── file_monitor_repository.py # File monitoring & stability tracking
│   │
│   ├── services/                    # Business services
│   │   ├── base_transfer_service.py
│   │   ├── connection_manager_service.py # SSH/SFTP connection management
│   │   ├── file_deletion_service.py
│   │   ├── movie_service.py            # Movie transfer logic
│   │   └── tv_service.py               # TV show transfer logic
│   │
│   ├── config/                      # Configuration management
│   │   └── settings.py                 # Pydantic settings model
│   │
│   ├── utils/                       # Utility functions
│   │   ├── constants.py                # Application constants
│   │   ├── helper.py                   # Helper functions
│   │   └── logging_signal.py           # Logging signals for UI
│   │
│   └── widgets/                     # Reusable UI components
│       └── file_explorer_widget.py     # File browser widget
│
├── assets/
│   ├── icons/                       # Application icons
│   │   └── pisync_logo.png
│   └── styles/
│       ├── modern_theme.qss         # Dark theme stylesheet
│       └── styles.qss               # Additional styles
│
├── docs/                            # Documentation
│   ├── README.md                    # Getting started guide
│   ├── ARCHITECTURE.md              # Detailed architecture
│   ├── DEVELOPMENT.md               # This file
│   ├── BUGS.md                      # Known issues & fixes
│   └── ROADMAP.md                   # Future enhancements
│
└── .venv/                           # Virtual environment (git-ignored)
```

## Development Workflow

### 1. Creating a New Feature

#### Step 1: Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

#### Step 2: Plan the change

- Identify which layer(s) it affects (presentation, application, domain, infrastructure)
- Check for related models/protocols in the domain
- Consider thread safety if it involves background operations

#### Step 3: Implement following architecture layers

**Example: Adding a new transfer status**

1. **Domain** (`src/domain/models.py`): Add model
2. **Infrastructure** (`src/infrastructure/`): Implement low-level logic
3. **Application** (`src/application/`): Add business logic
4. **UI** (`src/components/`): Add UI components
5. **Services** (`src/services/`): Connect services if needed

#### Step 4: Test locally

```bash
python main.py
```

#### Step 5: Commit with clear message

```bash
git add .
git commit -m "feat: add transfer status indicator"
```

### 2. Bug Fixes

Check [BUGS.md](./BUGS.md) for known issues and recent fixes.

```bash
# Create fix branch
git checkout -b fix/issue-description

# Implement fix
# Test thoroughly

git commit -m "fix: resolve duplicate queue entries"
```

### 3. Code Review

All PRs should:

- Pass GitHub Copilot review
- Include tests for new functionality
- Update relevant documentation
- Follow code standards (see below)

## Architecture Overview

### Layered Architecture

```
┌──────────────────────────────────────┐
│  Presentation Layer (UI)             │
│  - MainWindow, SettingsWindow        │
│  - FileExplorerWidget                │
│  - SplashScreen                      │
└──────────────┬───────────────────────┘
               │ Qt Signals
┌──────────────┴───────────────────────┐
│  Application Layer (Controllers)     │
│  - AutoSyncController                │
│  - ManualTransferController          │
│  - MainWindowController              │
│  - TransferEngine (interface)        │
└──────────────┬───────────────────────┘
               │ Protocol-based
┌──────────────┴───────────────────────┐
│  Domain Layer (Models & Protocols)   │
│  - TransferRequest, TransferResult   │
│  - FileInfo, ConnectionInfo          │
│  - FileSystem, TransferEngine (protocols)
└──────────────┬───────────────────────┘
               │ Polymorphic
┌──────────────┴───────────────────────┐
│  Infrastructure Layer                │
│  - LocalFileSystem                   │
│  - RemoteFileSystem (SFTP/Paramiko)  │
│  - ConnectionManagerService          │
│  - FileDeletionService               │
└──────────────────────────────────────┘
```

### Data Flow: Automatic Transfer

```
FileSystemEvent
       ↓
FileMonitorRepository.on_created()
       ↓
FileStabilityTracker.check_stability()
       ↓
Polling Thread (background)
       ↓
stable_files_queue.put(file_path)
       ↓
MonitorThread processes queue
       ↓
handle_file() or handle_folder()
       ↓
MovieService / TvService
       ↓
RemoteFileSystem.transfer()
       ↓
UI Signal (transfer_completed)
```

### Threading Model

- **Main Thread**: UI rendering, Qt event loop
- **MonitorThread** (QThread): Watchdog observer + queue processor
- **Stability Polling Thread**: Background file size checks every 0.5s
- **Transfer Worker Threads**: Individual SFTP operations

All thread communication uses **Qt Signals** for safety.

## Key Concepts

### 1. File Stability Tracking

**Problem**: Files detected before fully written → incomplete transfers

**Solution**: Polling-based stability check

```python
class FileStabilityTracker:
    def check_stability(self, file_path: str) -> bool:
        # Returns True if file size unchanged for 2 seconds
        # All SFTP operations happen on single thread (MonitorThread)
```

### 2. Multi-Server Support

Settings are stored per-server:

```python
settings.servers = {
    "server1": {"name": "Home Pi", "pi_ip": "192.168.1.1", ...},
    "server2": {"name": "Office Pi", "pi_ip": "192.168.1.2", ...},
}
settings.current_server_id = "server1"
```

### 3. Protocol-Based Abstractions

Interfaces in `src/domain/protocols.py`:

```python
@runtime_checkable
class FileSystem(Protocol):
    """Abstract file system interface (local or remote)."""
    def upload(self, local_path: str, remote_path: str) -> bool: ...
    def download(self, remote_path: str, local_path: str) -> bool: ...
```

This enables testability and future backends.

### 4. Configuration with Pydantic

Settings are validated and persisted:

```python
# Mutable defaults use Field(default_factory=...)
servers: dict[str, dict] = Field(default_factory=dict)

# Saved to ~/.PiSync/config.json
settings.save()
```

## Common Tasks

### Add a New Setting

**File**: `src/config/settings.py`

```python
class SettingsConfig(BaseModel):
    # Add new field
    my_new_setting: str = "default_value"

    @field_validator('my_new_setting')
    @classmethod
    def validate_setting(cls, v):
        # Optional: validate
        return v
```

### Add a UI Control Signal

**File**: `src/controllers/main_window_controller.py`

```python
# Define signal
transfer_completed = Signal(str)  # path

# Emit signal
self.transfer_completed.emit(file_path)

# Connect in UI
controller.transfer_completed.connect(self.on_transfer_done)
```

### Add a Logging Message

**File**: Any `.py` file

```python
from src.utils.logging_signal import logger

logger.info("Info message")
logger.success("Success message")
logger.error("Error message")
logger.warn("Warning message")
logger.upload("Upload started message")
```

Messages appear in the UI activity log automatically.

### Handle SSH Connection Errors

**Pattern**: Connection manager handles reconnection

```python
from src.services.connection_manager_service import ConnectionManagerService

conn_mgr = ConnectionManagerService(settings)
if conn_mgr.connect():
    sftp_client = conn_mgr.sftp_client
else:
    # Automatic retry logic handled
    logger.error("Connection failed")
```

## Testing

### Current Testing Status

- Manual UI testing primarily
- No automated test suite yet
- Entry point for tests: `pytest` structure ready

### Running Manual Tests

1. **Connection Test**:
   - Open Settings → Test Connection
   - Verify SSH key permissions: `chmod 600 ~/.ssh/id_rsa`

2. **File Monitoring Test**:
   - Create `~/Transfers/Movies/TestMovie (2024)/`
   - Add `.mp4` file (e.g., `TestMovie (2024).mp4`)
   - Verify it transfers and deletes (if enabled)

3. **Manual Transfer Test**:
   - Drag file to remote explorer
   - Verify progress bar and completion

### Future: Automated Tests

Recommended structure:

```
tests/
├── unit/
│   ├── test_path_mapper.py
│   ├── test_settings.py
│   └── test_file_stability_tracker.py
├── integration/
│   ├── test_transfer_workflow.py
│   └── test_connection_manager.py
└── conftest.py  # Pytest fixtures
```

Run with: `pytest tests/`

## Debugging

### Enable Debug Logging

**File**: `src/utils/logging_signal.py`

```python
# Uncomment for verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect SFTP Connection

```python
from src.services.connection_manager_service import ConnectionManagerService

conn = ConnectionManagerService(settings)
conn.connect()
sftp = conn.sftp_client
print(sftp.listdir("/mnt/external"))
```

### Monitor Thread Issues

Check `MonitorThread` in `src/controllers/monitor_thread.py`:

```python
def run(self) -> None:
    # Main thread loop - all SFTP operations here
    while self._running:
        file_path = self._stable_files_queue.get(timeout=0.5)
        # Process on this thread (thread-safe)
```

### Thread Safety Debugging

**Qt Signals are thread-safe by default**. All operations:

1. File detection → `stable_files_queue.put()`
2. Queue processor (MonitorThread) → SFTP operations
3. Completion → Signal emitted to UI thread

Never access SFTP client from multiple threads.

## Code Standards

### Style Guide

- **Python**: PEP 8 with 100-char line limit
- **Imports**: `from __future__ import annotations` for forward references
- **Type Hints**: Required for all functions
- **Docstrings**: Google-style for public methods

### File Organization

```python
# 1. Imports (organized in 3 groups)
from __future__ import annotations
import os  # stdlib
from pathlib import Path

from PySide6.QtCore import Signal  # third-party
from pydantic import BaseModel

from src.models.errors import CustomError  # local

# 2. Constants
TIMEOUT = 30
DEFAULT_PORT = 22

# 3. Classes
class MyClass:
    """Docstring."""

    def __init__(self):
        pass

    def public_method(self) -> str:
        """Public method description."""
        return ""

    def _private_method(self) -> None:
        """Private method (single underscore)."""
        pass
```

### Error Handling

Use custom exceptions from `src/models/errors.py`:

```python
from src.models.errors import SSHConnectionError

try:
    sftp.connect()
except Exception as e:
    raise SSHConnectionError(
        "Failed to connect to Pi",
        details=str(e)
    )
```

### Qt Signal Best Practices

```python
class MyController(QObject):
    # Define signals at class level
    operation_started = Signal(str)  # Include parameter types in docstring
    operation_finished = Signal(str, bool)  # path, success

    def __init__(self):
        super().__init__()
        # Connect signals
        self.operation_finished.connect(self._on_operation_finished)

    def start_operation(self, path: str) -> None:
        """Start an operation."""
        self.operation_started.emit(path)
        # Do work...
        self.operation_finished.emit(path, True)

    def _on_operation_finished(self, path: str, success: bool) -> None:
        """Handle operation finished signal."""
        if success:
            logger.success(f"Operation completed for {path}")
```

## Build & Packaging

### Create macOS .app Bundle

```bash
# Install PyInstaller (if not already in requirements.txt)
pip install pyinstaller

# Generate .app
pyinstaller --onefile \
    --windowed \
    --icon assets/icons/pisync_logo.png \
    --name PiSync \
    main.py

# .app will be in dist/ directory
```

### Create DMG Installer

```bash
# Install create-dmg
brew install create-dmg

# Create DMG from .app
create-dmg \
    --volname "PiSync" \
    --background assets/icons/pisync_logo.png \
    --window-pos 200 120 \
    --window-size 600 400 \
    --app-drop-link 450 280 \
    "PiSync-1.0.0.dmg" \
    "dist/PiSync.app"
```

### Version Management

Update version in:

1. `main.py`: `app.setApplicationVersion("1.0.0")`
2. `pyproject.toml` (if added)
3. Git tag: `git tag v1.0.0`

## Documentation Standards

- Keep docs in `docs/` directory
- Update docs with code changes
- Use Markdown with clear headings
- Include examples where helpful
- Reference file paths for complex features

---

## Quick Reference

| Task           | Command                        |
| -------------- | ------------------------------ |
| Run app        | `python main.py`               |
| Run with debug | `_DEBUG=1 python main.py`      |
| Format code    | `black src/ --line-length=100` |
| Check types    | `mypy src/`                    |
| Create bundle  | `pyinstaller main.py`          |
| Check config   | `~/.PiSync/config.json`        |

## Additional Resources

- [Architecture](./ARCHITECTURE.md) - Detailed system design
- [Known Issues](./BUGS.md) - Bug tracking & fixes
- [Future Ideas](./ROADMAP.md) - Roadmap & enhancements
- [PySide6 Docs](https://doc.qt.io/qtforpython-6/) - Qt framework
- [Paramiko Docs](https://www.paramiko.org/) - SSH/SFTP library
