#!/usr/bin/env python3
"""
Lab Cover Sheet Tool

Desktop tool for a printer test lab: technicians log print defects against
a test run and print matching cover sheets for the physical samples.

Author: Kelly St.Onge
"""

import sys
from PyQt6.QtWidgets import QApplication
import qdarktheme

from app import MainWindow


def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
