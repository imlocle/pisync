from PySide6.QtCore import QObject, Signal


class Logger(QObject):
    log_signal = Signal(str)  # For text logs
    progress_signal = Signal(int)  # For progress 0–100


logger = Logger()  # Singleton instance for global use
