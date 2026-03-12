# Known Issues & Limitations

**Last Updated:** March 12, 2026 | **Status:** Production v1.0.0

This document tracks known bugs, limitations, and workarounds for PiSync.

**Severity Levels:**

- 🔴 **Critical** - App crash or data loss
- 🟠 **High** - Core feature broken
- 🟡 **Medium** - Feature works incorrectly but has workaround
- 🔵 **Low** - Minor cosmetic or edge case issue

---

## Known Issues

### 1. 🟡 File Stability Check May Miss Rapid Transfers

**Issue:** Very fast file writes (e.g., copying from RAM disk) may complete before the 2-second stability check completes.

**Symptom:** File appears in remote directory after ~2.5s instead of immediately.

**Root Cause:** Stability check polls file size every 2 seconds. On fast writes, file may be fully written and start shrinking within this window.

**Workaround:**

- Increase `stability_duration` in settings to 3-4 seconds
- Accept the 2-second delay as part of the polling model

**Status:** Low priority - normal file writing (from downloads, etc.) completes over 5-30 seconds, so 2-second check is effective

**Resolution Timeline:** Monitor for real-world impact. Consider event-based file change detection if users report issues.

---

### 2. 🟡 SSH Connection Hangs on Network Interruption

**Issue:** If network drops while transfer is in progress, app may hang for 20-30 seconds before timing out.

**Symptom:** App becomes unresponsive; "Transferring..." status hangs; must force quit.

**Root Cause:** Paramiko SSH client has 20-30 second default timeout. Qt event loop is blocked waiting for I/O.

**Workaround:**

- Ensure stable network connection (WiFi with good signal)
- If stuck, force quit and restart
- Transfers restart from last stable checkpoint

**Status:** Medium priority - affects users with unreliable WiFi

**Fix in Progress:** Move all I/O to worker threads (already done for transfers, but connection validation still happens on main thread)

**Resolution:**

- Set explicit socket timeout in Paramiko (5-10 seconds)
- Implement non-blocking I/O with timeout handling
- Target: v1.1.0

---

### 3. 🔵 Duplicate Files After Failed Transfer

**Issue:** If transfer succeeds but verification fails (corrupted transfer), file is deleted locally but remote copy may be incomplete.

**Symptom:** Empty or truncated file appears on Raspberry Pi.

**Root Cause:** Delete happens AFTER verification, but verification race condition between transfer completion and file size check.

**Workaround:**

- SSH to Raspberry Pi and manually verify file sizes
- Re-transfer if file is corrupted (will overwrite)

**Status:** Low priority - transfer failures are rare with stable network

**Fix:** Add CRC32 checksum verification in addition to file size check (v1.2.0)

---

### 4. 🔵 Settings Dialog Won't Open on macOS 12.x

**Issue:** On some older macOS versions, SettingsWindow displays partially off-screen or without window decorations.

**Symptom:** Settings button unresponsive; must restart app to recover.

**Root Cause:** macOS window positioning bug with PySide6 on older versions.

**Workaround:**

- Tested and works on macOS 13+
- For macOS 12.x: Set QT_MAC_WANTS_LAYER=1 environment variable

**Status:** Low priority - PySide6 updated in next version may fix

---

### 5. 🟡 File Extensions Case-Sensitive

**Issue:** Extension matching is case-sensitive. File.MP4 won't match .mp4 setting.

**Symptom:** Files with uppercase extensions (e.g., .MP4, .MKV) are skipped by monitor.

**Root Cause:** String comparison uses `str.endswith()` directly without `lower()`

**Workaround:**

- Rename files to lowercase (e.g., movie.mp4)
- Or add both cases to extensions list: [".mp4", ".MP4"]

**Status:** Low priority - most download tools use lowercase

**Fix:** Normalize to lowercase in file extension filter (v1.1.0)

---

### 6. 🟡 Remote Path Must Already Exist

**Issue:** If remote base directory doesn't exist on Raspberry Pi, transfer fails with cryptic SFTP error.

**Symptom:** "Error: Path does not exist" after transfer starts.

**Root Cause:** SFTP doesn't auto-create directories; requires explicit mkdir.

**Workaround:**

- SSH to Raspberry Pi: `mkdir -p /mnt/external`
- Or set remote base to existing directory

**Status:** Medium priority - common setup mistake

**Fix:** Auto-create remote base directory on first connection (v1.1.0)

---

### 7. 🟠 TV Show Classification Often Incorrect

**Issue:** TV show naming conventions are inconsistent; classifier fails on non-standard names.

**Symptom:** "Breaking.Bad.S01E01.mkv" classified as Movie instead of TV.

**Root Cause:** Regex pattern only matches certain naming formats (Season/Episode info).

**Examples of Failures:**

- ❌ "Game of Thrones - The Watcher on the Walls.mkv" → Classified as Movie
- ❌ "The.Office.2005.S09E23.mkv" → Mostly works, occasional failures
- ✅ "Breaking Bad/Season 1/S01E01.mkv" → Works (matches folder structure)

**Workaround:**

- Use folder structure: `TV_shows/ShowName/Season 1/S01E01.mkv`
- Or manually organize on remote after transfer

**Status:** High priority - core feature

**Resolution:**

- Improve regex pattern with more naming conventions (v1.1.0)
- Add manual classification option (right-click → "Move to Movies/TV")
- Train ML classifier on common naming patterns (v1.2.0+)

---

### 8. 🔵 No Duplicate File Detection

