from __future__ import annotations
import os
import paramiko
from src.services.file_deletion_service import FileDeletionService
from src.utils.logging_signal import logger


class BaseTransferService:
    """
    Base class that performs SFTP-based transfers and ensures remote directories exist.
    Uses an already-connected paramiko.SFTPClient instance.
    """

    def __init__(self, sftp: paramiko.SFTPClient) -> None:
        self.sftp: paramiko.SFTPClient = sftp
        self.file_deletion_service: FileDeletionService = FileDeletionService()

    def ensure_remote_directory(self, remote_dir: str) -> None:
        """
        Ensure remote directory exists. Creates intermediate directories if required.
        remote_dir should be an absolute path like /mnt/external/TV_shows/the_sandman/s01
        """
        # Normalize
        remote_dir = remote_dir.rstrip("/")
        if remote_dir == "":
            return

        parts = remote_dir.split("/")
        # Build path progressively (skip leading empty string from split)
        cur = ""
        for p in parts:
            if p == "":
                continue
            cur += "/" + p
            try:
                self.sftp.stat(cur)
            except IOError:
                # remote dir doesn't exist -> create
                self.sftp.mkdir(cur)

    def transfer_folder(
        self, local_folder: str, remote_folder: str, skip_hidden: bool = True
    ) -> None:
        """
        Recursively upload local_folder (all files) into remote_folder preserving
        subpaths relative to local_folder.
        """
        local_folder = os.path.abspath(local_folder)

        for root, _, files in os.walk(local_folder):
            for f in files:
                if skip_hidden and (f.startswith(".") or f.startswith("._")):
                    continue
                local_file = os.path.join(root, f)
                rel = os.path.relpath(local_file, local_folder)
                remote_file = os.path.join(remote_folder, rel).replace("\\", "/")
                remote_dir = os.path.dirname(remote_file)
                self.ensure_remote_directory(remote_dir)
                logger.log_signal.emit(f"🚀 Start: Transfer: File: {local_file}")
                logger.log_signal.emit(
                    f"🚀 Start: Transfer: Destination: {remote_file}"
                )
                self.sftp.put(local_file, remote_file)
                logger.log_signal.emit(
                    f"✅ Complete: Transfer: Destination: {remote_file}\n"
                )
                self.file_deletion_service.delete_file(local_file)
