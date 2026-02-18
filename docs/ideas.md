# Ideas for Improvement

> **📅 Last Updated:** February 2026 (Post Phase 1-4 Redesign + Bug Fixes)
>
> **Status:** ✅ CURRENT - Reflects post-MVP roadmap
>
> **Recently Implemented:**
>
> - ✅ Idea #26: Dark Mode - Fully implemented with modern theme
> - ✅ Idea #27: Keyboard Shortcuts - Partially implemented
> - ✅ Idea #30: Customizable UI - Improved with modern design
> - ✅ Idea #32: Built-in Documentation - Comprehensive docs created
> - ✅ Bug Fixes: Drag & drop, Upload All progress, File stability tracking
>
> **Critical for MVP:**
>
> - 🔥 Remote Access (VPN/Tunnel) - See new section below
> - 🔥 Test Suite - Essential for reliability
> - 🔥 Packaging - macOS .app bundle
>
> **High Priority Post-MVP:**
>
> - 🔥 Idea #1: Smart File Organization (TMDB integration)
> - 🔥 Idea #3: Mobile Companion App
> - 🔥 Idea #6: Parallel Transfers
> - 🔥 Idea #11: Backup and Sync Modes

---

## 🌐 Remote Access (Critical Feature)

**Problem**: Currently, PiSync only works when on the same local network as the Raspberry Pi. When away from home, users cannot transfer files to their Pi.

**Goal**: Enable file transfers to the Pi from anywhere in the world, securely and reliably.

### Solution Options

#### Option 1: VPN (Recommended for MVP)

**Concept**: Use a VPN to create a secure tunnel to the home network.

**Implementation**:

- User sets up VPN server on home network (WireGuard, OpenVPN, or Tailscale)
- PiSync connects through VPN as if on local network
- No code changes needed in PiSync
- Works with existing SFTP implementation

**Pros**:

- ✅ Most secure option
- ✅ No PiSync code changes needed
- ✅ Works with all existing features
- ✅ Protects entire home network
- ✅ Can access other home devices too

**Cons**:

- ❌ Requires VPN setup (technical)
- ❌ VPN client must be running
- ❌ May have performance overhead

**Recommended VPN Solutions**:

1. **Tailscale** (Easiest)
   - Zero-config mesh VPN
   - Free for personal use
   - Works behind NAT
   - Automatic key management
   - Cross-platform
   - Setup: Install on Mac and Pi, authenticate, done

2. **WireGuard** (Best Performance)
   - Modern, fast VPN protocol
   - Minimal overhead
   - Built into Linux kernel
   - Requires port forwarding
   - Manual configuration

3. **OpenVPN** (Most Compatible)
   - Widely supported
   - Mature and stable
   - More complex setup
   - Requires port forwarding

**PiSync Integration**:

```python
# In settings, add VPN status indicator
class Settings:
    vpn_enabled: bool = False
    vpn_type: str = "tailscale"  # or "wireguard", "openvpn"

# In UI, show VPN status
if vpn_connected:
    status_label.setText("🔒 VPN Connected - Remote Access Enabled")
```

#### Option 2: SSH Tunnel / Port Forwarding

**Concept**: Forward SSH port through router or use SSH tunnel.

**Implementation A - Router Port Forwarding**:

- Forward port 22 (or custom) on router to Pi
- Use dynamic DNS for changing IP
- Connect to home IP from anywhere

**Implementation B - Reverse SSH Tunnel**:

- Pi maintains connection to cloud server
- Mac connects to cloud server
- Traffic tunneled through cloud

**Pros**:

- ✅ No VPN needed
- ✅ Direct connection
- ✅ Lower latency

**Cons**:

- ❌ Security risk (exposed SSH port)
- ❌ Requires dynamic DNS
- ❌ Router configuration needed
- ❌ May not work behind CGNAT

#### Option 3: Cloud Relay Service (Future)

**Concept**: Build a cloud service that relays transfers.

**Architecture**:

```
Mac → Cloud Service → Pi
```

**Implementation**:

- Mac uploads to cloud storage (S3, etc.)
- Pi polls cloud for new files
- Pi downloads and processes
- Cloud deletes after successful transfer

