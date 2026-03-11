# Known Issues & Bug Tracking

> **Last Updated:** March 10, 2026  
> **Version:** 1.0.0

## 🐛 Active Bugs

Currently no critical bugs. Minor issues and enhancements tracked below.

## ✅ Recently Fixed (March 2026)

### Singleton Settings Mutation During Connection Test (CRITICAL)

**Issue**: In server_mode, `test_connection()` created `temp_settings = Settings()` (getting the singleton) and then overwrote `temp_settings.config`. Since Settings is a singleton, this mutated the global application settings just to test connectivity, which could leak into the running app/session and corrupt configuration.

**Fix**: Created a lightweight `TempSettings` class that wraps SettingsConfig without touching the singleton. The test connection is now side-effect free and doesn't mutate global state.

**Files Changed**: `src/components/settings_window.py`

### Auto-Connect Ignoring Settings

**Issue**: MainWindow scheduled `_auto_connect_and_start()` on load, which always called `connect()` and `start_monitor()` regardless of the `auto_start_monitor` setting. This conflicted with the intended behavior (default: False) and ignored user preferences. Additionally, there were inconsistent defaults: field default was False, but `from_json()` and settings UI used True as fallback.

**Fix**:

- Made `_auto_connect_and_start()` conditional on `settings.auto_start_monitor`
- Fixed inconsistent defaults to all use False
- Updated `from_json()` fallback from True to False
- Updated settings window checkbox fallback from True to False

**Files Changed**: `src/components/main_window.py`, `src/config/settings.py`, `src/components/settings_window.py`

### Server Change Monitoring Check

**Issue**: `change_server()` checked for `self.controller.monitor_thread`, but MainWindowController doesn't expose `monitor_thread` (it's internal to AutoSyncController). This meant monitoring could keep running while switching servers, potentially causing transfers to the wrong server or connection errors.

**Fix**: Updated to use the correct API: `self.controller.auto_sync.is_monitoring()` to properly check if monitoring is active before stopping it.

**Files Changed**: `src/components/main_window.py`

### Multiple Polling Thread Prevention

**Issue**: `start_polling()` could be called multiple times without checking if a polling thread was already running. This would spawn multiple daemon threads, causing duplicate file processing, race conditions, and wasted resources. Similarly, `start_monitoring()` could start multiple Observer threads.

**Fix**: Added guards to both methods:

- `start_polling()`: Checks if thread is alive, stops existing thread before starting new one
- `start_monitoring()`: Checks if Observer is alive, skips start if already running

**Files Changed**: `src/repositories/file_monitor_repository.py`

### Incorrect Configuration Key in Documentation

**Issue**: The configuration examples in README.md and docs/README.md used `pi_username` as the key, but the actual application settings use `pi_user` (as defined in SettingsConfig). Users following the documentation would create configs that wouldn't populate the username field correctly.

**Fix**: Updated all configuration examples to use the correct key `pi_user` to match the actual config schema.

**Files Changed**: `README.md`, `docs/README.md`

### Duplicate Connect Button Signal Connection

**Issue**: The `connect_btn.clicked` signal was connected to `controller.connect()` in both `_setup_toolbar()` and `_setup_connections()`. This caused clicking Connect to call the connection method twice, leading to duplicate connection attempts and potentially confusing UI states.

**Fix**: Removed the duplicate connection from `_setup_toolbar()`, keeping only the one in `_setup_connections()` where all signal wiring is centralized.

**Files Changed**: `src/components/main_window.py`

### Local Explorer Refresh After Auto Transfer

**Issue**: The `_on_auto_transfer_completed()` method checked for `self.view.local_explorer`, but MainWindow exposes the local explorer as `watch_explorer`. This caused the local file view to not refresh after automatic transfers, showing stale file listings.

**Fix**: Updated the method to reference the correct attribute `watch_explorer`.

**Files Changed**: `src/controllers/main_window_controller.py`

### Transfer Retry Logic (CRITICAL)

**Issue**: When `transfer_tv_folder()` or `transfer_movie_folder()` returned False (indicating failure), files were removed from stability tracking with no retry mechanism. Transient failures (network hiccups, temporary disk issues) would permanently lose files without user notification beyond log entries.

**Fix**: Implemented automatic retry with backoff:

- Failed transfers are re-queued up to 3 times
- Retry count tracked per file/folder path
- Clear error messages showing retry attempts (e.g., "retry 2/3")
- After max retries, permanent failure is logged
- Successful transfers clear retry counters

**Files Changed**: `src/repositories/file_monitor_repository.py`

### Thread Safety Issue with SFTP Operations (CRITICAL)

**Issue**: The stability polling thread (`_poll_files()`) invoked callbacks directly from a background thread, while watchdog's Observer thread also called file/folder handlers. Both threads accessed the same Paramiko SFTPClient instance, which is not thread-safe. This caused intermittent transfer failures, connection corruption, and race conditions.

**Fix**: Implemented queue-based architecture where all stable file/folder paths are enqueued by background threads and processed sequentially by MonitorThread's main loop. All SFTP operations now happen on a single thread, eliminating race conditions.

**Files Changed**: `src/repositories/file_monitor_repository.py`, `src/controllers/monitor_thread.py`

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
