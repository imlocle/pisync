from pydantic import BaseModel, validator, field_validator
import json
import os
import ipaddress
from pathlib import Path
import sys
from src.utils.constants import CONFIG_JSON, SOFTWARE_NAME
from src.utils.logging_signal import logger
from src.models.errors import (
    ConfigurationLoadError,
    ConfigurationSaveError,
    InvalidConfigurationError,
    IPAddressValidationError,
    PathValidationError,
    SSHKeyValidationError,
)


class SettingsConfig(BaseModel):
    pi_user: str = ""
    pi_ip: str = ""
    pi_root_dir: str = "/"
    pi_movies: str = ""
    pi_tv: str = ""

    watch_dir: str = os.path.expanduser("~/Transfers")
    ssh_key_path: str = os.path.expanduser("~/.ssh/id_rsa")
    auto_start_monitor: bool = True
    file_exts: set[str] = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".srt", ".nfo"}
    skip_files: set[str] = {".DS_Store", "Thumbs.db", ".Trashes"}
    last_modified: str = ""

    @field_validator('pi_ip')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate IP address format if not empty."""
        if v and v.strip():
            try:
                ipaddress.ip_address(v.strip())
            except ValueError:
                raise IPAddressValidationError(
                    f"Invalid IP address format: {v}",
                    details="Please enter a valid IPv4 or IPv6 address"
                )
        return v

    @field_validator('ssh_key_path')
    @classmethod
    def validate_ssh_key(cls, v: str) -> str:
        """Validate SSH key path if not empty."""
        if v and v.strip():
            expanded_path = os.path.expanduser(v.strip())
            if not os.path.exists(expanded_path):
                # Don't raise error, just log warning (key might not exist yet)
                logger.warn(f"SSH key not found at: {expanded_path}")
            elif not os.path.isfile(expanded_path):
                raise SSHKeyValidationError(
                    f"SSH key path is not a file: {expanded_path}",
                    details="Please provide a path to a valid SSH private key file"
                )
        return v

    @field_validator('watch_dir')
    @classmethod
    def validate_watch_dir(cls, v: str) -> str:
        """Validate watch directory path."""
        if v and v.strip():
            expanded_path = os.path.expanduser(v.strip())
            # Create directory if it doesn't exist
            try:
                os.makedirs(expanded_path, exist_ok=True)
            except Exception as e:
                raise PathValidationError(
                    f"Cannot create watch directory: {expanded_path}",
                    details=str(e)
                )
        return v

    @field_validator('pi_root_dir')
    @classmethod
    def validate_pi_root_dir(cls, v: str) -> str:
        """Validate Pi root directory format."""
        if v and v.strip():
            # Ensure it starts with / for absolute path
            if not v.strip().startswith('/'):
                raise PathValidationError(
                    f"Pi root directory must be an absolute path: {v}",
                    details="Path should start with /"
                )
        return v

    @classmethod
    def from_json(cls, data: dict) -> "SettingsConfig":
        """
        Create SettingsConfig from JSON data.

        Args:
            data: Dictionary from JSON config file

        Returns:
            SettingsConfig instance

        Raises:
            InvalidConfigurationError: If validation fails
        """
        # Convert lists from JSON to sets for file_exts and skip_files
        data = data.copy()
        if "file_exts" in data:
            data["file_exts"] = set(data["file_exts"])
        if "skip_files" in data:
            data["skip_files"] = set(data["skip_files"])
        data["auto_start_monitor"] = data.get("auto_start_monitor", True)

        try:
            return cls(**data)
        except Exception as e:
            raise InvalidConfigurationError(
                "Failed to parse configuration",
                details=str(e)
            )



class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            # First, try loading from the user's local config directory
            local_config_path = Path.home() / f".{SOFTWARE_NAME}" / CONFIG_JSON
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
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationLoadError: If loading fails critically
        """
        try:
            if config_path.exists() and config_path.is_file():
                with open(config_path, "r") as f:
                    data = json.load(f)
                    logger.info(f"Config: Loaded from {config_path}")
                    return data
            else:
                logger.warn(
                    f"Config: File not found: {config_path}, using defaults"
                )
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Config: Invalid JSON in {config_path}: {e}")
            raise ConfigurationLoadError(
                f"Invalid JSON in configuration file",
                details=f"File: {config_path}, Error: {str(e)}"
            )
        except PermissionError as e:
            logger.error(f"Config: Permission denied: {config_path}")
            raise ConfigurationLoadError(
                f"Cannot read configuration file",
                details=f"Permission denied: {config_path}"
            )
        except Exception as e:
            logger.error(f"Config: Error loading {config_path}: {e}")
            # Return empty dict for non-critical errors
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
    def auto_start_monitor(self):
        return self.config.auto_start_monitor

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

    def save_config(self, config_data: dict) -> None:
        """
        Save configuration to JSON file.

        Args:
            config_data: Configuration dictionary to save

        Raises:
            ConfigurationSaveError: If save fails
        """
        # Determine save path in user directory
        save_dir = Path.home() / f".{SOFTWARE_NAME}"

        try:
            save_dir.mkdir(exist_ok=True)
        except Exception as e:
            raise ConfigurationSaveError(
                f"Cannot create config directory: {save_dir}",
                details=str(e)
            )

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
            logger.success(f"Config: Saved to {config_path}")
        except PermissionError as e:
            raise ConfigurationSaveError(
                f"Permission denied writing config",
                details=f"Path: {config_path}"
            )
        except Exception as e:
            raise ConfigurationSaveError(
                f"Failed to save configuration",
                details=f"Path: {config_path}, Error: {str(e)}"
            )


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