**Pros**:

- ✅ Works from anywhere
- ✅ No network configuration
- ✅ Can work offline (async)
- ✅ Built-in backup

**Cons**:

- ❌ Requires cloud infrastructure
- ❌ Monthly costs
- ❌ Privacy concerns
- ❌ Slower (two transfers)
- ❌ Complex to build

#### Option 4: Hybrid Approach (Best Long-Term)

**Concept**: Combine multiple methods with automatic fallback.

**Priority Order**:

1. Local network (fastest, most secure)
2. VPN (secure, good performance)
3. Direct SSH (if configured)
4. Cloud relay (fallback)

**Implementation**:

```python
class ConnectionStrategy:
    def connect(self) -> Connection:
        # Try local network first
        if self.try_local_connection():
            return LocalConnection()

        # Try VPN
        if self.vpn_available():
            return VPNConnection()

        # Try direct SSH
        if self.direct_ssh_configured():
            return DirectSSHConnection()

        # Fallback to cloud relay
        return CloudRelayConnection()
```

**Pros**:

- ✅ Always works
- ✅ Optimal performance
- ✅ Graceful degradation

**Cons**:

- ❌ Complex to implement
- ❌ Multiple failure modes
- ❌ Harder to debug

### Recommended Implementation Plan

#### Phase 1: VPN Support (MVP)

**Goal**: Document VPN setup, add VPN status indicator

**Tasks**:

1. Create VPN setup guide (Tailscale, WireGuard, OpenVPN)
2. Add VPN status detection in UI
3. Add connection method indicator
4. Test with Tailscale (easiest)

**Deliverables**:

- `docs/vpn-setup-guide.md`
- VPN status in UI
- Connection method indicator

**Effort**: 1-2 days

#### Phase 2: Connection Detection (Post-MVP)

**Goal**: Auto-detect connection method

**Tasks**:

1. Detect if on local network
2. Detect if VPN is active
3. Show connection method in UI
4. Warn if no connection available

**Deliverables**:

- Smart connection detection
- Better error messages
- Connection troubleshooting

**Effort**: 2-3 days

#### Phase 3: Direct SSH Support (Future)

**Goal**: Support direct SSH with dynamic DNS

**Tasks**:

1. Add dynamic DNS configuration
2. Add custom SSH port support
3. Add connection testing
4. Security warnings

**Deliverables**:

- Dynamic DNS support
- Port forwarding guide
- Security best practices

**Effort**: 3-5 days

#### Phase 4: Cloud Relay (Future)

**Goal**: Build cloud relay service

**Tasks**:

1. Design cloud architecture
2. Build relay service (FastAPI)
3. Implement client-side logic
4. Add encryption
5. Deploy to cloud

**Deliverables**:

- Cloud relay service
- Client integration
- Subscription model

**Effort**: 2-3 weeks

### Security Considerations

**VPN Approach**:

- ✅ End-to-end encryption
- ✅ No exposed ports
- ✅ Network-level security
- ⚠️ Requires trust in VPN provider (use Tailscale or self-hosted)

**Direct SSH Approach**:

- ⚠️ Exposed SSH port (brute force risk)
- ✅ SSH encryption
- ⚠️ Requires strong authentication
- ⚠️ Requires firewall rules

**Cloud Relay Approach**:

- ⚠️ Data passes through third party
- ✅ Can add end-to-end encryption
- ⚠️ Requires trust in cloud provider
- ✅ No home network exposure

### User Experience

**Ideal UX**:

1. User installs Tailscale on Mac and Pi
2. User authenticates both devices
3. PiSync automatically detects VPN
4. Connection "just works" from anywhere
5. Status shows "🔒 Remote Access (VPN)"

**Settings UI**:

```
┌─────────────────────────────────────┐
│ Connection Settings                  │
├─────────────────────────────────────┤
│ Connection Method:                   │
│ ○ Automatic (Recommended)           │
│ ○ Local Network Only                │
│ ○ VPN (Tailscale/WireGuard)        │
│ ○ Direct SSH (Advanced)            │
│                                      │
│ VPN Status: ✅ Connected            │
│ VPN Type: Tailscale                 │
│                                      │
│ [Test Connection]                   │
└─────────────────────────────────────┘
```

