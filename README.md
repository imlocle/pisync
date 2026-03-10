# PiSync: Automated Media Transfer to Raspberry Pi

**PiSync** is a modern macOS desktop application that automatically transfers media files to your Raspberry Pi over SSH/SFTP. Built with PySide6, it features a clean dark-themed UI, real-time monitoring, and intelligent file handling.

![PiSync Logo](assets/icons/pisync_logo.png)

## ✨ Features

- **Automatic Monitoring**: Watches for new media files with stability checking
- **Smart Path Mapping**: Mirrors your local directory structure on the Pi
- **Dual-Pane Explorers**: Browse local and remote files simultaneously
- **Drag & Drop**: Seamless file transfers from Finder
- **Modern UI**: Professional dark theme with real-time activity log
- **Auto-Delete**: Optional cleanup after successful transfers

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- macOS (Windows/Linux support planned)
- SSH key access to your Raspberry Pi

### Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/pisync.git
cd pisync
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python main.py
```

### First-Time Setup

1. Click **Settings** (⚙️ icon)
2. Configure connection:
   - Pi IP Address (e.g., `192.168.1.100`)
   - Username (typically `pi`)
   - SSH Key Path (e.g., `~/.ssh/id_rsa`)
3. Set directories:
   - Local: `~/Transfers`
   - Remote: `/mnt/external`
4. Click **Connect** and **Start Monitoring**

## 📖 Documentation

- **[Getting Started](docs/README.md)** - Complete setup guide
- **[Architecture](docs/architecture.md)** - How PiSync works
- **[Troubleshooting](docs/README.md#troubleshooting)** - Common issues

## 🏗️ Architecture

```
Presentation (UI) → Application (Controllers) → Domain (Models) → Infrastructure (SFTP)
```

PiSync uses a clean layered architecture with protocol-based abstractions for testability.

## 📁 Project Structure

```
pisync/
├── main.py              # Entry point
├── src/
│   ├── application/     # Business logic
│   ├── components/      # UI windows
│   ├── domain/          # Models & protocols
│   └── infrastructure/  # SFTP & filesystem
├── assets/              # Icons & styles
└── docs/                # Documentation
```

## 🔧 Configuration

Settings stored in `~/.PiSync/config.json`:

```json
{
  "pi_ip": "192.168.1.100",
  "pi_username": "pi",
  "ssh_key_path": "~/.ssh/id_rsa",
  "local_watch_dir": "~/Transfers",
  "remote_base_dir": "/mnt/external",
  "delete_after_transfer": true
}
```

## 🐛 Troubleshooting

**Connection Issues:**

- Test SSH: `ssh pi@192.168.1.100`
- Check key permissions: `chmod 600 ~/.ssh/id_rsa`

**Transfer Issues:**

- Check activity log for errors
- Verify remote directory permissions
- Ensure sufficient disk space

## 🗺️ Roadmap

**Current (MVP):**

- ✅ Core functionality
- ✅ Modern UI
- ✅ File stability tracking

**Planned:**

- [ ] Test suite
- [ ] Parallel transfers
- [ ] Windows/Linux support
- [ ] Multi-Pi support

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Ensure type checking passes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with PySide6, Paramiko, Watchdog, and Pydantic.

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: ✅ Stable
