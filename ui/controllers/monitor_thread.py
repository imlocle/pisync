from PySide6.QtCore import QThread, Signal
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.services.file_transfer_service import FileTransferService
from src.services.file_deletion_service import FileDeletionService
from src.services.file_classifier_service import FileClassifierService
from typing import Set


class MonitorThread(QThread):
    log_signal = Signal(str)
    file_processed = Signal(str, str)

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
        self.main_window = main_window
        self.pi_user = pi_user
        self.pi_ip = pi_ip
        self.pi_movies = pi_movies
        self.pi_tv = pi_tv
        self.file_exts = file_exts
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

    def refresh_pi_list(self) -> None:
        """Refresh the Pi folder list with current contents from pi_movies and pi_tv."""
        if not all([self.pi_user, self.pi_ip, self.pi_movies, self.pi_tv]):
            self.log_signal.emit("Pi settings not configured, skipping refresh.")
            return

        try:
            # Assume FileTransferService has a method to list Pi files (e.g., via SSH/SFTP)
            pi_files = self.file_monitor_repo.transfer_service.list_pi_files()
            if pi_files:
                # Emit signal to update MainWindow's pi_list
                if hasattr(self.main_window, "refresh_pi_list"):
                    self.main_window.refresh_pi_list.emit()  # Trigger UI update
                self.log_signal.emit("Pi folder list refreshed.")
            else:
                self.log_signal.emit("No files found on Pi.")
        except Exception as e:
            self.log_signal.emit(f"Failed to refresh Pi list: {e}")