### Documentation Needed

1. **VPN Setup Guide**
   - Tailscale setup (step-by-step)
   - WireGuard setup
   - OpenVPN setup
   - Troubleshooting

2. **Remote Access FAQ**
   - How does it work?
   - Is it secure?
   - What's the best option?
   - Performance comparison

3. **Security Best Practices**
   - VPN vs Direct SSH
   - SSH key management
   - Firewall configuration
   - Monitoring access logs

### Cost Analysis

**VPN Options**:

- Tailscale: Free for personal use (up to 20 devices)
- WireGuard: Free (self-hosted)
- OpenVPN: Free (self-hosted)

**Cloud Relay** (if built):

- AWS/GCP costs: ~$20-50/month
- Storage costs: ~$0.02/GB
- Transfer costs: ~$0.09/GB
- Total: ~$30-100/month depending on usage

**Recommendation**: Start with VPN (free), consider cloud relay only if there's demand and willingness to pay.

### Success Metrics

**MVP Success**:

- ✅ Users can transfer files from anywhere
- ✅ Setup takes < 15 minutes
- ✅ Works reliably
- ✅ Secure by default

**Post-MVP Success**:

- ✅ 90%+ connection success rate
- ✅ < 5% performance overhead
- ✅ Automatic fallback works
- ✅ Clear error messages

---

# Ideas for Improvement

## User Experience Enhancements

### 1. Smart File Organization

**Concept**: Automatically organize media files using metadata from online databases.

**Features**:

- Integration with TMDB (The Movie Database) API
- Automatic movie/TV show identification from filename
- Fetch metadata: title, year, season, episode, poster art
- Rename files to standardized format: `Movie Title (Year).ext` or `Show Name - S01E01 - Episode Title.ext`
- Download and embed subtitles automatically
- Create NFO files for media center compatibility (Plex, Kodi, Jellyfin)

**Benefits**:

- Consistent naming conventions
- Better media center integration
- Reduced manual organization

**Implementation**:

```python
class MetadataService:
    def fetch_movie_metadata(self, filename: str) -> MovieMetadata:
        # Parse filename, query TMDB, return metadata
        pass

    def rename_with_metadata(self, file_path: str, metadata: MovieMetadata):
        # Rename file using metadata
        pass
```

---

### 2. Drag-and-Drop from Anywhere

**Concept**: System-wide drag-and-drop support without opening the app.

**Features**:

- Menu bar icon (macOS) or system tray icon (Windows/Linux)
- Drop files onto icon to queue for transfer
- Show notification when transfer completes
- Quick access to settings and logs from menu bar

**Benefits**:

- Faster workflow
- No need to keep app window open
- Less screen clutter

**Implementation**:

- Use `rumps` (macOS) or `pystray` (cross-platform)
- Background service mode
- Notification system integration

---

### 3. Mobile Companion App

**Concept**: iOS/Android app to monitor and control transfers remotely.

**Features**:

- View transfer progress
- Start/stop monitoring
- Browse Pi files
- Trigger manual uploads from phone
- Receive push notifications on transfer completion
- Remote settings management

**Technology Stack**:

- React Native or Flutter for cross-platform
- REST API on desktop app
- WebSocket for real-time updates

---

### 4. Web Interface

**Concept**: Browser-based interface for remote access.

**Features**:

- Access PiSync from any device on local network
- Upload files via web browser
- Monitor transfer status
- View logs and statistics
- Responsive design for mobile browsers

**Implementation**:

- FastAPI or Flask backend
- React or Vue.js frontend
- WebSocket for real-time updates
- Authentication for security

---

### 5. Batch Operations

**Concept**: Perform operations on multiple files simultaneously.

**Features**:

- Multi-select in file explorer
- Batch delete
- Batch rename with patterns
- Batch move to different directory
- Batch metadata editing

**UI Enhancement**:

- Checkbox selection mode
- "Select All" / "Select None" buttons
- Bulk action toolbar

---

## Performance Improvements

