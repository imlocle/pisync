# Issues and Potential Bugs

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.1  
> **Status:** ✅ Many issues resolved

> **📅 Last Updated:** December 2024 (Post Phase 1-4 Redesign)
>
> **Status:** ✅ PARTIALLY RESOLVED - Many critical issues have been fixed
>
> **Fixed Issues:**
>
> - ✅ Issue #1: Race Condition in File Monitoring - FIXED with FileStabilityTracker
> - ✅ Issue #10: Settings Validation Insufficient - FIXED with Pydantic validators
> - ✅ Issue #13: Classification Heuristics Too Simple - FIXED by removing classification
> - ✅ Issue #15: Error Messages Not User-Friendly - IMPROVED with custom exceptions
> - ✅ Issue #17: No Transfer Statistics - IMPROVED with better logging
>
> **Still Relevant:**
>
> - ⚠️ Issue #2: SFTP Connection Thread-Safety - Partially addressed
> - ⚠️ Issue #3: No Verification of Successful Transfer - Still needed
> - ⚠️ Issue #4: AutoAddPolicy Security Risk - Still present
> - ⚠️ Issue #5: Unhandled Socket Closure - Improved but not perfect
> - ⚠️ Issue #6-25: Various improvements still pending
>
> **For Current Status:** Check individual issues below

---

# Issues and Potential Bugs

## Critical Issues

### 1. Race Condition in File Monitoring

**Location**: `src/repositories/file_monitor_repository.py`

**Issue**: Files may be transferred before they're fully written to disk.

**Scenario**:

1. Large file starts copying to watch directory
2. Watchdog fires `on_created` event immediately
3. Transfer begins while file is still being written
4. Partial file transferred to Pi
5. Local file deleted before complete

**Impact**: Corrupted or incomplete files on Raspberry Pi

**Reproduction**:

```python
# Copy large file to watch directory
# Transfer may start before copy completes
```

**Solution**:

- Implement file stability check (wait for size to stabilize)
- Add configurable delay before transfer
- Check if file is still being written (platform-specific)

---

### 2. SFTP Connection Not Thread-Safe

**Location**: `src/components/main_window.py`, `src/controllers/transfer_worker.py`

**Issue**: Multiple threads may use the same SFTP client simultaneously.

**Scenario**:

1. UI explorer uses `self.connection_manager.sftp_client`
2. MonitorThread uses same SFTP client for automated transfers
3. User triggers manual upload (TransferWorker)
4. All three operations may conflict

**Impact**:

- "Socket is closed" errors
- Transfer failures
- Application crashes

**Evidence**: `_reset_remote_state_after_failure()` suggests this happens

**Solution**:

- Use connection pooling
- Create dedicated SFTP session per operation
- Implement locking mechanism
- Use thread-local storage for SFTP clients

---

### 3. No Verification of Successful Transfer

**Location**: `src/services/base_transfer_service.py`

**Issue**: Files deleted locally without verifying remote transfer success.

**Code**:

```python
self.sftp.put(local_file, remote_file, callback=progress_callback)
logger.success(f"Transfer: Uploaded: File: {local_file}")
self.file_deletion_service.delete_file(local_file)
```

**Problem**: If `put()` fails silently or network drops, file is still deleted

**Impact**: Data loss - file deleted locally but not on Pi

**Solution**:

- Verify remote file exists after transfer
- Compare file sizes
- Calculate and verify checksums
- Only delete on confirmed success

---

### 4. AutoAddPolicy Security Risk

**Location**: `src/services/connection_manager_service.py`

**Issue**: Automatically accepts unknown SSH host keys.

**Code**:

```python
self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
```

**Risk**: Vulnerable to man-in-the-middle attacks

**Impact**: Attacker could intercept connection and steal credentials/data

**Solution**:

- Use `RejectPolicy()` and require manual host key verification
- Store known host keys in `~/.ssh/known_hosts`
- Prompt user to verify host key fingerprint on first connection

---

### 5. Unhandled Socket Closure

**Location**: `src/widgets/file_explorer_widget.py`

**Issue**: SFTP operations fail when socket closes unexpectedly.

**Evidence**: `_reset_remote_state_after_failure()` method exists to handle this

**Causes**:

- Network interruption
- Pi reboot
- SSH timeout
- Concurrent access conflicts

**Impact**:

