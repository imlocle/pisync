from __future__ import annotations
import os
from src.services.base_transfer_service import BaseTransferService


class TvService(BaseTransferService):
    """
    Handles transferring TV-show files while preserving the directory hierarchy
    under /mnt/external/TV_shows or general /mnt/external root.
    """

    def transfer_tv_folder(self, local_folder: str) -> bool:
        """
        Transfer contents of a local_folder to remote root preserving the path relative
        to ~/Transfers. For example:
          local_folder = ~/Transfers/TV_shows/the_sandman/s01
        remote target = /mnt/external/TV_shows/the_sandman/s01
        """
        local_folder = os.path.abspath(local_folder)
        if not local_folder.startswith(os.path.abspath(self.watch_dir)):
            # fallback: just map local folder name under remote_root
            remote_folder = os.path.join(
                self.pi_root_dir, os.path.basename(local_folder)
            ).replace("\\", "/")
        else:
            rel = os.path.relpath(local_folder, self.watch_dir)
            remote_folder = os.path.join(self.pi_root_dir, rel).replace("\\", "/")

        try:
            self.transfer_folder(local_folder, remote_folder)
            return True
        except Exception as e:
            return False
