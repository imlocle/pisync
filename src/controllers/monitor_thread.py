from __future__ import annotations

import os
from typing import Optional

from paramiko import SFTPClient
from PySide6.QtCore import QThread, Signal

from src.config.settings import Settings
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.services.file_deletion_service import FileDeletionService
from src.services.movie_service import MovieService
from src.services.tv_service import TvService
from src.utils.logging_signal import logger


class MonitorThread(QThread):
    # Signal emitted after each file/folder is processed during scan
    scan_progress = Signal(str, int, int)  # item_name, current, total
    
    def __init__(
        self,
        settings: Settings,
        sftp_client: SFTPClient,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.sftp_client = sftp_client
        self._running = True

        self.file_monitor_repo: Optional[FileMonitorRepository] = None
        self.movie_service: Optional[MovieService] = None
        self.tv_service: Optional[TvService] = None

    def run(self) -> None:
        """
        Run the monitoring thread.
        
        Initializes services and starts file monitoring.
        """
        try:
            # Initialize services with simplified path mapping
            self.movie_service = MovieService(
                sftp=self.sftp_client,
                watch_dir=self.settings.local_watch_dir,
                pi_root_dir=self.settings.remote_base_dir,
            )

            self.tv_service = TvService(
                sftp=self.sftp_client,
                watch_dir=self.settings.local_watch_dir,
                pi_root_dir=self.settings.remote_base_dir,
            )

            deletion = FileDeletionService()

            self.file_monitor_repo = FileMonitorRepository(
                watch_dir=self.settings.local_watch_dir,
                movie_service=self.movie_service,
                tv_service=self.tv_service,
                deletion_service=deletion,
                file_exts=self.settings.file_extensions,
                stability_duration=self.settings.stability_duration,
            )

            self.file_monitor_repo.create_directories()
            self.file_monitor_repo.start_monitoring()

            while self._running:
                self.msleep(500)

            if self.file_monitor_repo:
                self.file_monitor_repo.stop_monitoring()

        except Exception as e:
            logger.error(f"MonitorThread: {e}")

    def stop(self) -> None:
        self._running = False

    def scan_and_transfer(self) -> None:
        """
        Scan watch directory and upload existing files before enabling live monitoring.
        
        This method processes any files that were added while the app was not running.
        It scans the Movies/ and TV_shows/ subdirectories and transfers their contents.
        """
        root = self.settings.local_watch_dir
        logger.start(f"Scan: Start: {root}")
        
        if not os.path.isdir(root):
            logger.info(f"{root} not found, skipping pre-scan.")
            return

        # Count total items first
        total_items = 0
        movies_dir = os.path.join(root, "Movies")
        tv_dir = os.path.join(root, "TV_shows")
        
        if os.path.isdir(movies_dir):
            total_items += len([f for f in os.listdir(movies_dir) if not f.startswith(".")])
        if os.path.isdir(tv_dir):
            total_items += len([f for f in os.listdir(tv_dir) if not f.startswith(".")])
        
        current_item = 0

        # Scan Movies directory
        if os.path.isdir(movies_dir):
            logger.info(f"Scan: Processing Movies directory")
            for movie_folder in sorted(os.listdir(movies_dir)):
                if movie_folder.startswith("."):
                    continue
                local_folder = os.path.join(movies_dir, movie_folder)
                if not os.path.isdir(local_folder):
                    continue
                
                current_item += 1
                self.scan_progress.emit(movie_folder, current_item, total_items)
                self.msleep(10)  # Small delay to allow GUI to update
                    
                try:
                    logger.info(f"Scan: Movies: {movie_folder}")
                    if self.movie_service and self.movie_service.transfer_movie_folder(local_folder):
                        # Delete local folder after successful transfer
                        if self.settings.delete_after_transfer and self.file_monitor_repo:
                            self.file_monitor_repo.deletion_service.delete_folder(local_folder)
                except Exception as e:
                    logger.error(f"Scan: Movie transfer failed: {local_folder} - {e}")

        # Scan TV_shows directory
        if os.path.isdir(tv_dir):
            logger.info(f"Scan: Processing TV_shows directory")
            for show in sorted(os.listdir(tv_dir)):
                if show.startswith("."):
                    continue
                show_path = os.path.join(tv_dir, show)
                if not os.path.isdir(show_path):
                    continue
                
                current_item += 1
                self.scan_progress.emit(show, current_item, total_items)
                self.msleep(10)  # Small delay to allow GUI to update
                    
                try:
                    logger.info(f"Scan: TV show: {show}")
                    if self.tv_service and self.tv_service.transfer_tv_folder(show_path):
                        # Delete only video files after successful transfer
                        if self.settings.delete_after_transfer and self.file_monitor_repo:
                            for root_dir, _, files in os.walk(show_path):
                                for f in files:
                                    if f.startswith("."):
                                        continue
                                    ext = os.path.splitext(f)[1].lower()
                                    if ext in self.settings.file_extensions:
                                        try:
                                            self.file_monitor_repo.deletion_service.delete_file(
                                                os.path.join(root_dir, f)
                                            )
                                        except Exception as e:
                                            logger.warn(f"Scan: Could not delete {f}: {e}")
                except Exception as e:
                    logger.error(f"Scan: TV show transfer failed: {show_path} - {e}")

        logger.success(f"Scan: Complete: {root}")
