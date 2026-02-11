"""
File monitoring repository for detecting and processing media file changes.

This module uses watchdog to monitor a directory for new media files and
automatically transfers them to a Raspberry Pi. It includes file stability
checking to prevent race conditions where files are transferred before
they're fully written to disk.
"""

import os
import time
from typing import Set, Dict, Optional
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.services.file_classifier_service import FileClassifierService
from src.services.file_deletion_service import FileDeletionService
from src.services.movie_service import MovieService
from src.services.tv_service import TvService
from src.utils.constants import MOVIES_DIR, TV_SHOWS_DIR
from src.utils.logging_signal import logger
from src.models.errors import FileMonitorError, FileStabilityError


class FileStabilityTracker:
    """
    Tracks file stability to prevent transferring files that are still being written.
    
    A file is considered stable when its size hasn't changed for a specified duration.
    This prevents race conditions where watchdog detects a file before it's fully copied.
    """
    
    def __init__(self, stability_duration: float = 2.0):
        """
        Initialize the stability tracker.
        
        Args:
            stability_duration: Seconds to wait for file size to stabilize (default: 2.0)
        """
        self.stability_duration = stability_duration
        self._file_info: Dict[str, tuple[float, int]] = {}  # path -> (timestamp, size)
        self._lock = Lock()
    
    def check_stability(self, file_path: str) -> bool:
        """
        Check if a file is stable (not being written to).
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file is stable, False if still being written
            
        Raises:
            FileStabilityError: If file cannot be accessed
        """
        try:
            if not os.path.exists(file_path):
                # File was deleted, remove from tracking
                with self._lock:
                    self._file_info.pop(file_path, None)
                return False
            
            current_size = os.path.getsize(file_path)
            current_time = time.time()
            
            with self._lock:
                if file_path not in self._file_info:
                    # First time seeing this file, record its size
                    self._file_info[file_path] = (current_time, current_size)
                    logger.info(f"Monitor: Tracking file stability: {os.path.basename(file_path)}")
                    return False
                
                last_time, last_size = self._file_info[file_path]
                
                if current_size != last_size:
                    # Size changed, file still being written
                    self._file_info[file_path] = (current_time, current_size)
                    logger.info(
                        f"Monitor: File still growing: {os.path.basename(file_path)} "
                        f"({last_size} -> {current_size} bytes)"
                    )
                    return False
                
                # Size hasn't changed, check if enough time has passed
                elapsed = current_time - last_time
                if elapsed >= self.stability_duration:
                    # File is stable, remove from tracking
                    self._file_info.pop(file_path, None)
                    logger.success(
                        f"Monitor: File stable: {os.path.basename(file_path)} "
                        f"({current_size} bytes)"
                    )
                    return True
                
                # Not enough time has passed yet
                logger.info(
                    f"Monitor: Waiting for stability: {os.path.basename(file_path)} "
                    f"({elapsed:.1f}/{self.stability_duration}s)"
                )
                return False
                
        except OSError as e:
            raise FileStabilityError(
                f"Cannot check file stability",
                path=file_path,
                details=str(e)
            )
    
    def clear_tracking(self, file_path: str) -> None:
        """Remove a file from stability tracking."""
        with self._lock:
            self._file_info.pop(file_path, None)
    
    def clear_all(self) -> None:
        """Clear all tracked files."""
        with self._lock:
            self._file_info.clear()


