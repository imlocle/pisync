from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QFormLayout,
)
from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt

from src.config.settings import Settings, SettingsConfig
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.constants import SOFTARE_NAME
from src.utils.logging_signal import logger


class SettingsWindow(QDialog):
    """Settings dialog - now also displays the last-modified date of the config file."""

    def __init__(
        self, settings: Settings, connection_manager_service: ConnectionManagerService
    ):
        super().__init__()
        self.setWindowTitle(f"{SOFTARE_NAME} Settings")
        self.setMinimumSize(420, 650)

        self.settings = settings
        self.connection_manager_service = connection_manager_service

        # === 1. Layout Setup ===
        main_layout = QVBoxLayout(self)
        self._setup_form(main_layout)
        self._setup_labels(main_layout)
        self._setup_buttons(main_layout)

        # === 2. Connect Signals ===
        self._setup_connections()

        # === 3. Test SSH Connection ===
        self.test_connection()

    def save_settings(self):
        """Collect UI values, write the config, and refresh the date."""

        config_data = {
            "pi_user": self.pi_user_input.text().strip(),
            "pi_ip": self.pi_ip_input.text().strip(),
            "pi_root_dir": self.pi_root_dir_input.text().rstrip("/").strip(),
            "pi_movies": self.pi_movies_input.text().strip(),
            "pi_tv": self.pi_tv_input.text().strip(),
            "watch_dir": self.watch_dir_input.text().rstrip("/").strip(),
            "ssh_key_path": self.ssh_key_path.text().strip(),
            "file_exts": [
                ext.strip()
                for ext in self.file_exts_input.toPlainText().split(",")
                if ext.strip()
            ],
            "skip_files": [
                f.strip()
                for f in self.skip_files_input.toPlainText().split(",")
                if f.strip()
            ],
            "last_modified": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        }

        self.settings.save_config(config_data)
        self.settings.config = SettingsConfig.from_json(config_data)

        logger.success("Settings: Saved")
        self.accept()

    def test_connection(self):
        if self.connection_manager_service.test_connection():
            self.connection_status_label.setText("Connection: ✅")
        else:
            self.connection_status_label.setText("Connection: ❌")

    def _setup_connections(self):
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
        self.test_connection_btn.clicked.connect(self.test_connection)

    def _setup_form(self, layout: QVBoxLayout) -> None:
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # ---- Pi connection ------------------------------------------------
        self.pi_user_input = QLineEdit(self.settings.pi_user)
        self.pi_ip_input = QLineEdit(self.settings.pi_ip)
        self.pi_root_dir_input = QLineEdit(self.settings.pi_root_dir)
        self.pi_movies_input = QLineEdit(self.settings.pi_movies)
        self.pi_tv_input = QLineEdit(self.settings.pi_tv)
        self.watch_dir_input = QLineEdit(self.settings.watch_dir)
        self.ssh_key_path = QLineEdit(self.settings.ssh_key_path)

        # Set minimum width for text inputs (e.g., 300 pixels)
        for input_field in [
            self.pi_user_input,
            self.pi_ip_input,
            self.pi_root_dir_input,
            self.pi_movies_input,
            self.pi_tv_input,
            self.watch_dir_input,
            self.ssh_key_path,
        ]:
            input_field.setMinimumWidth(300)

        form.addRow("Pi User:", self.pi_user_input)
        form.addRow("Pi IP:", self.pi_ip_input)
        form.addRow("Pi Root Directory:", self.pi_root_dir_input)
        form.addRow("Pi Movies Path:", self.pi_movies_input)
        form.addRow("Pi TV Path:", self.pi_tv_input)
        form.addRow("Local Watch Directory:", self.watch_dir_input)
        form.addRow("Local SSH Key Path:", self.ssh_key_path)

        # ---- File extensions / skip files --------------------------------
        self.file_exts_input = QTextEdit(", ".join(sorted(self.settings.file_exts)))
        self.file_exts_input.setMaximumHeight(80)
        self.file_exts_input.setAcceptRichText(False)
        self.file_exts_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        self.skip_files_input = QTextEdit(", ".join(sorted(self.settings.skip_files)))
        self.skip_files_input.setMaximumHeight(80)
        self.skip_files_input.setAcceptRichText(False)
        self.skip_files_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        self.file_exts_input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.skip_files_input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        form.addRow("File Extensions (comma separated):", self.file_exts_input)
        form.addRow("Skip Files (comma separated):", self.skip_files_input)

        layout.addLayout(form)

    def _setup_labels(self, layout: QVBoxLayout):
        self.last_mod_label = QLabel()
        self.last_mod_label.setStyleSheet("color: #555; font-style: italic;")
        if self.settings.last_modified:
            self.last_mod_label.setText(f"Last Modified: {self.settings.last_modified}")
        else:
            self.last_mod_label.setText("Last Modified: Config file not yet created")
        layout.addWidget(self.last_mod_label)

        self.connection_status_label = QLabel("Connection: ")
        self.connection_status_label.setStyleSheet("color: #555; font-style: italic;")
        layout.addWidget(self.connection_status_label)

    def _setup_buttons(self, layout: QVBoxLayout):
        btn_layout = QHBoxLayout()
        self.test_connection_btn = QPushButton("Test Connection")
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(self.test_connection_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
