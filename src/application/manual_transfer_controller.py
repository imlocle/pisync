"""
Manual transfer controller.

Handles user-initiated transfers (drag-and-drop, manual selection).
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, QThread, Signal

from src.application.path_mapper import PathMapper
from src.config.settings import Settings
from src.controllers.transfer_worker import TransferWorker
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.logging_signal import logger


class ManualTransferController(QObject):
    """
    Controller for manual (user-initiated) transfers.
    
    This controller handles:
    - Drag-and-drop transfers
    - Manual file selection
    - User-controlled transfer options
    - Progress reporting to UI
    
    Unlike AutoSyncController, this gives users full control over:
    - What to transfer
    - When to transfer
    - Whether to delete local files
    """
    
    # Signals
    transfer_started = Signal(str)  # path
    transfer_completed = Signal(str)  # path
    transfer_failed = Signal(str, str)  # path, error
    progress_updated = Signal(int)  # percentage
    
    def __init__(
        self,
        settings: Settings,
        connection_manager: ConnectionManagerService,
        parent: Optional[QObject] = None
    ):
        """
        Initialize manual transfer controller.
        
        Args:
            settings: Application settings
            connection_manager: Connection manager for SFTP
            parent: Parent QObject
        """
        super().__init__(parent)
        self.settings = settings
        self.connection_manager = connection_manager
        self.path_mapper = PathMapper(
            settings.local_watch_dir,
            settings.remote_base_dir
        )
        
        self._active_worker: Optional[TransferWorker] = None
        self._active_thread: Optional[QThread] = None
        self._is_busy = False
    
    def is_busy(self) -> bool:
        """Check if a transfer is currently in progress."""
        return self._is_busy
    
    def transfer_to_pi(
        self,
        local_paths: List[str],
        remote_destination: Optional[str] = None,
        delete_after: bool = False
    ) -> bool:
        """
        Transfer files/folders to Raspberry Pi.
        
        This is the main entry point for manual transfers.
        
        Args:
            local_paths: List of local file/folder paths to transfer
            remote_destination: Optional specific remote destination
                               If None, uses PathMapper to determine destination
            delete_after: Whether to delete local files after transfer
            
        Returns:
            True if transfer started successfully, False if busy or error
            
        Example:
            # Transfer with automatic path mapping
            controller.transfer_to_pi([
                "~/Transfers/Movies/movie_2024"
            ])
            
            # Transfer to specific destination
            controller.transfer_to_pi(
                ["~/Downloads/movie.mkv"],
                remote_destination="/mnt/external/Movies/new_movie",
                delete_after=False
            )
        """
        if self._is_busy:
            logger.warn("Manual Transfer: Already in progress")
            return False
        
        if not local_paths:
            logger.warn("Manual Transfer: No paths provided")
            return False
        
        # Ensure connection
        if not self.connection_manager.is_connected():
            logger.info("Manual Transfer: Connecting...")
            if not self.connection_manager.connect():
                logger.error("Manual Transfer: Connection failed")
                return False
        
        # Determine remote destination
        if remote_destination:
            # User specified destination
            remote_dir = remote_destination
        else:
            # Use PathMapper for first path (all should map to same base)
            try:
                first_path = Path(local_paths[0])
                if self.path_mapper.is_under_local_base(first_path):
                    # Map to remote
                    remote_path = self.path_mapper.map_to_remote(first_path)
                    remote_dir = str(remote_path.parent)
                else:
                    # Not under watch dir, use remote base
                    remote_dir = self.settings.remote_base_dir
            except Exception as e:
                logger.error(f"Manual Transfer: Path mapping failed: {e}")
                return False
        
        # Create worker for transfer
        try:
            sftp = self.connection_manager.open_sftp_session()
            if sftp is None:
                logger.error("Manual Transfer: Could not open SFTP session")
                return False
            
            # Create thread and worker
            self._active_thread = QThread()
            self._active_worker = TransferWorker(
                sftp=sftp,
                local_paths=local_paths,
                remote_root=remote_dir,
                parent=None  # No parent since it will be moved to thread
            )
            
            # Move worker to thread
            self._active_worker.moveToThread(self._active_thread)
            
            # Connect signals
            self._active_thread.started.connect(self._active_worker.run)
            self._active_worker.finished.connect(self._on_transfer_finished)
            self._active_worker.error.connect(self._on_transfer_error)
            
            # Cleanup when done
            self._active_worker.finished.connect(self._active_thread.quit)
            self._active_worker.error.connect(self._active_thread.quit)
            self._active_worker.finished.connect(self._active_worker.deleteLater)
            self._active_worker.error.connect(self._active_worker.deleteLater)
            self._active_thread.finished.connect(self._active_thread.deleteLater)
            
            # Start transfer
            self._is_busy = True
            self._active_thread.start()
            
            logger.start(f"Manual Transfer: Started {len(local_paths)} item(s)")
            self.transfer_started.emit(str(local_paths[0]))
            
            return True
            
        except Exception as e:
            logger.error(f"Manual Transfer: Failed to start: {e}")
            self._is_busy = False
            return False
    
    def cancel_transfer(self) -> bool:
        """
        Cancel the current transfer.
        
        Returns:
            True if cancelled, False if no transfer in progress
        """
        if not self._is_busy or not self._active_worker:
            return False
        
        # Note: TransferWorker doesn't currently support cancellation
        # This would need to be implemented
        logger.warn("Manual Transfer: Cancellation not yet implemented")
        return False
    
    def _on_transfer_finished(self) -> None:
        """Handle transfer completion."""
        self._is_busy = False
        logger.success("Manual Transfer: Completed")
        
        if self._active_worker and self._active_worker.local_paths:
            # Get the first path for signal
            self.transfer_completed.emit(self._active_worker.local_paths[0])
        
        self._active_worker = None
        self._active_thread = None
    
    def _on_transfer_error(self, error_msg: str) -> None:
        """Handle transfer error."""
        self._is_busy = False
        logger.error(f"Manual Transfer: Error: {error_msg}")
        
        if self._active_worker and self._active_worker.local_paths:
            self.transfer_failed.emit(self._active_worker.local_paths[0], error_msg)
        
        self._active_worker = None
        self._active_thread = None
    
    def get_transfer_preview(self, local_paths: List[str]) -> dict:
        """
        Get a preview of what would be transferred.
        
        Useful for showing user what will happen before transfer.
        
        Args:
            local_paths: Paths to preview
            
        Returns:
            Dictionary with preview information:
            - total_size: Total bytes to transfer
            - file_count: Number of files
            - folder_count: Number of folders
            - destinations: List of remote destinations
        """
        import os
        
        total_size = 0
        file_count = 0
        folder_count = 0
        destinations = []
        
        for path_str in local_paths:
            path = Path(path_str)
            
            if path.is_file():
                total_size += path.stat().st_size
                file_count += 1
            elif path.is_dir():
                folder_count += 1
                # Walk directory to count files and size
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            total_size += file_path.stat().st_size
                            file_count += 1
                        except OSError:
                            pass
            
            # Get destination
            try:
                if self.path_mapper.is_under_local_base(path):
                    remote_path = self.path_mapper.map_to_remote(path)
                    destinations.append(str(remote_path))
                else:
                    destinations.append(f"{self.settings.remote_base_dir}/{path.name}")
            except Exception:
                destinations.append("Unknown")
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "folder_count": folder_count,
            "destinations": destinations
        }
