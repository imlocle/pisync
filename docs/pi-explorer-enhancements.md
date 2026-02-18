# Pi Explorer Enhancements

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.0  
> **Status:** ✅ Current

## Overview

Enhanced the Pi Explorer widget to display file/directory sizes and disk usage information, providing better visibility into storage usage.

## Changes Made

### 1. Widget Type Change: QListWidget → QTreeWidget

**File**: `src/widgets/file_explorer_widget.py`

Changed from single-column list to multi-column tree view to support additional data columns.

**Before**: QListWidget with icon and name only
**After**: QTreeWidget with columns: Name, Size

### 2. Size Column Added

Each file and directory now displays its size in human-readable format:

- **Files**: Shows actual file size
- **Directories**: Shows total size of all contents (recursive calculation)
- **Format**: Automatically scales to appropriate unit (B, KB, MB, GB)
  - < 1 KB: "512 B"
  - < 1 MB: "234.5 KB"
  - < 1 GB: "45.3 MB"
  - ≥ 1 GB: "1.25 GB"

**Implementation**:

- `_get_size_string()`: Main method to get size for any path
- `_format_size()`: Converts bytes to human-readable format
- `_get_local_dir_size()`: Calculates local directory size using os.walk()
- `_get_remote_dir_size()`: Calculates remote directory size using SFTP listdir_attr()

### 3. Disk Usage in Title (Remote Explorer Only)

The Pi Explorer title now shows disk usage information:

**Format**: `Pi Explorer (/path) - 45.2 GB / 128 GB`

Shows:

- Used space / Total space
- Updates on every refresh
- Only displayed for remote (SFTP) explorer
- Gracefully handles errors (shows path only if unavailable)

**Implementation**:

- `_get_disk_usage()`: Uses SFTP statvfs() to get filesystem statistics
- Calculates used space from total - free blocks
- Formats both values using `_format_size()`

## Technical Details

### Size Calculation Performance

**Local Directories**:

- Uses `os.walk()` to traverse directory tree
- Sums file sizes using `os.path.getsize()`
- Handles missing files gracefully

**Remote Directories**:

- Uses `sftp.listdir_attr()` for efficient attribute retrieval
- Recursively calculates subdirectory sizes
- Uses cached stat information (no extra SFTP calls per file)

**Note**: Large directories may take a moment to calculate. Consider adding caching or background calculation for very large directories if performance becomes an issue.

### Disk Usage Calculation

Uses SFTP's `statvfs()` method which provides:

- `f_blocks`: Total blocks in filesystem
- `f_frsize`: Fragment size (block size)
- `f_bfree`: Free blocks available

Calculation:

```python
total_bytes = stat.f_blocks * stat.f_frsize
free_bytes = stat.f_bfree * stat.f_frsize
used_bytes = total_bytes - free_bytes
```

## UI Changes

### Column Layout

- **Name column**: 300px width (icon + filename)
- **Size column**: 100px width (right-aligned size)
- Header labels: "Name", "Size"
- No expand arrows (setRootIsDecorated(False))

### Visual Consistency

- Maintains all existing features:
  - Drag & drop support
  - Context menu (delete/rename)
  - Navigation (double-click)
  - Back button
  - Selection signals
  - Error handling

## Code Quality

### Error Handling

- All size calculations wrapped in try-except
- Returns "—" for unavailable sizes
- Disk usage silently fails (shows path only)
- No crashes on permission errors or missing files

### Backward Compatibility

- All existing signals maintained
- All existing methods preserved
- API unchanged for MainWindow integration
- Only internal widget type changed

## Testing Recommendations

1. **Local Explorer**:
   - Verify file sizes display correctly
   - Verify directory sizes calculate properly
   - Test with empty directories
   - Test with large directories (>1GB)

2. **Remote Explorer**:
   - Verify SFTP file sizes display
   - Verify SFTP directory sizes calculate
   - Verify disk usage appears in title
   - Test with disconnected SFTP (should show error gracefully)

3. **Performance**:
   - Test with directories containing many files
   - Monitor calculation time for large directories
   - Verify UI remains responsive during size calculations

4. **Edge Cases**:
   - Hidden files (should be skipped)
   - Symlinks (should handle gracefully)
   - Permission denied (should show "—")
   - Very large files (>100GB)

## Future Enhancements

Potential improvements for future versions:

1. **Caching**: Cache directory sizes to avoid recalculation
2. **Background Calculation**: Calculate sizes in background thread
3. **Progress Indicator**: Show spinner while calculating large directories
4. **Sort by Size**: Allow sorting by size column
5. **Size Filtering**: Filter files by size range
6. **Disk Usage Graph**: Visual representation of disk usage
7. **Free Space Warning**: Highlight when disk is nearly full

## Summary

The Pi Explorer now provides comprehensive size information for all files and directories, plus disk usage statistics for the remote Pi. This helps users understand storage usage at a glance and make informed decisions about file management.

**Status**: ✅ Complete
**Date**: February 11, 2026
**Files Changed**: 1 (`src/widgets/file_explorer_widget.py`)
**Lines Added**: ~120 lines
**New Features**: 2 (size column, disk usage display)
