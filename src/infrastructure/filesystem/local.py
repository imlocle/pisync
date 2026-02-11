"""
Local file system implementation.

Provides file system operations for the local machine.
"""

import os
from pathlib import Path
from typing import List
from datetime import datetime
from src.domain.models import FileInfo


class LocalFileSystem:
    """
    Local file system implementation.
    
    Wraps standard Python file operations to match the FileSystem protocol.
    """
    
    def exists(self, path: Path) -> bool:
        """Check if a path exists."""
        return path.exists()
    
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        return path.is_file()
    
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        return path.is_dir()
    
    def list_dir(self, path: Path) -> List[str]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path
            
        Returns:
            List of file/directory names
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            NotADirectoryError: If path is not a directory
        """
        if not self.exists(path):
            raise FileNotFoundError(f"Directory not found: {path}")
        if not self.is_dir(path):
            raise NotADirectoryError(f"Not a directory: {path}")
        
        return [item.name for item in path.iterdir()]
    
    def get_size(self, path: Path) -> int:
        """
        Get size of a file in bytes.
        
        Args:
            path: File path
            
        Returns:
            Size in bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not self.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        return path.stat().st_size
    
    def get_info(self, path: Path) -> FileInfo:
        """
        Get detailed information about a file or directory.
        
        Args:
            path: Path to get info for
            
        Returns:
            FileInfo object with details
            
        Raises:
            FileNotFoundError: If path doesn't exist
        """
        if not self.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        
        stat = path.stat()
        
        return FileInfo(
            path=path,
            is_directory=self.is_dir(path),
            size_bytes=stat.st_size if self.is_file(path) else 0,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            is_remote=False
        )
    
    def delete(self, path: Path) -> None:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            
        Raises:
            FileNotFoundError: If path doesn't exist
        """
        if not self.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        
        if self.is_file(path):
            path.unlink()
        else:
            # Remove directory recursively
            import shutil
            shutil.rmtree(path)
    
    def mkdir(self, path: Path, parents: bool = True) -> None:
        """
        Create a directory.
        
        Args:
            path: Directory path to create
            parents: Create parent directories if needed
        """
        path.mkdir(parents=parents, exist_ok=True)
    
    def __repr__(self) -> str:
        return "LocalFileSystem()"
