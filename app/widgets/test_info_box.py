"""
Test Info box widget with printer selector and data fields.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QPushButton, QScrollArea,
    QWidget, QGridLayout
)
from PyQt6.QtCore import pyqtSignal

from ..constants import PRINTERS, TEST_INFO_FIELDS


class TestInfoBox(QFrame):
    """Widget displaying test information with printer and line selection."""

    # Signals
    printer_changed = pyqtSignal(str)
    line_changed = pyqtSignal(int)
    load_requested = pyqtSignal()

    STYLESHEET = """
        #testInfoBox {
            background-color: #333;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QLabel#boxTitle {
            font-size: 14px;
            font-weight: bold;
            color: #fff;
        }
        QLabel#sectionTitle {
            font-size: 11px;
            font-weight: bold;
            color: #888;
            padding-top: 6px;
        }
        QLabel#fieldLabel {
            color: #aaa;
            font-size: 20px;
        }
        QLabel#fieldValue {
            color: #4CAF50;
            font-size: 15px;
            font-weight: bold;
        }
        QLabel#pageCountLabel {
            color: #aaa;
            font-size: 12px;
        }
        QLabel#pageCountValue {
            color: #FF9800;
            font-size: 14px;
            font-weight: bold;
        }
        QComboBox {
            min-width: 120px;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("testInfoBox")
        self.setStyleSheet(self.STYLESHEET)

        self.field_values = {}  # Stores {display_name: {"label": QLabel, "columns": [...]}}
        self._page_count_label = None  # Will store the page count value label
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("📋 Test Info")
        title.setObjectName("boxTitle")
        layout.addWidget(title)

        # Selector row
        layout.addLayout(self._create_selector_row())

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #555;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Scrollable fields area
        layout.addWidget(self._create_fields_scroll())

    def _create_selector_row(self) -> QHBoxLayout:
        """Create the printer and line selector row."""
        selector_row = QHBoxLayout()
        selector_row.setSpacing(15)

        # Printer selector
        printer_section = QHBoxLayout()
        printer_section.setSpacing(6)

        printer_label = QLabel("Printer:")
        printer_label.setStyleSheet("color: #fff;")

        self.printer_combo = QComboBox()
        self.printer_combo.addItems(PRINTERS)
        self.printer_combo.setFixedWidth(130)

        printer_section.addWidget(printer_label)
        printer_section.addWidget(self.printer_combo)
        selector_row.addLayout(printer_section)

        # Separator line
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #555;")
        sep.setFixedWidth(1)
        selector_row.addWidget(sep)

        # Line # selector
        line_section = QHBoxLayout()
        line_section.setSpacing(6)

        line_label = QLabel("Line #:")
        line_label.setStyleSheet("color: #fff;")

        self.line_spinbox = QSpinBox()
        self.line_spinbox.setMinimum(1)
        self.line_spinbox.setMaximum(9999)
        self.line_spinbox.setValue(1)
        self.line_spinbox.setFixedWidth(70)

        self.load_btn = QPushButton("Load")
        self.load_btn.setFixedSize(60, 26)

        line_section.addWidget(line_label)
        line_section.addWidget(self.line_spinbox)
        line_section.addWidget(self.load_btn)

        selector_row.addLayout(line_section)
        selector_row.addStretch()

        return selector_row

    def _create_fields_scroll(self) -> QScrollArea:
        """Create the scrollable area containing all data fields."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget { 
                background-color: transparent;
            }
        """)

        scroll_content = QWidget()
        fields_layout = QVBoxLayout(scroll_content)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(4)

        for group_name, fields in TEST_INFO_FIELDS.items():
            # Section header
            section_label = QLabel(group_name)
            section_label.setObjectName("sectionTitle")
            fields_layout.addWidget(section_label)

            # Grid for fields
            grid = QGridLayout()
            grid.setSpacing(4)
            grid.setColumnMinimumWidth(0, 70)
            grid.setColumnStretch(1, 1)

            for i, (display_name, column_names) in enumerate(fields):
                label = QLabel(f"{display_name}:")
                label.setObjectName("fieldLabel")

                value = QLabel("—")
                value.setObjectName("fieldValue")

                grid.addWidget(label, i, 0)
                grid.addWidget(value, i, 1)

                self.field_values[display_name] = {
                    "label": value,
                    "columns": column_names
                }

            # Add Page Count after Firmware (at the end of the grid)
            page_count_row = len(fields)
            page_count_label = QLabel("Page Count:")
            page_count_label.setObjectName("pageCountLabel")
            
            self._page_count_label = QLabel("—")
            self._page_count_label.setObjectName("pageCountValue")
            
            grid.addWidget(page_count_label, page_count_row, 0)
            grid.addWidget(self._page_count_label, page_count_row, 1)

            fields_layout.addLayout(grid)

        fields_layout.addStretch()
        scroll.setWidget(scroll_content)
        return scroll

    def _connect_signals(self):
        self.printer_combo.currentTextChanged.connect(self.printer_changed.emit)
        self.line_spinbox.valueChanged.connect(self.line_changed.emit)
        self.load_btn.clicked.connect(self.load_requested.emit)

    # Public API
    def current_printer(self) -> str:
        return self.printer_combo.currentText()

    def current_line(self) -> int:
        return self.line_spinbox.value()

    def set_max_lines(self, max_val: int):
        self.line_spinbox.setMaximum(max_val)

    def set_line(self, value: int):
        self.line_spinbox.setValue(value)

    def set_field_value(self, field_name: str, value: str):
        """Set the value of a specific field."""
        if field_name in self.field_values:
            self.field_values[field_name]["label"].setText(value)

    def get_field_columns(self, field_name: str) -> list:
        """Get the column names for a field."""
        if field_name in self.field_values:
            return self.field_values[field_name]["columns"]
        return []

    def clear_all_fields(self):
        """Reset all fields to default value."""
        for field_info in self.field_values.values():
            field_info["label"].setText("—")

    def get_all_field_names(self) -> list:
        """Return all field display names."""
        return list(self.field_values.keys())
    
    def get_field_value(self, field_name: str) -> str:
        """Get the current value of a specific field."""
        if field_name in self.field_values:
            return self.field_values[field_name]["label"].text()
        return ""
    
    def get_all_values(self) -> dict:
        """Return all field values as a dictionary."""
        return {name: info["label"].text() for name, info in self.field_values.items()}
    
    def set_page_count(self, value: str):
        """Set the page count display value."""
        if self._page_count_label:
            self._page_count_label.setText(value)
