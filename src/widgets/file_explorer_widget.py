from __future__ import annotations
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QListWidgetItem,
)
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QPainter, QColor, QFont
import os
import shutil
import paramiko
from src.utils.logging_signal import logger


class FileExplorerWidget(QWidget):
    """A reusable file explorer widget for both local and remote (SFTP) directories."""

    file_opened: Signal = Signal(str)
    directory_changed: Signal = Signal(str)

    def __init__(
        self,
        root_path: str,
        is_remote: bool = False,
        sftp: Optional[paramiko.SFTPClient] = None,
        title: str = "Explorer",
    ) -> None:
        super().__init__()
        self.title = title
        self.log_signal = logger.log_signal
        self.root_path: str = root_path
        self.current_path: str = root_path
        self.is_remote: bool = is_remote
        self.sftp: Optional[paramiko.SFTPClient] = sftp
        self.drag_over: bool = False  # visual feedback flag

        layout: QVBoxLayout = QVBoxLayout(self)
        header_layout: QHBoxLayout = QHBoxLayout()

        self.back_btn: QPushButton = QPushButton("← Back")
        self.title_label: QLabel = QLabel(f"{self.title} ({self.root_path})")
        self.title_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.list_widget: QListWidget = QListWidget()
        layout.addWidget(self.list_widget)

        self.back_btn.clicked.connect(self.go_back)
        self.list_widget.itemDoubleClicked.connect(self.navigate)

        # Enable drag-and-drop only for local explorer
        if not self.is_remote:
            self.setAcceptDrops(True)

        self.refresh()

    def refresh(self) -> None:
        """Refreshes the list to show the current directory contents."""
        self.list_widget.clear()
        self.title_label: QLabel = QLabel(f"{self.title} ({self.root_path})")
        try:
            entries: List[str] = []
            if self.is_remote and self.sftp:
                entries = self.sftp.listdir(self.current_path)
            else:
                entries = os.listdir(self.current_path)

            filtered_entries = [
                e
                for e in entries
                if not (
                    e.startswith(".")
                    or e.startswith("._")
                    or e in {".DS_Store", ".Trashes", "Thumbs.db"}
                )
            ]

            filtered_entries.sort()

            for entry in filtered_entries:
                full_path: str = os.path.join(self.current_path, entry)
                icon: QIcon = self._get_icon(full_path)
                item: QListWidgetItem = QListWidgetItem(icon, entry)
                self.list_widget.addItem(item)

        except Exception as e:
            self.list_widget.addItem(f"⚠️ Error loading directory: {e}")

    def navigate(self, item: QListWidgetItem) -> None:
        """Handles double-clicking an item to navigate folders or open files."""
        entry: str = item.text()
        new_path: str = os.path.join(self.current_path, entry)

        try:
            if self.is_remote:
                if self._is_remote_directory(new_path):
                    self.current_path = new_path
                    self.refresh()
                    self.directory_changed.emit(self.current_path)
                else:
                    self.file_opened.emit(new_path)
            else:
                if os.path.isdir(new_path):
                    self.current_path = new_path
                    self.refresh()
                    self.directory_changed.emit(self.current_path)
                else:
                    self.file_opened.emit(new_path)
        except Exception as e:
            self.list_widget.addItem(f"⚠️ Cannot open {entry}: {e}")

    def go_back(self) -> None:
        """Goes up one directory level, unless already at root."""
        if self.current_path == self.root_path:
            return
        self.current_path = os.path.dirname(self.current_path)
        self.refresh()
        self.directory_changed.emit(self.current_path)

    def _is_remote_directory(self, path: str) -> bool:
        """Checks if a remote path is a directory."""
        if not self.sftp:
            return False
        try:
            self.sftp.listdir(path)
            return True
        except IOError:
            return False

    def _get_icon(self, path: str) -> QIcon:
        """Returns an appropriate icon for a file or folder."""
        try:
            if self.is_remote:
                if self._is_remote_directory(path):
                    return QIcon.fromTheme("folder")
                return QIcon.fromTheme("text-x-generic")
            else:
                return (
                    QIcon.fromTheme("folder")
                    if os.path.isdir(path)
                    else QIcon.fromTheme("text-x-generic")
                )
        except Exception:
            return QIcon.fromTheme("unknown")

    # === Drag & Drop ===
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept drag enter events if they contain file URLs."""
        if not self.is_remote and event.mimeData().hasUrls():
            self.drag_over = True
            self.update()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event: QDragEnterEvent) -> None:
        """Reset visual when drag leaves."""
        self.drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle files dropped into the explorer — copy to current directory."""
        if self.is_remote:
            return  # Do not support dropping into remote side yet

        urls: List[QUrl] = event.mimeData().urls()
        for url in urls:
            local_path: str = url.toLocalFile()
            if os.path.exists(local_path):
                dest_path: str = os.path.join(
                    self.current_path, os.path.basename(local_path)
                )
                try:
                    if os.path.isdir(local_path):
                        shutil.copytree(local_path, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(local_path, dest_path)
                except Exception as e:
                    print(f"Error copying {local_path}: {e}")

        self.drag_over = False
        self.refresh()
        self.update()

    def paintEvent(self, event) -> None:
        """Draws drop zone visual feedback when dragging files over."""
        super().paintEvent(event)

        if self.drag_over:
            painter: QPainter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            overlay_color: QColor = QColor(0, 120, 215, 40)  # Light blue overlay
            border_color: QColor = QColor(0, 120, 215)  # Blue border

            # Semi-transparent overlay
            painter.fillRect(self.rect(), overlay_color)

            # Border
            painter.setPen(border_color)
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 10, 10)

            # Text in the center
            painter.setPen(Qt.GlobalColor.black)
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "📂 Drop files here to add to Watch Directory",
            )
