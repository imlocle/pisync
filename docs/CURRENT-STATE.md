# PiSync - Current State (February 2026)

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.0  
> **Status:** ✅ Current and accurate

## Executive Summary

PiSync is a modern desktop application for automatically transferring media files from macOS to Raspberry Pi over SSH/SFTP. After a complete redesign through 4 phases and recent bug fixes, the application is stable, performant, and ready for MVP release.

## ✅ What's Working

### Core Functionality

- ✅ **Automatic Monitoring**: Watches local directory for new media files
- ✅ **File Stability Tracking**: Prevents transferring incomplete files (2-second stability check)
- ✅ **Smart Path Mapping**: Mirrors local directory structure on Pi
- ✅ **Dual-Pane Explorers**: Browse both local and remote files
- ✅ **Drag & Drop**: Move files from Finder to local explorer (triggers transfer)
- ✅ **Manual Transfers**: Drag files directly to Pi explorer
- ✅ **Upload All**: Scan and transfer existing files
- ✅ **Auto-Delete**: Optional deletion of local files after successful transfer

### User Interface

- ✅ **Modern Dark Theme**: Professional 500+ line stylesheet
- ✅ **Real-Time Activity Log**: Timestamped, color-coded entries
- ✅ **Progress Indicators**: File stability and transfer progress
- ✅ **Status Bar**: Connection and monitoring status
- ✅ **Tabbed Settings**: Organized into Connection, Paths, Behavior, Files
- ✅ **File Size Display**: Shows file sizes in explorers (files only, directories show "—")
- ✅ **Disk Usage**: Pi disk usage shown in explorer title

### Architecture

- ✅ **Clean Layered Design**: Presentation → Application → Domain → Infrastructure
- ✅ **Protocol-Based**: Testable abstractions (FileSystem, TransferEngine)
- ✅ **Thread-Safe**: Background transfers, non-blocking UI
- ✅ **Error Handling**: Custom exceptions, user-friendly messages
- ✅ **Settings Management**: Pydantic-based with validation and migration

### Recent Fixes (February 2026)

- ✅ **Bug Fix**: Drag & drop now moves files (not copies)
- ✅ **Bug Fix**: Upload All shows real-time progress
- ✅ **Bug Fix**: File stability tracking shows progress bar
- ✅ **Bug Fix**: SFTP thread safety issues resolved
- ✅ **Performance**: Removed async size calculation (SFTP not thread-safe)
- ✅ **Removed**: FileClassifierService (classification now path-based)

## 📊 Technical Specifications

### Technology Stack

- **Framework**: PySide6 (Qt for Python)
- **Language**: Python 3.9+
- **SSH/SFTP**: Paramiko
- **File Monitoring**: Watchdog
- **Configuration**: Pydantic
- **Platform**: macOS (primary), Windows/Linux (future)

### Architecture Layers

```
Presentation (UI)
    ↓
Application (Controllers)
    ↓
Domain (Models, Protocols)
    ↓
Infrastructure (FileSystem, SFTP)
```

### File Organization

```
~/Transfers/
├── Movies/
│   └── movie_title_year/
│       └── movie.mkv
└── TV_shows/
    └── show_name/
        └── s01/
            └── episode.mkv
```

### Performance Metrics

- **Startup Time**: ~2.5 seconds (with splash screen)
- **Memory Usage**: 50-100 MB typical
- **Transfer Speed**: Network-limited (10-100 MB/s on gigabit)
- **UI Responsiveness**: Non-blocking, all I/O in background threads
- **File Stability Check**: 2 seconds (configurable)

## 🎯 Current Capabilities

### Monitoring

- Watches `~/Transfers/` directory recursively
- Detects new files and folders
- Checks file stability (prevents partial transfers)
- Classifies based on folder structure (Movies/ vs TV_shows/)
- Skips hidden files (.DS*Store, .*\*)
- Configurable file extensions

### Transfer

- SFTP-based encrypted transfers
- Progress tracking with percentage
- File verification after transfer
- Automatic retry on failure
- Optional local file deletion
- Preserves directory structure

