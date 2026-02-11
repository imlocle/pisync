from __future__ import annotations

import os
import shutil
from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox, QDialog

from src.config.settings import Settings
from src.controllers.monitor_thread import MonitorThread
from src.services.connection_manager_service import ConnectionManagerService
from src.components.settings_window import SettingsWindow
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
    from src.controllers.transfer_controller import TransferController


class MainWindowController:
    """Controller for MainWindow. Handles all logic & event handlers."""

    def __init__(
        self, view, connection_manager: ConnectionManagerService, transfer_controller
    ):
        self.view = view
        self.connection_manager = connection_manager or ConnectionManagerService(
            self.settings
        )
        self.settings: Settings = view.settings
        self.transfer_controller = transfer_controller or TransferController()

        self.monitor_thread: Optional[MonitorThread] = None
        self.selected_item: Optional[str] = None

    # --------------------------------------------------------------
    #  CONNECTION MANAGEMENT
    # --------------------------------------------------------------
    def connect(self) -> None:
        """Establish connection to Raspberry Pi with error handling."""
        try:
            if not self.connection_manager.connect():
                self.view.connection_status_label.setText("🛑 Disconnected")
                return

            self.view.connection_status_label.setText(
                f"🟢 Connected: {self.settings.pi_ip}"
            )

            # bind sftp to remote explorer
            if self.connection_manager.sftp_client:
                self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
                self.view.pi_explorer.refresh()
                logger.success("Connected & Explorer Bound")
                
        except AuthenticationError as e:
            self.view.connection_status_label.setText("🛑 Authentication Failed")
            QMessageBox.critical(
                self.view,
                "Authentication Error",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except FileAccessError as e:
            self.view.connection_status_label.setText("🛑 SSH Key Error")
            QMessageBox.critical(
                self.view,
                "SSH Key Error",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except SSHConnectionError as e:
            self.view.connection_status_label.setText("🛑 Connection Failed")
            QMessageBox.warning(
                self.view,
                "Connection Failed",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            self.view.connection_status_label.setText("🛑 Error")
            logger.error(f"Unexpected connection error: {e}")
            QMessageBox.critical(
                self.view,
                "Connection Error",
                f"An unexpected error occurred:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
            self.view.pi_explorer.refresh()
            logger.success("Connected & Explorer Bound")

    def check_connection(self) -> None:
        if not self.connection_manager.is_connected():
            self.view.connection_status_label.setText("🛑 Disconnected")
            self.connect()

    def handle_remote_explorer_failure(self, error_msg: str) -> None:
        logger.error(f"Explorer Error: {error_msg}")
        ok = self.connection_manager.connect()
        if ok and self.connection_manager.sftp_client:
            self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
            self.view.pi_explorer.refresh(self.settings.pi_root_dir)
        else:
            self.view.connection_status_label.setText("🛑 Disconnected")
            logger.error("Cannot recover connection.")

    # --------------------------------------------------------------
    #  EXPLORER OPS
    # --------------------------------------------------------------
    def refresh_explorers(self):
        self.view.watch_explorer.refresh()

        if (
            self.connection_manager.is_connected()
            and self.connection_manager.sftp_client
        ):
            self.view.pi_explorer.set_sftp(self.connection_manager.sftp_client)
            self.view.pi_explorer.refresh()
        else:
            # Don't spam errors; just reflect disconnected state
            self.view.connection_status_label.setText("🛑 Disconnected")

        logger.success("Explorers refreshed")

    def handle_file_open(self, path: str):
        logger.info(f"📂 Opened file: {path}")

    def handle_selection_changed(self, path: str):
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
        is_remote = path.startswith(self.settings.pi_root_dir)

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
    def rename_item(self, old_path: str):
        explorer = (
            self.view.pi_explorer
            if old_path.startswith(self.settings.pi_root_dir)
            else self.view.watch_explorer
        )
        new_name = explorer.prompt_rename(old_path)
        if not new_name:
            return

        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            if old_path.startswith(self.settings.pi_root_dir):
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

    # --------------------------------------------------------------
    #  MONITORING
    # --------------------------------------------------------------
    def start_monitor(self):
        if self.monitor_thread and self.monitor_thread.isRunning():
            logger.warn("Already monitoring.")
            return

        self.check_connection()
        self.monitor_thread = MonitorThread(
            self.settings, self.connection_manager.sftp_client
        )
        self.monitor_thread.start()

        logger.start(f"Monitor: Start: {self.settings.watch_dir}")
        self.view.status_label.setText("🟢 Status: Monitoring: Active")

        self.view.start_btn.setEnabled(False)
        self.view.stop_btn.setEnabled(True)
        self.view.upload_all_btn.setEnabled(True)

    def stop_monitor(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.monitor_thread = None
            logger.stop("Monitor stopped")

        self.view.start_btn.setEnabled(True)
        self.view.stop_btn.setEnabled(False)
        self.view.upload_all_btn.setEnabled(False)
        self.view.status_label.setText("🛑 Status: Monitoring: Idle")

    # --------------------------------------------------------------
    #  UPLOAD
    # --------------------------------------------------------------
    def upload_all(self):
        if not os.path.exists(self.settings.watch_dir):
            logger.error("Watch directory missing.")
            return

        if self.transfer_controller.is_busy():
            logger.warn("Upload already in progress.")
            return

        logger.search("Scanning for files...")
        self.view.upload_all_btn.setEnabled(False)
        self.transfer_controller.upload_all_watch_dir()
        self.view.upload_all_btn.setEnabled(
            True
        )  # optional: you can re-enable on finished signal

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
    def shutdown(self):
        try:
            self.stop_monitor()
        except:
            pass
        self.connection_manager.disconnect()
