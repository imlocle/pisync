from PySide6.QtWidgets import QSplashScreen, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QColor, QPainter, QBrush
from PySide6.QtCore import Qt, QTimer


class SplashScreen(QSplashScreen):
    def __init__(self, logo_path: str, duration: int = 2500):
        # Load original image
        original = QPixmap(logo_path)

        # ---- CREATE ROUNDED VERSION ----
        size = original.size()
        rounded = QPixmap(size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(original))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(original.rect(), 15, 15)  # 15px radius
        painter.end()

        super().__init__(rounded)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.duration = duration

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 80))  # semi-transparent black
        self.setGraphicsEffect(shadow)

    def show_and_wait(self, callback):
        self.show()
        QTimer.singleShot(self.duration, callback)
