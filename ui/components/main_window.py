import os
import subprocess
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

from src.config.settings import Settings
from src.utils.helper import get_path
from src.utils.logging_signal import logger
from ui.controllers.monitor_thread import MonitorThread
from ui.components.settings_window import SettingsWindow
from ui.components.file_explorer_widget import FileExplorerWidget


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PiSync")
        self.setMinimumSize(1000, 650)

        # ========== Layout setup ==========
        main_layout: QVBoxLayout = QVBoxLayout()

        # --- Navbar ---
        navbar_layout: QHBoxLayout = QHBoxLayout()
        self.start_btn: QPushButton = QPushButton(" Start Monitoring")
        self.stop_btn: QPushButton = QPushButton(" Stop Monitoring")
        self.stop_btn.setEnabled(False)
        self.refresh_btn: QPushButton = QPushButton("↻")
        self.settings_btn: QPushButton = QPushButton("⚙️")

        # Add icons
        icon_path = get_path("assets/icons/")
        self.start_btn.setIcon(QIcon(f"{icon_path}/play_icon.svg"))
        self.stop_btn.setIcon(QIcon(f"{icon_path}/stop_icon.svg"))

        navbar_layout.addWidget(self.start_btn)
        navbar_layout.addWidget(self.stop_btn)
        navbar_layout.addWidget(self.refresh_btn)
        navbar_layout.addWidget(self.settings_btn)
        navbar_layout.addStretch()
        navbar_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.addLayout(navbar_layout)

        # --- Status label ---
        self.status_label: QLabel = QLabel("Status: Idle 🛑")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.status_label)

        # --- Settings check ---
        self.settings: Settings = Settings()
        if not self.settings.is_valid():
            QMessageBox.warning(
                self,
                "Setup Required",
                "Please configure your settings before proceeding.",
                QMessageBox.StandardButton.Ok,
            )
            settings_window = SettingsWindow(self.settings)
            if (
                settings_window.exec() != QDialog.accepted
                or not self.settings.is_valid()
            ):
                QMessageBox.critical(
                    self,
                    "Setup Failed",
                    "Settings are required to run PiSync. Please provide valid settings.",
                    QMessageBox.StandardButton.Ok,
                )
                self.close()
                return

        # ========== Splitter for two explorers ==========
        splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left: Mac Watch Directory ---
        self.watch_explorer: FileExplorerWidget = FileExplorerWidget(
            root_path=self.settings.watch_dir,
            title="Watch Directory",
        )

        # --- Right: Raspberry Pi Directory ---
        self.ssh_for_ui = None
        self.sftp_for_ui = None
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.settings.pi_ip, username=self.settings.pi_user, timeout=10)
            self.sftp_for_ui = ssh.open_sftp()
            self.ssh_for_ui = ssh
        except Exception as e:
            logger.log_signal.emit(
                f"⚠️ Could not connect to Pi SFTP for UI explorer: {e}"
            )
            self.sftp_for_ui = None
            self.ssh_for_ui = None

        self.pi_explorer = FileExplorerWidget(
            root_path="/mnt/external/",
            title="Raspberry Pi Files",
            is_remote=True,
            sftp=self.sftp_for_ui,
        )

        # Add explorers to splitter
        splitter.addWidget(self.watch_explorer)
        splitter.addWidget(self.pi_explorer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        # --- Log Box ---
        self.log_box: QTextEdit = QTextEdit()
        self.log_box.setReadOnly(True)
        main_layout.addWidget(self.log_box)

        # ========== Setup connections ==========
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.refresh_btn.clicked.connect(self.refresh_explorers)
        self.settings_btn.clicked.connect(self.open_settings)
        self.watch_explorer.file_opened.connect(self.handle_file_open)
        self.pi_explorer.file_opened.connect(self.handle_file_open)
        logger.log_signal.connect(self.log)
        self.setLayout(main_layout)

        self.check_pi_connection(
            pi_user=self.settings.pi_user, pi_ip=self.settings.pi_ip
        )

        self.monitor_thread: Optional[MonitorThread] = None

        # Auto-refresh local folder
        self.refresh_timer: QTimer = QTimer(self)
        self.refresh_timer.timeout.connect(self.watch_explorer.refresh)
        self.refresh_timer.start(5000)

    # ========== Event Handlers ==========

    def refresh_explorers(self) -> None:
        """Manual refresh for both explorers."""
        self.watch_explorer.refresh()
        self.pi_explorer.refresh()
        self.log("🔄 Refreshed both explorers.")

    def handle_file_open(self, path: str) -> None:
        """Handle double-click on file event (placeholder)."""
        self.log(f"📂 Opened file: {path}")

    def start_monitor(self) -> None:
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.log("⚠️ Already monitoring.")
            return

        # create and start monitor thread, reusing UI sftp client if available
        self.monitor_thread = MonitorThread(
            self.settings.watch_dir,
            self.settings.pi_user,
            self.settings.pi_ip,
            self.settings.pi_movies,
            self.settings.pi_tv,
            self.settings.file_exts,
            self,
            sftp_client=self.sftp_for_ui,
        )
        self.monitor_thread.log_signal.connect(self.log)
        self.monitor_thread.start()
        self.status_label.setText("Status: Monitoring 🟢")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitor(self) -> None:
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.log("🛑 Monitor: Stopped")
            self.status_label.setText("Status: Idle 🛑")
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
        if settings_window.exec() == QDialog.accepted:
            self.refresh_explorers()

    def log(self, message: str) -> None:
        """Write log messages to text box."""
        self.log_box.append(message)

    def check_pi_connection(self, pi_user: str, pi_ip: str) -> None:
        """Quick connectivity test before starting the service."""
        logger.log_signal.emit(f"🔍 Checking connection to {pi_ip}...")
        try:
            subprocess.run(
                ["ssh", f"{pi_user}@{pi_ip}", "echo", "connected"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.log_signal.emit(f"✅ Successfully connected to {pi_ip}\n")
        except subprocess.CalledProcessError as e:
            logger.log_signal.emit(f"❌ Cannot connect to {pi_ip}. Error:")
            logger.log_signal.emit(e.stderr.strip())
            logger.log_signal.emit("\nPlease check:")
            logger.log_signal.emit("- Is the Raspberry Pi online?")
            logger.log_signal.emit("- Is SSH enabled on the Pi?")
            logger.log_signal.emit("- Is the IP/hostname correct?")
            logger.log_signal.emit("- Are both devices on the same Wi-Fi?")
            exit(1)

    def transfer_existing_files(self) -> None:
        """Scan ~/Transfers for files and upload them to the Raspberry Pi before monitoring."""
        transfers_dir = self.settings.watch_dir
        if not os.path.exists(transfers_dir):
            self.log("📁 No ~/Transfers folder found. Skipping pre-scan.")
            return

        self.log("🔍 Scanning ~/Transfers for files to transfer...")
        transferred_count = 0

        try:
            # Ensure SFTP connection
            if not self.pi_explorer.sftp:
                self.log(
                    "⚠️ SFTP connection not available. Cannot transfer existing files."
                )
                return

            for root, _, files in os.walk(transfers_dir):
                for file in files:
                    # ✅ Skip unwanted system files
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
                    self.log(f"⬆️ Uploading: {local_path} → {remote_path}")
                    self.pi_explorer.sftp.put(local_path, remote_path)
                    transferred_count += 1

            if transferred_count > 0:
                self.log(
                    f"✅ Completed transfer of {transferred_count} file(s) from ~/Transfers."
                )
            else:
                self.log("ℹ️ No valid files found to transfer in ~/Transfers.")
        except Exception as e:
            self.log(f"❌ Error during pre-transfer: {e}")

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
