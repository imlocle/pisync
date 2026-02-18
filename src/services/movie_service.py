"""
Movie transfer service.

Handles transferring movie directories to the Raspberry Pi.
Uses PathMapper for consistent path mapping.
"""

from __future__ import annotations

import os

from src.application.path_mapper import PathMapper
from src.services.base_transfer_service import BaseTransferService
from src.utils.logging_signal import logger


class MovieService(BaseTransferService):
    """
    Handles transferring movie directories.
    
    Movies are transferred with their complete folder structure preserved.
    Example:
        Local:  ~/Transfers/Movies/tron_legacy_2010/movie.mkv
        Remote: /mnt/external/Movies/tron_legacy_2010/movie.mkv
    """

    def __init__(self, sftp, watch_dir: str, pi_root_dir: str):
        """
        Initialize movie transfer service.
        
        Args:
            sftp: Active SFTP client
            watch_dir: Local watch directory (e.g., ~/Transfers)
            pi_root_dir: Remote base directory (e.g., /mnt/external)
        """
        super().__init__(sftp, watch_dir, pi_root_dir)
        self.path_mapper = PathMapper(watch_dir, pi_root_dir)

    def transfer_movie_folder(self, local_folder: str) -> bool:
        """
        Transfer a movie folder to remote server.
        
        The folder structure is preserved using PathMapper.
        
        Args:
            local_folder: Path to local movie folder
            
        Returns:
            True on success, False on failure
            
        Example:
            local_folder = ~/Transfers/Movies/tron_legacy_2010
            remote_folder = /mnt/external/Movies/tron_legacy_2010
        """
        local_folder = os.path.abspath(local_folder)
        
        if not os.path.isdir(local_folder):
            logger.warn(f"Movie: Not a directory: {local_folder}")
            return False

        try:
            # Use PathMapper to get remote path
            remote_folder = str(self.path_mapper.map_to_remote(local_folder))
            
            logger.info(f"Movie: Mapping {local_folder} -> {remote_folder}")
            
            # Transfer the folder
            self.transfer_folder(local_folder, remote_folder)
            return True
            
        except ValueError as e:
            # Path not under watch directory
            logger.error(f"Movie: Path mapping error: {e}")
            return False
        except Exception as e:
            logger.error(f"Movie: Transfer failed: {e}")
            return False
