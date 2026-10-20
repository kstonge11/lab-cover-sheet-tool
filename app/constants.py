"""
Constants and configuration for Lab Cover Sheet Tool
"""

APP_NAME = "Lab Cover Sheet Tool"
APP_VERSION = "1.0.6"
WINDOW_TITLE = f"{APP_NAME} V.{APP_VERSION}"

# Printer units under test (one sheet per unit in the tracking workbook)
PRINTERS = [f"UNIT{n:03d}" for n in range(1, 9)]

# Short names for printer checkboxes
PRINTER_SHORT_NAMES = [p[-3:] for p in PRINTERS]

# Excel data row where headers are located (0-indexed)
EXCEL_HEADER_ROW = 8

# Field definitions for Test Info box
# Format: (display_name, [possible_column_names])
TEST_INFO_FIELDS = {
    "Test Setup": [
        ("Operator", ["_STORED_OPERATOR_"]),
        ("Climate", ["Environment"]),
        ("Unit", ["Unit"]),
        ("Media #", ["Media_Number*"]),
        ("Script #", ["Suite_ID*"]),
        ("Plexity", ["Print_Options*"]),
        ("Load #", ["Load_NR*"]),
        ("Run #", ["Run_NR*"]),
        ("Phase", ["Load_Phase"]),
        ("Firmware", ["Firmware"]),
    ]
}
