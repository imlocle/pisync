from __future__ import annotations
import os
from send2trash import send2trash
from src.utils.logging_signal import logger


class FileDeletionService:
    """Move files/folders to the trash (cross-platform when using send2trash)."""

    def delete_file(self, file_path: str) -> bool:
        try:
            if os.path.isfile(file_path):
                send2trash(file_path)
                logger.log_signal.emit(f"✅ Complete: Transfer: Trash: {file_path}")
                return True
            return False
        except Exception as e:
            raise

    def delete_folder(self, folder_path: str) -> bool:
        try:
            if os.path.isdir(folder_path):
                send2trash(folder_path)
                return True
            return False
        except Exception:
            raise
