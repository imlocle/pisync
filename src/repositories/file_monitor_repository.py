import os
from typing import Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.services.file_classifier_service import FileClassifierService
from src.services.file_deletion_service import FileDeletionService
from src.services.movie_service import MovieService
from src.services.tv_service import TvService
from src.utils.constants import MOVIES_DIR, TV_SHOWS_DIR


class FileMonitorRepository(FileSystemEventHandler):
    def __init__(
        self,
        watch_dir: str,
        classifier_service: FileClassifierService,
        movie_service: MovieService,
        tv_service: TvService,
        deletion_service: FileDeletionService,
        file_exts: Set[str],
    ) -> None:
        super().__init__()
        self.watch_dir = watch_dir
        self.classifier_service = classifier_service
        self.movie_service = movie_service
        self.tv_service = tv_service
        self.deletion_service = deletion_service
        self.file_exts = file_exts
        self.observer = Observer()

    def create_directories(self) -> None:
        movies_dir = os.path.join(self.watch_dir, MOVIES_DIR)
        tv_dir = os.path.join(self.watch_dir, TV_SHOWS_DIR)
        for directory in [self.watch_dir, movies_dir, tv_dir]:
            os.makedirs(directory, exist_ok=True)

    def start_monitoring(self) -> None:
        self.observer.schedule(self, self.watch_dir, recursive=True)
        self.observer.start()

    def stop_monitoring(self) -> None:
        self.observer.stop()
        self.observer.join()

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            self.handle_folder(event.src_path)
        else:
            self.handle_file(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.handle_file(event.src_path)

    def handle_file(self, file_path: str) -> None:
        # ignore hidden/system files
        name = os.path.basename(file_path)
        if name.startswith(".") or name.startswith("._"):
            return

        # decide type
        if MOVIES_DIR in file_path.split(os.sep):
            dest_type = "movie"
        elif TV_SHOWS_DIR in file_path.split(os.sep):
            dest_type = "tv"
        else:
            dest_type = self.classifier_service.classify_file(file_path, self.file_exts)

        try:
            if dest_type == "movie":
                # for loose movie files, transfer parent folder (movie folder expected)
                folder = os.path.dirname(file_path)
                if self.movie_service.transfer_movie_folder(folder):
                    self.deletion_service.delete_folder(folder)
            elif dest_type == "tv":
                # ensure remote structure and upload the file's folder
                folder = os.path.dirname(file_path)
                if self.tv_service.transfer_tv_folder(folder):
                    if os.path.splitext(file_path)[1].lower() in self.file_exts:
                        self.deletion_service.delete_file(file_path)
        except Exception as e:
            print(f"Transfer error for {file_path}: {e}")

    def handle_folder(self, folder_path: str) -> None:
        name = os.path.basename(folder_path)
        if name.startswith(".") or name in [MOVIES_DIR, TV_SHOWS_DIR]:
            return

        dest_type = self.classifier_service.classify_folder(folder_path)
        try:
            if dest_type == "movie":
                if self.movie_service.transfer_movie_folder(folder_path):
                    self.deletion_service.delete_folder(folder_path)
            elif dest_type == "tv":
                if self.tv_service.transfer_tv_folder(folder_path):
                    # delete only video files in the folder
                    for root, _, files in os.walk(folder_path):
                        for f in files:
                            if f.startswith("."):
                                continue
                            ext = os.path.splitext(f)[1].lower()
                            if ext in self.file_exts:
                                self.deletion_service.delete_file(os.path.join(root, f))
        except Exception as e:
            print(f"Transfer error for folder {folder_path}: {e}")
