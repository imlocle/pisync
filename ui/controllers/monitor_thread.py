from PySide6.QtCore import QThread, Signal
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.services.file_transfer_service import FileTransferService
from src.services.file_deletion_service import FileDeletionService
from src.services.file_classifier_service import FileClassifierService
from typing import Set


class MonitorThread(QThread):
    log_signal = Signal(str)

    def __init__(
        self,
        watch_dir: str,
        pi_user: str,
        pi_ip: str,
        pi_movies: str,
        pi_tv: str,
        file_exts: Set[str],
        main_window,
    ) -> None:
        super().__init__()
        self.watch_dir: str = watch_dir
        self._running: bool = True
        # Initialize your existing services
        classifier: FileClassifierService = FileClassifierService()
        deletion: FileDeletionService = FileDeletionService()
        transfer: FileTransferService = FileTransferService(
            pi_user,
            pi_ip,
            pi_movies,
            pi_tv,
            file_exts,
        )
        self.file_monitor_repo: FileMonitorRepository = FileMonitorRepository(
            watch_dir=self.watch_dir,
            classifier_service=classifier,
            transfer_service=transfer,
            deletion_service=deletion,
            file_exts=file_exts,
        )
        self.main_window = main_window

    def run(self) -> None:
        self.log_signal.emit(f"📡 Starting Directory Monitor: {self.watch_dir}")
        self.file_monitor_repo.create_directories()
        self.file_monitor_repo.start_monitoring()
        while self._running:
            self.msleep(500)  # Keep thread alive but non-blocking
        self.file_monitor_repo.stop_monitoring()

    def stop(self) -> None:
        self._running = False

    def handle_dropped_file(self, file_path: str, dest_type: str) -> None:
        """Handle files dropped onto the Pi list."""
        if self.file_monitor_repo.transfer_service.transfer_file(file_path, dest_type):
            self.log_signal.emit(f"✅ Transferred {file_path} to Pi.")
        else:
            self.log_signal.emit(f"❌ Failed to transfer {file_path} to Pi.")
