# Known Issues & Bug Tracking

> **Last Updated:** March 10, 2026  
> **Version:** 1.0.0

## 🐛 Active Bugs

Currently no critical bugs. Minor issues and enhancements tracked below.

## ✅ Recently Fixed (March 2026)

### File Stability Tracking

**Issue**: When dragging a complete file into the Local Files explorer, the monitor would detect it but not transfer it because it relied on `on_modified` events that never occurred for already-complete files.

**Fix**: Implemented a background polling thread that checks tracked files every 0.5 seconds, ensuring files are transferred after 2 seconds of stability regardless of modification events.

**Files Changed**: `src/repositories/file_monitor_repository.py`, `src/controllers/monitor_thread.py`

### Auto-Connect After Server Selection

**Issue**: After selecting a server in the server selection dialog, users had to manually click "Connect" and "Start Monitoring" buttons.

**Fix**: Added automatic connection and monitoring start after the main window loads, triggered 200ms after the window is fully initialized.

**Files Changed**: `src/components/main_window.py`

### Local Explorer Refresh

**Issue**: Local Files explorer didn't refresh after automatic transfers completed, showing stale file listings.

**Fix**: Added `transfer_completed` signal that propagates from FileMonitorRepository → MonitorThread → AutoSyncController → MainWindowController, triggering explorer refresh.

**Files Changed**: Multiple files in signal chain

### Server Selection Dialog Centering

**Issue**: Server selection dialog wasn't centered on screen when shown during startup.

**Fix**: Added `_center_on_screen()` method that centers the dialog using Qt's screen geometry.

**Files Changed**: `src/components/server_selection_dialog.py`

## 🔍 Known Limitations

### Single File Transfer

**Description**: Only one file transfers at a time (sequential, not parallel)

**Impact**: Low - Most users transfer one file at a time anyway

**Workaround**: None needed

**Planned Fix**: v1.1 - Parallel transfer support

### No Transfer Resume

**Description**: If a transfer is interrupted (network issue, app crash), it cannot be resumed

**Impact**: Medium - Large files must restart from beginning

**Workaround**: Ensure stable network connection

**Planned Fix**: v1.2 - Resume capability

### macOS Only

**Description**: Not tested on Windows or Linux

**Impact**: Medium - Limits user base

**Workaround**: Use macOS

**Planned Fix**: v2.0 - Cross-platform support

### Directory Size Calculation

**Description**: Remote directories show "—" instead of calculated size

**Impact**: Low - Performance trade-off (SFTP not thread-safe for async operations)

**Workaround**: None needed

**Planned Fix**: Not planned (performance consideration)

## 📝 Reporting Bugs

When reporting bugs, please include:

1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Activity log output** (copy from app)
5. **System info** (macOS version, Python version)
6. **Configuration** (sanitize sensitive info)

## 🔧 Debugging Tips

### Enable Verbose Logging

Check the activity log in the app for detailed error messages.

### Test SSH Connection

```bash
ssh pi@192.168.1.100
```

### Check File Permissions

```bash
ls -la ~/.ssh/id_rsa
# Should be: -rw------- (600)
```

### Verify Remote Directory

```bash
ssh pi@192.168.1.100 "ls -la /mnt/external"
```

### Check Disk Space

```bash
ssh pi@192.168.1.100 "df -h"
```

---

**Last Updated**: March 10, 2026  
**Status**: ✅ No critical bugs
