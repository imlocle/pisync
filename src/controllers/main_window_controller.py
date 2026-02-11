from __future__ import annotations

import os
import shutil
from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox, QDialog

from src.config.settings import Settings
from src.services.connection_manager_service import ConnectionManagerService
from src.components.settings_window import SettingsWindow
from src.application.manual_transfer_controller import ManualTransferController
from src.application.auto_sync_controller import AutoSyncController
from src.utils.logging_signal import logger
from src.models.errors import (
    SSHConnectionError,
    AuthenticationError,
    FileAccessError,
    FileDeletionError,
    ConnectionLostError,
)

if TYPE_CHECKING:
    from src.components.main_window import MainWindow


class MainWindowController:
    """
    Controller for MainWindow.
    
    This controller now delegates to specialized controllers:
    - ManualTransferController: For user-initiated transfers
    - AutoSyncController: For automatic monitoring
    
    It focuses on:
    - Connection management
    - UI coordination
    - Settings management
    - File operations (delete, rename)
    """

    def __init__(
        self, 
        view, 
        connection_manager: ConnectionManagerService,
    ):
        self.view = view
        self.settings: Settings = view.settings
        self.connection_manager = connection_manager
        
        # Create specialized controllers
        self.manual_transfer = ManualTransferController(
            self.settings,
            self.connection_manager,
            parent=view
        )
        
        self.auto_sync = AutoSyncController(
            self.settings,
            self.connection_manager,
            parent=view
        )
        
        # Connect controller signals to UI updates
        self._connect_controller_signals()
        
        self.selected_item: Optional[str] = None

    def _connect_controller_signals(self) -> None:
        """Connect controller signals to UI updates."""
        # Manual transfer signals
        self.manual_transfer.transfer_started.connect(self._on_manual_transfer_started)
        self.manual_transfer.transfer_completed.connect(self._on_manual_transfer_completed)
        self.manual_transfer.transfer_failed.connect(self._on_manual_transfer_failed)
        
        # Auto sync signals
        self.auto_sync.monitoring_started.connect(self._on_monitoring_started)
        self.auto_sync.monitoring_stopped.connect(self._on_monitoring_stopped)

    # --------------------------------------------------------------
    #  SIGNAL HANDLERS
    # --------------------------------------------------------------
    def _on_manual_transfer_started(self, path: str) -> None:
        """Handle manual transfer started."""
        logger.info(f"UI: Manual transfer started: {path}")
        self.view.upload_all_btn.setEnabled(False)
    
    def _on_manual_transfer_completed(self, path: str) -> None:
        """Handle manual transfer completed."""
        logger.success(f"UI: Manual transfer completed: {path}")
        self.view.upload_all_btn.setEnabled(True)
        self.refresh_explorers()
    
    def _on_manual_transfer_failed(self, path: str, error: str) -> None:
        """Handle manual transfer failed."""
        logger.error(f"UI: Manual transfer failed: {path}: {error}")
        self.view.upload_all_btn.setEnabled(True)
        QMessageBox.warning(
            self.view,
            "Transfer Failed",
            f"Failed to transfer {os.path.basename(path)}\n\n{error}",
            QMessageBox.StandardButton.Ok
        )
    
    def _on_monitoring_started(self) -> None:
        """Handle monitoring started."""
        self.view.status_label.setText("▶ Monitoring: Active")
        self.view.status_label.setStyleSheet("color: #4ec9b0; font-weight: 500;")
        self.view.start_btn.setEnabled(False)
        self.view.stop_btn.setEnabled(True)
        self.view.upload_all_btn.setEnabled(True)
    
    def _on_monitoring_stopped(self) -> None:
        """Handle monitoring stopped."""
        self.view.status_label.setText("⏸ Monitoring: Idle")
        self.view.status_label.setStyleSheet("color: #858585; font-weight: 500;")
        self.view.start_btn.setEnabled(True)
        self.view.stop_btn.setEnabled(False)
        self.view.upload_all_btn.setEnabled(False)

    # --------------------------------------------------------------
    #  CONNECTION MANAGEMENT
    # --------------------------------------------------------------
    def connect(self) -> None:
        """Establish connection to Raspberry Pi with error handling."""
        try:
            if not self.connection_manager.connect():
                self.view.connection_status_label.setText("● Disconnected")
                self.view.connection_status_label.setObjectName("connection_disconnected")
                self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
                return

            self.view.connection_status_label.setText(f"● Connected to {self.settings.pi_ip}")
            self.view.connection_status_label.setObjectName("connection_connected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())

            # bind sftp to remote explorer
            if self.connection_manager.sftp_client:
                self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
                self.view.pi_explorer.refresh()
                logger.success("Connected to Raspberry Pi")
                
        except AuthenticationError as e:
            self.view.connection_status_label.setText("● Authentication Failed")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            QMessageBox.critical(
                self.view,
                "Authentication Error",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except FileAccessError as e:
            self.view.connection_status_label.setText("● SSH Key Error")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            QMessageBox.critical(
                self.view,
                "SSH Key Error",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except SSHConnectionError as e:
            self.view.connection_status_label.setText("● Connection Failed")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            QMessageBox.warning(
                self.view,
                "Connection Failed",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            self.view.connection_status_label.setText("● Error")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            logger.error(f"Unexpected connection error: {e}")
            QMessageBox.critical(
                self.view,
                "Connection Error",
                f"An unexpected error occurred:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def check_connection(self) -> None:
        """Check connection and reconnect if needed."""
        if not self.connection_manager.is_connected():
            self.view.connection_status_label.setText("● Disconnected")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            self.connect()

    def handle_remote_explorer_failure(self, error_msg: str) -> None:
        """Handle remote explorer errors by attempting to reconnect."""
        logger.error(f"Explorer Error: {error_msg}")
        ok = self.connection_manager.connect()
        if ok and self.connection_manager.sftp_client:
            self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
            self.view.pi_explorer.refresh(self.settings.remote_base_dir)
        else:
            self.view.connection_status_label.setText("● Disconnected")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())
            logger.error("Cannot recover connection.")

    # --------------------------------------------------------------
    #  EXPLORER OPS
    # --------------------------------------------------------------
    def refresh_explorers(self) -> None:
        """Refresh both local and remote file explorers."""
        self.view.watch_explorer.refresh()

        if (
            self.connection_manager.is_connected()
            and self.connection_manager.sftp_client
        ):
            self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
            self.view.pi_explorer.refresh()
        else:
            # Don't spam errors; just reflect disconnected state
            self.view.connection_status_label.setText("● Disconnected")
            self.view.connection_status_label.setObjectName("connection_disconnected")
            self.view.connection_status_label.setStyle(self.view.connection_status_label.style())

        logger.success("Explorers refreshed")

    def handle_file_open(self, path: str) -> None:
        """Handle file open event from explorer."""
        logger.info(f"📂 Opened file: {path}")

    def handle_selection_changed(self, path: str) -> None:
        """Handle selection change in explorer."""
        self.selected_item = path or None
        self.view.delete_btn.setEnabled(bool(self.selected_item))

    # --------------------------------------------------------------
    #  DELETE
    # --------------------------------------------------------------
    def delete_selected_item(self) -> None:
        if self.selected_item:
            self.delete_item(self.selected_item)

    def delete_item(self, path: str) -> None:
        """
        Delete a file or folder with proper error handling.
        
        Args:
            path: Path to file or folder to delete
        """
        basename = os.path.basename(path)
        is_remote = path.startswith(self.settings.remote_base_dir)

        reply = QMessageBox.question(
            self.view,
            "Delete",
            f"Are you sure you want to delete:\n{basename}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if is_remote:
                self._delete_remote(path)
                self.view.pi_explorer.refresh()
            else:
                self._delete_local(path)
                self.view.watch_explorer.refresh()

            logger.trash(f"Deleted: {path}")

        except ConnectionLostError as e:
            logger.error(f"Delete failed: Connection lost: {e}")
            QMessageBox.warning(
                self.view,
                "Connection Lost",
                f"Connection to Pi was lost during deletion.\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            # Try to reconnect
            self.connect()
        except FileDeletionError as e:
            logger.error(f"Delete failed: {e}")
            QMessageBox.critical(
                self.view,
                "Deletion Failed",
                f"{e.message}\n\nPath: {e.path}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            QMessageBox.critical(
                self.view,
                "Deletion Failed",
                f"An unexpected error occurred:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def _is_remote_dir(self, path: str) -> bool:
        try:
            self.connection_manager.sftp_client.listdir(path)
            return True
        except Exception:
            return False

    def _delete_remote(self, path: str) -> None:
        """
        Delete remote file or directory.
        
        Args:
            path: Remote path to delete
            
        Raises:
            ConnectionLostError: If connection is lost
            FileDeletionError: If deletion fails
        """
        sftp = self.connection_manager.sftp_client
        if not sftp:
            raise ConnectionLostError("No SFTP connection available")

        try:
            if self._is_remote_dir(path):
                self._delete_remote_dir(path, sftp)
            else:
                sftp.remove(path)
        except IOError as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError(
                    "Connection lost during remote deletion",
                    details=str(e)
                )
            raise FileDeletionError(
                "Failed to delete remote item",
                path=path,
                details=str(e)
            )
        except Exception as e:
            raise FileDeletionError(
                "Unexpected error during remote deletion",
                path=path,
                details=str(e)
            )

    def _delete_remote_dir(self, path: str, sftp) -> None:
        """
        Recursively delete remote directory.
        
        Args:
            path: Remote directory path
            sftp: SFTP client
            
        Raises:
            ConnectionLostError: If connection is lost
            FileDeletionError: If deletion fails
        """
        try:
            for item in sftp.listdir(path):
                item_path = f"{path}/{item}"
                if self._is_remote_dir(item_path):
                    self._delete_remote_dir(item_path, sftp)
                else:
                    sftp.remove(item_path)
            sftp.rmdir(path)
        except IOError as e:
            if "Socket is closed" in str(e) or "not open" in str(e).lower():
                raise ConnectionLostError(
                    "Connection lost during directory deletion",
                    details=str(e)
                )
            raise FileDeletionError(
                "Failed to delete remote directory",
                path=path,
                details=str(e)
            )

    def _delete_local(self, path: str) -> None:
        """
        Delete local file or directory.
        
        Args:
            path: Local path to delete
            
        Raises:
            FileDeletionError: If deletion fails
        """
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except PermissionError as e:
            raise FileDeletionError(
                "Permission denied",
                path=path,
                details="You don't have permission to delete this item"
            )
        except FileNotFoundError as e:
            raise FileDeletionError(
                "File not found",
                path=path,
                details="The file may have already been deleted"
            )
        except Exception as e:
            raise FileDeletionError(
                "Failed to delete local item",
                path=path,
                details=str(e)
            )

    # --------------------------------------------------------------
    #  RENAME
    # --------------------------------------------------------------
    def rename_item(self, old_path: str) -> None:
        """
        Rename a file or folder.
        
        Args:
            old_path: Current path of item to rename
        """
        explorer = (
            self.view.pi_explorer
            if old_path.startswith(self.settings.remote_base_dir)
            else self.view.watch_explorer
        )
        new_name = explorer.prompt_rename(old_path)
        if not new_name:
            return

        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            if old_path.startswith(self.settings.remote_base_dir):
                if not self.connection_manager.sftp_client:
                    raise RuntimeError("No SFTP connection")
                self.connection_manager.sftp_client.rename(old_path, new_path)
                self.view.pi_explorer.refresh()
            else:
                os.rename(old_path, new_path)
                self.view.watch_explorer.refresh()

            logger.success(f"Renamed: {old_path} → {new_path}")
        except Exception as e:
            logger.error(f"Rename failed: {e}")
            QMessageBox.critical(
                self.view,
                "Rename Failed",
                f"Failed to rename item:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    # --------------------------------------------------------------
    #  MONITORING
    # --------------------------------------------------------------
    def start_monitor(self) -> None:
        """Start automatic monitoring via AutoSyncController."""
        self.check_connection()
        self.auto_sync.start_monitoring()

    def stop_monitor(self) -> None:
        """Stop automatic monitoring via AutoSyncController."""
        self.auto_sync.stop_monitoring()

    # --------------------------------------------------------------
    #  UPLOAD
    # --------------------------------------------------------------
    def upload_all(self) -> None:
        """Scan and transfer all existing files in watch directory."""
        if not os.path.exists(self.settings.local_watch_dir):
            logger.error("Watch directory missing.")
            QMessageBox.warning(
                self.view,
                "Directory Not Found",
                f"Watch directory does not exist:\n{self.settings.local_watch_dir}",
                QMessageBox.StandardButton.Ok
            )
            return

        if not self.auto_sync.is_monitoring():
            logger.warn("Monitoring not active. Start monitoring first.")
            QMessageBox.information(
                self.view,
                "Monitoring Required",
                "Please start monitoring before uploading all files.",
                QMessageBox.StandardButton.Ok
            )
            return

        logger.search("Scanning for existing files...")
        self.auto_sync.scan_and_transfer_existing()

    # --------------------------------------------------------------
    #  SETTINGS
    # --------------------------------------------------------------
    def open_settings(self):
        settings_window = SettingsWindow(self.settings)
        if settings_window.exec() == QDialog.DialogCode.Accepted:
            self.refresh_explorers()

    # --------------------------------------------------------------
    #  SHUTDOWN
    # --------------------------------------------------------------
    def shutdown(self) -> None:
        """Clean shutdown of all controllers and connections."""
        try:
            self.auto_sync.stop_monitoring()
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
        
        try:
            self.connection_manager.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
