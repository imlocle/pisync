from __future__ import annotations
import os
from src.services.base_transfer_service import BaseTransferService
from src.utils.logging_signal import logger


class MovieService(BaseTransferService):
    """
    Handles transferring movie directories.
    After successful transfer, caller should invoke deletion if desired.
    """

    def transfer_movie_folder(self, local_folder: str) -> bool:
        """
        Transfer a movie folder (entire folder) to remote_base/<folder_name>
        Returns True on success.
        """
        local_folder = os.path.abspath(local_folder)
        if not os.path.isdir(local_folder):
            logger.warn("local_folder must be a directory")
            return False

        folder_name = os.path.basename(local_folder.rstrip("/"))
        remote_folder = os.path.join(self.pi_root_dir, folder_name).replace("\\", "/")

        try:
            self.transfer_folder(local_folder, remote_folder)
            return True
        except Exception as e:
            # Let caller handle logging
            return False
