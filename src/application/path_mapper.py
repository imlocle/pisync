"""
Path mapping service for converting local paths to remote paths.

This module provides simple, predictable path mapping that mirrors
the local directory structure on the remote server.
"""

import os
from pathlib import Path
from typing import Union


class PathMapper:
    """
    Maps local paths to remote paths by mirroring the directory structure.
    
    This is a simple, predictable mapping strategy:
    - Local: ~/Transfers/Movies/tron_legacy_2010/movie.mkv
    - Remote: /mnt/external/Movies/tron_legacy_2010/movie.mkv
    
    The local base directory is replaced with the remote base directory,
    preserving all subdirectory structure.
    
    Example:
        mapper = PathMapper(
            local_base="~/Transfers",
            remote_base="/mnt/external"
        )
        
        local = "~/Transfers/Movies/tron_legacy_2010/movie.mkv"
        remote = mapper.map_to_remote(local)
        # Result: "/mnt/external/Movies/tron_legacy_2010/movie.mkv"
    """
    
    def __init__(self, local_base: Union[str, Path], remote_base: Union[str, Path]):
        """
        Initialize the path mapper.
        
        Args:
            local_base: Base directory for local files (e.g., ~/Transfers)
            remote_base: Base directory on remote server (e.g., /mnt/external)
        """
        # Normalize and expand paths
        self.local_base = Path(os.path.expanduser(str(local_base))).resolve()
        self.remote_base = Path(str(remote_base))
        
        # Ensure remote base is absolute (starts with /)
        if not str(self.remote_base).startswith('/'):
            raise ValueError(f"Remote base must be absolute path: {remote_base}")
    
    def map_to_remote(self, local_path: Union[str, Path]) -> Path:
        """
        Map a local path to its corresponding remote path.
        
        Args:
            local_path: Local file or directory path
            
        Returns:
            Corresponding remote path
            
        Raises:
            ValueError: If local_path is not under local_base
            
        Example:
            >>> mapper = PathMapper("~/Transfers", "/mnt/external")
            >>> mapper.map_to_remote("~/Transfers/Movies/movie.mkv")
            Path('/mnt/external/Movies/movie.mkv')
        """
        # Normalize and expand local path
        local_path = Path(os.path.expanduser(str(local_path))).resolve()
        
        # Ensure local path is under local base
        try:
            relative_path = local_path.relative_to(self.local_base)
        except ValueError:
            raise ValueError(
                f"Local path must be under local base directory.\n"
                f"Local path: {local_path}\n"
                f"Local base: {self.local_base}"
            )
        
        # Construct remote path
        remote_path = self.remote_base / relative_path
        
        # Convert to POSIX path (forward slashes) for remote
        return Path(str(remote_path).replace('\\', '/'))
    
    def map_to_local(self, remote_path: Union[str, Path]) -> Path:
        """
        Map a remote path to its corresponding local path.
        
        Args:
            remote_path: Remote file or directory path
            
        Returns:
            Corresponding local path
            
        Raises:
            ValueError: If remote_path is not under remote_base
            
        Example:
            >>> mapper = PathMapper("~/Transfers", "/mnt/external")
            >>> mapper.map_to_local("/mnt/external/Movies/movie.mkv")
            Path('~/Transfers/Movies/movie.mkv')
        """
        remote_path = Path(str(remote_path))
        
        # Ensure remote path is under remote base
        try:
            relative_path = remote_path.relative_to(self.remote_base)
        except ValueError:
            raise ValueError(
                f"Remote path must be under remote base directory.\n"
                f"Remote path: {remote_path}\n"
                f"Remote base: {self.remote_base}"
            )
        
        # Construct local path
        return self.local_base / relative_path
    
    def is_under_local_base(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is under the local base directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is under local_base, False otherwise
        """
        try:
            path = Path(os.path.expanduser(str(path))).resolve()
            path.relative_to(self.local_base)
            return True
        except (ValueError, OSError):
            return False
    
    def is_under_remote_base(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is under the remote base directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is under remote_base, False otherwise
        """
        try:
            path = Path(str(path))
            path.relative_to(self.remote_base)
            return True
        except (ValueError, OSError):
            return False
    
    def __repr__(self) -> str:
        return f"PathMapper(local_base={self.local_base}, remote_base={self.remote_base})"
