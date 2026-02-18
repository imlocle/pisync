from datetime import datetime

from PySide6.QtCore import QObject, Signal


class Logger(QObject):
    """
    Enhanced logger with timestamps and HTML formatting.
    
    Emits formatted log messages with:
    - Timestamps
    - Color-coded severity levels
    - Icons for visual identification
    - HTML formatting for rich text display
    """
    
    log_signal = Signal(str)  # For text logs (HTML formatted)
    progress_signal = Signal(int)  # For progress 0–100

    def _format_message(self, icon: str, msg: str, color: str) -> str:
        """Format message with timestamp, icon, and color."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return (
            f'<span style="color: #858585;">[{timestamp}]</span> '
            f'<span style="color: {color};">{icon}</span> '
            f'<span style="color: #cccccc;">{msg}</span>'
        )

    def info(self, msg: str):
        """Log informational message."""
        formatted = self._format_message("ℹ️", msg, "#4ec9b0")
        self.log_signal.emit(formatted)

    def success(self, msg: str):
        """Log success message."""
        formatted = self._format_message("✅", msg, "#4ec9b0")
        self.log_signal.emit(formatted)

    def error(self, msg: str):
        """Log error message."""
        formatted = self._format_message("❌", msg, "#f48771")
        self.log_signal.emit(formatted)

    def warn(self, msg: str):
        """Log warning message."""
        formatted = self._format_message("⚠️", msg, "#ce9178")
        self.log_signal.emit(formatted)

    def start(self, msg: str):
        """Log start event."""
        formatted = self._format_message("▶️", msg, "#4ec9b0")
        self.log_signal.emit(formatted)

    def stop(self, msg: str):
        """Log stop event."""
        formatted = self._format_message("⏹️", msg, "#858585")
        self.log_signal.emit(formatted)

    def search(self, msg: str):
        """Log search/scan event."""
        formatted = self._format_message("🔍", msg, "#007acc")
        self.log_signal.emit(formatted)

    def upload(self, msg: str):
        """Log upload event."""
        formatted = self._format_message("⬆️", msg, "#007acc")
        self.log_signal.emit(formatted)

    def trash(self, msg: str):
        """Log deletion event."""
        formatted = self._format_message("🗑️", msg, "#ce9178")
        self.log_signal.emit(formatted)

    def log(self, msg: str):
        """Emit raw message without formatting."""
        self.log_signal.emit(msg)


logger = Logger()
