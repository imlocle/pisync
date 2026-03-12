# Known Issues & Bug Tracking

> **Last Updated:** March 11, 2026  
> **Version:** 1.0.0

## 🐛 Active Bugs

Currently no critical bugs reported. See potential issues and limitations below.

## 🔍 Potential Issues (Ranked by Severity)

### CRITICAL - Risk of data loss or crashes

1. **SFTP File Handle Leak on Transfer Failure** (HIGH IMPACT)
   - **Location**: [src/services/base_transfer_service.py](src/services/base_transfer_service.py#L195), [src/controllers/transfer_worker.py](src/controllers/transfer_worker.py#L155)
   - **Issue**: On transfer failure, partial remote files are not always cleaned up. If `sftp.put()` fails after creating the file, the incomplete file remains with no mechanism to remove it on retry.
   - **Symptom**: Remote storage gradually fills with incomplete/corrupted files after failed transfers
   - **Scenario**: Large file transfer interrupted mid-way, exception caught, retry happens but orphan file persists
   - **Fix Required**: Wrap `sftp.put()` in try-finally block to remove incomplete files on exception

2. **Race Condition on Startup - Auto-connect Before Server Selection** (HIGH IMPACT)
   - **Location**: [src/components/main_window.py](src/components/main_window.py#L93-L103)
   - **Issue**: `_auto_connect_and_start()` called via QTimer with 200ms delay, but happens immediately after window show. If user hasn't selected a server yet, it may connect with stale/default credentials
   - **Symptom**: Connecting to wrong Pi if user has multiple servers configured
   - **Scenario**: First run with multi-server setup, initial server connection fails silently, user not aware wrong Pi is connected
   - **Fix Required**: Only call auto-connect AFTER server selection is confirmed, add server-changed signal check

3. **File Retry Loop May Bypass Stability Check** (MEDIUM-HIGH IMPACT)
   - **Location**: [src/repositories/file_monitor_repository.py](src/repositories/file_monitor_repository.py#L536)
   - **Issue**: On transfer failure, file is re-enqueued but stability tracker may still hold stale size data. If file is modified mid-retry, stability timestamp is not reset, could result in transferring unstable file
   - **Symptom**: Partially written files transferred if they fail and are retried quickly
   - **Scenario**: Large file fails to transfer at 50%, gets retried, but stability tracker thinks file is stable because previous timestamp still active
   - **Fix Required**: Clear file from stability tracker before re-enqueuing on retry in `handle_file()` error path

4. **SFTP Connection Not Verified Before Worker Thread Starts** (HIGH IMPACT)
   - **Location**: [src/controllers/transfer_controller.py](src/controllers/transfer_controller.py#L56-L90)
   - **Issue**: `open_sftp_session()` called to create worker SFTP, but if connection dies between check and thread start, worker will fail with cryptic error
   - **Symptom**: Transfer starts then immediately fails with "Socket is closed" before any progress
   - **Scenario**: User connects, waits 30 seconds before starting drag-drop transfer, connection times out, transfer fails non-intuitively
   - **Fix Required**: Add SFTP connection verify immediately before thread.start(), emit user-friendly error if connection drops

### HIGH - Important functionality broken

5. **Settings Port Input Validation Inconsistency** (HIGH IMPACT)
   - **Location**: [src/components/settings_window.py](src/components/settings_window.py#L651-L675)
   - **Issue**: Port input validation in `test_connection()` fails silently without user feedback. If port is non-numeric AND settings dialog is closed, saved config has invalid port value
   - **Symptom**: User enters invalid port like "22a", clicks test (fails silently), then saves settings - port value corrupts config
   - **Scenario**: User types wrong port, dialog rejects test, but save still stores corrupted value
   - **Fix Required**: Validate port format in `save_settings()` before persisting, show error for non-numeric input

6. **Incomplete Error Recovery in File Monitor Loop** (HIGH IMPACT)
   - **Location**: [src/controllers/monitor_thread.py](src/controllers/monitor_thread.py#L86)
   - **Issue**: Exception in `handle_file()` or `handle_folder()` is caught broadly with `logger.error()` but processing continues. If transfer service loses SFTP connection, error is logged but loop keeps pulling from queue without reconnecting
   - **Symptom**: After SFTP connection drops during monitoring, all subsequent transfers fail silently
   - **Scenario**: Network interruption occurs mid-transfer during monitoring, connection lost, but queue keeps processing with dead SFTP
   - **Fix Required**: Propagate ConnectionLostError to stop_monitoring(), auto-reconnect or emit signal to main thread

7. **File Already Processed Lock Gap** (HIGH IMPACT)
   - **Location**: [src/repositories/file_monitor_repository.py](src/repositories/file_monitor_repository.py#L359-L380)
   - **Issue**: Race condition: file can be scheduled twice if `_schedule_file_processing()` called twice from watchdog events before `_mark_as_processed()` is called. Lock is only held during check, not during subsequent operations
   - **Symptom**: Files transferred twice in rare cases
   - **Scenario**: Rapid file modifications trigger on_created and on_modified in quick succession, both pass the lock check before either marks as processed
   - **Fix Required**: Extend lock to cover entire scheduling operation, not just the check

### MEDIUM - Degraded functionality

8. **Signal Disconnection on Application Close May Leak Memory** (MEDIUM IMPACT)
   - **Location**: [src/components/main_window.py](src/components/main_window.py#L513-L523)
   - **Issue**: Signals are connected in `_setup_connections()` but never explicitly disconnected. When window closes, if shutdown() is slow, signals may still fire on dangling objects
   - **Symptom**: Occasional crashes on exit if transfer completes during shutdown
   - **Scenario**: User closes app while transfer in progress, transfer finishes, signal fires on deleted UI object
   - **Fix Required**: Disconnect all signals in `closeEvent()` before shutdown, or use context managers

9. **Empty Queue Timeout May Block Shutdown** (MEDIUM IMPACT)
   - **Location**: [src/controllers/monitor_thread.py](src/controllers/monitor_thread.py#L86)
   - **Issue**: `self._stable_files_queue.get(timeout=0.5)` in tight loop. If queue backs up with 1000s of files, getting each item takes O(n) time, shutdown can hang
   - **Symptom**: App takes 30+ seconds to shutdown if large backlog of queued files
   - **Scenario**: Add 1000 files to watch directory quickly, then close app immediately
   - **Fix Required**: Implement queue drain on stop signal, or use priority queue with size bounds

10. **Configuration Migration Silent Failures** (MEDIUM IMPACT)

- **Location**: [src/config/settings.py](src/config/settings.py#L260-L268)
- **Issue**: If config file is corrupted JSON, `_load_config()` catches exception and returns empty dict. This silently loses user configuration instead of prompting recovery
- **Symptom**: User configuration disappears, app reverts to defaults without warning
- **Scenario**: Config file partially written during save crash, becomes invalid JSON, next startup silently loses all settings
- **Fix Required**: Create config backup on load failure, show recovery dialog to user

11. **Path Expansion Race in Settings Validator** (MEDIUM IMPACT)
    - **Location**: [src/config/settings.py](src/config/settings.py#L106-L115)
    - **Issue**: `validate_watch_dir` creates directory if missing with `os.makedirs()`. But Pydantic validators run during model creation, not during save, so directory created immediately even if user cancels dialog
    - **Symptom**: Empty watch directories created in user's home directory even if user doesn't finalize settings
    - **Scenario**: User opens settings, changes watch dir, changes mind, clicks Cancel - directory was already created
    - **Fix Required**: Move directory creation to `save_settings()` instead of validator, validators should only validate

### LOW - Minor issues

12. **Remote Explorer Error Doesn't Update UI State** (LOW IMPACT)
    - **Location**: [src/widgets/file_explorer_widget.py](src/widgets/file_explorer_widget.py#L217-L228)
    - **Issue**: When remote explorer fails and emits error, UI path label may show outdated path. While `_reset_remote_state_after_failure()` resets current_path, the title_label text was already displayed
    - **Symptom**: UI shows wrong path after connection error, confusing user
    - **Scenario**: Browse remote folder, connection drops, title shows old folder path briefly
    - **Fix Required**: Minor - just update title_label refresh after path reset

13. **Monitor Thread Stop Signal Race** (LOW IMPACT)
    - **Location**: [src/controllers/monitor_thread.py](src/controllers/monitor_thread.py#L100)
    - **Issue**: `stop()` sets `self._running = False` but main loop checks it with 0.5s queue timeout. If file processing takes >0.5s, shutdown delay is added
    - **Symptom**: App shutdown takes extra 0.5s+ if processing large file
    - **Scenario**: Stop called during file processing, must wait for current item to finish then timeout loop
    - **Fix Required**: Add Event-based signaling instead of boolean flag for immediate responsiveness

14. **Transfer Cancellation Not Implemented** (LOW IMPACT)
    - **Location**: [src/application/manual_transfer_controller.py](src/application/manual_transfer_controller.py#L183-L188)
    - **Issue**: `cancel_transfer()` always returns False with TODO comment, cancellation just logs warning
    - **Symptom**: Users cannot cancel ongoing transfers
    - **Scenario**: User starts large file transfer, realizes mistake, no way to stop it
    - **Fix Required**: Implement SFTP transfer cancellation mechanism, or at least doc why it's not supported

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

**Last Updated**: March 11, 2026  
**Status**: ✅ No critical bugs
