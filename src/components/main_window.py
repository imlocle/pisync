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
    QFrame,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QCloseEvent, QShowEvent, QIcon

from src.components.settings_window import SettingsWindow
from src.config.settings import Settings
from src.controllers.main_window_controller import MainWindowController
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.constants import SOFTWARE_NAME
from src.utils.logging_signal import logger
from src.widgets.file_explorer_widget import FileExplorerWidget


class MainWindow(QWidget):
    """
    Modern, clean main window for PiSync.
    
    Features:
    - Clean toolbar with icon + text buttons
    - Status bar with connection and monitoring status
    - Dual-pane file explorer
    - Activity log with timestamps
    - Progress indicator
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(SOFTWARE_NAME)
        self.setMinimumSize(1200, 800)

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._setup_toolbar(main_layout)
        self._setup_status_bar(main_layout)
        self._setup_content_area(main_layout)
        self._setup_activity_log(main_layout)
        self._setup_progress_bar(main_layout)
        
        self.setLayout(main_layout)

        # === 3. Wire Signals ===
        self._setup_connections()
        
        # === 4. Connect logger ===
        logger.log_signal.connect(self.log)
        logger.progress_signal.connect(self.update_progress)

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

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def _setup_toolbar(self, layout: QVBoxLayout) -> None:
        """Create modern toolbar with icon + text buttons."""
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar.setStyleSheet("""
            QFrame#toolbar {
                background-color: #252526;
                border-bottom: 1px solid #3e3e42;
                padding: 8px;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        # Start button
        self.start_btn = QPushButton("▶  Start Monitoring")
        self.start_btn.setObjectName("primary_btn")
        self.start_btn.setMinimumHeight(36)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Stop button
        self.stop_btn = QPushButton("⏹  Stop Monitoring")
        self.stop_btn.setMinimumHeight(36)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Upload all button
        self.upload_all_btn = QPushButton("⬆  Upload All")
        self.upload_all_btn.setMinimumHeight(36)
        self.upload_all_btn.setEnabled(False)
        self.upload_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Spacer
        toolbar_layout.addWidget(self.start_btn)
        toolbar_layout.addWidget(self.stop_btn)
        toolbar_layout.addWidget(self.upload_all_btn)
        toolbar_layout.addStretch()

        # Right side buttons
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setObjectName("icon_btn")
        self.refresh_btn.setToolTip("Refresh Explorers")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setObjectName("icon_btn")
        self.delete_btn.setToolTip("Delete Selected Item")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("icon_btn")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addWidget(self.settings_btn)

        layout.addWidget(toolbar)

    def _setup_status_bar(self, layout: QVBoxLayout) -> None:
        """Create status bar with connection and monitoring status."""
        status_bar = QFrame()
        status_bar.setObjectName("status_bar")
        status_bar.setStyleSheet("""
            QFrame#status_bar {
                background-color: #252526;
                border-bottom: 1px solid #3e3e42;
                padding: 6px 12px;
            }
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 6, 12, 6)
        status_layout.setSpacing(16)

        # Connection status
        self.connection_status_label = QLabel("● Disconnected")
        self.connection_status_label.setObjectName("connection_disconnected")
        self.connection_status_label.setStyleSheet("font-weight: 500;")

        # Monitoring status
        self.status_label = QLabel("⏸ Monitoring: Idle")
        self.status_label.setStyleSheet("color: #858585; font-weight: 500;")

        status_layout.addWidget(self.connection_status_label)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addWidget(status_bar)

    def _setup_content_area(self, layout: QVBoxLayout) -> None:
        """Create main content area with file explorers."""
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(12, 12, 12, 12)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        self.watch_explorer = FileExplorerWidget(
            settings=self.settings,
            root_path=self.settings.local_watch_dir,
            title="📁 Local Files",
        )

        self.pi_explorer = FileExplorerWidget(
            settings=self.settings,
            root_path=self.settings.remote_base_dir,
            title="🥧 Raspberry Pi",
            is_remote=True,
            sftp=None,
        )

        splitter.addWidget(self.watch_explorer)
        splitter.addWidget(self.pi_explorer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        content_layout.addWidget(splitter)
        layout.addWidget(content_container, stretch=1)

    def _setup_activity_log(self, layout: QVBoxLayout) -> None:
        """Create activity log section."""
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(12, 0, 12, 12)
        log_layout.setSpacing(6)

        # Log header
        log_header = QLabel("Activity Log")
        log_header.setObjectName("section_header")
        log_layout.addWidget(log_header)

        # Log text box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(180)
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 8px;
                font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_box)

        layout.addWidget(log_container)

    def _setup_progress_bar(self, layout: QVBoxLayout) -> None:
        """Create progress bar."""
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(12, 0, 12, 12)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(28)
        
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_container)

    # ------------------------------------------------------------------
    # Logging & Progress
    # ------------------------------------------------------------------
    def log(self, message: str) -> None:
        """Append message to activity log."""
        self.log_box.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_progress(self, value: int) -> None:
        """Update progress bar."""
        self.progress_bar.setValue(value)
        if value < 100:
            self.progress_bar.setFormat(f"Transferring... {value}%")
        else:
            self.progress_bar.setFormat("✓ Transfer Complete")
            # Reset after 2 seconds
            QTimer.singleShot(2000, lambda: self.progress_bar.setFormat(""))

    # ------------------------------------------------------------------
    # Lifecycle Events
    # ------------------------------------------------------------------
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        QTimer.singleShot(150, self.controller.connect)
        if self.settings.auto_start_monitor:
            QTimer.singleShot(300, self.controller.start_monitor)

    def closeEvent(self, event: QCloseEvent):
        """Called when user clicks the window's close button."""
        reply = QMessageBox.question(
            self,
            f"Exit {SOFTWARE_NAME}",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
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
