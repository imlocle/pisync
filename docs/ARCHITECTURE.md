# PiSync Architecture

## Overview

PiSync is a **layered desktop application** built with Python and PySide6, designed to automatically monitor and transfer media files from macOS to Raspberry Pi systems over SSH/SFTP. The architecture separates concerns across four distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Layer (PySide6)                       │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │ MainWindow   │  │ SettingsWindow  │  │ServerDialog  │   │
│  └──────────────┘  └─────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Controller Layer (Business Logic)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MainWindowController  │  TransferController          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ MonitorThread  │  TransferWorker  │  ConnectionMgr   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Service Layer (Business Rules)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ConnectionManager  │  FileTransfer  │  FileMonitor    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │MovieService  │  TVService  │  FileDeletion          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             Infrastructure Layer (I/O & External APIs)      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Settings/Config  │  FileSystem (Local/Remote)       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ SSH/SFTP Connection  │  File Monitoring             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### 1. UI Layer (`src/components/`)

**Responsibility:** Display state and capture user input. All UI components are "dumb" - they receive data and emit signals. No business logic.

**Key Components:**

- **MainWindow** (`main_window.py`)
  - Root UI container
  - Toolbar with connection/monitoring controls
  - Dual-pane file explorer
  - Activity log
  - Progress bar
  - Status bar with connection state

- **SettingsWindow** (`settings_window.py`)
  - Tabbed settings dialog
  - Server management (add/edit/delete/select)
  - Configuration for paths, behavior, file extensions
  - Input validation before passing to controllers

- **FileExplorerWidget** (`file_explorer_widget.py`)
  - Dual-pane file browser (local + remote)
  - Drag-drop transfer support
  - Context menus for operations

- **SplashScreen** (`splash_screen.py`)
  - Startup animation
  - Synchronized with main window loading

**Design Pattern:** PySide6 Signals/Slots

- UI components emit signals when user interacts
- Controllers connect to these signals
- Results propagate back via `logger.log_signal`

---

### 2. Controller Layer (`src/controllers/`)

**Responsibility:** Orchestrate between UI and services. Handle threading, error handling, state management.

**Key Components:**

- **MainWindowController** (`main_window_controller.py`)
  - Router for UI events from MainWindow
  - Manages connection lifecycle
  - Coordinates monitoring and manual transfers
  - Error recovery and user notifications

- **TransferController** (`transfer_controller.py`)
  - High-level transfer orchestration
  - Delegates to services (FileMonitor, FileTransfer, MovieService, etc.)
  - Implements retry logic and stability checking

