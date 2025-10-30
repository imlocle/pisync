from __future__ import annotations
from typing import Set, Optional, Tuple
from PySide6.QtCore import QThread
import paramiko
import os
from src.repositories.file_monitor_repository import FileMonitorRepository
from src.services.file_classifier_service import FileClassifierService
from src.services.file_deletion_service import FileDeletionService
from src.services.movie_service import MovieService
from src.services.tv_service import TvService
from src.utils.logging_signal import logger


class MonitorThread(QThread):
    def __init__(
        self,
        watch_dir: str,
        pi_user: str,
        pi_ip: str,
        pi_root_dir: str,
        pi_movies: str,
        pi_tv: str,
        file_exts: Set[str],
        main_window,
        sftp_client: Optional[paramiko.SFTPClient] = None,
    ) -> None:
        super().__init__()
        self.watch_dir = watch_dir
        self.pi_user = pi_user
        self.pi_ip = pi_ip
        self.pi_root_dir = pi_root_dir
        self.pi_movies = pi_movies
        self.pi_tv = pi_tv
        self.file_exts = file_exts
        self.main_window = main_window

        self._running = True
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = sftp_client
        self.file_monitor_repo: Optional[FileMonitorRepository] = None
        self.movie_service: Optional[MovieService] = None
        self.tv_service: Optional[TvService] = None

    def run(self) -> None:
        try:
            # Establish sftp if not provided
            if self.sftp_client is None:
                logger.info(f"Connecting to {self.pi_ip}...")
                self.ssh_client, self.sftp_client = self._connect_sftp(
                    self.pi_ip, self.pi_user
                )
                if not self.sftp_client:
                    logger.error("SFTP connection failed; aborting monitor.")
                    return
            else:
                # If we got sftp_client from main window, try to create an ssh client wrapper for cleanup later.
                try:
                    # we still want an ssh client for closing on shutdown, but can't reliably derive one from SFTP,
                    # so we leave ssh_client as None and only close sftp_client on finish if provided by main.
                    pass
                except Exception:
                    pass

            self.movie_service = MovieService(
                sftp=self.sftp_client,
                watch_dir=self.watch_dir,
                pi_root_dir=f"{self.pi_root_dir}/{self.pi_movies}",
            )
            self.tv_service = TvService(
                sftp=self.sftp_client,
                watch_dir=self.watch_dir,
                pi_root_dir=self.pi_root_dir,
            )
            classifier = FileClassifierService()
            deletion = FileDeletionService()

            # Pre-scan: transfer existing files in ~/Transfers
            # self._pre_scan_and_transfer()

            # Create monitor repo and start monitoring
            self.file_monitor_repo = FileMonitorRepository(
                watch_dir=self.watch_dir,
                classifier_service=classifier,
                movie_service=self.movie_service,
                tv_service=self.tv_service,
                deletion_service=deletion,
                file_exts=self.file_exts,
            )
            self.file_monitor_repo.create_directories()
            self.file_monitor_repo.start_monitoring()

            while self._running:
                self.msleep(500)

            # Stop monitoring
            self.file_monitor_repo.stop_monitoring()

        except Exception as e:
            logger.error(f"MonitorThread error: {e}")
        finally:
            # cleanup: close sftp/ssh only if this thread created them
            try:
                if self.sftp_client and (self.ssh_client is not None):
                    self.sftp_client.close()
                if self.ssh_client:
                    self.ssh_client.close()
            except Exception:
                pass

    def stop(self) -> None:
        self._running = False

    def _connect_sftp(
        self, host: str, username: str, port: int = 22
    ) -> Tuple[Optional[paramiko.SSHClient], Optional[paramiko.SFTPClient]]:
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, port=port, timeout=15)
            sftp = ssh.open_sftp()
            return ssh, sftp
        except Exception as e:
            logger.error(f"SFTP connect failed: {e}")
            return None, None

    def scan_and_transfer(self) -> None:
        """
        Scan ~/Transfers and upload existing files before enabling live monitoring.
        Behavior:
         - For movie folders under ~/Transfers/Movies -> upload entire folder via MovieService
         - For TV_shows -> upload folder structure via TvService
         - Skips hidden/system files
        """
        root = self.watch_dir
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
            if entry == self.pi_movies:
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

            elif entry == self.pi_tv:
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
                                        if ext in self.file_exts:
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
                        kind = FileClassifierService().classify_folder(entry_path)
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
                                            if ext in self.file_exts:
                                                self.file_monitor_repo.deletion_service.delete_file(
                                                    os.path.join(root_dir, f)
                                                )
                    except Exception as e:
                        logger.error(f"Scan: Generic: Failed: {entry_path} - {e}")

        logger.success(f"Scan: Complete: {root}")
