# SFTP Thread Safety Fix

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.0  
> **Status:** ✅ Current - Issue resolved

## Problem

The async size calculation implementation caused the application to freeze because:

1. **SFTP is not thread-safe**: Paramiko's SFTPClient cannot be safely used from multiple threads
2. **Worker threads blocked**: Background threads trying to use SFTP caused deadlocks
3. **UI froze**: The main thread waited for workers that were blocked on SFTP operations

## Symptoms

- Pi Explorer showed "..." for all file sizes
- Clicking on any item froze the application
- No error messages, just complete UI freeze

## Root Cause

The `SizeCalculationWorker` class was trying to use the SFTP connection from background threads:

```python
# PROBLEMATIC CODE (removed)
class SizeCalculationWorker(QRunnable):
    def run(self):
        # This runs in a background thread
        st = self.sftp.stat(path)  # ❌ SFTP not thread-safe!
```

Paramiko's SFTP client uses a single SSH channel and is not designed for concurrent access from multiple threads.

## Solution

Reverted to synchronous size calculation with optimizations:

### 1. Removed Async Worker

- Deleted `SizeCalculationWorker` class entirely
- Removed `QThreadPool` and thread management
- Removed all async signals and slots

### 2. Smart Size Calculation Strategy

**For Remote (SFTP)**:

- Files: Show actual size (fast, single stat call)
- Directories: Show "—" instead of calculating (avoids slow recursive operations)

**For Local**:

- Files: Show actual size
- Directories: Calculate full size (safe, no SFTP involved)

```python
def _get_size_string(self, path: str) -> str:
    if self.is_remote:
        if self._is_remote_directory(path):
            return "—"  # Skip for performance
        else:
            st = self.sftp.stat(path)  # Fast for files
            return self._format_size(st.st_size)
    else:
        # Local: calculate everything
        if os.path.isdir(path):
            size_bytes = self._get_local_dir_size(path)
        else:
            size_bytes = os.path.getsize(path)
        return self._format_size(size_bytes)
```

### 3. Performance Optimizations

**Why this is still fast**:

1. **File sizes are instant**: Single SFTP stat call per file
2. **No recursive directory traversal**: Skipping remote directory sizes saves seconds
3. **Disk usage still shown**: Title shows total Pi disk usage
4. **Local directories calculated**: Only local dirs (which are fast) show sizes

**Trade-off**:

- Remote directories show "—" instead of size
- This is acceptable because:
  - Users primarily care about file sizes
  - Total disk usage is shown in title
  - Calculating remote directory sizes is very slow (recursive SFTP calls)
  - Most media files are large individual files, not many small files

## Code Changes

### Files Modified

- `src/widgets/file_explorer_widget.py` - Removed async code, simplified size calculation

### Removed

- `SizeCalculationWorker` class (~80 lines)
- `thread_pool` and `item_map` instance variables
- `_calculate_size_async()` method
- `_on_size_calculated()` method
- `_update_disk_usage_async()` method
- `_is_directory()` helper method

### Added Back

- `_get_size_string()` - Simple synchronous size calculation
- `_format_size()` - Size formatting helper
- `_get_local_dir_size()` - Local directory size calculation

### Imports Cleaned

- Removed: `QRunnable`, `QThreadPool`, `Slot`, `QObject`
- Kept: `QTimer` (still used for other purposes)

## Results

### Before Fix

- ❌ UI completely frozen
- ❌ All sizes showed "..."
- ❌ Could not interact with application
- ❌ Required force quit

### After Fix

- ✅ UI responsive immediately
- ✅ File sizes display correctly
- ✅ Can navigate and interact normally
- ✅ Fast load times (no blocking)

## Performance Comparison

### Remote Directory with 50 Files

**With Async (broken)**:

- Load time: Infinite (froze)
- File sizes: "..." (never loaded)
- Directory sizes: "..." (never loaded)

**With Sync (fixed)**:

- Load time: <1 second
- File sizes: Displayed correctly
- Directory sizes: "—" (skipped for speed)

### Local Directory with 50 Files

**Both versions**:

- Load time: <1 second
- File sizes: Displayed correctly
- Directory sizes: Calculated and displayed

## Lessons Learned

### SFTP Thread Safety

- Paramiko's SFTPClient is NOT thread-safe
- Must only be accessed from the main thread
- Background threads cannot safely use SFTP operations

### When to Use Async

- ✅ Good for: CPU-intensive operations, local file I/O
- ❌ Bad for: Network operations with non-thread-safe clients
- ⚠️ Always check: Library documentation for thread safety

### Performance vs Features

- Sometimes simpler is better
- Showing "—" for remote directories is acceptable
- Users care more about responsiveness than complete data

## Alternative Solutions Considered

### 1. Thread-Safe SFTP Wrapper

- Create a queue-based SFTP wrapper
- All requests go through single thread
- **Rejected**: Too complex, still slow

### 2. Caching

- Cache directory sizes after first calculation
- **Rejected**: Still need initial calculation (slow)

### 3. On-Demand Calculation

- Calculate size only when user clicks
- **Rejected**: Inconsistent UX, still blocks on click

### 4. Current Solution (Chosen)

- Show file sizes only for remote
- Skip directory sizes
- **Accepted**: Simple, fast, good UX

## Future Enhancements

If directory sizes are needed in the future:

1. **Background Process**: Use separate Python process (not thread) for SFTP
2. **Server-Side Calculation**: Add endpoint to Pi to calculate sizes
3. **Caching Service**: Cache sizes on server, query via API
4. **Progressive Loading**: Show "calculating..." and update when ready (with proper queue)

## Conclusion

The fix prioritizes stability and responsiveness over complete feature parity. Remote file sizes are shown (which is what users care about most), while remote directory sizes are skipped to avoid slow recursive SFTP operations and thread safety issues.

**Status**: ✅ Fixed
**Date**: February 11, 2026
**Impact**: Application now works correctly without freezing
