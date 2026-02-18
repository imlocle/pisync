# PiSync: Automated Media Transfer System

**PiSync** is a modern desktop application for automatically transferring media files from your macOS to a Raspberry Pi over SSH/SFTP. Built with PySide6, it features a clean dark-themed UI, real-time monitoring, and intelligent file handling.

![PiSync Logo](assets/icons/pisync_logo.png)

## ✨ Features

### Core Functionality

- **Automatic Monitoring**: Watches local directory for new media files with file stability checking
- **Smart Path Mapping**: Mirrors local directory structure on your Raspberry Pi
- **Dual-Pane File Explorers**: Browse both local and remote files simultaneously
- **Drag & Drop**: Move files from Finder to local explorer (triggers automatic transfer)
- **Manual Transfers**: Drag files directly to Pi explorer for immediate upload
- **Upload All**: Scan and transfer existing files with real-time progress
- **Auto-Delete**: Optional deletion of local files after successful transfer

### User Interface

- **Modern Dark Theme**: Professional, polished interface with 500+ line stylesheet
- **Real-Time Activity Log**: Timestamped, color-coded log entries with emoji icons
- **Progress Indicators**: Visual feedback for file stability checks and transfers
- **Status Bar**: Connection and monitoring status at a glance
- **Tabbed Settings**: Organized into Connection, Paths, Behavior, and Files sections
- **File Size Display**: Shows file sizes in explorers (files only, directories show "—")
- **Disk Usage**: Pi disk usage displayed in explorer title

### Technical Highlights

- **Clean Architecture**: Layered design (Presentation → Application → Domain → Infrastructure)
- **Protocol-Based**: Testable abstractions with dependency inversion
- **Thread-Safe**: Background transfers with non-blocking UI
- **Type-Safe**: Full Pyright type checking compliance
- **Error Handling**: Custom exception hierarchy with user-friendly messages
- **Settings Management**: Pydantic-based validation with automatic migration

## 📋 Prerequisites

- **Python 3.9+**
- **macOS** (primary platform, Windows/Linux support planned)
- **SSH Access** to Raspberry Pi with key-based authentication
- **Network Access** to Raspberry Pi (same local network)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/imlocle/pisync.git
cd pisync
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure SSH Key

Ensure you have SSH key-based authentication set up:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy key to Raspberry Pi
ssh-copy-id pi@192.168.1.100
```

## 🎮 Usage

### Run Locally

```bash
python main.py
```

### First-Time Setup

1. Click the **Settings** button (gear icon)
2. Configure your connection:
   - **Pi IP Address**: Your Raspberry Pi's local IP (e.g., `192.168.1.100`)
   - **Username**: SSH username (typically `pi`)
   - **SSH Key Path**: Path to your private key (e.g., `~/.ssh/id_rsa`)
   - **SSH Port**: SSH port (default: `22`)
3. Configure paths:
   - **Local Watch Directory**: Where you'll place files (e.g., `~/Transfers`)
   - **Remote Base Directory**: Destination on Pi (e.g., `/mnt/external`)
4. Configure behavior:
   - **Auto-start Monitoring**: Start monitoring on app launch
   - **Delete After Transfer**: Remove local files after successful transfer
   - **Stability Duration**: Wait time before transferring (default: 2 seconds)
5. Configure file handling:
   - **File Extensions**: Supported file types (e.g., `.mkv`, `.mp4`, `.avi`)
   - **Skip Patterns**: Files to ignore (e.g., `.DS_Store`, `._*`)

### Daily Workflow

1. **Start Monitoring**: Click the play button (▶️) to begin watching for new files
2. **Add Files**: Drop media files into your watch directory
3. **Automatic Transfer**: PiSync detects, stabilizes, and transfers files automatically
4. **Monitor Progress**: Watch the activity log and progress bar for real-time updates
5. **Browse Files**: Use the dual-pane explorers to manage local and remote files

### Manual Operations

- **Upload All**: Click to scan and transfer all existing files in watch directory
- **Refresh**: Update file explorer views
- **Delete**: Remove selected files (moves to trash, not permanent deletion)
- **Drag & Drop**: Drag files between explorers for manual transfers

## 📦 Building for Distribution

### Build macOS App Bundle

```bash
pyinstaller --noconfirm --onedir --windowed \
  -n "PiSync" \
  --icon="assets/icons/pisync_logo.png" \
  --add-data="assets:assets" \
  main.py
