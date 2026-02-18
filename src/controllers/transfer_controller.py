from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional

from PySide6.QtCore import QObject, QThread

from src.config.settings import Settings
from src.controllers.transfer_worker import TransferWorker
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.logging_signal import logger


MappingMode = Literal["drop", "relative"]


@dataclass(frozen=True)
class TransferRequest:
    local_paths: List[str]
    remote_root: str
    mode: MappingMode
    local_root: Optional[str] = None  # used only for "relative"


class TransferController(QObject):
    """
    Runs uploads in a background worker thread.

    - For drag/drop onto Pi explorer: mode="drop"
        remote path = remote_root / basename(local_item)
    - For Upload All: mode="relative"
        remote path = remote_root / relpath(local_item, local_root)
    """

    def __init__(
        self,
        settings: Settings,
        connection_manager: ConnectionManagerService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self.connection_manager = connection_manager

        self._thread: Optional[QThread] = None
        self._worker: Optional[TransferWorker] = None
        self._busy: bool = False

    def is_busy(self) -> bool:
        return self._busy

    # ------------------------------------------------------------------
    #  Internal helper
    # ------------------------------------------------------------------
    def _start_worker(self, req: TransferRequest) -> None:
        if self._busy:
            logger.warn("Manual upload already in progress.")
            return

        # Ensure we have a live connection / sftp
        if not self.connection_manager.is_connected():
            if not self.connection_manager.connect():
                logger.error("Transfer: Cannot establish SSH connection.")
                return

        worker_sftp = self.connection_manager.open_sftp_session()
        if not worker_sftp:
            logger.error("Transfer: Cannot open worker SFTP session.")
            return

        self._thread = QThread()
        self._worker = TransferWorker(
            sftp=worker_sftp,
            local_paths=req.local_paths,
            remote_root=req.remote_root,
            parent=None  # No parent since it will be moved to thread
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)

        # Wire signals
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)

        # Cleanup when done
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)

        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.error.connect(self._worker.deleteLater)

        self._thread.finished.connect(self._thread.deleteLater)

        self._busy = True
        logger.start(f"Transfer: {len(req.local_paths)} item(s) → {req.remote_root}")
        self._thread.start()

    def _on_worker_finished(self):
        logger.stop("Transfer: Complete")
        self._busy = False

    def _on_worker_error(self, msg: str):
        logger.error(f"Transfer failed: {msg}")
        self._busy = False

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def upload_to_pi(self, local_paths: List[str], remote_dir: str) -> None:
        """
        Entry point for drag-and-drop onto the Pi explorer.

        local_paths: list of local filesystem paths from Finder
        remote_dir:  directory on the Pi to upload into (e.g. /mnt/external/TV_shows/...)
        """
        if not local_paths:
            return

        req = TransferRequest(
            local_paths=local_paths,
            remote_root=remote_dir,
            mode="drop",
            local_root=None,
        )
        self._start_worker(req)

    def upload_all_watch_dir(self) -> None:
        """Upload All: preserve structure relative to watch_dir into pi_root_dir."""
        req = TransferRequest(
            local_paths=[self.settings.watch_dir],
            remote_root=self.settings.pi_root_dir,
            mode="relative",
            local_root=self.settings.watch_dir,
        )
        self._start_worker(req)
