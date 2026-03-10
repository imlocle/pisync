# PiSync Documentation

> **Last Updated:** March 10, 2026  
> **Version:** 1.0.0

Welcome to the PiSync documentation! This guide will help you set up and use PiSync effectively.

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Architecture](#architecture)
5. [Troubleshooting](#troubleshooting)
6. [Development](#development)

## 🚀 Getting Started

### System Requirements

- macOS 10.15 or later
- Python 3.9+
- Raspberry Pi with SSH access
- Local network connection

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/pisync.git
cd pisync

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### SSH Key Setup

PiSync requires SSH key-based authentication:

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Copy key to Raspberry Pi
ssh-copy-id pi@192.168.1.100

# Test connection
ssh pi@192.168.1.100
```

### First Run

```bash
python main.py
```

On first launch, you'll see a server selection dialog. Click "Add New Server" and configure:

- **Server Name**: My Raspberry Pi
- **IP Address**: 192.168.1.100
- **Username**: pi
- **SSH Key**: ~/.ssh/id_rsa
- **Local Directory**: ~/Transfers
- **Remote Directory**: /mnt/external

## ⚙️ Configuration

### Settings Overview

PiSync settings are organized into tabs:

#### Connection Tab

- **Pi IP Address**: Your Raspberry Pi's local IP
- **Username**: SSH username (typically `pi`)
- **SSH Key Path**: Path to your private key
- **SSH Port**: SSH port (default: 22)

#### Paths Tab

- **Local Watch Directory**: Where you place files (e.g., `~/Transfers`)
- **Remote Base Directory**: Destination on Pi (e.g., `/mnt/external`)

#### Behavior Tab

- **Auto-start Monitoring**: Start watching on app launch
- **Delete After Transfer**: Remove local files after successful transfer
- **Stability Duration**: Wait time before transferring (default: 2 seconds)

#### Files Tab

- **File Extensions**: Supported types (`.mkv`, `.mp4`, `.avi`, `.m4v`)
- **Skip Patterns**: Files to ignore (`.DS_Store`, `._*`)

### Directory Structure

PiSync expects this structure:

```
~/Transfers/
├── Movies/
│   └── Movie Title (2024)/
│       └── movie.mkv
└── TV_shows/
    └── Show Name/
        └── Season 01/
            └── episode.mkv
```

The structure is mirrored on your Pi:

```
/mnt/external/
├── Movies/
│   └── Movie Title (2024)/
│       └── movie.mkv
└── TV_shows/
    └── Show Name/
        └── Season 01/
            └── episode.mkv
```

## 📖 Usage

### Automatic Monitoring

1. Click **Connect** to establish SSH connection
2. Click **Start Monitoring** (▶️)
3. Drop files into `~/Transfers/Movies/` or `~/Transfers/TV_shows/`
4. PiSync automatically:
   - Detects new files
   - Waits for file stability (2 seconds)
   - Transfers to Pi
   - Deletes local copy (if enabled)

### Manual Transfers

**Drag & Drop to Local Explorer:**

- Drag files from Finder to Local Files explorer
- Files are moved (not copied) to the watch directory
- Automatic transfer begins after stability check

**Drag & Drop to Remote Explorer:**

- Drag files directly to Raspberry Pi explorer
- Immediate upload without monitoring

### Upload All

Click **Upload All** to scan and transfer all existing files in your watch directory. Useful for:

- Initial setup with existing files
- Recovering from interrupted monitoring
- Batch transfers

### File Operations

**Refresh**: Update file explorer views  
**Delete**: Move selected files to trash (⌘+Delete)  
**Context Menu**: Right-click for additional options

## 🏗️ Architecture

### Layered Design

```
┌─────────────────────────────┐
│   Presentation (UI)         │  MainWindow, Settings
├─────────────────────────────┤
│   Application (Controllers) │  AutoSync, ManualTransfer
├─────────────────────────────┤
│   Domain (Models)           │  TransferRequest, FileInfo
├─────────────────────────────┤
│   Infrastructure (SFTP)     │  LocalFS, RemoteFS
└─────────────────────────────┘
```

### Key Components

**FileMonitorRepository**: Watches directory using watchdog, tracks file stability with background polling

**ConnectionManagerService**: Manages SSH/SFTP connections with retry logic

**TransferEngine**: Core transfer logic, protocol-based and testable

**PathMapper**: Maps local paths to remote paths, preserving structure

**FileExplorerWidget**: Reusable file browser with drag & drop

### File Stability Tracking

PiSync uses a polling-based stability tracker to prevent transferring incomplete files:

1. File detected in watch directory
2. Background thread checks file size every 0.5 seconds
3. After 2 seconds of no size changes, file is considered stable
4. Transfer begins automatically

This ensures files are fully copied before transfer starts.

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "Connection Failed" error

**Solutions**:

- Verify Pi IP address: `ping 192.168.1.100`
- Test SSH manually: `ssh pi@192.168.1.100`
- Check SSH key permissions: `chmod 600 ~/.ssh/id_rsa`
- Ensure SSH service is running on Pi: `sudo systemctl status ssh`

**Problem**: "Authentication Failed" error

**Solutions**:

- Verify SSH key is copied to Pi: `ssh-copy-id pi@192.168.1.100`
- Check username is correct (typically `pi`)
- Try connecting with password first, then copy key

### Transfer Issues

**Problem**: Files not transferring after monitoring starts

**Solutions**:

- Check activity log for specific errors
- Verify files are in `Movies/` or `TV_shows/` subdirectories
- Ensure file extensions are in allowed list
- Check remote directory exists and has write permissions

**Problem**: "File stable" message but no transfer

**Solutions**:

- Check if file is in a subfolder (not root of Movies/TV_shows)
- Verify remote directory path is correct
- Check disk space on Pi: `df -h`

**Problem**: Transfer fails midway

**Solutions**:

- Check network connection stability
- Verify sufficient disk space on Pi
- Review activity log for specific error
- Try manual transfer to test connection

### UI Issues

**Problem**: File explorers not updating

**Solutions**:

- Click **Refresh** button
- Restart monitoring (Stop → Start)
- Check connection status in status bar

**Problem**: Activity log not showing messages

**Solutions**:

- Scroll to bottom of log
- Check if monitoring is actually started
- Restart application

### Performance Issues

**Problem**: Slow transfers

**Solutions**:

- Check network speed: `iperf3` between Mac and Pi
- Verify Pi isn't CPU/disk bound
- Consider wired connection instead of WiFi
- Check for other network activity

**Problem**: High memory usage

**Solutions**:

- Restart application
- Check for large number of files in watch directory
- Monitor system resources

## 🔧 Development

### Running from Source

```bash
# Activate virtual environment
source .venv/bin/activate

# Run application
python main.py
```

### Code Structure

```
src/
├── application/          # Business logic
│   ├── auto_sync_controller.py
│   ├── manual_transfer_controller.py
│   ├── path_mapper.py
│   └── transfer_engine.py
├── components/           # UI windows
│   ├── main_window.py
│   ├── settings_window.py
│   └── server_selection_dialog.py
├── domain/              # Models & protocols
│   ├── models.py
│   └── protocols.py
├── infrastructure/      # External integrations
│   └── filesystem/
│       ├── local.py
│       └── remote.py
├── repositories/        # Data access
│   └── file_monitor_repository.py
└── services/            # Business services
    ├── connection_manager_service.py
    ├── movie_service.py
    └── tv_service.py
```

### Type Checking

PiSync uses Pyright for type safety:

```bash
# Install Pyright
npm install -g pyright

# Run type checking
pyright src/
```

### Building for Distribution

```bash
# Build macOS app
pyinstaller --noconfirm --onedir --windowed \
  -n "PiSync" \
  --icon="assets/icons/pisync_logo.png" \
  --add-data="assets:assets" \
  main.py

# Run built app
open dist/PiSync.app
```

## 📊 Performance

- **Startup Time**: ~2.5 seconds
- **Memory Usage**: 50-100 MB
- **Transfer Speed**: Network-limited (10-100 MB/s on gigabit)
- **File Stability Check**: 2 seconds (configurable)

## 🔐 Security

- ✅ SSH key-based authentication
- ✅ SFTP encrypted transfers
- ✅ No password storage
- ⚠️ Config file not encrypted (paths only)

## 📝 Configuration File

Location: `~/.PiSync/config.json`

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

## 🗺️ Roadmap

**Current (v1.0)**:

- ✅ Automatic monitoring
- ✅ File stability tracking
- ✅ Modern UI
- ✅ Multi-server support

**Planned (v1.1+)**:

- [ ] Parallel transfers
- [ ] Transfer resume
- [ ] Windows/Linux support
- [ ] Test suite

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pisync/issues)
- **Documentation**: This file
- **Activity Log**: Check in-app for detailed error messages

---

**Last Updated**: March 10, 2026  
**Version**: 1.0.0
