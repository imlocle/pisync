from __future__ import annotations

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
from PySide6.QtGui import QCloseEvent, QShowEvent

from src.components.settings_window import SettingsWindow
from src.config.settings import Settings
from src.controllers.main_window_controller import MainWindowController
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.constants import SOFTWARE_NAME
from src.utils.logging_signal import logger
from src.widgets.file_explorer_widget import FileExplorerWidget


class MainWindow(QWidget):
    """Pure UI class. All logic is delegated to MainWindowController."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(SOFTWARE_NAME)
        self.setMinimumSize(1000, 800)

        self.connection_status_label = QLabel()
        self.log_box = QTextEdit(readOnly=True)
        logger.log_signal.connect(self.log)
        logger.progress_signal.connect(self.update_progress)

        # === 1. Load Settings ===
        if not self._validate_settings():
            return

        # Create controller
        self.connection_manager_service = ConnectionManagerService(self.settings)
        self.controller = MainWindowController(
            self, self.connection_manager_service
        )

        # === 2. Build Layout ===
        main_layout = QVBoxLayout()
        self._setup_navbar(main_layout)
        self._setup_splitter(main_layout)
        self._setup_connection_status_label(main_layout)
        self._setup_log_box(main_layout)
        self._setup_status_label(main_layout)
        self._setup_progress_bar(main_layout)
        self.setLayout(main_layout)

        # === 3. Wire Signals (to controller) ===
        self._setup_connections()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_settings(self) -> bool:
        self.settings = Settings()

        if not self.settings.is_valid():
            QMessageBox.warning(
                self,
                "Setup Required",
                "Please configure your settings first.",
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

    # ------------------------------------------------------------------
    # Signal Wiring
    # ------------------------------------------------------------------
    def _setup_connections(self) -> None:
        """Wire UI signals to controller actions."""
        self.start_btn.clicked.connect(self.controller.start_monitor)
        self.stop_btn.clicked.connect(self.controller.stop_monitor)
        self.upload_all_btn.clicked.connect(self.controller.upload_all)
        self.refresh_btn.clicked.connect(self.controller.refresh_explorers)
        self.settings_btn.clicked.connect(self.controller.open_settings)
        self.delete_btn.clicked.connect(self.controller.delete_selected_item)

        # Watch explorer
        self.watch_explorer.file_delete_requested.connect(self.controller.delete_item)
        self.watch_explorer.file_rename_requested.connect(self.controller.rename_item)
        self.watch_explorer.item_selected.connect(
            self.controller.handle_selection_changed
        )
        self.watch_explorer.file_opened.connect(self.controller.handle_file_open)

        # Pi explorer
        self.pi_explorer.file_delete_requested.connect(self.controller.delete_item)
        self.pi_explorer.file_rename_requested.connect(self.controller.rename_item)
        self.pi_explorer.item_selected.connect(self.controller.handle_selection_changed)
        self.pi_explorer.file_opened.connect(self.controller.handle_file_open)
        self.pi_explorer.files_dropped.connect(self._handle_pi_drop)
        self.pi_explorer.remote_error.connect(
            self.controller.handle_remote_explorer_failure
        )
        self.pi_explorer.files_dropped.connect(self._handle_pi_drop)

    def _start_refresh_timer(self) -> None:
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.controller.refresh_explorers)
        self.refresh_timer.start(30000)

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def _setup_navbar(self, layout: QVBoxLayout):
        nav = QHBoxLayout()

        self.start_btn = QPushButton("▶︎")
        self.start_btn.setToolTip("Start Monitoring")

        self.stop_btn = QPushButton("◼")
        self.stop_btn.setToolTip("Stop Monitoring")
        self.stop_btn.setEnabled(False)

        self.upload_all_btn = QPushButton("⬆")
        self.upload_all_btn.setToolTip("Upload All")
        self.upload_all_btn.setEnabled(False)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Refresh")
        self.settings_btn = QPushButton("⛯")
        self.settings_btn.setToolTip("Settings")

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip("Delete File")
        self.delete_btn.setEnabled(False)

        nav.addWidget(self.start_btn)
        nav.addWidget(self.stop_btn)
        nav.addWidget(self.upload_all_btn)
        nav.addWidget(self.refresh_btn)
        nav.addWidget(self.settings_btn)
        nav.addWidget(self.delete_btn)
        nav.addStretch()
        nav.setContentsMargins(10, 5, 10, 5)
        layout.addLayout(nav)

    def _setup_splitter(self, layout: QVBoxLayout):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.watch_explorer = FileExplorerWidget(
            settings=self.settings,
            root_path=self.settings.local_watch_dir,
            title="Watch Directory",
        )

        self.pi_explorer = FileExplorerWidget(
            settings=self.settings,
            root_path=self.settings.remote_base_dir,
            title="Raspberry Pi Files",
            is_remote=True,
            sftp=None,
        )

        splitter.addWidget(self.watch_explorer)
        splitter.addWidget(self.pi_explorer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _setup_connection_status_label(self, layout: QVBoxLayout) -> None:
        self.connection_status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.connection_status_label.setText("🟡 Status: Not Connected")
        layout.addWidget(self.connection_status_label)

    def _setup_log_box(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self.log_box)

    def _setup_status_label(self, layout: QVBoxLayout) -> None:
        self.status_label = QLabel("🛑 Status: Monitoring: Idle")
        layout.addWidget(self.status_label)

    def _setup_progress_bar(self, layout: QVBoxLayout) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        layout.addWidget(self.progress_bar)

    # ------------------------------------------------------------------
    # Logging & Progress
    # ------------------------------------------------------------------
    def log(self, message: str) -> None:
        self.log_box.append(message)

    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)
        if value < 100:
            self.progress_bar.setFormat(f"Uploading... {value}%")
        else:
            self.progress_bar.setFormat("Upload Complete")

    # ------------------------------------------------------------------
    # Lifecycle Events
    # ------------------------------------------------------------------
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        QTimer.singleShot(150, self.controller.connect)
        if self.settings.auto_start_monitor:
            self.controller.start_monitor()

    def closeEvent(self, event: QCloseEvent):
        """Called when user clicks the window's close button."""
        reply = QMessageBox.question(
            self,
            f"Exit {SOFTWARE_NAME}",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"Closing {SOFTWARE_NAME}...")
            self.controller.shutdown()
            event.accept()
        else:
            event.ignore()

    def _handle_pi_drop(self, local_paths: list[str], remote_dir: str) -> None:
        """
        Called when user drags files/folders from Finder onto the Pi explorer.
        
        Delegates to ManualTransferController for handling.
        """
        self.controller.manual_transfer.transfer_to_pi(
            local_paths=local_paths,
            remote_destination=remote_dir
        )
