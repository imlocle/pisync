# Infrastructure and Deployment

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.1  
> **Status:** ✅ Current

> **📅 Last Updated:** December 2024 (Post Phase 1-4 Redesign)
>
> **Status:** ✅ MOSTLY CURRENT - Minor updates needed
>
> **What's Changed:**
>
> - ✅ New dependencies added (see requirements.txt)
> - ✅ New configuration fields (Phase 1)
> - ✅ Modern UI assets (Phase 4)
> - ⚠️ PyInstaller config may need updates
>
> **Still Accurate:**
>
> - Development setup
> - Raspberry Pi configuration
> - Network requirements
> - Security considerations
> - Troubleshooting guide

---

# Infrastructure and Deployment

## Development Environment

### Prerequisites

- **Python**: 3.9 or higher
- **Operating System**: macOS (primary target), may work on Linux with modifications
- **SSH Access**: Raspberry Pi with SSH enabled and key-based authentication configured

### Dependencies

**Core Framework**:

- `PySide6==6.10.0` - Qt6 bindings for Python (GUI framework)

**File Operations**:

- `watchdog==5.0.3` - Filesystem monitoring
- `send2trash==1.8.3` - Safe file deletion

**Remote Operations**:

- `paramiko==3.5.1` - SSH/SFTP client

**Configuration**:

- `pydantic-settings==2.5.2` - Settings validation
- `python-dotenv==1.0.1` - Environment variable management

**Utilities**:

- `pillow==12.0.0` - Image processing (icon manipulation)

**Build Tools**:

- `pyinstaller==6.16.0` - Application bundling

### Setup Instructions

1. **Clone Repository**:

```bash
git clone https://github.com/imlocle/pisync.git
cd pisync
```

2. **Create Virtual Environment**:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

3. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

4. **Configure SSH Key**:

```bash
# Generate SSH key if not exists
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Copy to Raspberry Pi
ssh-copy-id user@raspberry-pi-ip
```

5. **Run Application**:

```bash
python main.py
```

## Configuration

### Application Configuration

**Location**: `~/.PiSync/config.json`

**Structure**:

```json
{
  "pi_user": "pi",
  "pi_ip": "192.168.1.100",
  "pi_root_dir": "/mnt/external",
  "pi_movies": "Movies",
  "pi_tv": "TV_shows",
  "watch_dir": "/Users/username/Transfers",
  "ssh_key_path": "/Users/username/.ssh/id_rsa",
  "auto_start_monitor": true,
  "file_exts": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".srt"],
  "skip_files": [".DS_Store", "Thumbs.db", ".Trashes"],
  "last_modified": "2024-01-15 10:30:00 AM"
}
```

**First Run**: If config doesn't exist, settings dialog appears on startup

### Environment Variables

Currently not used, but could be added for:

- `PISYNC_CONFIG_PATH` - Override config location
- `PISYNC_LOG_LEVEL` - Set logging verbosity
- `PISYNC_DEBUG` - Enable debug mode

## Build and Packaging

### PyInstaller Configuration

**Build Command**:

```bash
pyinstaller --noconfirm --onedir --windowed \
  -n "PiSync" \
  --icon="assets/icons/pisync_logo.png" \
  --add-data="assets:assets" \
  --add-data="src/config/settings.py:src/config" \
  --add-data="src/controllers/monitor_thread.py:src/controllers" \
  --add-data="src/components/main_window.py:src/components" \
  --add-data="src/components/settings_window.py:src/components" \
  --add-data="src/components/splash_screen.py:src/components" \
  --add-data="src/utils/logging_signal.py:src/utils" \
  --add-data="src/widgets/file_explorer_widget.py:src/widgets" \
  main.py
```

**Output**: `dist/PiSync.app` (macOS application bundle)

**Flags Explained**:

- `--noconfirm`: Overwrite output without prompting
- `--onedir`: Create one-folder bundle (not single file)
- `--windowed`: No console window (GUI only)
- `-n "PiSync"`: Application name
- `--icon`: Application icon
- `--add-data`: Include non-Python files (format: `source:destination`)

### Asset Bundling

**Path Resolution**: `src/utils/helper.py::get_path()`

```python
if getattr(sys, "_MEIPASS", False):
    # PyInstaller bundle
    base_path = Path(sys._MEIPASS)
else:
    # Development
    base_path = Path("main.py").resolve().parent
```

**Bundled Assets**:

- `assets/icons/` - Application icons (PNG, SVG)
- `assets/styles/` - QSS stylesheets
- Python source files explicitly listed in `--add-data`

### Distribution

**Current Method**: Manual distribution of `.app` bundle

**Potential Improvements**:

- DMG creation for macOS distribution
- Code signing for macOS Gatekeeper
- Notarization for macOS Catalina+
- Auto-update mechanism
- Homebrew cask formula