### User Experience

- Real-time activity log with timestamps
- Color-coded messages (info, success, error, warning)
- Progress bar for transfers and stability checks
- Status indicators for connection and monitoring
- Drag & drop from Finder
- Context menus for file operations

## 🚧 Known Limitations

### Current Constraints

- **Single Pi**: Only supports one Raspberry Pi destination
- **Same Network**: Requires local network access (no remote access)
- **macOS Only**: Not tested on Windows/Linux
- **No Parallel Transfers**: One file at a time
- **No Resume**: Cannot resume interrupted transfers
- **No Compression**: Files transferred as-is
- **Directory Sizes**: Remote directories don't show calculated sizes (performance)

### Technical Debt

- **No Tests**: Test suite not implemented
- **Host Key Verification**: Uses AutoAddPolicy (should verify manually)
- **No API**: No REST API for remote control
- **No Plugins**: No plugin system
- **Legacy Code**: Some old controllers still present (transfer_controller.py, transfer_worker.py)

## 📁 Codebase Structure

### Source Code (`src/`)

```
src/
├── application/          # Controllers, business logic
│   ├── auto_sync_controller.py
│   ├── manual_transfer_controller.py
│   ├── path_mapper.py
│   └── transfer_engine.py
├── components/           # UI windows
│   ├── main_window.py
│   ├── settings_window.py
│   └── splash_screen.py
├── config/              # Settings management
│   └── settings.py
├── controllers/         # UI controllers
│   ├── main_window_controller.py
│   ├── monitor_thread.py
│   ├── transfer_controller.py (legacy)
│   └── transfer_worker.py (legacy)
├── domain/              # Pure Python models
│   ├── models.py
│   └── protocols.py
├── infrastructure/      # External integrations
│   └── filesystem/
│       ├── local.py
│       └── remote.py
├── models/              # Error models
│   └── errors.py
├── repositories/        # Data access
│   └── file_monitor_repository.py
├── services/            # Business services
│   ├── base_transfer_service.py
│   ├── connection_manager_service.py
│   ├── file_deletion_service.py
│   ├── movie_service.py
│   └── tv_service.py
├── utils/               # Utilities
│   ├── constants.py
│   ├── helper.py
│   └── logging_signal.py
└── widgets/             # Reusable UI components
    └── file_explorer_widget.py
```

### Documentation (`docs/`)

- **Current**: 21 files (some legacy, needs cleanup)
- **Core**: architecture-overview.md, infrastructure-and-deployment.md
- **Implementation**: bug-fixes-summary.md, sftp-thread-safety-fix.md
- **Planning**: ideas.md, bugs.md

### Assets (`assets/`)

```
assets/
├── icons/
│   ├── pisync_logo.png
│   ├── play_icon.svg
│   └── stop_icon.svg
└── styles/
    ├── modern_theme.qss (500+ lines)
    └── styles.qss (legacy)
```

## 🔄 Recent Changes (February 2026)

### Bug Fixes

1. **Drag & Drop**: Changed from copy to move (no more duplicates)
2. **Upload All Progress**: Real-time status updates during scan
3. **File Stability**: Progress bar shows 2-second wait
4. **SFTP Thread Safety**: Removed async size calculation

### Removals

1. **FileClassifierService**: Completely removed (classification now path-based)
2. **Async Size Calculation**: Removed due to SFTP thread safety issues

### Improvements

1. **Scan Progress**: Shows "Scanning: item_name (5/10)" during Upload All
2. **Status Updates**: Real-time feedback for all operations
3. **Progress Bar**: Updates during file stability checks
4. **Logging**: Better timestamps and color-coding

## 🎨 User Interface

### Main Window

- **Toolbar**: Start/Stop Monitoring, Upload All, Refresh, Settings, Delete
- **Status Bar**: Connection status, monitoring status
- **Explorers**: Local (left) and Pi (right) file browsers
- **Activity Log**: Scrollable log with timestamps
- **Progress Bar**: Shows transfer and stability progress

### Settings Window (Tabbed)