class FileMonitorRepository(FileSystemEventHandler):
    """
    Monitors a directory for media files and automatically transfers them to Raspberry Pi.
    
    This class uses watchdog to detect file system events and processes media files
    (movies and TV shows) by transferring them to a remote server via SFTP.
    
    Features:
    - File stability checking to prevent race conditions
    - Automatic classification of movies vs TV shows
    - Preserves directory structure for TV shows
    - Automatic cleanup after successful transfer
    """
    
    def __init__(
        self,
        watch_dir: str,
        classifier_service: FileClassifierService,
        movie_service: MovieService,
        tv_service: TvService,
        deletion_service: FileDeletionService,
        file_exts: Set[str],
        stability_duration: float = 2.0,
    ) -> None:
        """
        Initialize the file monitor.
        
        Args:
            watch_dir: Directory to monitor for new files
            classifier_service: Service for classifying files as movies/TV
            movie_service: Service for transferring movies
            tv_service: Service for transferring TV shows
            deletion_service: Service for deleting local files after transfer
            file_exts: Set of allowed file extensions (e.g., {'.mp4', '.mkv'})
            stability_duration: Seconds to wait for file stability (default: 2.0)
        """
        super().__init__()
        self.watch_dir = watch_dir
        self.classifier_service = classifier_service
        self.movie_service = movie_service
        self.tv_service = tv_service
        self.deletion_service = deletion_service
        self.file_exts = file_exts
        self.observer = Observer()
        self.stability_tracker = FileStabilityTracker(stability_duration)
        
        # Track processed items to avoid duplicate processing
        self._processed_items: Set[str] = set()
        self._processed_lock = Lock()

    def create_directories(self) -> None:
        """
        Create the watch directory structure if it doesn't exist.
        
        Creates:
        - Main watch directory
        - Movies subdirectory
        - TV_shows subdirectory
        """
        movies_dir = os.path.join(self.watch_dir, MOVIES_DIR)
        tv_dir = os.path.join(self.watch_dir, TV_SHOWS_DIR)
        
        for directory in [self.watch_dir, movies_dir, tv_dir]:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Monitor: Directory ready: {directory}")
            except Exception as e:
                logger.error(f"Monitor: Failed to create directory {directory}: {e}")
                raise FileMonitorError(
                    f"Failed to create watch directory",
                    path=directory,
                    details=str(e)
                )

    def start_monitoring(self) -> None:
        """
        Start monitoring the watch directory for file system events.
        
        Raises:
            FileMonitorError: If monitoring cannot be started
        """
        try:
            self.observer.schedule(self, self.watch_dir, recursive=True)
            self.observer.start()
            logger.start(f"Monitor: Started watching: {self.watch_dir}")
        except Exception as e:
            raise FileMonitorError(
                f"Failed to start file monitoring",
                path=self.watch_dir,
                details=str(e)
            )

    def stop_monitoring(self) -> None:
        """
        Stop monitoring and clean up resources.
        
        This method blocks until the observer thread has finished.
        """
        try:
            self.observer.stop()
            self.observer.join()
            self.stability_tracker.clear_all()
            logger.stop("Monitor: Stopped")
        except Exception as e:
            logger.error(f"Monitor: Error stopping: {e}")

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file/folder creation events.
        
        Args:
            event: Watchdog file system event
        """
        if event.is_directory:
            self._schedule_folder_processing(event.src_path)
        else:
            self._schedule_file_processing(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Handle file modification events.
        
        Only processes file modifications (not directories) to detect when
        files finish being written.
        
        Args:
            event: Watchdog file system event
        """
        if not event.is_directory:
            self._schedule_file_processing(event.src_path)

    def _schedule_file_processing(self, file_path: str) -> None:
        """
        Schedule a file for processing after stability check.
        
        This method checks if the file is stable (not being written to) before
        processing. If the file is still being written, it will be checked again
        on the next modification event.
        
        Args:
            file_path: Path to file to process
        """
        # Skip if already processed
        with self._processed_lock:
            if file_path in self._processed_items:
                return
        
        # Check stability
        try:
            if not self.stability_tracker.check_stability(file_path):
                # File not stable yet, will be checked again on next event
                return
        except FileStabilityError as e:
            logger.error(f"Monitor: Stability check failed: {e}")
            return
        
        # File is stable, process it
        self.handle_file(file_path)

    def _schedule_folder_processing(self, folder_path: str) -> None:
        """
        Schedule a folder for processing.
        
        Folders are processed immediately without stability checking since
        folder creation is atomic.
        
        Args:
            folder_path: Path to folder to process
        """
        # Skip if already processed
        with self._processed_lock:
            if folder_path in self._processed_items:
                return
        
        self.handle_folder(folder_path)

    def _mark_as_processed(self, path: str) -> None:
        """
        Mark a file or folder as processed to prevent duplicate processing.
        
        Args:
            path: Path to mark as processed
        """
        with self._processed_lock:
            self._processed_items.add(path)

    def handle_file(self, file_path: str) -> None:
        """
        Process a stable file for transfer.
        
        This method:
        1. Validates the file (not hidden, valid extension)
        2. Classifies the file as movie or TV show
        3. Transfers the parent folder
        4. Deletes local files after successful transfer
        
        Args:
            file_path: Path to file to process
        """
        # Validate file exists
        if not os.path.exists(file_path):
            logger.warn(f"Monitor: File no longer exists: {file_path}")
            self.stability_tracker.clear_tracking(file_path)
            return
        
        # Ignore hidden/system files
        name = os.path.basename(file_path)
        if name.startswith(".") or name.startswith("._"):
            logger.info(f"Monitor: Skipping hidden file: {name}")
            return
        
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.file_exts:
            logger.info(f"Monitor: Skipping unsupported file type: {name} ({ext})")
            return

        # Determine destination type based on path structure
        path_parts = file_path.split(os.sep)
        if MOVIES_DIR in path_parts:
            dest_type = "movie"
            logger.info(f"Monitor: Classified as movie (path-based): {name}")
        elif TV_SHOWS_DIR in path_parts:
            dest_type = "tv"
            logger.info(f"Monitor: Classified as TV show (path-based): {name}")
        else:
            # Use classifier for files outside standard directories
            dest_type = self.classifier_service.classify_file(file_path, self.file_exts)
            logger.info(f"Monitor: Classified as {dest_type} (heuristic): {name}")

        try:
            folder = os.path.dirname(file_path)
            
            if dest_type == "movie":
                # Transfer entire movie folder
                logger.upload(f"Monitor: Transferring movie folder: {os.path.basename(folder)}")
                if self.movie_service.transfer_movie_folder(folder):
                    self._mark_as_processed(file_path)
                    self._mark_as_processed(folder)
                    self.deletion_service.delete_folder(folder)
                    logger.success(f"Monitor: Movie transfer complete: {os.path.basename(folder)}")
                    
            elif dest_type == "tv":
                # Transfer TV show folder (preserves structure)
                logger.upload(f"Monitor: Transferring TV show folder: {os.path.basename(folder)}")
                if self.tv_service.transfer_tv_folder(folder):
                    self._mark_as_processed(file_path)
                    # Only delete media files, keep folder structure
                    if ext in self.file_exts:
                        self.deletion_service.delete_file(file_path)
                    logger.success(f"Monitor: TV show transfer complete: {name}")
                    
        except Exception as e:
            logger.error(f"Monitor: Transfer error for {file_path}: {e}")
            # Clear from processed so it can be retried
            with self._processed_lock:
                self._processed_items.discard(file_path)
            # Clear stability tracking
            self.stability_tracker.clear_tracking(file_path)

    def handle_folder(self, folder_path: str) -> None:
        """
        Process a folder for transfer.
        
        This method:
        1. Validates the folder (not hidden, not root directories)
        2. Classifies the folder as movie or TV show
        3. Transfers the folder
        4. Deletes local files after successful transfer
        
        Args:
            folder_path: Path to folder to process
        """
        # Validate folder exists
        if not os.path.exists(folder_path):
            logger.warn(f"Monitor: Folder no longer exists: {folder_path}")
            return
        
        # Ignore hidden folders and root directories
        name = os.path.basename(folder_path)
        if name.startswith(".") or name in [MOVIES_DIR, TV_SHOWS_DIR]:
            logger.info(f"Monitor: Skipping system folder: {name}")
            return

        # Classify folder
        dest_type = self.classifier_service.classify_folder(folder_path)
        logger.info(f"Monitor: Classified folder as {dest_type}: {name}")
        
        try:
            if dest_type == "movie":
                # Transfer entire movie folder
                logger.upload(f"Monitor: Transferring movie folder: {name}")
                if self.movie_service.transfer_movie_folder(folder_path):
                    self._mark_as_processed(folder_path)
                    self.deletion_service.delete_folder(folder_path)
                    logger.success(f"Monitor: Movie folder transfer complete: {name}")
                    
            elif dest_type == "tv":
                # Transfer TV show folder (preserves structure)
                logger.upload(f"Monitor: Transferring TV show folder: {name}")
                if self.tv_service.transfer_tv_folder(folder_path):
                    self._mark_as_processed(folder_path)
                    # Delete only video files in the folder, keep structure
                    for root, _, files in os.walk(folder_path):
                        for f in files:
                            if f.startswith("."):
                                continue
                            ext = os.path.splitext(f)[1].lower()
                            if ext in self.file_exts:
                                file_to_delete = os.path.join(root, f)
                                try:
                                    self.deletion_service.delete_file(file_to_delete)
                                except Exception as e:
                                    logger.warn(f"Monitor: Could not delete {f}: {e}")
                    logger.success(f"Monitor: TV show folder transfer complete: {name}")
                    
        except Exception as e:
            logger.error(f"Monitor: Transfer error for folder {folder_path}: {e}")
            # Clear from processed so it can be retried
            with self._processed_lock:
                self._processed_items.discard(folder_path)

