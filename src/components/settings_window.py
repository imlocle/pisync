"""
Modern settings window with tabbed interface.

Organized into logical sections:
- Connection: SSH/SFTP settings
- Paths: Local and remote directories
- Behavior: Auto-start, delete after transfer, stability
- Files: Extensions and skip patterns
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFormLayout,
    QCheckBox,
    QMessageBox,
    QTabWidget,
    QWidget,
    QGroupBox,
    QFrame,
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
    """Modern settings dialog with tabbed interface."""

    def __init__(self, settings: Settings):
        super().__init__()
        self.setWindowTitle(f"{SOFTWARE_NAME} - Settings")
        self.setMinimumSize(600, 700)

        self.settings = settings

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self._setup_header(main_layout)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        self._setup_connection_tab()
        self._setup_paths_tab()
        self._setup_behavior_tab()
        self._setup_files_tab()

        main_layout.addWidget(self.tab_widget, stretch=1)

        # Footer with buttons
        self._setup_footer(main_layout)

        # Test connection on load
        self.test_connection()

    def _setup_header(self, layout: QVBoxLayout) -> None:
        """Create header with title and connection status."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-bottom: 1px solid #3e3e42;
                padding: 16px;
            }
        """)
        
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #ffffff;")
        header_layout.addWidget(title)

        # Connection status
        self.connection_status_label = QLabel("● Testing connection...")
        self.connection_status_label.setStyleSheet("color: #858585; font-weight: 500;")
        header_layout.addWidget(self.connection_status_label)

        # Last modified
        self.last_mod_label = QLabel()
        self.last_mod_label.setStyleSheet("color: #858585; font-size: 11px;")
        if self.settings.last_modified:
            self.last_mod_label.setText(f"Last modified: {self.settings.last_modified}")
        else:
            self.last_mod_label.setText("Configuration not yet saved")
        header_layout.addWidget(self.last_mod_label)

        layout.addWidget(header)

    def _setup_connection_tab(self) -> None:
        """Create connection settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # SSH Connection group
        ssh_group = QGroupBox("SSH Connection")
        ssh_layout = QFormLayout()
        ssh_layout.setSpacing(12)
        ssh_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.pi_user_input = QLineEdit(self.settings.pi_user)
        self.pi_user_input.setPlaceholderText("e.g., pi")
        
        self.pi_ip_input = QLineEdit(self.settings.pi_ip)
        self.pi_ip_input.setPlaceholderText("e.g., 192.168.1.100")
        
        self.ssh_port_input = QLineEdit(str(self.settings.ssh_port))
        self.ssh_port_input.setPlaceholderText("22")
        
        self.ssh_key_path = QLineEdit(self.settings.ssh_key_path)
        self.ssh_key_path.setPlaceholderText("e.g., ~/.ssh/id_rsa")

        ssh_layout.addRow("Username:", self.pi_user_input)
        ssh_layout.addRow("IP Address:", self.pi_ip_input)
        ssh_layout.addRow("SSH Port:", self.ssh_port_input)
        ssh_layout.addRow("SSH Key Path:", self.ssh_key_path)

        ssh_group.setLayout(ssh_layout)
        layout.addWidget(ssh_group)

        # Test connection button
        test_btn = QPushButton("🔌 Test Connection")
        test_btn.setObjectName("primary_btn")
        test_btn.clicked.connect(self.test_connection)
        test_btn.setMinimumHeight(36)
        layout.addWidget(test_btn)

        layout.addStretch()
        self.tab_widget.addTab(tab, "🔌 Connection")

    def _setup_paths_tab(self) -> None:
        """Create paths settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Local paths group
        local_group = QGroupBox("Local Paths")
        local_layout = QFormLayout()
        local_layout.setSpacing(12)
        local_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.local_watch_dir_input = QLineEdit(self.settings.local_watch_dir)
        self.local_watch_dir_input.setPlaceholderText("e.g., ~/Transfers")

        local_layout.addRow("Watch Directory:", self.local_watch_dir_input)
        local_group.setLayout(local_layout)
        layout.addWidget(local_group)

        # Remote paths group
        remote_group = QGroupBox("Remote Paths")
        remote_layout = QFormLayout()
        remote_layout.setSpacing(12)
        remote_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.remote_base_dir_input = QLineEdit(self.settings.remote_base_dir)
        self.remote_base_dir_input.setPlaceholderText("e.g., /mnt/external")

        remote_layout.addRow("Base Directory:", self.remote_base_dir_input)
        remote_group.setLayout(remote_layout)
        layout.addWidget(remote_group)

        # Info label
        info_label = QLabel(
            "💡 Tip: Local directory structure will be mirrored on the remote Pi"
        )
        info_label.setStyleSheet("color: #858585; padding: 8px; background-color: #252526; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📁 Paths")

    def _setup_behavior_tab(self) -> None:
        """Create behavior settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Monitoring group
        monitoring_group = QGroupBox("Monitoring Behavior")
        monitoring_layout = QFormLayout()
        monitoring_layout.setSpacing(12)
        monitoring_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.auto_start_monitor_checkbox = QCheckBox()
        self.auto_start_monitor_checkbox.setChecked(
            getattr(self.settings, "auto_start_monitor", True)
        )

        self.stability_duration_input = QLineEdit(str(self.settings.stability_duration))
        self.stability_duration_input.setPlaceholderText("2.0")

        monitoring_layout.addRow("Auto-start monitoring:", self.auto_start_monitor_checkbox)
        monitoring_layout.addRow("File stability duration (seconds):", self.stability_duration_input)

        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)

        # Transfer group
        transfer_group = QGroupBox("Transfer Behavior")
        transfer_layout = QFormLayout()
        transfer_layout.setSpacing(12)
        transfer_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.delete_after_transfer_checkbox = QCheckBox()
        self.delete_after_transfer_checkbox.setChecked(
            self.settings.delete_after_transfer
        )

        transfer_layout.addRow("Delete local files after transfer:", self.delete_after_transfer_checkbox)

        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)

        # Info labels
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        stability_info = QLabel(
            "💡 File stability: Wait time to ensure files are completely written before transfer"
        )
        stability_info.setStyleSheet("color: #858585; padding: 8px; background-color: #252526; border-radius: 4px;")
        stability_info.setWordWrap(True)
        info_layout.addWidget(stability_info)

        delete_info = QLabel(
            "⚠️ Delete after transfer: Use with caution! Files will be permanently deleted after successful transfer"
        )
        delete_info.setStyleSheet("color: #ce9178; padding: 8px; background-color: #252526; border-radius: 4px;")
        delete_info.setWordWrap(True)
        info_layout.addWidget(delete_info)

        layout.addLayout(info_layout)
        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ Behavior")

    def _setup_files_tab(self) -> None:
        """Create file filtering settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # File extensions group
        extensions_group = QGroupBox("File Extensions to Monitor")
        extensions_layout = QVBoxLayout()
        extensions_layout.setSpacing(8)

        extensions_label = QLabel("Comma-separated list of file extensions:")
        extensions_label.setStyleSheet("color: #858585;")
        extensions_layout.addWidget(extensions_label)

        self.file_extensions_input = QTextEdit(", ".join(sorted(self.settings.file_extensions)))
        self.file_extensions_input.setMaximumHeight(100)
        self.file_extensions_input.setAcceptRichText(False)
        self.file_extensions_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.file_extensions_input.setPlaceholderText(".mkv, .mp4, .avi, .srt")
        extensions_layout.addWidget(self.file_extensions_input)

        extensions_group.setLayout(extensions_layout)
        layout.addWidget(extensions_group)

        # Skip patterns group
        skip_group = QGroupBox("Skip Patterns")
        skip_layout = QVBoxLayout()
        skip_layout.setSpacing(8)

        skip_label = QLabel("Comma-separated list of patterns to skip:")
        skip_label.setStyleSheet("color: #858585;")
        skip_layout.addWidget(skip_label)

        self.skip_patterns_input = QTextEdit(", ".join(sorted(self.settings.skip_patterns)))
        self.skip_patterns_input.setMaximumHeight(100)
        self.skip_patterns_input.setAcceptRichText(False)
        self.skip_patterns_input.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.skip_patterns_input.setPlaceholderText(".DS_Store, Thumbs.db, ._*")
        skip_layout.addWidget(self.skip_patterns_input)

        skip_group.setLayout(skip_layout)
        layout.addWidget(skip_group)

        # Info label
        info_label = QLabel(
            "💡 Tip: Hidden files (starting with .) are automatically skipped"
        )
        info_label.setStyleSheet("color: #858585; padding: 8px; background-color: #252526; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📄 Files")

    def _setup_footer(self, layout: QVBoxLayout) -> None:
        """Create footer with action buttons."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border-top: 1px solid #3e3e42;
                padding: 16px;
            }
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setSpacing(8)

        footer_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setMinimumWidth(140)
        self.save_btn.clicked.connect(self.save_settings)

        footer_layout.addWidget(self.cancel_btn)
        footer_layout.addWidget(self.save_btn)

        layout.addWidget(footer)

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
            # Validate configuration
            validated_config = SettingsConfig.from_json(config_data)
            
            # Save to file
            self.settings.save_config(config_data)
            
            # Update in-memory config
            self.settings.config = validated_config

            logger.success("Settings saved successfully")
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
            self.tab_widget.setCurrentIndex(0)  # Switch to Connection tab
            self.pi_ip_input.setFocus()
            
        except SSHKeyValidationError as e:
            QMessageBox.warning(
                self,
                "Invalid SSH Key",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            self.tab_widget.setCurrentIndex(0)  # Switch to Connection tab
            self.ssh_key_path.setFocus()
            
        except PathValidationError as e:
            QMessageBox.warning(
                self,
                "Invalid Path",
                f"{e.message}\n\n{e.details if e.details else ''}",
                QMessageBox.StandardButton.Ok
            )
            self.tab_widget.setCurrentIndex(1)  # Switch to Paths tab
            
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
        self.connection_status_label.setText("● Testing connection...")
        self.connection_status_label.setStyleSheet("color: #ce9178; font-weight: 500;")
        
        connection_manager_service = ConnectionManagerService(self.settings)

        if connection_manager_service.test_connection():
            self.connection_status_label.setText("● Connected successfully")
            self.connection_status_label.setStyleSheet("color: #4ec9b0; font-weight: 500;")
        else:
            self.connection_status_label.setText("● Connection failed")
            self.connection_status_label.setStyleSheet("color: #f48771; font-weight: 500;")
