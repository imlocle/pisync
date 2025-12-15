from __future__ import annotations

import os
import shutil
from stat import S_ISDIR
from typing import Optional, List

from paramiko import SFTPClient
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QListWidgetItem,
    QMenu,
    QInputDialog,
)
from PySide6.QtCore import Signal, Qt, QUrl, QPoint
from PySide6.QtGui import (
    QIcon,
    QDragEnterEvent,
    QDropEvent,
    QPainter,
    QColor,
    QFont,
)

from src.config.settings import Settings


class FileExplorerWidget(QWidget):
    """
    A reusable file explorer widget for both local and remote (SFTP) directories.

    Emits:
        - directory_changed(str): when current_path changes to a new directory
        - file_opened(str): when a file is double-clicked
        - file_delete_requested(str): when user requests delete via context menu
        - file_rename_requested(str): when user requests rename via context menu
        - item_selected(str): when selection changes
        - remote_error(str): when remote (SFTP) refresh fails (socket closed, etc)
        - files_dropped(list[str], str): local paths dropped, + destination path (current_path)
    """

    directory_changed = Signal(str)
    file_delete_requested = Signal(str)
    files_dropped = Signal(
        list, str
    )  # [local_paths], remote_dest_dir (or local dest dir)
    file_opened = Signal(str)
    file_rename_requested = Signal(str)
    item_selected = Signal(str)
    remote_error = Signal(str)

    def __init__(
        self,
        settings: Settings,
        root_path: str,
        is_remote: bool = False,
        sftp: Optional[SFTPClient] = None,
        title: str = "Explorer",
    ) -> None:
        super().__init__()

        self.settings: Settings = settings
        self.root_path: str = root_path
        self.is_remote: bool = is_remote
        self.sftp: Optional[SFTPClient] = sftp
        self.title: str = title

        self.current_path: str = root_path
        self.drag_over: bool = False

        # ------------------------------------------------------------------
        # Layout / Header
        # ------------------------------------------------------------------
        layout: QVBoxLayout = QVBoxLayout(self)
        header_layout: QHBoxLayout = QHBoxLayout()

        self.back_btn: QPushButton = QPushButton("←")
        self.title_label: QLabel = QLabel(f"{self.title} ({self.current_path})")
        self.title_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        header_layout.addWidget(self.back_btn)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # ------------------------------------------------------------------
        # List widget
        # ------------------------------------------------------------------
        self.list_widget: QListWidget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.list_widget)

        self.back_btn.clicked.connect(self.go_back)
        self.list_widget.itemSelectionChanged.connect(self._on_item_selected)
        self.list_widget.itemDoubleClicked.connect(self.navigate)

        # Context menu
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Drag & drop (both local + remote; remote emits files_dropped)
        self.setAcceptDrops(True)
        self.list_widget.setAcceptDrops(True)

        self.refresh()

    # ------------------------------------------------------------------
    #  Context menu (delete / rename)
    # ------------------------------------------------------------------
    def show_context_menu(self, position: QPoint) -> None:
        item = self.list_widget.itemAt(position)
        if not item:
            return

        entry = item.text()
        full_path = os.path.join(self.current_path, entry)

        menu = QMenu(self)
        delete_action = menu.addAction("🗑️ Delete")
        rename_action = menu.addAction("✏️ Rename")

        action = menu.exec(self.list_widget.mapToGlobal(position))

        if action == delete_action:
            self.file_delete_requested.emit(full_path)
        elif action == rename_action:
            self.file_rename_requested.emit(full_path)

    def prompt_rename(self, old_path: str) -> Optional[str]:
        basename = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(
            self,
            "Rename File/Folder",
            f"Rename '{basename}' to:",
            text=basename,
        )
        if ok and new_name.strip():
            return new_name.strip()
        return None

    # ------------------------------------------------------------------
    #  Core Refresh / Navigation
    # ------------------------------------------------------------------
    def refresh(self, path: str | None = None) -> None:
        if path is not None:
            self.current_path = path

        self.list_widget.clear()
        self.title_label.setText(f"{self.title} ({self.current_path})")

        try:
            if self.is_remote:
                if not self.sftp:
                    raise RuntimeError("SFTP connection not available")
                entries: List[str] = self.sftp.listdir(self.current_path)
            else:
                entries = os.listdir(self.current_path)

            filtered_entries = [
                e
                for e in entries
                if not (
                    e.startswith(".")
                    or e.startswith("._")
                    or e in self.settings.skip_files
                )
            ]
            filtered_entries.sort(key=lambda s: s.lower())

            for entry in filtered_entries:
                full_path = os.path.join(self.current_path, entry)
                icon = self._get_icon(full_path)
                self.list_widget.addItem(QListWidgetItem(icon, entry))

        except Exception as e:
            # Friendly UI message
            self.list_widget.addItem(QListWidgetItem(f"⚠️ Error loading directory: {e}"))

            # Remote recovery: reset view state so UI doesn't get "stuck"
            if self.is_remote:
                self._reset_remote_state_after_failure(str(e))

    def _reset_remote_state_after_failure(self, error_msg: str) -> None:
        """
        If remote operations fail (socket closed, etc), reset to safe state:
        - reset current_path to root_path
        - clear sftp reference (forces controller to rebind)
        - emit remote_error so MainWindow/controller can reconnect
        """
        # Reset UI path to root (don't call listdir again here)
        self.current_path = self.root_path
        self.title_label.setText(f"{self.title} ({self.current_path})")

        # Drop the dead client (important: prevents repeated "Socket is closed")
        self.sftp = None

        # Let the app/controller decide how to recover
        self.remote_error.emit(error_msg)

    def navigate(self, item: QListWidgetItem) -> None:
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
            self.list_widget.addItem(QListWidgetItem(f"⚠️ Cannot open {entry}: {e}"))
            if self.is_remote:
                self._reset_remote_state_after_failure(str(e))

    def go_back(self) -> None:
        if self.current_path == self.root_path:
            return
        self.current_path = os.path.dirname(self.current_path)
        self.refresh()
        self.directory_changed.emit(self.current_path)

    def set_sftp(self, sftp: Optional[SFTPClient]) -> None:
        self.sftp = sftp

    def _on_item_selected(self) -> None:
        items = self.list_widget.selectedItems()
        if not items:
            self.item_selected.emit("")
            return
        entry = items[0].text()
        full_path = os.path.join(self.current_path, entry)
        self.item_selected.emit(full_path)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_remote_directory(self, path: str) -> bool:
        if not self.sftp:
            return False
        try:
            st = self.sftp.stat(path)
            return S_ISDIR(st.st_mode)
        except Exception:
            return False

    def _get_icon(self, path: str) -> QIcon:
        try:
            if self.is_remote:
                return (
                    QIcon.fromTheme("folder")
                    if self._is_remote_directory(path)
                    else QIcon.fromTheme("text-x-generic")
                )
            return (
                QIcon.fromTheme("folder")
                if os.path.isdir(path)
                else QIcon.fromTheme("text-x-generic")
            )
        except Exception:
            return QIcon.fromTheme("unknown")

    # ------------------------------------------------------------------
    # Drag & Drop
    # ------------------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        # Only accept local filesystem drops
        urls = event.mimeData().urls()
        if not any(u.isLocalFile() for u in urls):
            event.ignore()
            return

        self.drag_over = True
        self.update()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event: QDragEnterEvent) -> None:
        self.drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            return

        urls: List[QUrl] = event.mimeData().urls()
        local_paths: List[str] = []
        for url in urls:
            if not url.isLocalFile():
                continue
            p = url.toLocalFile()
            if p:
                local_paths.append(p)

        if not local_paths:
            return

        # Remote explorer: emit for controller (upload in background)
        if self.is_remote:
            # IMPORTANT: do not attempt to upload here; just emit intent
            self.files_dropped.emit(local_paths, self.current_path)
            self.drag_over = False
            self.update()
            return

        # Local explorer: copy into current directory
        for src in local_paths:
            if not os.path.exists(src):
                continue
            dst = os.path.join(self.current_path, os.path.basename(src))
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            except Exception as e:
                print(f"Error copying {src}: {e}")

        self.refresh()
        self.drag_over = False
        self.update()

    # ------------------------------------------------------------------
    # Paint overlay
    # ------------------------------------------------------------------
    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        if self.drag_over:
            painter: QPainter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            overlay_color: QColor = QColor(0, 120, 215, 40)
            border_color: QColor = QColor(0, 120, 215)

            painter.fillRect(self.rect(), overlay_color)
            painter.setPen(border_color)
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 10, 10)

            painter.setPen(Qt.GlobalColor.black)
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "📂 Drop files/folders here",
            )