### 6. Parallel Transfers

**Concept**: Transfer multiple files simultaneously for faster throughput.

**Features**:

- Configurable number of concurrent transfers (default: 3)
- Intelligent scheduling (small files first)
- Bandwidth distribution across transfers
- Per-transfer progress tracking

**Benefits**:

- Faster overall transfer time
- Better network utilization
- Reduced idle time

**Implementation**:

```python
class ParallelTransferController:
    def __init__(self, max_workers: int = 3):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_transfers = []

    def submit_transfer(self, request: TransferRequest):
        future = self.executor.submit(self._transfer, request)
        self.active_transfers.append(future)
```

---

### 7. Compression During Transfer

**Concept**: Compress files before transfer to save bandwidth and time.

**Features**:

- Automatic compression for large files
- Decompress on Pi after transfer
- Configurable compression level
- Skip compression for already-compressed formats (mkv, mp4)

**Benefits**:

- Faster transfers on slow networks
- Reduced bandwidth usage
- Lower network costs (if metered)

**Implementation**:

- Use `gzip` or `lz4` for compression
- Compress in chunks to avoid memory issues
- SSH compression option: `ssh -C`

---

### 8. Delta Sync (Rsync-like)

**Concept**: Only transfer changed portions of files.

**Features**:

- Compare local and remote files
- Transfer only differences
- Resume interrupted transfers
- Verify checksums

**Benefits**:

- Much faster for updated files
- Resume capability
- Bandwidth savings

**Implementation**:

- Use `librsync` Python bindings
- Or implement custom delta algorithm
- Store checksums for comparison

---

### 9. Intelligent Scheduling

**Concept**: Schedule transfers during off-peak hours or when network is idle.

**Features**:

- Set transfer time windows (e.g., 2 AM - 6 AM)
- Detect network activity and pause transfers
- Priority queue (urgent vs. background)
- Bandwidth throttling during peak hours

**Benefits**:

- Doesn't interfere with work
- Better network utilization
- Reduced congestion

---

### 10. Caching and Deduplication

**Concept**: Avoid transferring duplicate files.

**Features**:

- Calculate file checksums (MD5, SHA256)
- Maintain database of transferred files
- Skip files already on Pi
- Detect renamed files by checksum
- Deduplicate across different folders

**Benefits**:

- Saves bandwidth
- Faster transfers
- Reduced storage on Pi

**Implementation**:

```python
class DeduplicationService:
    def __init__(self):
        self.checksum_db = {}  # checksum -> remote_path

    def calculate_checksum(self, file_path: str) -> str:
        # Calculate SHA256
        pass

    def is_duplicate(self, checksum: str) -> bool:
        return checksum in self.checksum_db
```

---

## Feature Additions

### 11. Backup and Sync Modes

**Concept**: Different operation modes for different use cases.

**Modes**:

1. **Transfer Mode** (current): Move files from Mac to Pi, delete local
2. **Sync Mode**: Keep files in sync bidirectionally
3. **Backup Mode**: Copy to Pi but keep local files
4. **Mirror Mode**: Pi mirrors Mac exactly (delete files removed from Mac)

**Configuration**:

- Per-directory mode settings
- Global default mode
- Mode indicator in UI

---

### 12. Version Control for Media

**Concept**: Keep multiple versions of files with history.

**Features**:

- Automatic versioning on overwrite
- Configurable retention (keep last N versions)
- Restore previous versions
- Compare versions
- Show version history timeline

**Storage**:

- Versions stored in `.pisync/versions/` on Pi
- Metadata in SQLite database
- Automatic cleanup of old versions

---

### 13. Transcoding Pipeline

**Concept**: Automatically transcode media files to optimal formats.

**Features**:

- Convert to H.265 for space savings
- Normalize audio levels
- Remove unwanted audio/subtitle tracks
- Resize videos for streaming
- Generate thumbnails and previews

**Implementation**:

- Use `ffmpeg` for transcoding
- Queue-based processing
- Progress tracking
- Configurable presets (quality vs. size)

---

### 14. Smart Playlists and Collections

**Concept**: Organize media into dynamic collections.

**Features**:

