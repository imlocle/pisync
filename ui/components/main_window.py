import subprocess
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QSplitter,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
import os
import shutil
from src.config.settings import Settings
from src.utils.helper import get_path
from src.utils.logging_signal import logger
from ui.controllers.monitor_thread import MonitorThread
from ui.components.settings_window import SettingsWindow
from typing import Optional


class MainWindow(QWidget):
    file_dropped = Signal(str, str)  # Source path, dest_type

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PiSync")
        self.setMinimumSize(900, 600)
        main_layout: QVBoxLayout = QVBoxLayout()

        # Top Navbar
        navbar_layout: QHBoxLayout = QHBoxLayout()
        navbar_layout.setObjectName("navbar_layout")  # Set object name for styling
        self.start_btn: QPushButton = QPushButton(" Start Monitoring")
        self.stop_btn: QPushButton = QPushButton(" Stop Monitoring")
        self.stop_btn.setEnabled(False)
        self.settings_btn: QPushButton = QPushButton("⚙️")

        navbar_layout.addWidget(self.start_btn)
        navbar_layout.addWidget(self.stop_btn)
        navbar_layout.addWidget(self.settings_btn)
        navbar_layout.addStretch()  # Push buttons to the left
        navbar_layout.setContentsMargins(10, 5, 10, 5)  # Add padding
        main_layout.addLayout(navbar_layout)

        # Set icons for buttons
        icon_path_base = get_path("assets/icons/")
        self.start_btn.setIcon(QIcon(str(icon_path_base / "play_icon.svg")))
        self.stop_btn.setIcon(QIcon(str(icon_path_base / "stop_icon.svg")))

        # Status Label below navbar
        self.status_label: QLabel = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Splitter for two columns
        splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Column: MacBook Folder
        left_widget: QWidget = QWidget()
        left_layout: QVBoxLayout = QVBoxLayout()
        self.macbook_list: QListWidget = QListWidget()
        self.macbook_list.setAcceptDrops(True)  # Enable drop

        left_layout.addWidget(QLabel("MacBook Folder"))
        left_layout.addWidget(self.macbook_list)
        left_widget.setLayout(left_layout)

        # Right Column: Pi Folder
        right_widget: QWidget = QWidget()
        right_layout: QVBoxLayout = QVBoxLayout()
        self.pi_list: QListWidget = QListWidget()  # Ensure pi_list is defined here
        self.pi_list.setAcceptDrops(True)
        self.pi_list.addItems([])  # Initialize with empty list
        right_layout.addWidget(QLabel("Pi Folder"))
        right_layout.addWidget(self.pi_list)
        right_widget.setLayout(right_layout)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        # Log Box
        self.log_box: QTextEdit = QTextEdit()
        self.log_box.setReadOnly(True)
        main_layout.addWidget(self.log_box)

        self.setLayout(main_layout)
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.settings_btn.clicked.connect(self.open_settings)
        logger.log_signal.connect(self.log)  # Connect to logger's signal
        self.installEventFilter(self)  # Install event filter on MainWindow
        self.monitor_thread: Optional[MonitorThread] = None

        self.settings: Settings = Settings()

        # Checking on settings.
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

        self.check_pi_connection(
            pi_user=self.settings.pi_user, pi_ip=self.settings.pi_ip
        )

        self.macbook_list.addItems(self._scan_folder(self.settings.watch_dir) or [""])

    def _scan_folder(self, path: str) -> list[str]:
        """Scan folder for files and return a list of names."""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    def log(self, message: str) -> None:
        self.log_box.append(message)

    def start_monitor(self) -> None:
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.log("⚠️ Already monitoring.")
            return
        self.log("🚀 Launching monitor thread...")
        self.status_label.setText("Status: Monitoring")
        self.monitor_thread = MonitorThread(
            self.settings.watch_dir,
            self.settings.pi_user,
            self.settings.pi_ip,
            self.settings.pi_movies,
            self.settings.pi_tv,
            self.settings.file_exts,
            self,  # Pass self to connect signal
        )
        self.monitor_thread.log_signal.connect(self.log)
        self.file_dropped.connect(
            self.monitor_thread.handle_dropped_file
        )  # Connect here
        self.monitor_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitor(self) -> None:
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.log("🛑 Monitor stopped.")
            self.status_label.setText("Status: Idle")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def open_settings(self) -> None:
        settings_window = SettingsWindow(self.settings)
        if settings_window.exec() == QDialog.accepted:
            self.macbook_list.clear()
            self.macbook_list.addItems(self._scan_folder(self.settings.watch_dir))

    def eventFilter(self, obj: object, event: QEvent) -> bool:
        if obj == self.macbook_list and event.type() == QEvent.Type.DragEnter:
            event: QDragEnterEvent = event
            if event.mimeData().hasUrls():
                event.accept()
                return True
        elif obj == self.macbook_list and event.type() == QEvent.Type.Drop:
            event: QDropEvent = event
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    dest_path = os.path.join(
                        self.settings.watch_dir, os.path.basename(file_path)
                    )
                    try:
                        shutil.copy2(file_path, dest_path)  # Copy file to watch_dir
                        self.macbook_list.clear()
                        self.macbook_list.addItems(
                            self._scan_folder(self.settings.watch_dir)
                        )
                        logger.log_signal.emit(
                            f"✅ Added {os.path.basename(file_path)} to MacBook Folder"
                        )
                    except Exception as e:
                        logger.log_signal.emit(
                            f"❌ Failed to add {os.path.basename(file_path)}: {e}"
                        )
            return True
        elif obj == self.pi_list and event.type() == QEvent.Type.DragEnter:
            event: QDragEnterEvent = event
            if event.mimeData().hasUrls():
                event.accept()
                return True
        elif obj == self.pi_list and event.type() == QEvent.Type.Drop:
            event: QDropEvent = event
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.file_dropped.emit(file_path, "movie")  # Default to movie
            return True
        return super().eventFilter(obj, event)

    def check_pi_connection(self, pi_user: str, pi_ip: str):
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
