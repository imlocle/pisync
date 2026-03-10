# PiSync Architecture

> **Last Updated:** March 10, 2026  
> **Version:** 1.0.0

## Overview

PiSync is built with a clean layered architecture that separates concerns and enables testability.

## Architecture Layers

```
┌─────────────────────────────────────┐
│   Presentation Layer                │
│   - MainWindow, SettingsWindow      │
│   - FileExplorerWidget              │
│   - Server Selection Dialog         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Application Layer                 │
│   - AutoSyncController              │
│   - ManualTransferController        │
│   - TransferEngine                  │
│   - PathMapper                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Domain Layer                      │
│   - TransferRequest, TransferResult │
│   - FileInfo, ConnectionInfo        │
│   - FileSystem Protocol             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Infrastructure Layer              │
│   - LocalFileSystem                 │
│   - RemoteFileSystem (SFTP)         │
│   - ConnectionManagerService        │
└─────────────────────────────────────┘
```

## Key Components

### Presentation Layer

**MainWindow**: Main application interface

- Dual-pane file explorers (local and remote)
- Activity log with timestamps
- Toolbar with controls
- Status bar with connection indicators

**SettingsWindow**: Configuration interface

- Tabbed layout (Connection, Paths, Behavior, Files)
- Multi-server management
- Form validation

**FileExplorerWidget**: Reusable file browser

- Supports local and SFTP browsing
- Drag & drop operations
- Context menus

### Application Layer

**AutoSyncController**: Automatic monitoring

- Manages MonitorThread lifecycle
- Handles file detection and stability
- Triggers automatic transfers

**ManualTransferController**: User-initiated transfers

- Handles drag & drop operations
- Manages transfer queue
- Reports progress to UI

**TransferEngine**: Core transfer logic

- Protocol-agnostic operations
- File verification
- Progress tracking
- Error handling

**PathMapper**: Path translation

- Maps local paths to remote paths
- Preserves directory structure
- Bidirectional conversion

### Domain Layer

**Models** (Pure Python, no dependencies):

- `TransferRequest`: Transfer operation details
- `TransferResult`: Transfer outcome with metrics
- `FileInfo`: File metadata
- `ConnectionInfo`: SSH/SFTP connection details

**Protocols** (Interfaces):

- `FileSystem`: Abstract file operations
- `TransferEngine`: Transfer interface
- `ConnectionManager`: Connection management

### Infrastructure Layer

**LocalFileSystem**: Local file operations

- Uses Python `os` and `pathlib`
- Implements FileSystem protocol

**RemoteFileSystem**: SFTP operations

- Uses Paramiko for SSH/SFTP
- Implements FileSystem protocol
- Thread-safe operations

**ConnectionManagerService**: Connection management

- SSH connection pooling
- Automatic reconnection
- Health checks

## Data Flow

### Automatic Transfer Flow

1. User starts monitoring
2. FileMonitorRepository watches directory with watchdog
3. New file detected → FileStabilityTracker begins checking
4. Background polling thread checks file size every 0.5s
5. After 2s of stability → handle_file() called
6. PathMapper determines remote destination
7. TransferEngine executes transfer via RemoteFileSystem
8. Optional: Local file deleted after success
9. UI updated via signals

### Manual Transfer Flow

1. User drags files to remote explorer
2. FileExplorerWidget emits files_dropped signal
3. ManualTransferController creates TransferRequest
4. TransferEngine executes transfer
5. Progress updates sent via signals
6. UI shows real-time progress
7. Completion notification

## Threading Model

- **Main Thread**: UI rendering and event handling
- **MonitorThread**: Watchdog observer for file monitoring
- **Stability Polling Thread**: Checks file stability every 0.5s
- **Transfer Workers**: Background SFTP operations

All threads communicate via Qt Signals for thread-safety.

## File Stability Tracking

PiSync uses a polling-based approach to ensure files are complete before transfer:

```python
class FileStabilityTracker:
    def start_polling(self, callback):
        # Background thread checks files every 0.5s

    def check_stability(self, file_path):
        # Returns True if size unchanged for 2s
```

This prevents transferring incomplete files when:

- Copying large files from external drives
- Downloading files to watch directory
- Moving files between directories

## Configuration Management

**Settings** (Pydantic-based):

- JSON persistence at `~/.PiSync/config.json`
- Automatic validation
- Field migration from old versions
- Multi-server support

## Error Handling

Custom exception hierarchy:

- `PiSyncError`: Base exception
- `SSHConnectionError`: Connection failures
- `AuthenticationError`: Auth failures
- `FileAccessError`: File operation errors
- `TransferError`: Transfer failures

All errors provide user-friendly messages and are logged to activity log.

## Design Patterns

**Repository Pattern**: FileMonitorRepository encapsulates file monitoring logic

**Protocol Pattern**: FileSystem protocol enables testing with mocks

**Observer Pattern**: Qt Signals for event-driven communication

**Strategy Pattern**: Different transfer strategies for movies vs TV shows

**Dependency Injection**: Controllers receive dependencies via constructor

## Technology Stack

- **UI Framework**: PySide6 (Qt for Python)
- **SSH/SFTP**: Paramiko
- **File Monitoring**: Watchdog
- **Configuration**: Pydantic
- **Type Checking**: Pyright

## Performance Considerations

- Non-blocking UI (all I/O in background threads)
- Connection pooling for SFTP
- Efficient file stability checking (polling vs events)
- Minimal memory footprint (50-100 MB)

## Security

- SSH key-based authentication
- SFTP encrypted transfers
- No password storage
- No sensitive data in logs

## Future Improvements

- Parallel transfers (multiple files simultaneously)
- Transfer resume capability
- Compression during transfer
- Plugin system for extensibility
- REST API for remote control

---

**Last Updated**: March 10, 2026  
**Version**: 1.0.0
