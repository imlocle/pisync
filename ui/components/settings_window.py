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
from PySide6.QtCore import QDateTime, Qt
from pathlib import Path

from src.config.settings import Settings, SettingsConfig
from src.utils.logging_signal import logger


class SettingsWindow(QDialog):
    """Settings dialog – now also displays the last-modified date of the config file."""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("PiSync Settings")
        self.setMinimumSize(420, 560)

        # ------------------------------------------------------------------
        # Main layout
        # ------------------------------------------------------------------
        main_layout = QVBoxLayout(self)

        # ------------------------------------------------------------------
        # Form for the editable fields
        # ------------------------------------------------------------------
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # ---- Pi connection ------------------------------------------------
        self.pi_user_input = QLineEdit(settings.pi_user)
        self.pi_ip_input = QLineEdit(settings.pi_ip)
        self.pi_movies_input = QLineEdit(settings.pi_movies)
        self.pi_tv_input = QLineEdit(settings.pi_tv)
        self.watch_dir_input = QLineEdit(settings.watch_dir)

        form.addRow("Pi User:", self.pi_user_input)
        form.addRow("Pi IP:", self.pi_ip_input)
        form.addRow("Pi Movies Path:", self.pi_movies_input)
        form.addRow("Pi TV Path:", self.pi_tv_input)
        form.addRow("Watch Directory:", self.watch_dir_input)

        # ---- File extensions / skip files --------------------------------
        self.file_exts_input = QTextEdit("\n".join(settings.file_exts))
        self.file_exts_input.setMaximumHeight(80)
        self.skip_files_input = QTextEdit("\n".join(settings.skip_files))
        self.skip_files_input.setMaximumHeight(80)

        form.addRow("File Extensions (one per line):", self.file_exts_input)
        form.addRow("Skip Files (one per line):", self.skip_files_input)

        main_layout.addLayout(form)

        # ------------------------------------------------------------------
        # Last-modified date label (read-only)
        # ------------------------------------------------------------------
        self.last_mod_label = QLabel()
        self.last_mod_label.setStyleSheet("color: #555; font-style: italic;")
        self._update_last_modified()
        main_layout.addWidget(self.last_mod_label)

        # ------------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------------
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        # ------------------------------------------------------------------
        # Connections
        # ------------------------------------------------------------------
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)

    # ----------------------------------------------------------------------
    # Helper: refresh the “last modified” text
    # ----------------------------------------------------------------------
    def _update_last_modified(self):
        """Show the modification timestamp of the *active* config file."""
        # The config is always saved to ~/.PiSync/config.json
        cfg_path = Path.home() / ".PiSync" / "config.json"

        if cfg_path.is_file():
            mtime = cfg_path.stat().st_mtime
            dt = QDateTime.fromSecsSinceEpoch(int(mtime))
            # Human-readable format (e.g. “2025-10-20 19:42:13”)
            pretty = dt.toString("yyyy-MM-dd hh:mm:ss")
            self.last_mod_label.setText(f"Config last modified: {pretty}")
        else:
            self.last_mod_label.setText("Config file not yet created")

    # ----------------------------------------------------------------------
    # Save button handler
    # ----------------------------------------------------------------------
    def save_settings(self):
        """Collect UI values, write the config, and refresh the date."""
        config_data = {
            "pi_user": self.pi_user_input.text(),
            "pi_ip": self.pi_ip_input.text(),
            "pi_movies": self.pi_movies_input.text(),
            "pi_tv": self.pi_tv_input.text(),
            "watch_dir": self.watch_dir_input.text(),
            "file_exts": [
                ext.strip()
                for ext in self.file_exts_input.toPlainText().split("\n")
                if ext.strip()
            ],
            "skip_files": [
                f.strip()
                for f in self.skip_files_input.toPlainText().split("\n")
                if f.strip()
            ],
        }

        # Persist to ~/.PiSync/config.json
        self.settings.save_config(config_data)

        # Update the singleton *in-memory* model
        self.settings.config = SettingsConfig.from_json(config_data)

        # Refresh the timestamp label (the file was just written)
        self._update_last_modified()

        logger.log_signal.emit("Settings saved successfully")
        self.accept()
