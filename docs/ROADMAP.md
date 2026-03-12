# Roadmap & Ideas

**Last Updated:** March 12, 2026 | **Status:** Active Development

PiSync roadmap for future versions. Ideas are organized by priority, complexity, and target release.

---

## Version 1.1 (Q2 2026) - Quality & Stability

### High Priority (Core Improvements)

#### 1. **TV Show Classification Improvements** 🎯 (NEW)

**Target:** Fix the TV show mis-classification issue (see BUGS.md #7)

**Tasks:**

- [ ] Expand regex patterns to handle non-standard naming
  - Support: "SeriesName - EpisodeName.mkv"
  - Support: "Series.Name.SnnEnn.Year.mkv"
  - Support: "Series.Name.SnEnn.mkv" (single letter)
- [ ] Test against 50+ real TV file naming conventions
- [ ] Add "Manual Classification" UI (right-click → Move to Movies/TV)

**Effort:** 2-3 days | **Risk:** Low

---

#### 2. **Auto-Create Remote Base Directory** 🎯

**Target:** Eliminate common setup error where remote directory doesn't exist

**Tasks:**

- [ ] On first successful connection, test if remote base dir exists
- [ ] If not, attempt `mkdir -p /mnt/external` (or configured path)
- [ ] Show warning if directory creation fails (permission denied)

**Effort:** 1 day | **Risk:** Low

---

#### 3. **Case-Insensitive File Extension Matching**

**Target:** Support .MP4, .mkv, .MKV, etc.

**Tasks:**

- [ ] Normalize extensions to lowercase before comparison
- [ ] Backward compatible with existing lowercase lists

**Effort:** 2 hours | **Risk:** Minimal

---

#### 4. **SSH Connection Timeout Handling** 🎯

**Target:** Fix hanging UI on network interruption (see BUGS.md #2)

**Tasks:**

- [ ] Set explicit socket timeout in Paramiko (5-10 seconds)
- [ ] Implement connection validation in worker thread (not UI thread)
- [ ] Add retry UI with exponential backoff
- [ ] Test with WiFi disconnection scenarios

**Effort:** 2 days | **Risk:** Medium (threading)

---

### Medium Priority (Enhanced Features)

#### 5. **Detailed Activity Log Search/Filter**

**Target:** Find transfers from last week, all errors, etc.

**Tasks:**

- [ ] Add search box to activity log
- [ ] Filter by: result (success/error), date range, file type
- [ ] Export activity log to CSV
- [ ] Add timestamp to each log entry

**Effort:** 3 days | **Risk:** Low

---

#### 6. **Transfer Verification with Checksum**

**Target:** Replace file size verification with CRC32/SHA256

**Tasks:**

- [ ] Compute checksum of local file before transfer
- [ ] Compute checksum of remote file after transfer
- [ ] Compare; if mismatch, alert user and don't delete
- [ ] Option: Re-transfer automatically

**Effort:** 2 days | **Risk:** Low | **Complexity:** Medium

---

#### 7. **Skip Patterns Editor UI**

**Target:** Visual editor for skip patterns instead of JSON editing

**Tasks:**

- [ ] Add table to SettingsWindow for skip patterns
- [ ] Add/remove/edit patterns with UI
- [ ] Real-time preview: "This file would be SKIPPED"

**Effort:** 2 days | **Risk:** Low

---

#### 8. **Bandwidth Limiting**

**Target:** Cap transfer speed (useful for avoiding network congestion)

**Tasks:**

- [ ] Add "Max bandwidth" setting (MB/s)
- [ ] Implement rate limiting in SFTP transfer loop
- [ ] Show current bandwidth in activity log

**Effort:** 2 days | **Risk:** Low

---

### Low Priority (Polish)

#### 9. **Notification Center Integration**

**Target:** Native macOS notifications for key events

**Tasks:**

- [ ] Show notification when transfer completes
- [ ] Show notification on errors
- [ ] Option to enable/disable in settings

**Effort:** 1 day | **Risk:** Low

---

#### 10. **Keyboard Shortcuts**

**Target:** Common app shortcuts

**Tasks:**

- [ ] Cmd+, → Settings
- [ ] Cmd+Q → Quit (already works)
- [ ] Cmd+C → Connect
- [ ] Cmd+M → Toggle monitoring
- [ ] Space → Manual transfer selected file

**Effort:** 1 day | **Risk:** Minimal

---

---

## Version 1.2 (Q3-Q4 2026) - Advanced Features

### Core Features

#### 1. **Persistent Transfer Queue** 🎯

**Target:** Remember queued files across app restarts

**Architecture:**

```python
# queue.json (user home)
{
  "transfers": [
    {
      "source": "/Users/me/Transfers/movie.mp4",
      "destination": "/mnt/external/Movies/movie.mp4",
      "created_at": "2026-03-12T10:30:00Z",
      "priority": 1
    }
  ]
}
```

**Tasks:**

- [ ] Save queue to JSON before exit
- [ ] Load and resume queue on startup
- [ ] Show "X transfers queued" in UI
- [ ] Allow pause/resume/reorder queue

**Effort:** 3 days | **Risk:** Medium (state management)

---

#### 2. **Scheduled Transfers** ⏰

**Target:** Run monitoring only at specific times

**UI Changes:**

- Add "Schedule" tab to SettingsWindow
- Options:
  - Always on
  - Daily 3-6 PM
  - Weekdays only
  - Custom cron expression

**Tasks:**

- [ ] Integrate APScheduler library
- [ ] Add scheduling settings
- [ ] Persist schedule to config
- [ ] Pause monitoring outside schedule window

**Effort:** 3 days | **Risk:** Low

---

#### 3. **Duplicate File Detection**

**Target:** Skip/warning if file already exists on remote

**Options:**

- Skip if exists
- Skip if content matches (check CRC)
- Overwrite
- Ask user

**Tasks:**

- [ ] Check if remote file exists before transfer
- [ ] Show preview: "Movie.mp4 already on remote (125.3 MB)"
- [ ] User chooses action

**Effort:** 2 days | **Risk:** Low

---

#### 4. **Multiple Server Sync** 🎯 (Major)

**Target:** Transfer to multiple Raspberry Pis in parallel

**Architecture Changes:**

```
TransferWorker(s) - one per server
  ↓
  Each manages separate SFTP connection

MonitorThread → Route to appropriate server(s)
```

**UI Changes:**

- Server list checkboxes: "Sync to: [✓] Living Room [ ] Bedroom [✓] Kitchen"
- Per-server transfer status in activity log

**Tasks:**

- [ ] Redesign TransferWorker for multiple servers
- [ ] Add server multi-select UI
- [ ] Test parallel transfers to 2+ servers
- [ ] Load balance (slow down if one server backlogged)

**Effort:** 5-7 days | **Risk:** High (complex threading)

---

### Enhanced Features

#### 5. **Movie Metadata Enrichment**

**Target:** Fetch movie info from TMDb API

**On Transfer:**

- Fetch title, year, poster from TheMovieDB
- Organize as: `Movies/Title (Year)/movie.mp4`
- Cache metadata locally

**Tasks:**

- [ ] Register TheMovieDB API key (free tier: 40 req/10s)
- [ ] Create MovieMetadata service
- [ ] Add poster image display in UI
- [ ] Handle API failures gracefully

**Effort:** 4 days | **Risk:** Medium (external API)

---

#### 6. **Smart Folder Organization**

**Target:** Learn user's organization patterns and auto-apply

**Example:**

- User moves all "Marvel" movies to "Movies/Marvel/" on remote
- AI learns pattern: movies with "Marvel" in name → "Movies/Marvel/"
- Future Marvel movies auto-organize

**Tasks:**

- [ ] Analyze user's remote folder structure
- [ ] Extract common patterns (actors, genres, years)
- [ ] Train simple Bayesian classifier
- [ ] Suggest organization; allow user review

**Effort:** 5-7 days | **Risk:** Medium-High (ML)

---

#### 7. **Bandwidth & Storage Monitoring**

**Target:** Show graphs of transfer speed and remote disk usage

**UI:** New "Monitor" panel with:

- Real-time transfer speed graph
- Remote disk free space gauge
- Files transferred this week/month

**Tasks:**

- [ ] Sample transfer speed every 100ms
- [ ] Query remote disk usage via SFTP
- [ ] Plot graphs with matplotlib/pyqtgraph
- [ ] Store stats in SQLite for history

**Effort:** 3-4 days | **Risk:** Low

---

---

## Version 2.0 (2027) - Major Redesign

### Architectural Changes

#### 1. **Plugin System**

**Target:** Allow custom transfer handlers via plugins

```python
class CustomTransferPlugin:
    def classify(self, filename):
        return "custom_category"

    def get_destination(self, filename):
        return "/mnt/custom/path"
```

**Load plugins from:** `~/.pisync/plugins/`

---

#### 2. **Event-Based Architecture**

**Target:** Replace signal/slot with pub/sub event bus

```python
event_bus.subscribe("file.detected", handler)
event_bus.publish("file.detected", filename)
```

**Benefits:**

- Loose coupling
- Easier testing
- Easier to add features

---

#### 3. **Web UI Dashboard**

**Target:** Browser-based control panel (Flask backend)

**Accessible from:**

- `http://localhost:5000/pisync`
- Mobile browser on same network

**Features:**

- View transfer history
- Monitor current transfers
- Change settings
- Restart app

**Architecture:**

```
PiSync Desktop App
        ↓ (serves)
Flask Server (localhost:5000)
        ↓ (serves)
Browser UI
```

---

### New Features

#### 4. **Bidirectional Sync** (Optional)

**Target:** Two-way sync between macOS and Raspberry Pi

**Careful Design:**

- Conflict resolution strategy (newest wins, always local, always remote, ask)
- Deletion handling (propagate or keep locally?)
- Safe defaults to prevent data loss

---

#### 5. **Network Optimization**

**Target:** Better handling of unreliable networks

**Tasks:**

- [ ] Resume partial transfers
- [ ] Chunked transfer with retry per chunk
- [ ] Fallback to lower quality if bandwidth limited

---

---

## Community-Requested Features (Under Consideration)

### Popular Requests

1. **Linux Support** (⭐⭐⭐⭐)
   - Adapt for Linux/Fedora
   - Test with multiple distros
   - Priority: v1.2 or v2.0

2. **Windows Support** (⭐⭐⭐)
   - PySide6 works on Windows
   - Most code is cross-platform
   - Main work: Windows-specific file handling
   - Priority: v2.0 or later

3. **Alternate Media Servers** (⭐⭐)
   - Not just Raspberry Pi - support:
     - Synology NAS
     - Nextcloud
     - Jellyfin server
   - Priority: v2.0+

4. **Secure Deletion** (⭐⭐)
   - Overwrite file content before deletion
   - Prevent recovery via data recovery tools
   - Priority: v1.2 (low effort)

5. **Backup Versioning** (⭐)
   - Keep multiple versions of files
   - Automatic cleanup of old versions
   - Priority: v2.0+ (complex)

---

## Won't Implement (By Design)

These features are intentionally NOT planned:

- **Peer-to-Peer Sync** - Too complex; cloud sync exists (Synology, NextCloud)
- **Compression** - Better to compress before uploading or use SFTP compression
- **Redundancy/RAID** - Out of scope; manage on Raspberry Pi side
- **User Authentication** - Single user per instance; run multiple instances for multiple users
- **Encryption** - Use per-disk encryption on Raspberry Pi

---

## How to Request a Feature

1. **Check existing issues** - Don't duplicate
2. **Star popular issues** - Vote with reactions (⭐)
3. **Add details:**
   - Use case: What problem does this solve?
   - Proposed solution: How would it work?
   - Workaround: Can you work around it today?
4. **Link to similar projects** - Show how others solved it

**Post on:** [GitHub Discussions](https://github.com/imlocle/pisync/discussions)

---

## Release Timeline (Estimated)

| Version | Date          | Focus                                       |
| ------- | ------------- | ------------------------------------------- |
| **1.0** | ✅ March 2026 | Core functionality, production-ready        |
| **1.1** | Q2 2026       | Quality fixes, TV classification, stability |
| **1.2** | Q3-Q4 2026    | Queuing, scheduling, multi-server           |
| **2.0** | 2027          | Plugin system, web UI, major refactor       |

---

## Development Priorities

### Next Sprint (March-April 2026)

Priority 1 (MUST):

- [ ] TV classification improvements
- [ ] SSH timeout handling
- [ ] Auto-create remote directory

Priority 2 (SHOULD):

- [ ] Activity log search
- [ ] CRC32 verification
- [ ] Case-insensitive extensions

Priority 3 (NICE):

- [ ] Notifications
- [ ] Keyboard shortcuts
- [ ] Skip patterns UI

---

## Contribution Opportunities

Great ways to contribute:

1. **Bug Reports** - Test edge cases, file issues
2. **Regex Patterns** - Improve TV show classification (ROADMAP 1.1 #1)
3. **Documentation** - Write user guides, troubleshooting
4. **Translations** - Localize UI for other languages
5. **Unit Tests** - Write tests for services (HIGH NEED)
6. **Platform Testing** - Test on different macOS versions

See [DEVELOPMENT.md](./DEVELOPMENT.md) for contributor setup.