- UI shows error messages
- Explorer becomes unusable
- Requires manual reconnection

**Solution**:

- Implement automatic reconnection with exponential backoff
- Add connection health checks
- Show connection status prominently
- Queue operations during reconnection

---

## High Priority Issues

### 6. No Transfer Cancellation

**Location**: `src/controllers/transfer_worker.py`, `src/controllers/monitor_thread.py`

**Issue**: No way to cancel in-progress transfers.

**Impact**:

- User must wait for large transfers to complete
- Cannot stop accidental transfers
- Application may appear frozen

**Solution**:

- Add cancel button to UI
- Implement cancellation tokens
- Check cancellation flag in transfer loops
- Clean up partial transfers on cancellation

---

### 7. Progress Bar Resets Between Files

**Location**: `src/services/base_transfer_service.py`

**Issue**: Progress shows per-file, not overall batch progress.

**Code**:

```python
logger.progress_signal.emit(0)  # Reset for each file
```

**Impact**: User can't see overall progress for multi-file transfers

**Solution**:

- Calculate total size of all files upfront
- Track cumulative bytes transferred
- Show overall progress percentage
- Display current file name

---

### 8. Hardcoded Retry Logic

**Location**: `src/services/connection_manager_service.py`

**Issue**: Retry count and delay hardcoded, not configurable.

**Code**:

```python
while retries < 3:
    # ...
    sleep(3)
```

**Impact**:

- Cannot adjust for slow networks
- Fixed 9-second maximum wait may be insufficient
- No exponential backoff

**Solution**:

- Add retry configuration to settings
- Implement exponential backoff
- Make retry behavior configurable per operation

---

### 9. No Disk Space Validation

**Location**: All transfer services

**Issue**: No check if Pi has sufficient disk space before transfer.

**Impact**:

- Transfer fails mid-operation
- Partial files on Pi
- Local files already deleted
- Difficult to recover

**Solution**:

- Check available space via SFTP before transfer
- Compare with total transfer size
- Show warning if insufficient space
- Prevent transfer if space inadequate

---

### 10. Settings Validation Insufficient

**Location**: `src/config/settings.py`

**Issue**: `is_valid()` only checks if strings are non-empty.

**Code**:

```python
def is_valid(self) -> bool:
    return all([
        self.pi_user.strip(),
        self.pi_ip.strip(),
        # ...
    ])
```

**Problems**:

- No IP address format validation
- No path existence checks
- No SSH key validation
- Invalid settings can be saved

**Impact**: Application fails at runtime with cryptic errors

**Solution**:

- Validate IP address format
- Check SSH key file exists and has correct permissions
- Validate paths are absolute
- Test connection before saving

---

## Medium Priority Issues

### 11. Memory Leak in Log Widget

**Location**: `src/components/main_window.py`

**Issue**: Log messages accumulate indefinitely in QTextEdit.

**Code**:

```python
def log(self, message: str) -> None:
    self.log_box.append(message)  # Never cleared
```

**Impact**: Memory usage grows over time, especially with verbose logging

**Solution**:

- Limit log buffer to last N messages
- Add "Clear Logs" button
- Implement log rotation
- Write old logs to file

---

### 12. No Duplicate File Handling

**Location**: All transfer services

**Issue**: No check if file already exists on Pi.

**Impact**:

- Files overwritten without warning
- Wasted bandwidth re-transferring existing files
- No versioning or conflict resolution

**Solution**:

- Check if remote file exists before transfer
- Compare modification times or checksums
- Add user preference: skip, overwrite, or rename
- Show duplicate file dialog

---

### 13. Classification Heuristics Too Simple

**Location**: ~~`src/services/file_classifier_service.py`~~ (REMOVED)

**Issue**: ~~Simple pattern matching may misclassify files.~~ RESOLVED - Service removed, classification now purely path-based (Movies/ vs TV_shows/).

**Examples**:

- "The S01E01 Movie" classified as TV show
- "Season of the Witch" classified as TV show
- Files without patterns default to movie

**Impact**: Files transferred to wrong directory

**Solution**:

- Use more sophisticated patterns (regex)
- Check multiple indicators
- Allow manual classification override
- Learn from user corrections

---

### 14. No Transfer Queue Visibility

**Location**: `src/controllers/transfer_controller.py`

**Issue**: User can't see pending transfers or queue status.

