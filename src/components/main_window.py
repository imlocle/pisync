import os
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

import paramiko

from src.components.settings_window import SettingsWindow
from src.config.settings import Settings
from src.controllers.monitor_thread import MonitorThread
from src.utils.constants import SOFTARE_NAME
from src.utils.helper import get_path
from src.utils.logging_signal import logger
from src.widgets.file_explorer_widget import FileExplorerWidget


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(SOFTARE_NAME)
        self.setMinimumSize(1000, 650)

        self.log_box = QTextEdit()
        self.monitor_thread: Optional[MonitorThread] = None
        self.ssh_for_ui = None
        self.sftp_for_ui = None
        self.settings: Settings = Settings()

        # === 1. Validate Settings ===
        if not self._validate_settings():
            return

        self.is_pi_connected: bool = self._check_pi_connection()

        # ========== Layout setup ==========
        main_layout: QVBoxLayout = QVBoxLayout()
        self._setup_navbar(main_layout)
        self._setup_splitter(main_layout)
        self._setup_log_box(main_layout)
        self._setup_status_label(main_layout)
        self.setLayout(main_layout)

        # === 3. Connect Signals ===
        self._setup_connections()

        # === 4. Initialize Background Tasks ===
        self._start_refresh_timer()

    # ==========================================================
    #  UI SETUP METHODS
    # ==========================================================

    def _setup_navbar(self, layout: QVBoxLayout) -> None:
        navbar_layout = QHBoxLayout()
        self.start_btn = QPushButton(" Start Monitoring")
        self.stop_btn = QPushButton(" Stop Monitoring")
        self.stop_btn.setEnabled(False)
        self.upload_all_btn = QPushButton("⬆️ Upload All")
        self.refresh_btn = QPushButton("↻ Refresh")
        self.settings_btn = QPushButton("⚙️ Settings")

        icon_path = get_path("assets/icons/")
        self.start_btn.setIcon(QIcon(f"{icon_path}/play_icon.svg"))
        self.stop_btn.setIcon(QIcon(f"{icon_path}/stop_icon.svg"))

        navbar_layout.addWidget(self.start_btn)
        navbar_layout.addWidget(self.stop_btn)
        navbar_layout.addWidget(self.upload_all_btn)
        navbar_layout.addWidget(self.refresh_btn)
        navbar_layout.addWidget(self.settings_btn)
        navbar_layout.addStretch()
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        layout.addLayout(navbar_layout)

    def _setup_status_label(self, layout: QVBoxLayout) -> None:
        self.status_label = QLabel("Status: Idle 🛑")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)

    def _setup_splitter(self, layout: QVBoxLayout) -> None:
        splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Local Watch Directory ---
        self.watch_explorer: FileExplorerWidget = FileExplorerWidget(
            root_path=self.settings.watch_dir,
            title="Watch Directory",
        )

        # --- Right: Raspberry Pi Directory ---
        if not self.is_pi_connected:
            self.is_pi_connected = self._check_pi_connection()

        try:
            self.pi_explorer = FileExplorerWidget(
                root_path=self.settings.pi_root_dir,
                title="Raspberry Pi Files",
                is_remote=True,
                sftp=self.sftp_for_ui,
            )
        except Exception as e:
            logger.error(str(e))

        # Add explorers to splitter
        splitter.addWidget(self.watch_explorer)
        splitter.addWidget(self.pi_explorer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _setup_log_box(self, layout: QVBoxLayout) -> None:
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

    # ==========================================================
    #  SETUP HELPERS
    # ==========================================================

    def _validate_settings(self) -> bool:
        if not self.settings.is_valid():
            QMessageBox.warning(
                self,
                "Setup Required",
                "Please configure your settings before proceeding.",
                QMessageBox.StandardButton.Ok,
            )
            settings_window = SettingsWindow(self.settings)

            if (
                settings_window.exec() != QDialog.DialogCode.Accepted
                or not self.settings.is_valid()
            ):
                QMessageBox.critical(
                    self,
                    "Setup Failed",
                    "Settings are required to run PiSync.",
                    QMessageBox.StandardButton.Ok,
                )
                self.close()
                return False
        return True

    def _setup_connections(self) -> None:
        try:
            logger.log_signal.disconnect(self.log)
        except Exception:
            pass

        logger.log_signal.connect(self.log)
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.upload_all_btn.clicked.connect(self.transfer_existing_files)
        self.refresh_btn.clicked.connect(self.refresh_explorers)
        self.settings_btn.clicked.connect(self.open_settings)
        self.watch_explorer.file_opened.connect(self.handle_file_open)
        self.pi_explorer.file_opened.connect(self.handle_file_open)

    def _start_refresh_timer(self) -> None:
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.watch_explorer.refresh)
        self.refresh_timer.start(5000)

    def initialize_pi_explorer(self) -> None:
        if not self.is_pi_connected:
            logger.warn("Pi Explorer: Failed to connect")
            self.is_pi_connected = self._check_pi_connection()

    # ========== Event Handlers ==========

    def refresh_explorers(self) -> None:
        """Manual refresh for both explorers."""
        self.watch_explorer.root_path = self.settings.watch_dir
        self.pi_explorer.root_path = self.settings.pi_root_dir

        self.watch_explorer.refresh()
        self.pi_explorer.refresh()
        logger.info("Refreshed both explorers.")

    def handle_file_open(self, path: str) -> None:
        """Handle double-click on file event (placeholder)."""
        logger.info(f"📂 Opened file: {path}")

    def start_monitor(self) -> None:
        if self.monitor_thread and self.monitor_thread.isRunning():
            logger.warn("Already monitoring.")
            return

        if not self.is_pi_connected:
            self.is_pi_connected = self._check_pi_connection()
        else:
            logger.success(f"Connected: {self.settings.pi_ip}")

        self.monitor_thread = MonitorThread(
            self.settings.watch_dir,
            self.settings.pi_user,
            self.settings.pi_ip,
            self.settings.pi_root_dir,
            self.settings.pi_movies,
            self.settings.pi_tv,
            self.settings.file_exts,
            self,
            sftp_client=self.sftp_for_ui,
        )

        self.monitor_thread.start()
        logger.search(f"Monitor: Start: {self.settings.watch_dir}")
        self.status_label.setText("🟢 Status: Monitoring: Active")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitor(self) -> None:
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            logger.stop("Monitor: Stop")
            self.status_label.setText("🛑 Status: Monitoring: Idle")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        # close UI SFTP if it exists and wasn't passed/closed by monitor thread
        try:
            if self.sftp_for_ui:
                self.sftp_for_ui.close()
            if self.ssh_for_ui:
                self.ssh_for_ui.close()
        except Exception:
            pass

    def open_settings(self) -> None:
        """Open settings dialog."""
        settings_window = SettingsWindow(self.settings)
        if settings_window.exec() == QDialog.DialogCode.Accepted:
            self.refresh_explorers()

    def log(self, message: str) -> None:
        """Write log messages to text box."""
        self.log_box.append(message)

    def _check_pi_connection(self) -> bool:
        """Quick connectivity test before starting the service."""
        logger.search(f"Checking connection to {self.settings.pi_ip}...")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.settings.pi_ip, username=self.settings.pi_user, timeout=10)
            self.sftp_for_ui = ssh.open_sftp()
            self.ssh_for_ui = ssh
            logger.success(f"Successfully connected to {self.settings.pi_ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.settings.pi_ip}: {e}")
            self.sftp_for_ui = None
            self.ssh_for_ui = None
            return False

    def transfer_existing_files(self) -> None:
        """Scan ~/Transfers for files and upload them to the Raspberry Pi before monitoring."""
        transfers_dir = self.settings.watch_dir
        if not os.path.exists(transfers_dir):
            logger.info("No ~/Transfers folder found. Skipping pre-scan.")
            return

        logger.search("Scanning ~/Transfers for files to transfer...")
        transferred_count = 0

        try:
            # Ensure SFTP connection
            if not self.pi_explorer.sftp:
                logger.warn(
                    "SFTP connection not available. Cannot transfer existing files."
                )
                return

            for root, _, files in os.walk(transfers_dir):
                for file in files:
                    if file.startswith(".") or file in self.settings.skip_files:
                        continue

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, transfers_dir)
                    remote_path = os.path.join("/mnt/external/", relative_path)

                    # Ensure remote directory exists
                    remote_dir = os.path.dirname(remote_path)
                    try:
                        self.pi_explorer.sftp.stat(remote_dir)
                    except IOError:
                        self._make_remote_dirs(self.pi_explorer.sftp, remote_dir)

                    # Upload file
                    logger.info(f"Uploading: {local_path} → {remote_path}")
                    self.pi_explorer.sftp.put(local_path, remote_path)
                    transferred_count += 1

            if transferred_count > 0:
                logger.success(
                    f"Completed transfer of {transferred_count} file(s) from ~/Transfers."
                )
            else:
                logger.info("No valid files found to transfer in ~/Transfers.")
        except Exception as e:
            logger.error(f"Error during pre-transfer: {e}")

    def _make_remote_dirs(self, sftp, remote_directory: str) -> None:
        """Recursively create remote directories if they don't exist."""
        dirs = []
        while len(remote_directory) > 1:
            try:
                sftp.stat(remote_directory)
                break
            except IOError:
                dirs.append(remote_directory)
                remote_directory = os.path.dirname(remote_directory)

        for d in reversed(dirs):
            try:
                sftp.mkdir(d)
            except Exception:
                pass
