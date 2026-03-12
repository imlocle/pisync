"""
Auto sync controller.

Handles automatic folder synchronization and monitoring.
"""

from typing import Optional

from PySide6.QtCore import QObject, Signal

from src.config.settings import Settings
from src.controllers.monitor_thread import MonitorThread
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.logging_signal import logger


class AutoSyncController(QObject):
    """
    Controller for automatic folder synchronization.
    
    This controller handles:
    - Automatic monitoring of watch directory
    - File stability checking
    - Automatic classification and transfer
    - Automatic cleanup after transfer
    
    Unlike ManualTransferController, this operates automatically
    based on file system events.
    """
    
    # Signals
    monitoring_started = Signal()
    monitoring_stopped = Signal()
    file_detected = Signal(str)  # path
    file_transferred = Signal(str)  # path
    transfer_failed = Signal(str, str)  # path, error
    scan_progress = Signal(str, int, int)  # item_name, current, total
    
    def __init__(
        self,
        settings: Settings,
        connection_manager: ConnectionManagerService,
        parent: Optional[QObject] = None
    ):
        """
        Initialize auto sync controller.
        
        Args:
            settings: Application settings
            connection_manager: Connection manager for SFTP
            parent: Parent QObject
        """
        super().__init__(parent)
        self.settings = settings
        self.connection_manager = connection_manager
        
        self._monitor_thread: Optional[MonitorThread] = None
        self._is_monitoring = False
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active."""
        return self._is_monitoring
    
    def start_monitoring(self) -> bool:
        """
        Start automatic folder monitoring.
        
        Returns:
            True if started successfully, False if already monitoring or error
        """
        if self._is_monitoring:
            logger.warn("Auto Sync: Already monitoring")
            return False
        
        # Ensure connection
        if not self.connection_manager.is_connected():
            logger.info("Auto Sync: Connecting...")
            if not self.connection_manager.connect():
                logger.error("Auto Sync: Connection failed")
                return False
        
        try:
            # Ensure SFTP client exists
            if not self.connection_manager.sftp_client:
                logger.error("Auto Sync: No SFTP client available")
                return False
            
            # Create and start monitor thread
            self._monitor_thread = MonitorThread(
                settings=self.settings,
                sftp_client=self.connection_manager.sftp_client
            )
            
            # Connect monitor thread signals
            self._monitor_thread.scan_progress.connect(self.scan_progress.emit)
            self._monitor_thread.transfer_completed.connect(self.file_transferred.emit)
            
            self._monitor_thread.start()
            self._is_monitoring = True
            
            logger.start(f"Auto Sync: Started monitoring {self.settings.local_watch_dir}")
            self.monitoring_started.emit()
            
            return True
            
        except Exception as e:
            logger.error(f"Auto Sync: Failed to start: {e}")
            self._is_monitoring = False
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop automatic folder monitoring.
        
        Returns:
            True if stopped successfully, False if not monitoring
        """
        if not self._is_monitoring:
            logger.warn("Auto Sync: Not monitoring")
            return False
        
        try:
            if self._monitor_thread:
                self._monitor_thread.stop()
                self._monitor_thread.wait()  # Wait for thread to finish
                self._monitor_thread = None
            
            self._is_monitoring = False
            
            logger.stop("Auto Sync: Stopped monitoring")
            self.monitoring_stopped.emit()
            
            return True
            
        except Exception as e:
            logger.error(f"Auto Sync: Failed to stop: {e}")
            return False
    
    def scan_and_transfer_existing(self) -> bool:
        """
        Scan watch directory and transfer existing files.
        
        This is useful for processing files that were added while
        the app was not running.
        
        Returns:
            True if scan started successfully
        """
        if not self._monitor_thread:
            logger.warn("Auto Sync: Monitor not initialized")
            return False
        
        try:
            logger.start("Auto Sync: Scanning for existing files...")
            self._monitor_thread.scan_and_transfer()
            return True
        except Exception as e:
            logger.error(f"Auto Sync: Scan failed: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        Get current monitoring status.
        
        Returns:
            Dictionary with status information:
            - is_monitoring: Whether monitoring is active
            - watch_dir: Directory being monitored
            - connection_status: Connection status
            - files_processed: Number of files processed (if available)
        """
        return {
            "is_monitoring": self._is_monitoring,
            "watch_dir": self.settings.local_watch_dir,
            "connection_status": "connected" if self.connection_manager.is_connected() else "disconnected",
            "stability_duration": self.settings.stability_duration,
            "delete_after_transfer": self.settings.delete_after_transfer,
        }
    
    def update_settings(self, settings: Settings) -> None:
        """
        Update settings and restart monitoring if active.
        
        Args:
            settings: New settings
        """
        was_monitoring = self._is_monitoring
        
        if was_monitoring:
            self.stop_monitoring()
        
        self.settings = settings
        
        if was_monitoring and self.settings.auto_start_monitor:
            self.start_monitoring()
