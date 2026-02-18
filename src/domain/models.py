"""
Domain models for PiSync application.

These models represent the core business entities and operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional


@dataclass
class TransferRequest:
    """
    Represents a request to transfer files from local to remote.
    
    This is the core domain model for all transfer operations,
    whether initiated manually or automatically.
    """
    source_path: Path
    destination_path: Path
    transfer_type: Literal['file', 'folder']
    delete_after: bool = True
    verify_after: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Ensure paths are Path objects."""
        if not isinstance(self.source_path, Path):
            self.source_path = Path(self.source_path)
        if not isinstance(self.destination_path, Path):
            self.destination_path = Path(self.destination_path)


@dataclass
class TransferResult:
    """
    Result of a transfer operation.
    
    Contains all information about what happened during the transfer,
    including success/failure, bytes transferred, duration, and any errors.
    """
    request: TransferRequest
    success: bool
    bytes_transferred: int = 0
    duration_seconds: float = 0.0
    error: Optional[Exception] = None
    verified: bool = False
    deleted_local: bool = False
    completed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def failed(self) -> bool:
        """Check if transfer failed."""
        return not self.success
    
    @property
    def transfer_speed_mbps(self) -> float:
        """Calculate transfer speed in MB/s."""
        if self.duration_seconds > 0:
            mb_transferred = self.bytes_transferred / (1024 * 1024)
            return mb_transferred / self.duration_seconds
        return 0.0
    
    def __str__(self) -> str:
        """Human-readable representation."""
        if self.success:
            speed = f"{self.transfer_speed_mbps:.2f} MB/s" if self.duration_seconds > 0 else "N/A"
            return (
                f"✅ Transfer successful: {self.request.source_path.name} "
                f"({self.bytes_transferred:,} bytes in {self.duration_seconds:.1f}s, {speed})"
            )
        else:
            return f"❌ Transfer failed: {self.request.source_path.name} - {self.error}"


@dataclass
class ConnectionInfo:
    """
    Information about SSH/SFTP connection.
    
    Encapsulates all connection-related data.
    """
    host: str
    username: str
    port: int = 22
    key_path: Optional[Path] = None
    connected: bool = False
    connection_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Ensure key_path is Path object if provided."""
        if self.key_path and not isinstance(self.key_path, Path):
            self.key_path = Path(self.key_path)
    
    @property
    def connection_string(self) -> str:
        """Get connection string for display."""
        return f"{self.username}@{self.host}:{self.port}"
    
    def __str__(self) -> str:
        """Human-readable representation."""
        status = "🟢 Connected" if self.connected else "🔴 Disconnected"
        return f"{status} - {self.connection_string}"


@dataclass
class FileInfo:
    """
    Information about a file or directory.
    
    Provides a unified interface for both local and remote files.
    """
    path: Path
    is_directory: bool
    size_bytes: int = 0
    modified_time: Optional[datetime] = None
    is_remote: bool = False
    
    def __post_init__(self):
        """Ensure path is Path object."""
        if not isinstance(self.path, Path):
            self.path = Path(self.path)
    
    @property
    def name(self) -> str:
        """Get file/directory name."""
        return self.path.name
    
    @property
    def extension(self) -> str:
        """Get file extension (lowercase)."""
        return self.path.suffix.lower()
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def size_gb(self) -> float:
        """Get size in gigabytes."""
        return self.size_bytes / (1024 * 1024 * 1024)
    
    def __str__(self) -> str:
        """Human-readable representation."""
        type_icon = "📁" if self.is_directory else "📄"
        location = "remote" if self.is_remote else "local"
        size_str = f"{self.size_mb:.1f} MB" if not self.is_directory else "folder"
        return f"{type_icon} {self.name} ({size_str}, {location})"


@dataclass
class TransferProgress:
    """
    Progress information for an ongoing transfer.
    
    Used to report progress to the UI during transfers.
    """
    request: TransferRequest
    bytes_transferred: int = 0
    total_bytes: int = 0
    current_file: Optional[str] = None
    files_completed: int = 0
    total_files: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    
    @property
    def percentage(self) -> float:
        """Get completion percentage (0-100)."""
        if self.total_bytes > 0:
            return min(100.0, (self.bytes_transferred / self.total_bytes) * 100)
        return 0.0
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.started_at).total_seconds()
    
    @property
    def estimated_seconds_remaining(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.bytes_transferred > 0 and self.elapsed_seconds > 0:
            bytes_per_second = self.bytes_transferred / self.elapsed_seconds
            remaining_bytes = self.total_bytes - self.bytes_transferred
            return remaining_bytes / bytes_per_second
        return None
    
    @property
    def transfer_speed_mbps(self) -> float:
        """Get current transfer speed in MB/s."""
        if self.elapsed_seconds > 0:
            mb_transferred = self.bytes_transferred / (1024 * 1024)
            return mb_transferred / self.elapsed_seconds
        return 0.0
    
    def __str__(self) -> str:
        """Human-readable representation."""
        speed = f"{self.transfer_speed_mbps:.2f} MB/s"
        eta = f"{self.estimated_seconds_remaining:.0f}s" if self.estimated_seconds_remaining else "calculating..."
        return (
            f"📤 {self.current_file or 'Transferring'}: "
            f"{self.percentage:.1f}% ({self.files_completed}/{self.total_files} files, "
            f"{speed}, ETA: {eta})"
        )