**Issue:** If file already exists on remote, transfer overwrites it.

**Symptom:** Accidentally transfer same file twice; second overwrites first (benign but wasteful).

**Root Cause:** No pre-check for existing files before transfer.

**Workaround:**

- Manually check remote before re-transferring
- Use unique filenames locally to prevent accidental duplicates

**Status:** Low priority - edge case

**Fix:** Add "skip if exists" option to transfer settings (v1.2.0)

---

### 9. 🔵 No Persistent Transfer Queue

**Issue:** If app crashes during transfer, queued files are lost.

**Symptom:** Files detected but not transferred are forgotten after restart.

**Root Cause:** Queue kept in memory; not persisted to disk.

**Workaround:**

- Manual re-transfer after app restart
- Keep app running for reliable transfers

**Status:** Low priority - crashes rare

**Fix:** Persist queue to JSON file; resume on startup (v1.2.0)

---

### 10. 🟡 High CPU Usage During Monitoring

**Issue:** File monitoring uses watchdog library with polling; uses 3-5% CPU continuously.

**Symptom:** Laptop fans occasionally kick in; slightly faster battery drain.

**Root Cause:** Watchdog uses inotify (Linux) or FSEvents (macOS) but falls back to polling if OS events unavailable.

**Workaround:**

- Close PiSync when not actively transferring
- Or accept the minor CPU cost for always-on monitoring

**Status:** Low priority - modern computers handle 3-5% easily

**Note:** Switching to native macOS FSEvents API may reduce further (v1.3.0)

---

## Limitations (By Design)

### Intentional Design Choices

#### 1. **Single Server at a Time**

**Design:** Select one Raspberry Pi; transfer all files to that server.

**Why:** Simplifies UI and transfer logic. Most users have single Pi.

**If You Need:** Multiple Pis in sync:

- Run multiple PiSync instances with different config files
- Or wait for v2.0 multi-server mode

#### 2. **No Bidirectional Sync**

**Design:** One-way transfer: macOS → Raspberry Pi only.

**Why:** Avoids complexity of conflict resolution, deletion handling.

**If You Need:** Download from Pi → macOS:

- Use manual SFTP with Cyberduck or command line
- Or implement custom transfer script

#### 3. **No Encryption at Rest**

**Design:** Files stored unencrypted on Raspberry Pi.

**Why:** Most home media servers don't need full disk encryption.

**If You Need:** Secure remote storage:

- Enable LUKS encryption on Raspberry Pi disk
- Or store sensitive files in separate encrypted container

#### 4. **No User Permissions**

**Design:** All transfers use same SSH user (usually `pi`).

**Why:** Simplifies authentication; Raspberry Pi typically single-user.

**If You Need:** Multiple users with different permissions:

- Manually set up user accounts on Raspberry Pi
- PiSync will transfer as whichever user SSH key is configured for

#### 5. **No Scheduled Transfers**

**Design:** Manual start/stop or always-on monitoring (not scheduled).

**Why:** Requires additional scheduler infrastructure.

**If You Need:** Transfers at specific times:

- Launch PiSync via cron at desired time
- Monitor will auto-start based on `auto_start_monitor` setting
- Implement scheduled mode in v1.2.0

---

## Fixed Issues (Previous Versions)

### ✅ Config Save Overwrote Server Settings

- **Fixed in:** v1.0.0
- **Issue:** Settings dialog save would create incomplete config, losing server list
- **Solution:** Build complete config dict preserving servers before save

### ✅ Connection Status Wrong Color

- **Fixed in:** v1.0.0
- **Issue:** Connection status label didn't update color immediately
- **Solution:** Use CSS-based styling with style().polish()

---

## Workaround Index

| Issue                                 | Quick Fix                                               |
| ------------------------------------- | ------------------------------------------------------- |
| Stability check too fast              | Increase `stability_duration` to 3-4s                   |
| Connection hangs                      | Ensure stable WiFi; force quit if stuck                 |
| File duplicate on remote              | Check before re-transferring                            |
| TV show mis-classified                | Use folder structure: TV_shows/Show/Season 1/S01E01.mkv |
| Extensions not matching               | Rename to lowercase or add both cases                   |
| Remote path doesn't exist             | SSH and `mkdir -p /mnt/external`                        |
| Settings dialog won't open (macOS 12) | Set QT_MAC_WANTS_LAYER=1 environment variable           |

---

## Reporting New Issues

Found a bug not listed here?

**Please report:**

1. What happened (symptom)
2. Steps to reproduce
3. Expected behavior
4. Your system (macOS version, Python version, etc.)
5. Full error message (if any)

**Report via:** [GitHub Issues](https://github.com/imlocle/pisync/issues)

---

## Testing Issues

### How to Test for New Bugs

1. **Stability Check:** Upload 100MB file and watch for timing
2. **Network Interruption:** Disconnect WiFi mid-transfer
3. **TV Classification:** Test with various naming conventions
4. **Case Sensitivity:** Try .MP4 vs .mp4
5. **Remote Path:** Test with non-existent directory

---

## Performance Baseline (v1.0.0)

For debugging and comparison:

- **App Startup:** ~2-3 seconds (with splash screen)
- **First Connection Test:** ~1-2 seconds
- **File Transfer Speed:** 2-5 MB/s (network limited, not app limited)
- **Memory Usage:** ~150-200 MB when running
- **CPU Usage (Monitoring):** ~3-5% continuous
- **File Stability Check:** ~2 seconds default + transfer time
