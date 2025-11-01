from pydantic import BaseModel
import json
import os
from pathlib import Path
import sys
from src.utils.constants import CONFIG_JSON, SOFTARE_NAME
from src.utils.logging_signal import logger


class SettingsConfig(BaseModel):
    pi_user: str = ""
    pi_ip: str = ""
    pi_root_dir: str = "/"
    pi_movies: str = ""
    pi_tv: str = ""

    watch_dir: str = os.path.expanduser("~/Transfers")
    ssh_key_path: str = os.path.expanduser("~/.ssh/id_rsa")

    file_exts: set[str] = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".srt"}
    skip_files: set[str] = {".DS_Store", "Thumbs.db", ".Trashes"}
    last_modified: str = ""

    @classmethod
    def from_json(cls, data: dict) -> "SettingsConfig":
        # Convert lists from JSON to sets for file_exts and skip_files
        data = data.copy()
        if "file_exts" in data:
            data["file_exts"] = set(data["file_exts"])
        if "skip_files" in data:
            data["skip_files"] = set(data["skip_files"])
        return cls(**data)


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            # First, try loading from the user's local config directory
            local_config_path = Path.home() / f".{SOFTARE_NAME}" / CONFIG_JSON
            if local_config_path.exists() and local_config_path.is_file():
                config_data = cls._load_config(local_config_path)
                logger.success(f"Config: Loaded: {local_config_path}")
            else:
                # Determine config file path for loading
                if getattr(sys, "_MEIPASS", False):
                    base_path = Path(sys._MEIPASS)
                    config_path = base_path / f"src/config/{CONFIG_JSON}"
                else:
                    config_path = Path(__file__).parent / CONFIG_JSON
                # Load and validate config
                config_data = cls._load_config(config_path)
            cls._instance.config = SettingsConfig.from_json(config_data)
        return cls._instance

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        try:
            if config_path.exists() and config_path.is_file():
                with open(config_path, "r") as f:
                    return json.load(f)
            else:
                logger.warn(
                    f"Warning: {config_path} not found or is not a file, using empty defaults."
                )
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding {config_path}: {e}, using empty defaults.")
            return {}
        except Exception as e:
            logger.error(f"Error loading {config_path}: {e}, using empty defaults.")
            return {}

    @property
    def pi_user(self):
        return self.config.pi_user

    @property
    def pi_ip(self):
        return self.config.pi_ip

    @property
    def pi_root_dir(self):
        return self.config.pi_root_dir

    @property
    def pi_movies(self):
        return self.config.pi_movies

    @property
    def pi_tv(self):
        return self.config.pi_tv

    @property
    def file_exts(self):
        return self.config.file_exts

    @property
    def skip_files(self):
        return self.config.skip_files

    @property
    def ssh_key_path(self):
        return self.config.ssh_key_path

    @property
    def watch_dir(self):
        return self.config.watch_dir

    @property
    def last_modified(self):
        return self.config.last_modified

    def save_config(self, config_data: dict):
        # Determine save path in user directory
        save_dir = Path.home() / f".{SOFTARE_NAME}"
        save_dir.mkdir(exist_ok=True)
        # ~./PiSync/config.json
        config_path = save_dir / CONFIG_JSON

        # Convert sets back to lists for JSON serialization
        save_data = config_data.copy()
        if "file_exts" in save_data:
            save_data["file_exts"] = list(save_data["file_exts"])
        if "skip_files" in save_data:
            save_data["skip_files"] = list(save_data["skip_files"])

        try:
            with open(config_path, "w") as f:
                json.dump(save_data, f, indent=4)
        except Exception as e:
            logger.error(f"Settings: Failed: {config_path}: {e}")

    def is_valid(self) -> bool:
        """Check if critical settings are non-empty."""
        return all(
            [
                self.pi_user.strip(),
                self.pi_ip.strip(),
                self.pi_root_dir.strip(),
                self.pi_movies.strip(),
                self.pi_tv.strip(),
            ]
        )
