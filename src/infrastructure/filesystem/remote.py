"""
Remote file system implementation using SFTP.

Provides file system operations for remote servers via SSH/SFTP.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from paramiko import SFTPClient

from src.domain.models import FileInfo
from src.models.errors import ConnectionLostError, FileSystemError


class RemoteFileSystem:
    """
    Remote file system implementation using SFTP.
    
    Wraps paramiko SFTP operations to match the FileSystem protocol.
    """
    
    def __init__(self, sftp_client: SFTPClient):
        """
        Initialize remote file system.
        
        Args:
            sftp_client: Active paramiko SFTP client
        """
        self.sftp = sftp_client
    
    def _check_connection(self) -> None:
        """
        Check if SFTP connection is still active.
        
        Raises:
            ConnectionLostError: If connection is lost
        """
        if not self.sftp or not self.sftp.get_channel():
            raise ConnectionLostError("SFTP connection is not active")
    
    def exists(self, path: Path) -> bool:
        """
        Check if a path exists on remote server.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists, False otherwise
        """
        try:
            self._check_connection()
            self.sftp.stat(str(path))
            return True
        except (IOError, OSError):
            return False
        except Exception as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError("SFTP connection lost", details=str(e))
            return False
    
    def is_file(self, path: Path) -> bool:
        """
        Check if path is a file on remote server.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a file, False otherwise
        """
        try:
            self._check_connection()
            stat = self.sftp.stat(str(path))
            if stat.st_mode is None:
                return False
            from stat import S_ISREG
            return S_ISREG(stat.st_mode)
        except (IOError, OSError):
            return False
    
    def is_dir(self, path: Path) -> bool:
        """
        Check if path is a directory on remote server.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory, False otherwise
        """
        try:
            self._check_connection()
            stat = self.sftp.stat(str(path))
            if stat.st_mode is None:
                return False
            from stat import S_ISDIR
            return S_ISDIR(stat.st_mode)
        except (IOError, OSError):
            return False
    
    def list_dir(self, path: Path) -> List[str]:
        """
        List contents of a remote directory.
        
        Args:
            path: Directory path
            
        Returns:
            List of file/directory names
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            ConnectionLostError: If connection is lost
        """
        try:
            self._check_connection()
            return self.sftp.listdir(str(path))
        except IOError as e:
            if "No such file" in str(e):
                raise FileNotFoundError(f"Remote directory not found: {path}")
            raise FileSystemError(f"Failed to list remote directory", path=str(path), details=str(e))
        except Exception as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError("SFTP connection lost", details=str(e))
            raise
    
    def get_size(self, path: Path) -> int:
        """
        Get size of a remote file in bytes.
        
        Args:
            path: File path
            
        Returns:
            Size in bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ConnectionLostError: If connection is lost
        """
        try:
            self._check_connection()
            stat = self.sftp.stat(str(path))
            if stat.st_size is None:
                return 0
            return stat.st_size
        except IOError as e:
            if "No such file" in str(e):
                raise FileNotFoundError(f"Remote file not found: {path}")
            raise FileSystemError(f"Failed to get remote file size", path=str(path), details=str(e))
    
    def get_info(self, path: Path) -> FileInfo:
        """
        Get detailed information about a remote file or directory.
        
        Args:
            path: Path to get info for
            
        Returns:
            FileInfo object with details
            
        Raises:
            FileNotFoundError: If path doesn't exist
            ConnectionLostError: If connection is lost
        """
        try:
            self._check_connection()
            stat = self.sftp.stat(str(path))
            
            # Get size, defaulting to 0 if None or if it's a directory
            size_bytes = 0
            if self.is_file(path) and stat.st_size is not None:
                size_bytes = stat.st_size
            
            # Get modified time, defaulting to current time if None
            modified_time = datetime.now()
            if stat.st_mtime is not None:
                modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            return FileInfo(
                path=path,
                is_directory=self.is_dir(path),
                size_bytes=size_bytes,
                modified_time=modified_time,
                is_remote=True
            )
        except IOError as e:
            if "No such file" in str(e):
                raise FileNotFoundError(f"Remote path not found: {path}")
            raise FileSystemError(f"Failed to get remote file info", path=str(path), details=str(e))
    
    def delete(self, path: Path) -> None:
        """
        Delete a remote file or directory.
        
        Args:
            path: Path to delete
            
        Raises:
            FileNotFoundError: If path doesn't exist
            ConnectionLostError: If connection is lost
        """
        try:
            self._check_connection()
            
            if self.is_file(path):
                self.sftp.remove(str(path))
            elif self.is_dir(path):
                self._delete_dir_recursive(path)
            else:
                raise FileNotFoundError(f"Remote path not found: {path}")
                
        except Exception as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError("SFTP connection lost", details=str(e))
            raise
    
    def _delete_dir_recursive(self, path: Path) -> None:
        """
        Recursively delete a remote directory.
        
        Args:
            path: Directory path to delete
        """
        # List and delete all contents first
        for item in self.list_dir(path):
            item_path = path / item
            if self.is_dir(item_path):
                self._delete_dir_recursive(item_path)
            else:
                self.sftp.remove(str(item_path))
        
        # Delete the empty directory
        self.sftp.rmdir(str(path))
    
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """
        Create a remote directory.
        
        Args:
            path: Directory path to create
            parents: Create parent directories if needed
            
        Raises:
            ConnectionLostError: If connection is lost
        """
        try:
            self._check_connection()
            
            if self.exists(path):
                return  # Already exists
            
            if parents:
                # Create parent directories recursively
                parent = path.parent
                if parent != path and not self.exists(parent):
                    self.mkdir(parent, parents=True)
            
            self.sftp.mkdir(str(path))
            
        except Exception as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError("SFTP connection lost", details=str(e))
            raise FileSystemError(f"Failed to create remote directory", path=str(path), details=str(e))
    
    def __repr__(self) -> str:
        return f"RemoteFileSystem(connected={self.sftp is not None})"
