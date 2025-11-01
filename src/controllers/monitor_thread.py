from __future__ import annotations
from typing import Optional
from PySide6.QtCore import QThread
from paramiko import SFTPClient
import os
from src.config.settings import Settings
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.services.file_classifier_service import FileClassifierService
from src.services.file_deletion_service import FileDeletionService
from src.services.movie_service import MovieService
from src.services.tv_service import TvService
from src.utils.logging_signal import logger


class MonitorThread(QThread):
    def __init__(
        self,
        settings: Settings,
        sftp_client: SFTPClient,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.sftp_client = sftp_client
        self._running = True

        self.classifier = FileClassifierService()
        self.file_monitor_repo: Optional[FileMonitorRepository] = None
        self.movie_service: Optional[MovieService] = None
        self.tv_service: Optional[TvService] = None

    def run(self) -> None:
        try:
            self.movie_service = MovieService(
                sftp=self.sftp_client,
                watch_dir=self.settings.watch_dir,
                pi_root_dir=f"{self.settings.pi_root_dir}/{self.settings.pi_movies}",
            )

            self.tv_service = TvService(
                sftp=self.sftp_client,
                watch_dir=self.settings.watch_dir,
                pi_root_dir=self.settings.pi_root_dir,
            )

            deletion = FileDeletionService()

            self.file_monitor_repo = FileMonitorRepository(
                watch_dir=self.settings.watch_dir,
                classifier_service=self.classifier,
                movie_service=self.movie_service,
                tv_service=self.tv_service,
                deletion_service=deletion,
                file_exts=self.settings.file_exts,
            )

            self.file_monitor_repo.create_directories()
            self.file_monitor_repo.start_monitoring()

            while self._running:
                self.msleep(500)

            self.file_monitor_repo.stop_monitoring()

        except Exception as e:
            logger.error(f"MonitorThread: {e}")

    def stop(self) -> None:
        self._running = False

    def scan_and_transfer(self) -> None:
        """
        Scan ~/Transfers and upload existing files before enabling live monitoring.
        Behavior:
         - For movie folders under ~/Transfers/Movies -> upload entire folder via MovieService
         - For TV_shows -> upload folder structure via TvService
         - Skips hidden/system files
        """
        root = self.settings.watch_dir
        logger.start(f"Scan: Start: {root}")
        if not os.path.isdir(root):
            logger.info(f"{root} not found, skipping pre-scan.")
            return

        for top, dirs, files in os.walk(root):
            # We want to process at top-level folder level (e.g. Movies/<movie_folder> or TV_shows/<show>/...)
            # Skip nested traversal here; only handle actionable items when we discover folders/files
            break

        # Walk immediate children of root
        for entry in sorted(os.listdir(root)):
            if entry.startswith("."):
                continue
            entry_path = os.path.join(root, entry)
            # If top-level is Movies or TV_shows, iterate inside those
            if entry == self.settings.pi_movies:
                # iterate each movie folder
                for movie_folder in sorted(os.listdir(entry_path)):
                    if movie_folder.startswith("."):
                        continue
                    local_folder = os.path.join(entry_path, movie_folder)
                    try:
                        logger.info(f"Scan: Movies: {movie_folder}")
                        if self.movie_service.transfer_movie_folder(local_folder):
                            # delete local folder
                            # deletion via repository deletion service if available
                            if self.file_monitor_repo:
                                self.file_monitor_repo.deletion_service.delete_folder(
                                    local_folder
                                )
                    except Exception as e:
                        logger.error(
                            f"Pre-scan movie transfer failed: {local_folder} - {e}\n"
                        )

            elif entry == self.settings.pi_tv:
                # iterate each show (show -> seasons -> files)
                for show in sorted(os.listdir(entry_path)):
                    if show.startswith("."):
                        continue
                    show_path = os.path.join(entry_path, show)
                    # transfer recursively using tv_service
                    try:
                        logger.info(f"Scan: TV show: {show}")
                        if self.tv_service.transfer_tv_folder(show_path):
                            # delete only video files
                            if self.file_monitor_repo:
                                for root_dir, _, files in os.walk(show_path):
                                    for f in files:
                                        if f.startswith("."):
                                            continue
                                        ext = os.path.splitext(f)[1].lower()
                                        if ext in self.settings.file_exts:
                                            self.file_monitor_repo.deletion_service.delete_file(
                                                os.path.join(root_dir, f)
                                            )
                    except Exception as e:
                        logger.error(f"Scan: TV shows: Failed: {show_path} - {e}")
            else:
                # If someone dropped a folder directly under ~/Transfers (not Movies/TV_shows),
                # try to classify and process accordingly.
                if os.path.isdir(entry_path):
                    try:
                        kind = self.classifier.classify_folder(entry_path)
                        if kind == "movie":
                            if self.movie_service.transfer_movie_folder(entry_path):
                                if self.file_monitor_repo:
                                    self.file_monitor_repo.deletion_service.delete_folder(
                                        entry_path
                                    )
                        else:
                            if self.tv_service.transfer_tv_folder(entry_path):
                                if self.file_monitor_repo:
                                    for root_dir, _, files in os.walk(entry_path):
                                        for f in files:
                                            if f.startswith("."):
                                                continue
                                            ext = os.path.splitext(f)[1].lower()
                                            if ext in self.settings.file_exts:
                                                self.file_monitor_repo.deletion_service.delete_file(
                                                    os.path.join(root_dir, f)
                                                )
                    except Exception as e:
                        logger.error(f"Scan: Generic: Failed: {entry_path} - {e}")

        logger.success(f"Scan: Complete: {root}")
