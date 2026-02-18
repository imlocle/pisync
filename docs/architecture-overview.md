# Architecture Overview

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 2.0  
> **Status:** ✅ Current - Reflects latest architecture

> **📅 Last Updated:** December 2024 (Post Phase 1-4 Redesign)
>
> **Status:** ✅ CURRENT - Reflects the latest architecture after all redesign phases
>
> **Related Documents:**
>
> - `phase-1-simplify-complete.md` - Path mapping simplification
> - `phase-2-separate-concerns-complete.md` - Domain/Infrastructure/Application layers
> - `phase-3-ui-cleanup-complete.md` - UI integration
> - `ui-redesign-complete.md` - Modern UI design

---

# Architecture Overview

## Application Purpose

PiSync is a modern desktop application built with PySide6 that automates the transfer of media files (movies and TV shows) from a MacBook to a Raspberry Pi over SSH/SFTP. It features a clean, modern UI with dual-pane file explorers, automated monitoring, and intelligent transfer management.

## High-Level Architecture

PiSync follows a clean layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│         (UI Components - MainWindow, Settings, etc.)        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  (Controllers: ManualTransfer, AutoSync, TransferEngine)    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        Domain Layer                          │
│     (Models, Protocols, Business Rules - Pure Python)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│    (FileSystem Implementations, SFTP, SSH, Persistence)     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Presentation Layer (`src/components/`, `src/widgets/`)

**MainWindow** - Modern main interface featuring:

- Clean toolbar with text + icon buttons
- Status bar with connection and monitoring indicators
- Dual-pane file explorers (local and remote)
- Activity log with timestamps and color-coding
- Progress bar with percentage display

**SettingsWindow** - Tabbed settings interface:

- 🔌 Connection: SSH/SFTP configuration
- 📁 Paths: Local and remote directories
- ⚙️ Behavior: Monitoring and transfer options
- 📄 Files: Extensions and skip patterns

**FileExplorerWidget** - Reusable file browser:

- Supports both local and remote (SFTP) browsing
- Drag-and-drop support
- Context menus for file operations
- Visual feedback for operations

### 2. Application Layer (`src/application/`)

**ManualTransferController** - User-initiated transfers:

- Handles drag-and-drop operations
- Manages manual file selection
- Provides transfer preview
- Reports progress to UI

**AutoSyncController** - Automatic monitoring:

- Watches local directory for changes
- Manages MonitorThread lifecycle
- Handles file stability checking
- Triggers automatic transfers

**TransferEngine** - Core transfer logic:

- Protocol-agnostic transfer operations
- File verification
- Progress tracking
- Error handling and recovery

**PathMapper** - Simple path mapping:

- Mirrors local structure on remote
- Bidirectional path conversion
- No classification needed

### 3. Domain Layer (`src/domain/`)

**Models** (`models.py`):

- `TransferRequest`: Represents a transfer operation
- `TransferResult`: Transfer outcome with metrics
- `ConnectionInfo`: SSH/SFTP connection details
- `FileInfo`: File metadata
- `TransferProgress`: Progress tracking

**Protocols** (`protocols.py`):

- `FileSystem`: Abstract file operations
- `TransferEngine`: Transfer interface
- `ConnectionManager`: Connection management

**Benefits:**

- Pure Python (no Qt dependencies)
- Easy to test
- Reusable across different UIs

### 4. Infrastructure Layer (`src/infrastructure/`)

**LocalFileSystem** (`filesystem/local.py`):

- Implements FileSystem protocol for local files
- Uses standard Python os/pathlib
- Handles local file operations

**RemoteFileSystem** (`filesystem/remote.py`):

- Implements FileSystem protocol for SFTP
- Uses paramiko for SSH/SFTP
- Handles remote file operations

**ConnectionManagerService** (`src/services/`):

- Manages SSH connections
- Provides SFTP sessions
- Handles reconnection logic
- Connection pooling

### 5. Legacy Services (`src/services/`)

> **Note:** Some services were removed after Phase 1-2 redesign:
>
> - ✅ `file_classifier_service.py` - Removed (classification now path-based)
> - ⚠️ `movie_service.py` - Simplified (uses PathMapper)
> - ⚠️ `tv_service.py` - Simplified (uses PathMapper)
> - ✅ `connection_manager_service.py` - Still used
> - ✅ `file_deletion_service.py` - Still used

### 6. Configuration & Utilities

**Settings** (`src/config/settings.py`):

- Pydantic-based configuration
- Automatic migration from old field names
- Validation with helpful error messages
- JSON persistence

**Logger** (`src/utils/logging_signal.py`):

- Qt Signal-based logging
- HTML-formatted messages
- Timestamps on all entries
- Color-coded severity levels

## Data Flow

### Manual Transfer Flow (Drag & Drop)

