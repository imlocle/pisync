from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import sys
from src.components.main_window import MainWindow
from src.utils.helper import get_path


def main():
    app = QApplication(sys.argv)

    stylesheet_path = get_path("assets/styles/styles.qss")
    try:
        with open(stylesheet_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ No stylesheet found — using default theme.")

    try:
        app.setWindowIcon(QIcon("assets/icons/pisync_logo.png"))
    except FileNotFoundError:
        print("⚠️ Logo not found — using default icon.")

    # Main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
