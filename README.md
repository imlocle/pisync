# PiSync: Automated Media Transfer to Raspberry Pi

**PiSync** is a modern, production-ready macOS desktop application that automatically transfers media files to your Raspberry Pi over secure SSH/SFTP. Built with Python, PySide6, and modern best practices, it features a clean dark-themed UI, real-time file monitoring with stability checking, and intelligent multi-server support.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/imlocle/pisync/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()

## 🎯 What is PiSync?

PiSync solves the problem of seamlessly transferring media files from your Mac to a Raspberry Pi, while you're busy working. Whether you're downloading movies, recording TV shows, or organizing media files, PiSync handles the transfer intelligently:

- **Watch a folder** → Files added automatically trigger transfers
- **Smart stability checking** → Waits until files are fully written before transferring
- **Content-aware organization** → Automatically sorts movies and TV shows
- **One-click drag & drop** → Manual transfers for any file type
- **Multi-server support** → Manage multiple Raspberry Pi systems

## ✨ Key Features

| Feature                      | Description                                                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Automatic Monitoring**     | Watches a local directory and automatically transfers files as they appear, with intelligent file stability checking |
| **Smart Classification**     | Automatically categorizes content into Movies and TV shows based on folder structure                                 |
| **Dual-Pane Explorer**       | Browse local and remote Raspberry Pi files side-by-side with real-time updates                                       |
| **Drag & Drop Transfers**    | Manually transfer any files by dragging from Finder to the remote explorer                                           |
| **Multi-Server Support**     | Manage and switch between multiple Raspberry Pi servers                                                              |
| **Real-Time Activity Log**   | Monitor all operations with timestamped activity log and transfer status                                             |
| **Modern UI**                | Professional dark-themed interface built with PySide6                                                                |
| **Auto-Cleanup**             | Optionally delete transferred files to free up space                                                                 |
| **Configurable Behavior**    | Customize stability duration, extensions, skip patterns, and more                                                    |
| **Thread-Safe Architecture** | Non-blocking UI with all operations on background threads                                                            |

## 🚀 Quick Start

### Prerequisites

- **macOS**: 10.15 or later
- **Python**: 3.9 or higher
- **Raspberry Pi**: Any model with SSH key access enabled
- **Network**: Same local network or VPN access

### Installation (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/imlocle/pisync.git
cd pisync

# 2. Create isolated Python environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### First-Time Configuration

When you first run PiSync:

1. **Add Server**: Enter your Raspberry Pi details
   - IP Address (e.g., `192.168.1.100`)
   - Username (typically `pi`)
   - SSH Key Path (usually `~/.ssh/id_rsa`)
   - Port (default: 22)

2. **Set Directories**:
   - Local watch directory (default: `~/Transfers`)
   - Remote base path (default: `/mnt/external`)

3. **Configure Behavior** (Optional):
   - Auto-delete after transfer
   - File extensions to monitor
   - File stability duration

4. **Test Connection**: Click "Test Connection" to verify setup

5. **Start Monitoring**: Click "Start Monitoring" to begin automatic transfers

### SSH Key Setup

PiSync requires SSH key-based authentication (more secure than passwords):

```bash
# If you don't have an SSH key yet
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Copy key to your Raspberry Pi
ssh-copy-id -i ~/.ssh/id_rsa pi@YOUR_PI_IP

# Verify connection
ssh pi@YOUR_PI_IP
```

## 📖 Documentation

**Comprehensive documentation** is available in the `/docs` directory, organized by use case:

### 🎯 Quick Navigation

