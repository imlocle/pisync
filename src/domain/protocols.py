"""
Protocol definitions for PiSync application.

Protocols define interfaces that implementations must follow,
enabling dependency inversion and easier testing.
"""

from typing import Protocol, List, Optional
from pathlib import Path
from src.domain.models import FileInfo


class FileSystem(Protocol):
    """
    Abstract file system interface.
    
    This protocol defines the interface for file system operations,
    allowing the same code to work with both local and remote file systems.
    
    Implementations:
    - LocalFileSystem: Works with local file system
    - RemoteFileSystem: Works with SFTP
    """
    
    def exists(self, path: Path) -> bool:
        """
        Check if a path exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists, False otherwise
        """
        ...
    
    def is_file(self, path: Path) -> bool:
        """
        Check if path is a file.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a file, False otherwise
        """
        ...
    
    def is_dir(self, path: Path) -> bool:
        """
        Check if path is a directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory, False otherwise
        """
        ...
    
    def list_dir(self, path: Path) -> List[str]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path
            
        Returns:
            List of file/directory names (not full paths)
        """
        ...
    
    def get_size(self, path: Path) -> int:
        """
        Get size of a file in bytes.
        
        Args:
            path: File path
            
        Returns:
            Size in bytes
        """
        ...
    
    def get_info(self, path: Path) -> FileInfo:
        """
        Get detailed information about a file or directory.
        
        Args:
            path: Path to get info for
            
        Returns:
            FileInfo object with details
        """
        ...
    
    def delete(self, path: Path) -> None:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
        """
        ...
    
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """
        Create a directory.
        
        Args:
            path: Directory path to create
            parents: Create parent directories if needed
        """
        ...


class TransferEngine(Protocol):
    """
    Abstract transfer engine interface.
    
    This protocol defines the interface for transferring files
    between file systems.
    """
    
    def transfer_file(
        self,
        source_fs: FileSystem,
        source_path: Path,
        dest_fs: FileSystem,
        dest_path: Path,
        verify: bool = True
    ) -> bool:
        """
        Transfer a single file.
        
        Args:
            source_fs: Source file system
            source_path: Source file path
            dest_fs: Destination file system
            dest_path: Destination file path
            verify: Verify transfer by comparing sizes
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def transfer_folder(
        self,
        source_fs: FileSystem,
        source_path: Path,
        dest_fs: FileSystem,
        dest_path: Path,
        verify: bool = True
    ) -> bool:
        """
        Transfer a folder recursively.
        
        Args:
            source_fs: Source file system
            source_path: Source folder path
            dest_fs: Destination file system
            dest_path: Destination folder path
            verify: Verify each file transfer
            
        Returns:
            True if successful, False otherwise
        """
        ...


class ConnectionManager(Protocol):
    """
    Abstract connection manager interface.
    
    This protocol defines the interface for managing SSH/SFTP connections.
    """
    
    def connect(self) -> bool:
        """
        Establish connection.
        
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def disconnect(self) -> None:
        """Close connection and clean up resources."""
        ...
    
    def is_connected(self) -> bool:
        """
        Check if currently connected.
        
        Returns:
            True if connected, False otherwise
        """
        ...
    
    def get_file_system(self) -> FileSystem:
        """
        Get the remote file system interface.
        
        Returns:
            FileSystem implementation for remote operations
        """
        ...