**Code**:

```python
if self._busy:
    logger.warn("Manual upload already in progress.")
    return
```

**Impact**:

- User doesn't know what's queued
- Cannot reorder or remove queued items
- No visibility into transfer pipeline

**Solution**:

- Add transfer queue UI widget
- Show pending, in-progress, and completed transfers
- Allow queue manipulation (reorder, remove)
- Persist queue across restarts

---

### 15. Error Messages Not User-Friendly

**Location**: Throughout codebase

**Issue**: Technical error messages shown to users.

**Examples**:

```python
logger.error(f"Failed to upload {local_file}: {e}")
# Shows raw exception to user
```

**Impact**: Users confused by technical jargon

**Solution**:

- Create user-friendly error messages
- Provide actionable suggestions
- Show technical details in expandable section
- Add "Help" links for common errors

---

## Low Priority Issues

### 16. No Bandwidth Throttling

**Location**: Transfer services

**Issue**: Transfers use full available bandwidth.

**Impact**:

- Network congestion
- Other applications slow down
- May affect streaming or video calls

**Solution**:

- Add bandwidth limit setting
- Implement rate limiting in transfer loop
- Allow dynamic adjustment during transfer

---

### 17. No Transfer Statistics

**Location**: Application-wide

**Issue**: No tracking of transfer history or statistics.

**Missing Data**:

- Total bytes transferred
- Number of files transferred
- Success/failure rates
- Transfer speeds
- Historical trends

**Solution**:

- Add statistics database (SQLite)
- Show statistics dashboard
- Export statistics to CSV
- Graph transfer trends

---

### 18. Splash Screen Duration Hardcoded

**Location**: `src/components/splash_screen.py`

**Issue**: 2.5-second splash screen may be too long/short.

**Code**:

```python
def __init__(self, logo_path: str, duration: int = 2500):
```

**Impact**: Minor UX issue

**Solution**:

- Make duration configurable
- Skip splash on subsequent launches
- Show splash only on first run

---

### 19. No Undo Functionality

**Location**: Delete operations

**Issue**: Deleted files moved to trash but no undo in UI.

**Impact**: User must manually restore from system trash

**Solution**:

- Add "Undo" button after delete
- Keep delete history
- Implement undo stack
- Show notification with undo option

---

### 20. Settings Window Blocks Main Window

**Location**: `src/components/settings_window.py`

**Issue**: Settings dialog is modal, blocking main window.

**Code**:

```python
class SettingsWindow(QDialog):
```

**Impact**: Cannot view main window while adjusting settings

**Solution**:

- Make settings window non-modal
- Or add "Apply" button to test settings without closing
- Show live preview of changes

---

## Edge Cases

### 21. Symbolic Links Not Handled

**Issue**: Symbolic links may cause infinite loops or unexpected behavior.

**Impact**:

- Watchdog may follow symlinks recursively
- Transfer may fail on broken symlinks
- Circular symlinks cause infinite loops

**Solution**:

- Detect and skip symbolic links
- Or add option to follow symlinks
- Warn user about symlink behavior

---

### 22. Large File Handling

**Issue**: No special handling for very large files (>10GB).

**Impact**:

- Long transfers with no feedback
- Memory issues with progress tracking
- Timeout on slow connections

**Solution**:

- Show estimated time remaining
- Add pause/resume capability
- Use chunked transfers with checkpoints
- Warn user about large files

---

### 23. Unicode Filename Support

**Issue**: Non-ASCII characters in filenames may cause issues.

**Impact**:

- Transfer failures
- Incorrect filenames on Pi
- Path encoding errors

**Solution**:

- Test with various character sets
- Ensure UTF-8 encoding throughout
- Sanitize filenames if needed
- Show warning for problematic characters

---

### 24. Concurrent File Modifications

**Issue**: File modified while being transferred.

**Impact**:

- Corrupted transfer
- Checksum mismatch
- Partial file on Pi

**Solution**:

- Lock files during transfer
- Detect modifications and retry
- Warn user about active files

---

### 25. Network Interruption During Transfer

**Issue**: No resume capability if network drops mid-transfer.

**Impact**:

- Must restart entire transfer
- Wasted bandwidth
- Partial files on Pi

**Solution**:

- Implement resume capability
- Use rsync-like algorithm
- Checkpoint progress
- Verify and resume from last checkpoint
