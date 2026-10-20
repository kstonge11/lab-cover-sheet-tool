"""
Queue box widget for displaying and managing queued errors.
"""

from typing import List
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..models import ErrorEntry
from ..utils.logger import logger


class QueueBox(QFrame):
    """Widget for displaying the error queue and action buttons."""

    # Signals for actions
    save_covers_requested = pyqtSignal(list)  # Save cover sheets to chosen path
    print_requested = pyqtSignal(list)
    queue_cleared = pyqtSignal()
    group_by_printer_changed = pyqtSignal(bool)

    STYLESHEET = """
        #queueBox {
            background-color: #333;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QLabel#boxTitle {
            font-size: 14px;
            font-weight: bold;
            color: #fff;
        }
        QFrame#queueItem {
            background-color: #2a2a2a;
            border-radius: 3px;
        }
        QFrame#queueItem QLabel {
            color: #ccc;
            font-size: 10px;
            padding: 4px;
        }
        QPushButton#removeItem {
            color: #aaa;
            background-color: transparent;
            border: none;
            font-size: 12px;
            padding: 0;
        }
        QPushButton#removeItem:hover {
            color: #fff;
            background-color: #c62828;
            border-radius: 3px;
        }
        QLabel#emptyQueue {
            color: #666;
            font-size: 11px;
        }
        QLabel#savePath {
            color: #4CAF50;
            font-size: 9px;
            padding: 2px 4px;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("queueBox")
        self.setStyleSheet(self.STYLESHEET)

        self._queue: List[ErrorEntry] = []
        self._save_path: str = ""  # Custom save path
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        # Title with count
        title_row = QHBoxLayout()
        title = QLabel("📤 Queue")
        title.setObjectName("boxTitle")
        self.count_label = QLabel("(0)")
        self.count_label.setStyleSheet("color: #888; font-size: 12px;")
        title_row.addWidget(title)
        title_row.addWidget(self.count_label)
        title_row.addStretch()
        layout.addLayout(title_row)

        # Queue list (scrollable)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
        """)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(4)

        self._show_empty_state()

        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        # Save path display
        self.save_path_label = QLabel("")
        self.save_path_label.setObjectName("savePath")
        self.save_path_label.setWordWrap(True)
        layout.addWidget(self.save_path_label)

        # Action buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)

        # Save path button
        self.choose_path_btn = QPushButton("📁 Set Save Location...")
        self.choose_path_btn.setFixedHeight(28)

        # Save covers button
        self.save_covers_btn = QPushButton("💾 Save Covers")
        self.save_covers_btn.setFixedHeight(28)
        self.save_covers_btn.setEnabled(False)

        self.print_btn = QPushButton("🖨️ Print Covers")
        self.print_btn.setFixedHeight(28)
        self.print_btn.setEnabled(False)

        self.clear_btn = QPushButton("🗑️ Clear Queue")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.setEnabled(False)

        self.group_by_printer_cb = QCheckBox("Print grouped by printer")
        self.group_by_printer_cb.setToolTip(
            "Print every sheet for one printer before moving to the next,\n"
            "so each printer's covers come out together"
        )

        btn_layout.addWidget(self.group_by_printer_cb)
        btn_layout.addWidget(self.choose_path_btn)
        btn_layout.addWidget(self.save_covers_btn)
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.save_covers_btn.clicked.connect(self._on_save_covers)
        self.print_btn.clicked.connect(self._on_print)
        self.clear_btn.clicked.connect(self.clear)
        self.group_by_printer_cb.toggled.connect(self.group_by_printer_changed.emit)

    def _show_empty_state(self):
        label = QLabel("No errors queued")
        label.setObjectName("emptyQueue")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_layout.addWidget(label)
        self.scroll_layout.addStretch()

    def _clear_layout(self):
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                # Hide now; deletion waits for the event loop (the remove button
                # that triggered this refresh may still be handling its click)
                item.widget().hide()
                item.widget().deleteLater()

    def _refresh_display(self):
        self._clear_layout()
        self.count_label.setText(f"({len(self._queue)})")

        if not self._queue:
            self._show_empty_state()
            self._update_button_states()
            return

        for entry in self._queue:
            self.scroll_layout.addWidget(self._make_item(entry))

        self.scroll_layout.addStretch()
        self._update_button_states()

    def _make_item(self, entry: ErrorEntry) -> QFrame:
        """Build one queue row: the entry summary plus a remove button."""
        item = QFrame()
        item.setObjectName("queueItem")
        row = QHBoxLayout(item)
        row.setContentsMargins(0, 0, 4, 0)
        row.setSpacing(2)

        label = QLabel(f"{entry.error_type}\n{entry.printer_summary} • {entry.page_summary}")
        label.setWordWrap(True)
        row.addWidget(label, stretch=1)

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("removeItem")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setToolTip("Remove from queue")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(lambda _=False, e=entry: self.remove_entry(e))
        row.addWidget(remove_btn, alignment=Qt.AlignmentFlag.AlignTop)

        return item

    def _update_button_states(self):
        """Update button enabled states based on queue and save path."""
        has_items = len(self._queue) > 0
        has_save_path = bool(self._save_path)
        
        # Save requires both items and a path
        self.save_covers_btn.setEnabled(has_items and has_save_path)
        # Print just needs items (and a cover template, but that's checked elsewhere)
        self.print_btn.setEnabled(has_items)
        self.clear_btn.setEnabled(has_items)

    def set_save_path(self, path: str):
        """Set the save path for cover sheets."""
        self._save_path = path
        if path:
            # Truncate path for display
            display_path = path if len(path) < 50 else f"...{path[-47:]}"
            self.save_path_label.setText(f"📂 {display_path}")
            self.save_path_label.setToolTip(path)
        else:
            self.save_path_label.setText("")
        self._update_button_states()

    def get_save_path(self) -> str:
        """Get the current save path."""
        return self._save_path

    def add_entry(self, entry: ErrorEntry):
        """Add an error entry to the queue."""
        self._queue.append(entry)
        self._refresh_display()
        logger.info(f"Queued: {entry.error_type} on {entry.printer_summary}")

    def remove_entry(self, entry: ErrorEntry):
        """Remove one entry from the queue."""
        # Match by identity: two identical entries can both be queued
        for i, queued in enumerate(self._queue):
            if queued is entry:
                del self._queue[i]
                break
        else:
            return
        self._refresh_display()
        logger.info(f"Removed from queue: {entry.error_type} on {entry.printer_summary}")

    def set_entries(self, entries: List[ErrorEntry]):
        """Replace the queue contents (e.g. with the sheets that failed to print)."""
        self._queue = list(entries)
        self._refresh_display()

    def group_by_printer(self) -> bool:
        """Whether printing should go printer by printer."""
        return self.group_by_printer_cb.isChecked()

    def set_group_by_printer(self, enabled: bool):
        """Set the group-by-printer option without saving it again."""
        self.group_by_printer_cb.blockSignals(True)
        self.group_by_printer_cb.setChecked(enabled)
        self.group_by_printer_cb.blockSignals(False)

    def clear(self):
        """Clear all entries from the queue."""
        count = len(self._queue)
        self._queue.clear()
        self._refresh_display()
        self.queue_cleared.emit()
        logger.info(f"Queue cleared ({count} items removed)")

    def get_queue(self) -> List[ErrorEntry]:
        """Return a copy of the current queue."""
        return list(self._queue)

    def _on_save_covers(self):
        self.save_covers_requested.emit(list(self._queue))

    def _on_print(self):
        self.print_requested.emit(list(self._queue))
