from PySide6.QtCore import QObject, Signal


class Logger(QObject):
    log_signal = Signal(str)  # For text logs
    progress_signal = Signal(int)  # For progress 0–100

    def info(self, msg: str):
        self.log_signal.emit(f"ℹ️ {msg}")

    def success(self, msg: str):
        self.log_signal.emit(f"✅ {msg}")

    def error(self, msg: str):
        self.log_signal.emit(f"❌ {msg}")

    def warn(self, msg: str):
        self.log_signal.emit(f"⚠️ {msg}")

    def start(self, msg: str):
        self.log_signal.emit(f"🟢 {msg}")

    def stop(self, msg: str):
        self.log_signal.emit(f"🛑 {msg}")

    def search(self, msg: str):
        self.log_signal.emit(f"🔍 {msg}")

    def upload(self, msg: str):
        self.log_signal.emit(f"🚀 {msg}")

    def trash(self, msg: str):
        self.log_signal.emit(f"🗑️ {msg}")

    def emit(self, msg: str):
        self.log_signal.emit(msg)


logger = Logger()
