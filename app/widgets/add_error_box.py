"""
Add Error box widget for selecting error types, printers, and pages.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QCheckBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import pyqtSignal

from ..constants import PRINTERS, PRINTER_SHORT_NAMES
from ..models import ErrorEntry
from ..utils.logger import logger


class AddErrorBox(QFrame):
    """Widget for adding error entries to the queue."""

    # Emitted when an error is added to the queue
    error_added = pyqtSignal(ErrorEntry)

    STYLESHEET = """
        #addErrorBox {
            background-color: #333;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QLabel#boxTitle {
            font-size: 14px;
            font-weight: bold;
            color: #fff;
        }
        QLabel#sectionLabel {
            color: #aaa;
            font-size: 11px;
        }
        QCheckBox {
            color: #fff;
            font-size: 10px;
        }
        QCheckBox::indicator {
            width: 14px;
            height: 14px;
        }
        QComboBox#categoryCombo {
            background-color: #3a3a3a;
        }
        QComboBox#errorCombo {
            background-color: #3a3a3a;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("addErrorBox")
        self.setStyleSheet(self.STYLESHEET)

        self._context = {}  # Stores campaign, operator, firmware, line_number
        self._error_categories = {}  # {category_name: [error1, error2, ...]}
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("⚠️ Add Error")
        title.setObjectName("boxTitle")
        layout.addWidget(title)

        # Category dropdown
        category_row = QHBoxLayout()
        category_label = QLabel("Category:")
        category_label.setObjectName("sectionLabel")
        category_label.setFixedWidth(55)

        self.category_combo = QComboBox()
        self.category_combo.setObjectName("categoryCombo")
        self.category_combo.addItem("-- Select Category --")

        category_row.addWidget(category_label)
        category_row.addWidget(self.category_combo)
        layout.addLayout(category_row)

        # Error Type dropdown
        error_row = QHBoxLayout()
        error_label = QLabel("Error:")
        error_label.setObjectName("sectionLabel")
        error_label.setFixedWidth(55)

        self.error_type_combo = QComboBox()
        self.error_type_combo.setObjectName("errorCombo")
        self.error_type_combo.addItem("-- Select Error --")
        self.error_type_combo.setEnabled(False)

        error_row.addWidget(error_label)
        error_row.addWidget(self.error_type_combo)
        layout.addLayout(error_row)

        # Printer checkboxes
        printer_label = QLabel("Printers:")
        printer_label.setObjectName("sectionLabel")
        layout.addWidget(printer_label)

        # Printer checkbox grid (2 rows of 4)
        self.printer_checkboxes = {}
        printer_grid = QGridLayout()
        printer_grid.setSpacing(4)

        for i, (short, full) in enumerate(zip(PRINTER_SHORT_NAMES, PRINTERS)):
            cb = QCheckBox(short)
            cb.setToolTip(full)
            self.printer_checkboxes[full] = cb
            printer_grid.addWidget(cb, i // 4, i % 4)

        layout.addLayout(printer_grid)

        # Quick select buttons
        quick_btn_row = QHBoxLayout()
        quick_btn_row.setSpacing(4)

        self.all_btn = QPushButton("All")
        self.all_btn.setFixedHeight(22)
        self.none_btn = QPushButton("None")
        self.none_btn.setFixedHeight(22)
        self.invert_btn = QPushButton("Invert")
        self.invert_btn.setFixedHeight(22)

        quick_btn_row.addWidget(self.all_btn)
        quick_btn_row.addWidget(self.none_btn)
        quick_btn_row.addWidget(self.invert_btn)
        layout.addLayout(quick_btn_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #555;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Pages input
        pages_row = QHBoxLayout()
        pages_label = QLabel("Pages:")
        pages_label.setObjectName("sectionLabel")
        pages_label.setFixedWidth(55)

        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("e.g. 11, 15, 22")

        pages_row.addWidget(pages_label)
        pages_row.addWidget(self.pages_input)
        layout.addLayout(pages_row)

        # Count display
        count_row = QHBoxLayout()
        count_label = QLabel("Count:")
        count_label.setObjectName("sectionLabel")
        count_label.setFixedWidth(55)

        self.count_display = QLabel("0")
        self.count_display.setStyleSheet("color: #4CAF50; font-weight: bold;")

        count_row.addWidget(count_label)
        count_row.addWidget(self.count_display)
        count_row.addStretch()
        layout.addLayout(count_row)

        # Notes input
        notes_row = QHBoxLayout()
        notes_label = QLabel("Notes:")
        notes_label.setObjectName("sectionLabel")
        notes_label.setFixedWidth(55)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Optional details...")

        notes_row.addWidget(notes_label)
        notes_row.addWidget(self.notes_input)
        layout.addLayout(notes_row)

        # Add to Queue button
        self.add_btn = QPushButton("➕ Add to Queue")
        self.add_btn.setFixedHeight(30)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.add_btn)

        layout.addStretch()

    def _connect_signals(self):
        self.all_btn.clicked.connect(self._select_all)
        self.none_btn.clicked.connect(self._select_none)
        self.invert_btn.clicked.connect(self._invert_selection)
        self.pages_input.textChanged.connect(self._update_count)
        self.add_btn.clicked.connect(self._add_to_queue)
        self.category_combo.currentTextChanged.connect(self._on_category_changed)

    def _on_category_changed(self, category: str):
        """Update error dropdown when category changes."""
        self.error_type_combo.clear()
        
        if category == "-- Select Category --" or category not in self._error_categories:
            self.error_type_combo.addItem("-- Select Error --")
            self.error_type_combo.setEnabled(False)
            return
        
        errors = self._error_categories.get(category, [])
        if errors:
            self.error_type_combo.addItems(errors)
            self.error_type_combo.setEnabled(True)
        else:
            self.error_type_combo.addItem("-- No Errors --")
            self.error_type_combo.setEnabled(False)

    def set_error_categories(self, categories: dict):
        """
        Set the error categories and their errors.
        
        Args:
            categories: Dict of {category_name: [error1, error2, ...]}
        """
        self._error_categories = categories
        
        # Update category dropdown
        self.category_combo.clear()
        self.category_combo.addItem("-- Select Category --")
        
        for category_name in categories.keys():
            if category_name:  # Skip empty category names
                self.category_combo.addItem(category_name)
        
        # Reset error dropdown
        self.error_type_combo.clear()
        self.error_type_combo.addItem("-- Select Error --")
        self.error_type_combo.setEnabled(False)
        
        logger.debug(f"Loaded {len(categories)} error categories")

    def _select_all(self):
        for cb in self.printer_checkboxes.values():
            cb.setChecked(True)

    def _select_none(self):
        for cb in self.printer_checkboxes.values():
            cb.setChecked(False)

    def _invert_selection(self):
        for cb in self.printer_checkboxes.values():
            cb.setChecked(not cb.isChecked())

    def _update_count(self):
        pages = self._parse_pages()
        self.count_display.setText(str(len(pages)))
    
    def _parse_pages(self) -> list:
        """Parse comma-separated page numbers, supports ranges."""
        pages = []
        text = self.pages_input.text().strip()
        if not text:
            return pages
        
        for part in text.split(","):
            part = part.strip()
            if part.isdigit():
                pages.append(int(part))
            elif "-" in part:
                try:
                    start, end = part.split("-")
                    pages.extend(range(int(start.strip()), int(end.strip()) + 1))
                except ValueError:
                    pass
        return pages
    
    def _get_selected_printers(self) -> list:
        return [name for name, cb in self.printer_checkboxes.items() if cb.isChecked()]
    
    def _add_to_queue(self):
        printers = self._get_selected_printers()
        pages = self._parse_pages()
        error_type = self.error_type_combo.currentText()
        
        if not printers:
            logger.warning("Cannot add to queue: No printers selected")
            return
        if not pages:
            logger.warning("Cannot add to queue: No pages entered")
            return
        if error_type == "-- Select Error --" or error_type == "-- No Errors --":
            logger.warning("Cannot add to queue: No error type selected")
            return
        
        entry = ErrorEntry(
            error_type=error_type,
            printers=printers,
            pages=pages,
            notes=self.notes_input.text().strip(),
            line_number=self._context.get("line_number", 0),
            campaign=self._context.get("campaign", ""),
            operator=self._context.get("operator", ""),
            firmware=self._context.get("firmware", ""),
            climate=self._context.get("climate", ""),
            media=self._context.get("media", ""),
            script=self._context.get("script", ""),
            plexity=self._context.get("plexity", ""),
            load=self._context.get("load", ""),
            run=self._context.get("run", ""),
            phase=self._context.get("phase", ""),
        )
        
        self.error_added.emit(entry)
        
        # Clear inputs but keep category/error selection
        self.pages_input.clear()
        self.notes_input.clear()
        self._select_none()
    
    def set_context(self, **kwargs):
        """Set context values (campaign, operator, firmware, line_number, test_info fields)."""
        self._context.update(kwargs)