**New to PiSync?**
→ Start here: [Quick Start Guide](docs/DEVELOPMENT.md#getting-started)

**For Development:**
→ See [Developer Documentation](docs/DEVELOPMENT.md)

**Full Documentation Index:**
→ [📚 Complete Documentation Hub](docs/INDEX.md) (learn paths, all docs, FAQs)

### 📚 Key Documentation Files

| Document                                                      | Purpose                            | For                            |
| ------------------------------------------------------------- | ---------------------------------- | ------------------------------ |
| **[INDEX.md](docs/INDEX.md)**                                 | Navigation hub with learning paths | Everyone - start here for docs |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**                   | System design, layers, patterns    | Understanding how PiSync works |
| **[DEVELOPMENT.md](docs/DEVELOPMENT.md)**                     | Setup, workflows, coding standards | Contributors and developers    |
| **[PRODUCTION_STANDARDS.md](docs/PRODUCTION_STANDARDS.md)**   | Production readiness checklist     | Publishing and maintenance     |
| **[DISTRIBUTION.md](docs/DISTRIBUTION.md)**                   | Packaging, PyPI publishing, CI/CD  | Release management             |
| **[DEPENDENCY_MANAGEMENT.md](docs/DEPENDENCY_MANAGEMENT.md)** | Managing dependencies, updates     | Dependency maintenance         |
| **[BUGS.md](docs/BUGS.md)**                                   | Known issues, limitations          | Troubleshooting                |
| **[IDEAS.md](docs/IDEAS.md)**                                 | Roadmap, future features           | Project planning               |

## 📁 Directory Structure

PiSync expects a specific directory structure on your local machine:

```
~/Transfers/
├── Movies/
│   ├── Avatar/
│   │   ├── Avatar.mp4
│   │   └── Avatar.srt
│   └── Inception/
│       ├── Inception.mkv
│       └── Inception.srt
└── TV_shows/
    ├── Breaking Bad/
    │   ├── Season 1/
    │   │   ├── S01E01.mp4
    │   │   └── S01E02.mp4
    │   └── Season 2/
    │       └── S02E01.mp4
    └── The Office/
        └── Season 1/
            └── S01E01.mp4
```

Files in `Movies/` are transferred as complete folders. Files in `TV_shows/` are transferred while preserving the directory structure.

## 🏗️ Architecture

PiSync uses a **clean layered architecture** for maintainability and testability:

```
┌────────────────────────────────────────────┐
│  Presentation Layer (PySide6 UI)           │
│  MainWindow, Settings, FileExplorer        │
└────────────────────────────────────────────┘
                    ↓ Qt Signals
┌────────────────────────────────────────────┐
│  Application Layer (Controllers)           │
│  AutoSync, ManualTransfer, MainWindow      │
└────────────────────────────────────────────┘
                    ↓ Protocols
┌────────────────────────────────────────────┐
│  Domain Layer (Pure Python Models)         │
│  TransferRequest, FileInfo, Protocols      │
└────────────────────────────────────────────┘
                    ↓ Implementations
┌────────────────────────────────────────────┐
│  Infrastructure Layer (SSH/SFTP)           │
│  Paramiko, LocalFS, RemoteFS, Services     │
└────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams and data flows.

## 🔧 Configuration

### Configuration File

PiSync stores configuration in `~/.PiSync/config.json`:

```json
{
  "servers": {
    "home_pi": {
      "name": "Home Pi",
      "pi_ip": "192.168.1.100",
      "pi_user": "pi",
      "ssh_key_path": "/Users/you/.ssh/id_rsa",
      "ssh_port": 22,
      "remote_base_dir": "/mnt/external",
      "local_watch_dir": "/Users/you/Transfers"
    }
  },
  "current_server_id": "home_pi",
  "auto_start_monitor": false,
  "delete_after_transfer": true,
  "file_extensions": [".mp4", ".mkv", ".avi", ".mov"],
  "stability_duration": 2.0
}
```

### Configuration Options

| Option                  | Type    | Default                            | Description                                  |
| ----------------------- | ------- | ---------------------------------- | -------------------------------------------- |
| `auto_start_monitor`    | boolean | `false`                            | Start monitoring automatically on app launch |
| `delete_after_transfer` | boolean | `true`                             | Delete local files after successful transfer |
| `file_extensions`       | list    | `[".mp4", ".mkv", ".avi", ".mov"]` | File types to monitor                        |
| `stability_duration`    | float   | `2.0`                              | Seconds to wait for file stability (seconds) |
| `skip_patterns`         | list    | `[".DS_Store", "Thumbs.db"]`       | Patterns to ignore                           |

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "Connection failed" or "Cannot connect to Pi"

**Solutions**:

- Verify Pi IP address: `ping YOUR_PI_IP`
- Test SSH manually: `ssh pi@YOUR_PI_IP`
- Check SSH key permissions: `ls -l ~/.ssh/id_rsa` (should be `600`)
- Verify key was added to Pi: `ssh-copy-id -i ~/.ssh/id_rsa pi@YOUR_PI_IP`
- Ensure Raspberry Pi has SSH enabled: `sudo raspi-config` → Interface Options → SSH

### File Not Transferring

**Problem**: Files added to watch directory but don't transfer

**Solutions**:

- Check file extension matches configured extensions
- Verify file is in `Movies/` or `TV_shows/` subdirectories
- Files in nested folders may not be detected; check path structure
- Wait 2+ seconds (default stability duration) after file is complete
- Check activity log for error messages

### Performance Issues

**Problem**: High CPU usage or slow transfers

**Solutions**:

- Increase `stability_duration` if on slow network
- Check network bandwidth: `iftop -n`
- Monitor Pi disk space: `df -h` on Raspberry Pi
- Reduce number of concurrent operations if system is slow

### SSH Key Issues

**Problem**: "Permission denied (publickey)"

**Solutions**:

```bash
# Regenerate and install SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
ssh-copy-id -i ~/.ssh/id_rsa pi@YOUR_PI_IP

# Fix permissions (critical)
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Verify setup
ssh -v pi@YOUR_PI_IP  # (for detailed debugging)
```

## 🗺️ Roadmap

### Current (v1.0.0 - Stable)

- ✅ Automatic file monitoring
- ✅ Multi-server support
- ✅ Dual-pane file explorer
- ✅ Drag & drop transfers
- ✅ Activity logging
- ✅ Configuration management

### Planned (v1.1+)

- 🔲 Parallel transfers (multiple files simultaneously)
- 🔲 Transfer resume capability
- 🔲 Compression during transfer
- 🔲 Windows & Linux support
- 🔲 Automated test suite
- 🔲 Remote access (VPN/SSH tunnel support)

### Future Ideas

- Smart file organization (TMDB metadata integration)
- Mobile companion app
- Plugin system for extensibility
- REST API for remote control

See [ideas.md](docs/ideas.md) for detailed feature requests and design discussions.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** logical changes: `git commit -m "feat: add feature"`
4. **Push** to your branch: `git push origin feature/your-feature`
5. **Submit** a Pull Request with description

### Development Setup

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for:

- Setting up development environment
- Coding standards and style guide
- Testing procedures
- Build and packaging

## 📄 License

PiSync is released under the **MIT License**. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with these excellent open-source projects:

- **[PySide6](https://doc.qt.io/qtforpython-6/)** - Qt framework for Python
- **[Paramiko](https://www.paramiko.org/)** - SSH and SFTP protocol implementation
- **[Watchdog](https://watchdog.readthedocs.io/)** - File system monitoring
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management
- **[Pillow](https://python-pillow.org/)** - Image processing

## 📧 Support

- **Report Issues**: [GitHub Issues](https://github.com/imlocle/pisync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/imlocle/pisync/discussions)
- **Documentation**: See `/docs` directory

---

<div align="center">

**Version**: 1.0.0 | **Status**: ✅ Stable | **Last Updated**: March 11, 2026

Built with ❤️ for media enthusiasts and Raspberry Pi lovers

[⬆ Back to Top](#pisync-automated-media-transfer-to-raspberry-pi)

</div>
