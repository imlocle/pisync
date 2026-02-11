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
            "local_watch_dir": self.local_watch_dir_input.text().rstrip("/").strip(),
            "remote_base_dir": self.remote_base_dir_input.text().rstrip("/").strip(),
            "ssh_key_path": self.ssh_key_path.text().strip(),
            "ssh_port": int(self.ssh_port_input.text().strip() or "22"),
            "auto_start_monitor": self.auto_start_monitor_checkbox.isChecked(),
            "delete_after_transfer": self.delete_after_transfer_checkbox.isChecked(),
            "stability_duration": float(self.stability_duration_input.text().strip() or "2.0"),
            "file_extensions": [
                ext.strip()
                for ext in self.file_extensions_input.toPlainText().split(",")
                if ext.strip()
            ],
            "skip_patterns": [
                f.strip()
                for f in self.skip_patterns_input.toPlainText().split(",")
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
        self.ssh_port_input = QLineEdit(str(self.settings.ssh_port))
        self.ssh_key_path = QLineEdit(self.settings.ssh_key_path)
        
        # ---- Paths --------------------------------------------------------
        self.local_watch_dir_input = QLineEdit(self.settings.local_watch_dir)
        self.remote_base_dir_input = QLineEdit(self.settings.remote_base_dir)
        
        # ---- Options ------------------------------------------------------
        self.auto_start_monitor_checkbox = QCheckBox()
        self.auto_start_monitor_checkbox.setChecked(
            getattr(self.settings, "auto_start_monitor", True)
        )
        
        self.delete_after_transfer_checkbox = QCheckBox()
        self.delete_after_transfer_checkbox.setChecked(
            self.settings.delete_after_transfer
        )
        
        self.stability_duration_input = QLineEdit(str(self.settings.stability_duration))

        # Set minimum width for text inputs
        for input_field in [
            self.pi_user_input,
            self.pi_ip_input,
            self.ssh_port_input,
            self.local_watch_dir_input,
            self.remote_base_dir_input,
            self.ssh_key_path,
            self.stability_duration_input,
        ]:
            input_field.setMinimumWidth(300)

        form.addRow("Pi User:", self.pi_user_input)
        form.addRow("Pi IP:", self.pi_ip_input)
        form.addRow("SSH Port:", self.ssh_port_input)
        form.addRow("SSH Key Path:", self.ssh_key_path)
        form.addRow("Local Watch Directory:", self.local_watch_dir_input)
        form.addRow("Remote Base Directory:", self.remote_base_dir_input)
        form.addRow("Auto Start Monitor:", self.auto_start_monitor_checkbox)
        form.addRow("Delete After Transfer:", self.delete_after_transfer_checkbox)
        form.addRow("Stability Duration (seconds):", self.stability_duration_input)

        # ---- File extensions / skip patterns ------------------------------
        self.file_extensions_input = QTextEdit(", ".join(sorted(self.settings.file_extensions)))
        self.file_extensions_input.setMaximumHeight(80)
        self.file_extensions_input.setAcceptRichText(False)
        self.file_extensions_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        self.skip_patterns_input = QTextEdit(", ".join(sorted(self.settings.skip_patterns)))
        self.skip_patterns_input.setMaximumHeight(80)
        self.skip_patterns_input.setAcceptRichText(False)
        self.skip_patterns_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        self.file_extensions_input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.skip_patterns_input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        form.addRow("File Extensions (comma separated):", self.file_extensions_input)
        form.addRow("Skip Patterns (comma separated):", self.skip_patterns_input)

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