- Create playlists based on metadata
- Auto-collections: "Recently Added", "Unwatched", "Favorites"
- Genre-based collections
- Actor/director-based collections
- Share playlists with media centers

**UI**:

- Playlist editor
- Drag-and-drop to add items
- Export to M3U format

---

### 15. Watch Status Tracking

**Concept**: Track which media has been watched.

**Features**:

- Mark as watched/unwatched
- Resume position tracking
- Watch history
- Sync with media center (Plex, Jellyfin)
- Recommendations based on watch history

**Integration**:

- API integration with media centers
- Local database for standalone tracking
- Export watch history

---

## Advanced Features

### 16. Multi-Pi Support

**Concept**: Manage transfers to multiple Raspberry Pis.

**Features**:

- Configure multiple Pi destinations
- Route files based on rules (movies to Pi1, TV to Pi2)
- Load balancing across Pis
- Failover to backup Pi
- Sync between Pis

**UI**:

- Pi selector dropdown
- Multi-Pi dashboard
- Per-Pi statistics

---

### 17. Cloud Storage Integration

**Concept**: Backup to cloud storage in addition to Pi.

**Features**:

- Support for S3, Google Drive, Dropbox, OneDrive
- Automatic cloud backup after Pi transfer
- Cloud-only mode (no Pi required)
- Restore from cloud
- Encryption for cloud storage

**Benefits**:

- Offsite backup
- Disaster recovery
- Access from anywhere

---

### 18. Automated Quality Control

**Concept**: Verify file integrity and quality automatically.

**Features**:

- Check for corrupted files
- Verify video/audio streams playable
- Detect incomplete downloads
- Check subtitle sync
- Validate file formats
- Generate quality reports

**Implementation**:

- Use `ffprobe` for media analysis
- Checksum verification
- Automated testing on Pi
- Quarantine problematic files

---

### 19. Plugin System

**Concept**: Extensible architecture for custom functionality.

**Features**:

- Plugin API for custom transfer logic
- Custom file classifiers
- Post-transfer hooks
- Custom UI widgets
- Third-party integrations

**Plugin Types**:

- Transfer plugins (custom protocols)
- Classifier plugins (custom rules)
- Notification plugins (Slack, Discord, email)
- Metadata plugins (custom sources)

**Implementation**:

```python
class PluginInterface:
    def on_transfer_start(self, file_path: str):
        pass

    def on_transfer_complete(self, file_path: str):
        pass

    def classify_file(self, file_path: str) -> Optional[str]:
        pass
```

---

### 20. AI-Powered Features

**Concept**: Use machine learning for intelligent automation.

**Features**:

- Learn user's organization preferences
- Predict file classification from patterns
- Suggest optimal transfer times
- Detect duplicate content (different files, same movie)
- Auto-tag media with scene detection
- Generate smart thumbnails

**Implementation**:

- Local ML models (no cloud required)
- TensorFlow Lite or ONNX
- Train on user's transfer history
- Privacy-preserving

---

## Integration Ideas

### 21. Media Center Integration

**Concept**: Deep integration with popular media centers.

**Supported Platforms**:

- Plex
- Jellyfin
- Kodi
- Emby

**Features**:

- Trigger library scan after transfer
- Fetch metadata from media center
- Sync watch status
- Remote control media center
- Show "Now Playing" in PiSync

---

### 22. Torrent Client Integration

**Concept**: Automatically transfer completed downloads.

**Supported Clients**:

- Transmission
- qBittorrent
- Deluge
- rTorrent

**Features**:

- Monitor torrent completion
- Auto-classify and transfer
- Preserve seeding (copy, don't move)
- Bandwidth coordination
- Show torrent status in PiSync

---

### 23. NAS Integration

**Concept**: Support for network-attached storage.

**Features**:

- SMB/CIFS protocol support
- NFS protocol support
- Direct NAS transfers (bypass Mac)
- NAS as intermediate storage
- Multi-NAS support

---

### 24. Home Automation Integration

**Concept**: Integrate with smart home systems.

**Platforms**:

- Home Assistant
- HomeKit
- IFTTT
- Zapier

**Features**:

- Trigger transfers via voice commands
- Automation rules (transfer when home)
- Status notifications to smart displays
- Integration with scenes

---

### 25. Notification Enhancements

**Concept**: Rich notifications across multiple channels.

**Channels**:

- macOS Notification Center
- Email
- SMS (Twilio)
- Slack
- Discord
- Telegram
- Pushover

**Notification Types**:

- Transfer complete
- Transfer failed
- Low disk space on Pi
- Connection lost
- Daily summary

---

## Quality of Life Improvements

### 26. Dark Mode

**Concept**: Full dark theme support.

**Features**:

- System theme detection
- Manual theme toggle
- Custom theme colors
- High contrast mode
- Theme preview

---

### 27. Keyboard Shortcuts

**Concept**: Comprehensive keyboard navigation.

**Shortcuts**:

- `Cmd+R`: Refresh explorers
- `Cmd+U`: Upload all
- `Cmd+,`: Settings
- `Cmd+K`: Clear logs
- `Space`: Quick look file
- `Delete`: Delete selected
- `Cmd+F`: Search files

---

### 28. Search and Filter

**Concept**: Powerful search across local and remote files.

**Features**:

- Full-text search
- Filter by type, size, date
- Saved searches
- Regular expression support
- Search history

---

### 29. File Preview

**Concept**: Preview files without opening external apps.

**Features**:

- Video preview with playback controls
- Image preview
- Subtitle preview
- Audio waveform visualization
- Quick Look integration (macOS)

---

### 30. Customizable UI

**Concept**: User-configurable interface.

**Features**:

- Rearrangeable panels
- Hideable UI elements
- Custom toolbar buttons
- Saved layouts
- Compact mode for small screens

---

## Documentation and Help

### 31. Interactive Tutorial

**Concept**: Guided walkthrough for new users.

**Features**:

- Step-by-step setup wizard
- Interactive tooltips
- Video tutorials
- Sample configuration
- Troubleshooting guide

---

### 32. Built-in Documentation

**Concept**: Comprehensive help system within the app.

**Features**:

- Searchable documentation
- Context-sensitive help
- FAQ section
- Keyboard shortcut reference
- API documentation for plugins

---

### 33. Diagnostic Tools

**Concept**: Built-in troubleshooting utilities.

**Features**:

- Connection tester
- Network speed test
- Log analyzer
- Configuration validator
- System requirements checker
- Export diagnostic report

---

## Community Features

### 34. Configuration Sharing

**Concept**: Share and import configurations.

**Features**:

- Export configuration as file
- Import from file or URL
- Configuration templates
- Community configuration repository
- Version compatibility checking

---

### 35. Usage Analytics (Opt-in)

**Concept**: Anonymous usage statistics to improve the app.

**Collected Data**:

- Feature usage frequency
- Error rates
- Performance metrics
- Platform information

**Privacy**:

- Fully opt-in
- No personal data
- No file names or paths
- Open source analytics code

---

## Future-Proofing

### 36. Protocol Abstraction

**Concept**: Support multiple transfer protocols.

**Protocols**:

- SFTP (current)
- FTP/FTPS
- WebDAV
- Syncthing
- Resilio Sync
- Custom protocols via plugins

---

### 37. Cross-Platform Support

**Concept**: Full support for Windows and Linux.

**Considerations**:

- Path handling differences
- System tray vs. menu bar
- File system monitoring differences
- SSH client differences
- Installer for each platform

---

### 38. Containerization

**Concept**: Run PiSync in Docker container.

**Benefits**:

- Consistent environment
- Easy deployment
- Server mode (headless)
- Kubernetes support
- Scalability

---

### 39. API-First Architecture

**Concept**: Expose all functionality via REST API.

**Benefits**:

- Third-party integrations
- Custom clients
- Automation scripts
- Testing
- Future mobile apps

---

### 40. Internationalization

**Concept**: Multi-language support.

**Features**:

- Translatable UI strings
- Date/time localization
- Number formatting
- RTL language support
- Community translations

**Implementation**:

- Use Qt's translation system
- Extract strings to `.ts` files
- Crowdsource translations
- Auto-detect system language
