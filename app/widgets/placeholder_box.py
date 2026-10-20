"""
Placeholder box widget for features coming soon.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class PlaceholderBox(QFrame):
    """A placeholder box for future functionality."""

    STYLESHEET = """
        #placeholderBox {
            background-color: #333;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QLabel#boxTitle {
            font-size: 14px;
            font-weight: bold;
            color: #fff;
        }
        QLabel#placeholder {
            color: #666;
            font-size: 12px;
        }
    """

    def __init__(self, title: str, icon: str, parent=None):
        super().__init__(parent)
        self.setObjectName("placeholderBox")
        self.setStyleSheet(self.STYLESHEET)
        self._setup_ui(title, icon)

    def _setup_ui(self, title: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(10)

        # Title
        title_label = QLabel(f"{icon} {title}")
        title_label.setObjectName("boxTitle")
        layout.addWidget(title_label)

        # Placeholder text
        placeholder = QLabel("Coming soon...")
        placeholder.setObjectName("placeholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)

        layout.addStretch()
