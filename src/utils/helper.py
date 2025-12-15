import os
import sys
from pathlib import Path
from src.utils.logging_signal import logger
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtCore import Qt


def get_path(path_base: str) -> Path:
    """
    Get a path relative to the base directory, adjusting for PyInstaller bundling or development environment.

    Args:
        path_base (str): The relative path to append to the base directory.

    Returns:
        Path: The constructed absolute path.

    Notes:
        - In a PyInstaller bundle, uses sys._MEIPASS as the base.
        - In development, uses the directory containing main.py as the base.
    """
    if getattr(sys, "_MEIPASS", False):
        base_path = Path(sys._MEIPASS)
        full_path = base_path / path_base
        return full_path
    else:
        # In development, use the directory containing main.py as the base
        try:
            main_script = Path("main.py").resolve()
            if not main_script.exists():
                raise FileNotFoundError("main.py not found in current directory")
            base_path = main_script.parent
            full_path = base_path / path_base
            return full_path
        except (FileNotFoundError, Exception) as e:
            logger.error(f"Error determining development path: {e}")
            # Fallback to current file's parent directory as a last resort
            base_path = Path(__file__).parent
            full_path = base_path / path_base
            logger.info(f"Fallback to current file path: {full_path}")
            return full_path


def rounded_icon(path: str, radius: int = 15) -> QIcon:
    pix = QPixmap(path)
    size = pix.size()
    rounded = QPixmap(size)
    rounded.fill(Qt.GlobalColor.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(pix)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(pix.rect(), radius, radius)
    painter.end()
    return QIcon(rounded)


def format_size(num_bytes: int) -> str:
    """
    Convert a file size in bytes into a human-readable string.
    Always uses one decimal place.

    Examples:
        1024 -> "1.0 KB"
        1048576 -> "1.0 MB"
        450000000 -> "429.2 MB"
    """
    try:
        if num_bytes is None:
            return "0 B"
        if num_bytes < 0:
            return f"{num_bytes} B"

        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(num_bytes)
        index = 0

        while size >= 1024 and index < len(units) - 1:
            size /= 1024.0
            index += 1

        return f"{size:.1f} {units[index]}"

    except Exception:
        return f"{num_bytes} B"


def map_local_to_remote(local_path: str, watch_dir: str, pi_root_dir: str) -> str:
    local_path = os.path.abspath(local_path)
    watch_dir = os.path.abspath(watch_dir)
    rel = os.path.relpath(local_path, watch_dir)
    return os.path.join(pi_root_dir, rel).replace("\\", "/")
