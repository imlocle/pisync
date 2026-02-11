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
    QCheckBox,
    QMessageBox,
)
from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt

from src.config.settings import Settings, SettingsConfig
from src.services.connection_manager_service import ConnectionManagerService
from src.utils.constants import SOFTWARE_NAME
from src.utils.logging_signal import logger
from src.models.errors import (
    ConfigurationSaveError,
    InvalidConfigurationError,
    IPAddressValidationError,
    PathValidationError,
    SSHKeyValidationError,
)


class SettingsWindow(QDialog):
    """Settings dialog - now also displays the last-modified date of the config file."""

    def __init__(
        self,
        settings: Settings,
    ):
        super().__init__()
        self.setWindowTitle(f"{SOFTWARE_NAME} Settings")
        self.setMinimumSize(420, 650)

        self.settings = settings

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
        """Collect UI values, validate, and save configuration."""

        config_data = {
            "pi_user": self.pi_user_input.text().strip(),
            "pi_ip": self.pi_ip_input.text().strip(),
            "pi_root_dir": self.pi_root_dir_input.text().rstrip("/").strip(),
            "pi_movies": self.pi_movies_input.text().strip(),
            "pi_tv": self.pi_tv_input.text().strip(),
            "watch_dir": self.watch_dir_input.text().rstrip("/").strip(),
            "ssh_key_path": self.ssh_key_path.text().strip(),
            "auto_start_monitor": self.auto_start_monitor_checkbox.isChecked(),
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

        try:
            # Validate configuration by creating SettingsConfig
            validated_config = SettingsConfig.from_json(config_data)
            
            # Save to file
            self.settings.save_config(config_data)
            
            # Update in-memory config
            self.settings.config = validated_config

            logger.success("Settings: Saved")
            QMessageBox.information(
                self,
                "Settings Saved",
                "Your settings have been saved successfully.",
                QMessageBox.StandardButton.Ok
            )
            self.accept()
            
        except IPAddressValidationError as e:
            QMessageBox.warning(
                self,
                "Invalid IP Address",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            self.pi_ip_input.setFocus()
            
        except SSHKeyValidationError as e:
            QMessageBox.warning(
                self,
                "Invalid SSH Key",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            self.ssh_key_path.setFocus()
            
        except PathValidationError as e:
            QMessageBox.warning(
                self,
                "Invalid Path",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            
        except InvalidConfigurationError as e:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            
        except ConfigurationSaveError as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            
        except Exception as e:
            logger.error(f"Settings: Unexpected error: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An unexpected error occurred while saving settings:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def test_connection(self):
        """Test connection to Raspberry Pi."""
        connection_manager_service = ConnectionManagerService(self.settings)

        if connection_manager_service.test_connection():
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
        self.auto_start_monitor_checkbox = QCheckBox()
        self.auto_start_monitor_checkbox.setChecked(
            getattr(self.settings, "auto_start_monitor", True)
        )

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
        form.addRow("Auto Start Monitor:", self.auto_start_monitor_checkbox)

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
        self.test_connection_btn = QPushButton("🌐")
        self.test_connection_btn.setToolTip("Test Connection")

        self.save_btn = QPushButton("💾")
        self.save_btn.setToolTip("Save")

        self.cancel_btn = QPushButton("🚫")
        self.cancel_btn.setToolTip("Cancel")

        btn_layout.addWidget(self.test_connection_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