## Deployment Architecture

### Client-Server Model

```
┌─────────────────────┐         SSH/SFTP (Port 22)        ┌─────────────────────┐
│                     │◄──────────────────────────────────►│                     │
│   MacBook (Client)  │                                    │  Raspberry Pi       │
│   - PiSync App      │         Encrypted Connection       │  - SSH Server       │
│   - Watch Directory │                                    │  - Media Storage    │
│                     │                                    │  - File System      │
└─────────────────────┘                                    └─────────────────────┘
```

### Network Requirements

**Ports**:

- TCP 22 (SSH/SFTP) - Must be accessible from MacBook to Pi

**Firewall**:

- Pi must allow incoming SSH connections
- MacBook must allow outgoing SSH connections

**Network Topology**:

- Both devices on same local network (recommended)
- Or Pi accessible via port forwarding/VPN

### Raspberry Pi Setup

**Recommended Configuration**:

1. **Enable SSH**:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

2. **Create Media Directories**:

```bash
sudo mkdir -p /mnt/external/Movies
sudo mkdir -p /mnt/external/TV_shows
sudo chown -R pi:pi /mnt/external
```

3. **Configure SSH Key Authentication**:

```bash
# On Pi
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Add MacBook's public key to ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

4. **Optional - Mount External Drive**:

```bash
# Find drive
lsblk

# Mount
sudo mount /dev/sda1 /mnt/external

# Auto-mount on boot (add to /etc/fstab)
/dev/sda1 /mnt/external ext4 defaults 0 0
```

## Monitoring and Logging

### Application Logs

**Current Implementation**:

- In-memory logs displayed in UI
- No persistent logging to disk

**Recommended Addition**:

```python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

log_dir = Path.home() / ".PiSync" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

handler = RotatingFileHandler(
    log_dir / "pisync.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

### System Monitoring

**MacBook**:

- Activity Monitor - Check CPU/memory usage
- Console.app - View system logs
- Network Utility - Monitor network traffic

**Raspberry Pi**:

```bash
# Check disk space
df -h /mnt/external

# Monitor SSH connections
sudo tail -f /var/log/auth.log

# Check system resources
htop
```

## Performance Considerations

### Transfer Speed

**Factors**:

- Network bandwidth (WiFi vs Ethernet)
- Raspberry Pi I/O speed (SD card vs USB drive vs SSD)
- File size and count
- SSH encryption overhead

**Optimization**:

- Use Ethernet connection for both devices
- Use external SSD on Pi for better I/O
- Consider compression for large files (not currently implemented)

### Resource Usage

**MacBook**:

- Minimal CPU usage when idle
- Moderate CPU during transfers (encryption)
- Low memory footprint (~100-200MB)

**Raspberry Pi**:

- SSH daemon overhead
- Disk I/O during writes
- Consider Pi 4 or newer for better performance

## Backup and Recovery

### Configuration Backup

**Manual Backup**:

```bash
cp ~/.PiSync/config.json ~/.PiSync/config.json.backup
```

**Recommended**: Add to version control or cloud storage

### Media Backup

**Not Handled by PiSync**: Consider separate backup solution for Pi media:

- External backup drive
- Cloud storage (Backblaze, etc.)
- RAID configuration
- Automated backup scripts (rsync, rclone)

## Security Considerations

### SSH Security

**Current Implementation**:

- Key-based authentication (good)
- `AutoAddPolicy` for host keys (security risk)

**Recommendations**:

1. **Disable Password Authentication** on Pi:

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
```

2. **Use Known Hosts**:

```python
# Replace AutoAddPolicy with proper host key verification
ssh_client.load_system_host_keys()
ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
```

3. **Restrict SSH Access**:

```bash
# /etc/ssh/sshd_config
AllowUsers pi
```

### File Permissions

**Pi Directories**:

```bash
chmod 755 /mnt/external/Movies
chmod 755 /mnt/external/TV_shows
```

**SSH Key**:

```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Check Pi is powered on and network accessible
   - Verify SSH service running: `sudo systemctl status ssh`
   - Test manual connection: `ssh -i ~/.ssh/id_rsa user@pi-ip`

2. **Permission Denied**:
   - Check SSH key permissions (600)
   - Verify key added to Pi's `authorized_keys`
   - Check Pi directory permissions

3. **Transfer Failures**:
   - Check disk space on Pi: `df -h`
   - Verify network stability
   - Check Pi logs: `/var/log/syslog`

4. **App Won't Start**:
   - Check Python version: `python --version`
   - Verify dependencies: `pip list`
   - Run from terminal to see errors: `python main.py`

### Debug Mode

**Enable Verbose Logging**:

```python
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```