```

### Run the Built App

```bash
open dist/PiSync.app
```

**Note**: If you encounter permission issues, run the app locally with `python main.py`.

## 🏗️ Architecture

### Layered Design

```
┌─────────────────────────────────────┐
│   Presentation Layer (UI)           │
│   - MainWindow, SettingsWindow      │
│   - FileExplorerWidget              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Application Layer (Controllers)   │
│   - AutoSyncController              │
│   - ManualTransferController        │
│   - TransferEngine, PathMapper      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Domain Layer (Models, Protocols)  │
│   - TransferRequest, FileInfo       │
│   - FileSystem Protocol             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Infrastructure Layer              │
│   - LocalFileSystem                 │
│   - RemoteFileSystem (SFTP)         │
└─────────────────────────────────────┘
```

### Key Components

- **FileMonitorRepository**: Watches directory using watchdog, tracks file stability
- **ConnectionManagerService**: Manages SSH/SFTP connections with retry logic
- **TransferEngine**: Core transfer logic, protocol-based and testable
- **PathMapper**: Maps local paths to remote paths, preserving structure
- **FileExplorerWidget**: Reusable file browser with drag & drop support

## 📁 Project Structure

```
pisync/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── assets/                    # Icons and stylesheets
│   ├── icons/
│   └── styles/
├── docs/                      # Documentation
│   ├── START-HERE.md
│   ├── CURRENT-STATE.md
│   └── architecture-overview.md
└── src/                       # Source code
    ├── application/           # Business logic controllers
    ├── components/            # UI windows
    ├── config/                # Settings management
    ├── controllers/           # UI controllers
    ├── domain/                # Domain models and protocols
    ├── infrastructure/        # External integrations (SFTP, filesystem)
    ├── models/                # Error models
    ├── repositories/          # Data access layer
    ├── services/              # Business services
    ├── utils/                 # Utilities and helpers
    └── widgets/               # Reusable UI components
```

## 🔧 Configuration

Settings are stored in `~/.PiSync/config.json`:

```json
{
  "pi_ip": "192.168.1.100",
  "pi_username": "pi",
  "ssh_key_path": "~/.ssh/id_rsa",
  "ssh_port": 22,
  "local_watch_dir": "~/Transfers",
  "remote_base_dir": "/mnt/external",
  "file_extensions": [".mkv", ".mp4", ".avi", ".m4v"],
  "skip_patterns": [".DS_Store", "._*"],
  "delete_after_transfer": true,
  "auto_start_monitor": false,
  "stability_duration": 2.0
}
```

## 🐛 Troubleshooting

### Connection Issues

- Verify SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- Test SSH connection manually: `ssh pi@192.168.1.100`
- Check Pi IP address is correct and reachable
- Ensure SSH service is running on Pi: `sudo systemctl status ssh`

### Transfer Issues

- Check activity log for specific error messages
- Verify remote directory exists and has write permissions
- Ensure sufficient disk space on Pi
- Check file extensions are in allowed list

### UI Issues

- Refresh file explorers if they appear out of sync
- Restart monitoring if files aren't being detected
- Check that watch directory exists and is accessible

## 📊 Performance

- **Startup Time**: ~2.5 seconds (with splash screen)
- **Memory Usage**: 50-100 MB typical
- **Transfer Speed**: Network-limited (10-100 MB/s on gigabit ethernet)
- **UI Responsiveness**: Non-blocking, all I/O operations in background threads
- **File Stability Check**: 2 seconds default (configurable)

## 🔐 Security

- ✅ SSH key-based authentication (no password storage)
- ✅ SFTP encrypted transfers
- ✅ No sensitive data in logs
- ⚠️ Uses AutoAddPolicy for host keys (manual verification recommended)
- ⚠️ Config file not encrypted (contains paths only, no credentials)

## 🚧 Known Limitations

- **Single Pi**: Only supports one Raspberry Pi destination
- **Local Network**: Requires same network access (no remote/VPN support yet)
- **macOS Only**: Not tested on Windows/Linux
- **Sequential Transfers**: One file at a time (no parallel transfers)
- **No Resume**: Cannot resume interrupted transfers
- **No Compression**: Files transferred as-is

## 🗺️ Roadmap

### MVP (Current)

- ✅ Core functionality complete
- ✅ Modern UI with dark theme
- ✅ File stability tracking
- ✅ Type-safe codebase
- ⚠️ Documentation (in progress)
- ❌ Test suite (planned)
- ❌ Distribution packaging (planned)

### Post-MVP

- [ ] Comprehensive test suite
- [ ] Parallel transfers
- [ ] Transfer resume capability
- [ ] Better host key verification
- [ ] Windows/Linux support

### Future

- [ ] Remote access (VPN/tunnel support)
- [ ] Multi-Pi support
- [ ] Mobile companion app
- [ ] Plugin system
- [ ] Cloud backup integration

## 📚 Documentation

- **Getting Started**: `docs/START-HERE.md`
- **Current State**: `docs/CURRENT-STATE.md`
- **Architecture**: `docs/architecture-overview.md`
- **Infrastructure**: `docs/infrastructure-and-deployment.md`
- **Bug Tracking**: `docs/bugs.md`
- **Ideas**: `docs/ideas.md`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type hints
4. Ensure Pyright type checking passes
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PySide6**: Qt for Python framework
- **Paramiko**: SSH/SFTP implementation
- **Watchdog**: File system monitoring
- **Pydantic**: Data validation and settings management

## 📞 Support

For issues, questions, or suggestions:

- **Issues**: Open an issue on GitHub
- **Documentation**: Check `docs/` directory
- **Logs**: Review activity log in the application

---

**Version**: 1.0 (MVP)  
**Last Updated**: February 2026  
**Status**: ✅ Stable and ready for use
