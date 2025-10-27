import os
from typing import Set


class FileClassifierService:
    def classify_file(self, file_path: str, file_exts: Set[str]) -> str:
        """
        Heuristic classifier:
        - If extension matches known media extensions -> treat as movie by default
        - If filename contains season/episode patterns -> tv
        """
        _, ext = os.path.splitext(file_path.lower())
        filename = os.path.basename(file_path).lower()

        if ext in file_exts:
            # We'll still check filename for tv season pattern before defaulting to movie
            if any(
                token in filename for token in ("s0", "s1", "s2", "e0", "e1", "episode")
            ):
                return "tv"
            return "movie"

        if (
            "season" in filename
            or "episode" in filename
            or "s01" in filename
            or "s02" in filename
            or "s0" in filename
        ):
            return "tv"
        return "movie"

    def classify_folder(self, folder_path: str) -> str:
        folder_name = os.path.basename(folder_path).lower()
        if "season" in folder_name or "s0" in folder_name or "episode" in folder_name:
            return "tv"
        # If folder sits under TV_SHOWS dir we assume tv (monitor repo usually sets this)
        return "movie"