- **MonitorThread** (`monitor_thread.py`)
  - QThread that watches local directory for file changes
  - Uses `FileMonitorRepository` for OS-level file watching
  - Emits signals when stable files are detected
  - Runs continuously in background (doesn't block UI)

- **TransferWorker** (`transfer_worker.py`)
  - QThread that performs actual file transfers
  - Batch processes transfer requests
  - Emits progress signals to UI
  - Handles cleanup (delete after transfer, logging)

**Threading Model:**

```
MainThread (UI)
    ↓
    └─→ MonitorThread (watches filesystem)
            ↓ (emits file_detected signal)

    └─→ TransferWorker (transfers files)
            ↓ (emits progress_signal)
```

All signals emitted from worker threads are thread-safe (Qt's signal delivery is thread-safe).

---

### 3. Service Layer (`src/services/`)

**Responsibility:** Implement business rules and domain logic. Stateless, reusable across controllers.

**Key Services:**

- **ConnectionManagerService** (`connection_manager_service.py`)
  - Manages SSH/SFTP connections to Raspberry Pi
  - Connection pooling and reuse
  - Error handling (connection timeouts, auth failures)
  - Returns Paramiko SSH/SFTP client objects to callers

- **BaseTransferService** (`base_transfer_service.py`)
  - Abstract base for all transfer operations
  - Implements common logic (logging, error handling, verification)
  - Subclasses implement specific transfer types

- **MovieService** + **TVService**
  - Content-aware classification
  - Organize files into Movies/ or TV/ folders on remote
  - Extract season/episode info for sorting

- **FileMonitorRepository** + **FileMonitorService**
  - Detect file creation, modification, deletion
  - Implement "stability checking" to wait until file is fully written
  - Filter by file extension

- **FileDeletionService**
  - Safe local file deletion after successful transfer
  - Handles errors gracefully (file already deleted, permission denied)

**Service Isolation:**

- Services do NOT directly call each other (prevents circular dependencies)
- Controllers orchestrate multi-service workflows
- Each service focuses on ONE domain (transfers, connections, classification)

---

### 4. Infrastructure Layer (`src/infrastructure/`, `src/config/`)

**Responsibility:** Low-level I/O, external APIs, system integration.

**Key Components:**

- **Settings** (`src/config/settings.py`)
  - Pydantic BaseModel for type-safe configuration
  - Singleton pattern - one instance per app lifetime
  - Automatic serialization to/from JSON
  - Validation with detailed error messages
  - Supports multiple server configurations

- **FileSystem** (`src/infrastructure/filesystem/`)
  - `local.py` - OS-level file operations (using pathlib, send2trash)
  - `remote.py` - SFTP operations via Paramiko
  - Consistent interface across local/remote operations

- **Models & Errors** (`src/domain/`, `src/models/`)
  - `TransferRequest`, `TransferResult` domain dataclasses
  - `ConfigurationError`, `ConnectionError`, `SSHKeyError` - custom exception hierarchy
  - Precise error classification for better error handling

---

## Data Flow: File Transfer

### Automatic Transfer (Monitoring)

```
1. User clicks "Start Monitoring"
   ↓
2. MainWindowController starts MonitorThread
   ↓
3. MonitorThread watches filesystem (via watchdog library)
   ↓
4. File created/modified → MonitorThread applies:
   - Extension filter (.mp4, .mkv, etc.)
   - Stability check (waits 2s default, retries if still growing)
   - Skip patterns (.DS_Store, ._*, etc.)
   ↓
5. Stable file detected → file_detected signal emitted
   ↓
6. TransferController receives signal:
   - Classify file (Movie vs TV) using MovieService/TVService
   - Create TransferRequest with src/dest paths
   - Queue in TransferWorker
   ↓
7. TransferWorker (separate thread):
   - SSH connect
   - SFTP transfer
   - Verify file size matches
   - Delete local (if enabled)
   - Emit progress_signal
   ↓
8. MainWindow receives signals → updates UI
```

### Manual Transfer (Drag & Drop)

```
1. User drags file from Finder to FileExplorerWidget
   ↓
2. FileExplorerWidget accepts drop → manual_transfer_requested signal
   ↓
3. ManualTransferController:
   - Create TransferRequest (no classification)
   - Queue in TransferWorker
   ↓
4. Transfer follows same path as automatic
```

---

## Configuration Flow

### Loading Settings

```
1. Application startup
   ↓
2. Settings singleton initializes:
   - Load config.json from user home directory
   - Validate with Pydantic
   - Apply defaults for missing fields
   ↓
3. MainWindow loads current server from settings
   - If no server selected, show ServerSelectionDialog
   - Load SSH key, IP, port, remote directory
   ↓
4. MonitorThread reads settings for:
   - Stability duration
   - File extensions filter
   - Skip patterns
   - Local watch directory
```

### Saving Settings

```
1. User changes setting and clicks "Save"
   ↓
2. SettingsWindow validates all inputs:
   - IP address format
   - SSH key exists and readable
   - Directories accessible
   ↓
3. If valid:
   - Create complete config dict
   - Call Settings.save_config(dict)
   ↓
4. Settings writes to config.json atomically
   - Backup old file
   - Write new file
   - Only delete backup if success
```

---

## Error Handling Strategy

### Error Classification

**4 Tiers:**

1. **User Input Errors** → Show dialog, let user fix
   - "IP address is invalid" → SettingsWindow validation
   - "SSH key not found" → SettingsWindow validation

2. **Connection Errors** → Log and retry
   - "Connection refused" → Show retry dialog
   - "SSH key permission denied" → Suggest SSH setup

3. **Transfer Errors** → Log, mark as failed, continue
   - "File verification failed" → Log error, don't delete local
   - "Remote path doesn't exist" → Show error but keep retrying

4. **System Errors** → Crash gracefully
   - "Disk full" → Log error, request user intervention
   - "Config file corrupted" → Show error, offer reset

### Error Propagation

```
Service raises exception
    ↓
Controller catches and logs (via logger.error())
    ↓
Logger emits log_signal with error message
    ↓
MainWindow receives signal and shows to user
```

---

## Concurrency & Threading

### Why Multiple Threads?

- **MainThread (UI):** Qt event loop must never block (keeps UI responsive)
- **MonitorThread:** Continuous directory watching without blocking UI
- **TransferWorker:** File transfers (often slow) without blocking UI

### Thread Safety

✅ **Safe:**

- Qt signals/slots (thread-safe by design)
- Settings singleton (read operations only from threads)
- TransferRequest dataclasses (immutable)

⚠️ **Requires Locks:**

- Shared state in TransferWorker (disabled during transfers)
- Connection reuse (ConnectionManagerService manages this)

---

## Testing Architecture

### Unit Tests (Not Yet Implemented)

Tests should follow this pattern:

```python
# Test a service in isolation
def test_movie_service_classification():
    movie_svc = MovieService()
    result = movie_svc.classify("Inception.2010.1080p.mp4")
    assert result == ("Inception", "movie")

# Test a controller with mocked services
def test_transfer_controller_retry_on_failure(mock_connection_svc):
    controller = TransferController(mock_connection_svc)
    # Simulate connection failure
    result = controller.transfer_file(...)
    # Verify retry was attempted
```

### Integration Tests (Not Yet Implemented)

- Real SSH connection to test Raspberry Pi
- Real file transfers with cleanup
- Real settings JSON serialization

---

## Performance Considerations

### File Stability Check

**Problem:** Detect when a file is fully written

**Solution:** Poll file size with configurable wait time

- Default: 2 seconds between checks
- User configurable via Settings

**Trade-off:** Slower detection (2-5s) vs. false positives from partial files

### Transfer Speed

**Bottlenecks:**

1. Network bandwidth (SSH over WiFi often ~2-5 MB/s on local network)
2. Raspberry Pi I/O (SD card is usually the limiter)
3. Local disk I/O (less common on modern Macs)

**Optimization:** Use SFTP (more efficient than SCP), batch operations, connection reuse

### Memory

**Current:** ~150-200 MB when running (PySide6 + Python interpreter)

**Optimization Ideas:**

- Lazy loading of UI components
- Streaming file transfers (don't buffer entire file)

---

## Extension Points

### Adding a New Service

1. Create `CustomService` in `src/services/`
2. Implement domain-specific logic
3. Add to `TransferController` orchestration
4. Wire up to appropriate signal in MainWindowController

### Adding a New Transfer Type

1. Create `CustomTransferHandler` extending `BaseTransferService`
2. Implement transfer logic
3. Register with `TransferWorker`
4. Add UI for triggering it

### Adding a New Configuration Option

1. Add field to `SettingsConfig` in `src/config/settings.py`
2. Add UI control to `SettingsWindow`
3. Add to form layout and save logic
4. Services read from `self.settings` singleton

---

## Future Architecture Evolution

### Planned Improvements

1. **Plugin System** - Allow custom transfer handlers via plugins
2. **Event Bus** - Replace direct signal connections with pub/sub
3. **State Machine** - Explicit state transitions for transfer lifecycle
4. **Scheduler** - Scheduled transfers at specific times
5. **Retry Strategy** - Configurable exponential backoff

### Potential Refactoring

- Move signal/slot wiring to separate `SignalRegistry` class
- Extract `TransferQueue` as separate class (not embedded in worker)
- Create `ServerConnectionPool` for multi-server support