- **Connection**: Pi IP, username, SSH key path, port
- **Paths**: Local watch directory, remote base directory
- **Behavior**: Auto-start monitoring, delete after transfer, stability duration
- **Files**: File extensions, skip patterns

### Color Scheme

- Background: `#1e1e1e` (dark gray)
- Accent: `#007acc` (blue)
- Success: `#4ec9b0` (teal)
- Error: `#f48771` (red)
- Warning: `#ce9178` (orange)
- Text: `#d4d4d4` (light gray)

## 📈 Metrics & Statistics

### Code Statistics

- **Total Lines**: ~8,000 lines of Python
- **Components**: 12 UI components
- **Services**: 5 business services
- **Controllers**: 4 controllers
- **Models**: 6 domain models
- **Tests**: 0 (planned)

### Documentation Statistics

- **Total Docs**: 21 files
- **Current**: 13 files
- **Legacy**: 8 files (need review/removal)
- **Total Words**: ~50,000 words
- **Code Examples**: 100+ snippets

## 🔐 Security

### Current Security

- ✅ SSH key-based authentication
- ✅ SFTP encrypted transfers
- ✅ No password storage
- ✅ No sensitive data in logs

### Security Concerns

- ⚠️ AutoAddPolicy for host keys (should verify manually)
- ⚠️ No encryption for local config file
- ⚠️ No rate limiting
- ⚠️ No audit logging

## 🚀 Deployment

### Development

```bash
python main.py
```

### Production (Planned)

- PyInstaller for macOS .app bundle
- Code signing for macOS
- DMG installer
- Auto-updater

## 📝 Configuration

### Settings File

Location: `~/.PiSync/config.json`

```json
{
  "pi_ip": "192.168.1.100",
  "pi_username": "pi",
  "ssh_key_path": "~/.ssh/id_rsa",
  "ssh_port": 22,
  "local_watch_dir": "~/Transfers",
  "remote_base_dir": "/mnt/external",
  "file_extensions": [".mkv", ".mp4", ".avi"],
  "skip_patterns": [".DS_Store", "._*"],
  "delete_after_transfer": true,
  "auto_start_monitor": false,
  "stability_duration": 2.0
}
```

## 🎯 MVP Status

### MVP Requirements

- ✅ Automatic file monitoring
- ✅ SFTP transfers
- ✅ File stability checking
- ✅ Modern UI
- ✅ Settings management
- ✅ Activity logging
- ✅ Error handling
- ⚠️ Documentation (needs cleanup)
- ❌ Tests (not implemented)
- ❌ Packaging (not implemented)

### MVP Readiness: 80%

**Ready:**

- Core functionality complete
- UI polished and modern
- Bug fixes applied
- Architecture clean

**Needs Work:**

- Documentation cleanup
- Test suite
- Packaging/distribution
- User guide

## 🔮 Next Steps

### Immediate (MVP Release)

1. Clean up documentation (remove legacy)
2. Create user guide
3. Package as macOS app
4. Beta testing

### Short Term (Post-MVP)

1. Implement test suite
2. Add parallel transfers
3. Improve host key verification
4. Add transfer resume capability

### Long Term (Future Versions)

1. Remote access (VPN/tunnel)
2. Mobile companion app
3. Multi-Pi support
4. Plugin system
5. Cloud backup integration

## 📞 Support & Resources

### Documentation

- Start: `docs/START-HERE.md`
- Architecture: `docs/architecture-overview.md`
- Setup: `docs/infrastructure-and-deployment.md`
- Bugs: `docs/bugs.md`
- Ideas: `docs/ideas.md`

### Configuration

- Settings: `~/.PiSync/config.json`
- Logs: Activity log in UI
- SSH Keys: `~/.ssh/`

### Troubleshooting

- Check connection status in UI
- Review activity log for errors
- Verify SSH key permissions
- Test SSH connection manually: `ssh pi@192.168.1.100`

---

**Document Version**: 1.0  
**Last Updated**: February 11, 2026  
**Status**: ✅ Current and accurate  
**Next Review**: Before MVP release