1. User drags files onto Pi explorer
2. FileExplorerWidget emits `files_dropped` signal
3. MainWindowController delegates to ManualTransferController
4. ManualTransferController creates TransferRequest
5. TransferEngine executes transfer using RemoteFileSystem
6. Progress updates sent via signals
7. UI updates in real-time
8. Completion notification shown

### Automatic Monitoring Flow

1. User clicks "Start Monitoring"
2. MainWindowController delegates to AutoSyncController
3. AutoSyncController starts MonitorThread
4. MonitorThread uses FileMonitorRepository with watchdog
5. Watchdog detects file creation/modification
6. FileStabilityTracker ensures file is complete
7. PathMapper determines remote destination
8. Transfer executed via TransferEngine
9. Optional: Local file deleted after successful transfer
10. Activity log updated

## Threading Model

PiSync uses Qt's threading model for responsiveness:

- **Main Thread**: UI rendering, event handling
- **MonitorThread**: Watchdog observer for file monitoring
- **TransferWorker Threads**: Background transfers (legacy, being phased out)

All threads communicate via Qt Signals for thread-safety.

## Connection Management

- Persistent SSH connection with SFTP channels
- Connection pooling for multiple operations
- Automatic reconnection on failures
- Visual connection status in UI
- Health checks and timeout handling

## Configuration Storage

Settings stored in JSON at `~/.PiSync/config.json`:

**New Fields (Phase 1):**

- `local_watch_dir`: Local directory to monitor
- `remote_base_dir`: Remote base directory
- `file_extensions`: Extensions to monitor
- `skip_patterns`: Patterns to skip
- `delete_after_transfer`: Auto-delete option
- `stability_duration`: File stability wait time
- `ssh_port`: SSH port (default 22)

**Deprecated Fields (auto-migrated):**

- `watch_dir` → `local_watch_dir`
- `pi_root_dir` → `remote_base_dir`
- `file_exts` → `file_extensions`
- `skip_files` → `skip_patterns`
- `pi_movies`, `pi_tv` → removed (uses PathMapper)

## Modern UI Design

**Color Palette:**

- Background: `#1e1e1e` (dark gray)
- Accent: `#007acc` (blue)
- Success: `#4ec9b0` (teal)
- Error: `#f48771` (red)
- Warning: `#ce9178` (orange)

**Typography:**

- System fonts for native feel
- Monospace for activity log
- Clear hierarchy (18px headers, 13px body)

**Components:**

- Modern toolbar with text labels
- Status bar with color-coded indicators
- Tabbed settings window
- Activity log with timestamps
- Smooth progress indicators

## Key Improvements from Redesign

### Phase 1: Simplify

- ✅ Removed complex classification logic
- ✅ Simplified path mapping (mirror structure)
- ✅ Consolidated settings
- ✅ 30% less code

### Phase 2: Separate Concerns

- ✅ Clean domain layer (pure Python)
- ✅ Protocol-based abstractions
- ✅ FileSystem abstraction
- ✅ Specialized controllers

### Phase 3: UI Cleanup

- ✅ Integrated new controllers
- ✅ Removed legacy code
- ✅ Better signal handling

### Phase 4: Modern UI

- ✅ Professional dark theme
- ✅ Clear visual hierarchy
- ✅ Better user feedback
- ✅ Tabbed settings

## Asset Management

Assets bundled for development and distribution:

- **Icons**: PNG logo, SVG icons
- **Stylesheets**: `modern_theme.qss` (500+ lines)
- **Path Resolution**: Handles both dev and bundled environments

## Testing Strategy

> **Note:** Test infrastructure is planned but not yet implemented.

**Planned:**

- Unit tests for domain layer
- Integration tests for application layer
- UI tests for presentation layer
- Mock FileSystem for testing
- Fixture data for transfers

## Performance Characteristics

- **Startup Time**: ~2.5 seconds (with splash screen)
- **Memory Usage**: ~50-100 MB (typical)
- **Transfer Speed**: Limited by network (typically 10-100 MB/s on gigabit)
- **UI Responsiveness**: Non-blocking (all I/O in background threads)

## Security Considerations

- SSH key-based authentication
- No password storage
- SFTP for encrypted transfers
- Host key verification (AutoAddPolicy - should be improved)
- No sensitive data in logs

## Future Architecture Plans

1. **Testing**: Comprehensive test suite
2. **Async**: Consider asyncio for I/O operations
3. **Plugins**: Plugin system for extensibility
4. **API**: REST API for remote control
5. **Multi-Pi**: Support for multiple destinations

## Summary

PiSync now has a clean, modern architecture with:

- Clear separation of concerns
- Protocol-based abstractions
- Testable domain logic
- Modern, professional UI
- Simple, predictable behavior

The redesign transformed it from a functional but complex app into a well-architected, maintainable desktop application.
