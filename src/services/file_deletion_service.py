from __future__ import annotations
import os
from send2trash import send2trash
from src.utils.logging_signal import logger
from src.models.errors import FileDeletionError


class FileDeletionService:
    """Move files/folders to the trash (cross-platform when using send2trash)."""

    def delete_file(self, file_path: str) -> bool:
        """
        Move file to trash (recoverable deletion).
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            FileDeletionError: If deletion fails
        """
        try:
            if not os.path.exists(file_path):
                logger.warn(f"Deletion: File not found: {file_path}")
                return False
                
            if not os.path.isfile(file_path):
                logger.warn(f"Deletion: Not a file: {file_path}")
                return False
                
            send2trash(file_path)
            logger.trash(f"Transfer: Completed: {file_path}")
            return True
            
        except Exception as e:
            raise FileDeletionError(
                f"Failed to delete file",
                path=file_path,
                details=str(e)
            )

    def delete_folder(self, folder_path: str) -> bool:
        """
        Move folder to trash (recoverable deletion).
        
        Args:
            folder_path: Path to folder to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            FileDeletionError: If deletion fails
        """
        try:
            if not os.path.exists(folder_path):
                logger.warn(f"Deletion: Folder not found: {folder_path}")
                return False
                
            if not os.path.isdir(folder_path):
                logger.warn(f"Deletion: Not a folder: {folder_path}")
                return False
                
            send2trash(folder_path)
            logger.trash(f"Deletion: Folder moved to trash: {folder_path}")
            return True
            
        except Exception as e:
            raise FileDeletionError(
                f"Failed to delete folder",
                path=folder_path,
                details=str(e)
            )
