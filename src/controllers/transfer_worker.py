from __future__ import annotations
from typing import List

import os

from paramiko import SFTPClient
from PySide6.QtCore import QObject, Signal

from src.utils.logging_signal import logger
from src.utils.helper import format_size


class TransferWorker(QObject):
    """
    Performs manual uploads (drag-and-drop or 'Upload All') on a background thread.

    NOTE: This does NOT delete local files. It's copy semantics.
    """

    finished = Signal()
    error = Signal(str)

    def __init__(
        self,
        sftp: SFTPClient,
        local_paths: List[str],
        remote_root: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.sftp = sftp
        self.local_paths = local_paths
        self.remote_root = remote_root

    # ----------------------------
    #  Internal helpers
    # ----------------------------
    def _ensure_remote_directory(self, remote_dir: str) -> None:
        """
        Ensure remote directory exists. Creates intermediate directories as needed.
        """
        remote_dir = remote_dir.rstrip("/")
        if not remote_dir:
            return

        parts = remote_dir.split("/")
        cur = ""
        for p in parts:
            if not p:
                continue
            cur += "/" + p
            try:
                self.sftp.stat(cur)
            except IOError:
                self.sftp.mkdir(cur)

    def _upload_file(self, local_path: str, remote_dir: str) -> None:
        filename = os.path.basename(local_path)
        remote_file = os.path.join(remote_dir, filename).replace("\\", "/")
        remote_dir = os.path.dirname(remote_file)
        self._ensure_remote_directory(remote_dir)

        try:
            size_bytes = os.path.getsize(local_path)
        except OSError:
            logger.error(f"Manual Upload: Unable to stat file: {local_path}")
            return

        # progress callback
        def progress_callback(transferred: int, total: int):
            if total <= 0:
                return
            pct = int(transferred * 100 / total)
            if pct % 5 == 0:  # throttle logs a bit
                logger.progress_signal.emit(pct)

        logger.upload(f"Manual: Upload: {local_path} → {remote_file}")
        logger.progress_signal.emit(0)

        self.sftp.put(local_path, remote_file, callback=progress_callback)

        logger.success(f"Manual: Uploaded: {filename} ({format_size(size_bytes)})")
        logger.progress_signal.emit(100)

    def _upload_folder(self, local_folder: str, remote_root: str) -> None:
        local_folder = os.path.abspath(local_folder)
        base_name = os.path.basename(local_folder)
        target_root = os.path.join(remote_root, base_name).replace("\\", "/")

        for root, _, files in os.walk(local_folder):
            for f in files:
                if f.startswith(".") or f.startswith("._"):
                    continue
                local_file = os.path.join(root, f)
                rel = os.path.relpath(local_file, local_folder)
                remote_dir = os.path.dirname(
                    os.path.join(target_root, rel).replace("\\", "/")
                )
                self._upload_file(local_file, remote_dir)

    # ----------------------------
    #  Public entrypoint for QThread
    # ----------------------------
    def run(self) -> None:
        try:
            for path in self.local_paths:
                if os.path.isdir(path):
                    self._upload_folder(path, self.remote_root)
                else:
                    self._upload_file(path, self.remote_root)

            self.finished.emit()
        except Exception as e:
            msg = f"Manual transfer failed: {e}"
            logger.error(msg)
            self.error.emit(msg)
            self.finished.emit()
