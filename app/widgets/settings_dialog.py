"""
Settings dialog for editing Campaign #, Operator, Firmware, and Phase#.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    """Modal dialog for editing test session settings."""

    STYLESHEET = """
        QDialog {
            background-color: #2a2a2a;
        }
        QLabel#dialogTitle {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            padding-bottom: 10px;
        }
        QLabel#fieldLabel {
            color: #ccc;
            font-size: 12px;
        }
        QLineEdit {
            background-color: #3a3a3a;
            color: #fff;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border: 1px solid #4CAF50;
        }
        QPushButton#saveBtn {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
            font-weight: bold;
        }
        QPushButton#saveBtn:hover {
            background-color: #45a049;
        }
        QPushButton#cancelBtn {
            background-color: #555;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
        }
        QPushButton#cancelBtn:hover {
            background-color: #666;
        }
    """

    def __init__(self, parent=None, campaign="", operator="", firmware="", phase=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Settings")
        self.setModal(True)
        self.setFixedSize(350, 280)
        self.setStyleSheet(self.STYLESHEET)

        # Store initial values
        self._initial_values = {
            "campaign": campaign,
            "operator": operator,
            "firmware": firmware,
            "phase": phase
        }

        self._setup_ui()
        self._load_values()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("⚙️ Session Settings")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        # Form grid
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnMinimumWidth(0, 80)

        # Campaign #
        campaign_label = QLabel("Campaign #:")
        campaign_label.setObjectName("fieldLabel")
        self.campaign_input = QLineEdit()
        self.campaign_input.setPlaceholderText("Enter Campaign #")
        grid.addWidget(campaign_label, 0, 0)
        grid.addWidget(self.campaign_input, 0, 1)

        # Operator
        operator_label = QLabel("Operator:")
        operator_label.setObjectName("fieldLabel")
        self.operator_input = QLineEdit()
        self.operator_input.setPlaceholderText("Enter Operator Name")
        grid.addWidget(operator_label, 1, 0)
        grid.addWidget(self.operator_input, 1, 1)

        # Firmware
        firmware_label = QLabel("Firmware:")
        firmware_label.setObjectName("fieldLabel")
        self.firmware_input = QLineEdit()
        self.firmware_input.setPlaceholderText("Enter Firmware")
        grid.addWidget(firmware_label, 2, 0)
        grid.addWidget(self.firmware_input, 2, 1)

        # Phase #
        phase_label = QLabel("Phase #:")
        phase_label.setObjectName("fieldLabel")
        self.phase_input = QLineEdit()
        self.phase_input.setPlaceholderText("Enter Phase #")
        grid.addWidget(phase_label, 3, 0)
        grid.addWidget(self.phase_input, 3, 1)

        layout.addLayout(grid)

        # Spacer
        layout.addStretch()

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _load_values(self):
        """Load initial values into the form."""
        self.campaign_input.setText(self._initial_values["campaign"])
        self.operator_input.setText(self._initial_values["operator"])
        self.firmware_input.setText(self._initial_values["firmware"])
        self.phase_input.setText(self._initial_values["phase"])

    def get_values(self) -> dict:
        """Return the current values from the form."""
        return {
            "campaign": self.campaign_input.text().strip(),
            "operator": self.operator_input.text().strip(),
            "firmware": self.firmware_input.text().strip(),
            "phase": self.phase_input.text().strip()
        }
