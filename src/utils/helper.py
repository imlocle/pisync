from pathlib import Path
import sys


def get_path(path_base: str) -> Path:
    if getattr(sys, "_MEIPASS", False):
        base_path = Path(sys._MEIPASS)
        return base_path / path_base
    else:
        return Path(__file__).parent
