import os

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
    QProgressBar,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from src.components.settings_window import SettingsWindow
from src.config.settings import Settings
from src.controllers.monitor_thread import MonitorThread
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.constants import SOFTARE_NAME
from src.utils.helper import get_path
from src.utils.logging_signal import logger
from src.widgets.file_explorer_widget import FileExplorerWidget


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(SOFTARE_NAME)
        self.setMinimumSize(1000, 700)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        logger.log_signal.connect(self.log)
        logger.progress_signal.connect(self.update_progress)

        # === 1. Settings Connection ===
        self.settings: Settings = Settings()
        if not self._validate_settings():
            return

        self.connection_manager_service = ConnectionManagerService(self.settings)
        if not self.connection_manager_service.connect():
            # Create screen to deal with this
            return

        self.monitor_thread = MonitorThread(
            self.settings, self.connection_manager_service.sftp_client
        )

        # === 2. Layout Setup ===
        main_layout: QVBoxLayout = QVBoxLayout()
        self._setup_navbar(main_layout)
        self._setup_splitter(main_layout)
        self._setup_log_box(main_layout)
        self._setup_status_label(main_layout)
        self._setup_progress_bar(main_layout)
        self.setLayout(main_layout)

        # === 3. Connect Signals ===
        self._setup_connections()

        # === 4. Initialize Background Tasks ===
        self._start_refresh_timer()

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
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.upload_all_btn.clicked.connect(self.upload_all)
        self.refresh_btn.clicked.connect(self.refresh_explorers)
        self.settings_btn.clicked.connect(self.open_settings)

        self.watch_explorer.file_opened.connect(self.handle_file_open)
        self.pi_explorer.file_opened.connect(self.handle_file_open)

    def _start_refresh_timer(self) -> None:
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.watch_explorer.refresh)
        self.refresh_timer.start(5000)

    # ==========================================================
    #  EVENT HANDLERS
    # ==========================================================

    def refresh_explorers(self) -> None:
        """Manual refresh for both explorers."""
        self.watch_explorer.root_path = self.settings.watch_dir
        self.watch_explorer.refresh()

        self.pi_explorer.root_path = self.settings.pi_root_dir
        self.pi_explorer.refresh()
        logger.info("Refreshed both explorers.")

    def handle_file_open(self, path: str) -> None:
        """Handle double-click on file event (placeholder)."""
        logger.info(f"📂 Opened file: {path}")

    def start_monitor(self) -> None:
        if self.monitor_thread and self.monitor_thread.isRunning():
            logger.warn("Already monitoring.")
            return

        self.monitor_thread.start()
        logger.start(f"Monitor: Start: {self.settings.watch_dir}")
        self.status_label.setText("🟢 Status: Monitoring: Active")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.upload_all_btn.setEnabled(True)

    def stop_monitor(self) -> None:
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            logger.stop(f"Monitor: Stop: {self.settings.watch_dir}")
            self.status_label.setText("🛑 Status: Monitoring: Idle")

            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.upload_all_btn.setEnabled(False)

        self.connection_manager_service.close()

    def open_settings(self) -> None:
        """Open settings dialog."""
        settings_window = SettingsWindow(self.settings, self.connection_manager_service)
        if settings_window.exec() == QDialog.DialogCode.Accepted:
            self.refresh_explorers()

    def upload_all(self) -> None:
        """Scan ~/Transfers for files and upload them to the Raspberry Pi."""
        if not os.path.exists(self.settings.watch_dir):
            logger.info(
                f"No {self.settings.watch_dir} folder found. Skipping pre-scan."
            )
            return

        logger.search(f"Scan: {self.settings.watch_dir} for files to transfer...")
        try:
            self.upload_all_btn.setEnabled(False)
            self.monitor_thread.scan_and_transfer()
            self.upload_all_btn.setEnabled(True)
        except Exception as e:
            logger.error(f"Error during pre-transfer: {e}")

    def log(self, message: str) -> None:
        """Write log messages to text box."""
        self.log_box.append(message)

    def update_progress(self, value: int) -> None:
        """Update progress bar (0-100)."""
        self.progress_bar.setValue(value)
        if value < 100:
            self.progress_bar.setFormat(f"Uploading... {value}%")
            self.progress_bar.show()
        else:
            self.progress_bar.setFormat("Upload Complete")
            QTimer.singleShot(2000, lambda: self.progress_bar.setValue(0))

    # ==========================================================
    #  UI SETUP METHODS
    # ==========================================================

    def _setup_navbar(self, layout: QVBoxLayout) -> None:
        navbar_layout = QHBoxLayout()
        self.start_btn = QPushButton(" Start Monitoring")
        self.stop_btn = QPushButton(" Stop Monitoring")
        self.stop_btn.setEnabled(False)
        self.upload_all_btn = QPushButton("⬆️ Upload All")
        self.upload_all_btn.setEnabled(False)
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

    def _setup_splitter(self, layout: QVBoxLayout) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.watch_explorer: FileExplorerWidget = FileExplorerWidget(
            root_path=self.settings.watch_dir,
            title="Watch Directory",
        )

        try:
            self.pi_explorer = FileExplorerWidget(
                root_path=self.settings.pi_root_dir,
                title="Raspberry Pi Files",
                is_remote=True,
                sftp=self.connection_manager_service.sftp_client,
            )
        except Exception as e:
            logger.error(f"Failed to Connect: {e}")

        # Add explorers to splitter
        splitter.addWidget(self.watch_explorer)
        splitter.addWidget(self.pi_explorer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _setup_log_box(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self.log_box)

    def _setup_status_label(self, layout: QVBoxLayout) -> None:
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)

    def _setup_progress_bar(self, layout: QVBoxLayout) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

    def closeEvent(self, event) -> None:
        """Called when user clicks the window's close button."""
        reply = QMessageBox.question(
            self,
            f"Exit {SOFTARE_NAME}",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"Closing {SOFTARE_NAME} and disconnecting SSH...")
            self.stop_monitor()
            event.accept()
        else:
            event.ignore()
