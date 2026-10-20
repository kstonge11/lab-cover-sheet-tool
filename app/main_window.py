"""
Main application window for Lab Cover Sheet Tool
"""

from dataclasses import replace

import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog,
    QFrame, QSpacerItem, QSizePolicy, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt

from .constants import WINDOW_TITLE, EXCEL_HEADER_ROW, PRINTERS
from .widgets import TestInfoBox, PlaceholderBox, AddErrorBox, QueueBox, SettingsDialog
from .services import CoverSheetService
from .utils import truncate_path, open_in_default_app, logger, log_exception, get_log_path, Config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1200, 700)
        
        logger.info("Initializing Lab Cover Sheet Tool")

        # Configuration persistence
        self.config = Config()
        saved_settings = self.config.load()

        # File tracking
        self.data_file_path = None
        self.cover_file_path = None
        self.sheet_names = []  # Cache sheet names to avoid keeping file open
        self.data_df = None
        
        # Sheet cache for optimization (avoids re-reading sheets)
        self._sheet_cache: dict = {}

        # Stored values (load from config)
        self.stored_campaign = saved_settings.get("campaign", "")
        self.stored_operator = saved_settings.get("operator", "")
        self.stored_firmware = saved_settings.get("firmware", "")
        self.stored_phase = saved_settings.get("phase", "")

        # Page count from sheet metadata (cell N6)
        self.page_count = ""

        self._setup_ui()
        self._connect_signals()
        
        # Apply loaded settings to UI
        self._apply_loaded_settings()
        
        logger.info("Lab Cover Sheet Tool initialized successfully")

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        main_layout.addWidget(self._create_top_bar())

        # Content area
        main_layout.addWidget(self._create_content_area())

    def _create_top_bar(self) -> QFrame:
        """Create the top bar with file browsers and settings inputs."""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("""
            #topBar {
                background-color: #2a2a2a;
                border-bottom: 1px solid #444;
            }
            QLabel#pathLabel {
                color: #888;
                font-size: 11px;
            }
        """)
        top_bar.setFixedHeight(120)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(12, 8, 12, 8)

        # Left: File browsers
        layout.addLayout(self._create_file_browser_section())

        # Spacer
        layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Right: Settings inputs
        layout.addLayout(self._create_settings_section())

        return top_bar

    def _create_file_browser_section(self) -> QVBoxLayout:
        """Create the file browser buttons and labels."""
        section = QVBoxLayout()
        section.setSpacing(6)

        # Data file row
        data_row = QHBoxLayout()
        data_row.setSpacing(8)

        self.browse_data_btn = QPushButton("📂 Browse Data")
        self.browse_data_btn.setFixedSize(130, 28)

        self.open_data_btn = QPushButton("📊 Open in Excel")
        self.open_data_btn.setFixedSize(130, 28)
        self.open_data_btn.setEnabled(False)

        self.data_path_label = QLabel("No data file selected")
        self.data_path_label.setObjectName("pathLabel")
        self.data_path_label.setMinimumWidth(300)

        data_row.addWidget(self.browse_data_btn)
        data_row.addWidget(self.open_data_btn)
        data_row.addWidget(self.data_path_label)
        data_row.addStretch()
        section.addLayout(data_row)

        # Cover sheet row
        cover_row = QHBoxLayout()
        cover_row.setSpacing(8)

        self.browse_cover_btn = QPushButton("📂 Browse Cover")
        self.browse_cover_btn.setFixedSize(130, 28)

        self.open_cover_btn = QPushButton("📊 Open in Excel")
        self.open_cover_btn.setFixedSize(130, 28)
        self.open_cover_btn.setEnabled(False)

        self.cover_path_label = QLabel("No cover sheet selected")
        self.cover_path_label.setObjectName("pathLabel")
        self.cover_path_label.setMinimumWidth(300)

        cover_row.addWidget(self.browse_cover_btn)
        cover_row.addWidget(self.open_cover_btn)
        cover_row.addWidget(self.cover_path_label)
        cover_row.addStretch()
        section.addLayout(cover_row)

        return section

    def _create_settings_section(self) -> QVBoxLayout:
        """Create the compact settings display with edit button."""
        section = QVBoxLayout()
        section.setSpacing(4)
        section.setContentsMargins(0, 0, 10, 0)

        # Settings display frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
            }
            QLabel#settingLabel {
                color: #888;
                font-size: 10px;
            }
            QLabel#settingValue {
                color: #4CAF50;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        frame_layout = QVBoxLayout(settings_frame)
        frame_layout.setContentsMargins(8, 6, 8, 6)
        frame_layout.setSpacing(2)

        # Create compact display rows
        def make_setting_row(label_text):
            row = QHBoxLayout()
            row.setSpacing(4)
            
            label = QLabel(f"{label_text}:")
            label.setObjectName("settingLabel")
            label.setFixedWidth(55)
            
            value = QLabel("—")
            value.setObjectName("settingValue")
            value.setMinimumWidth(80)
            
            row.addWidget(label)
            row.addWidget(value)
            row.addStretch()
            
            return row, value

        campaign_row, self.campaign_display = make_setting_row("Campaign #")
        operator_row, self.operator_display = make_setting_row("Operator")
        firmware_row, self.firmware_display = make_setting_row("Firmware")
        phase_row, self.phase_display = make_setting_row("Phase #")

        frame_layout.addLayout(campaign_row)
        frame_layout.addLayout(operator_row)
        frame_layout.addLayout(firmware_row)
        frame_layout.addLayout(phase_row)

        section.addWidget(settings_frame)

        # Edit button
        self.edit_settings_btn = QPushButton("✏️ Edit Settings")
        self.edit_settings_btn.setFixedHeight(28)
        self.edit_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #fff;
                border: 1px solid #666;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        section.addWidget(self.edit_settings_btn)

        return section

    def _create_content_area(self) -> QWidget:
        """Create the main content area with the four boxes."""
        content = QWidget()
        content.setObjectName("contentArea")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Test Info box (custom widget)
        self.test_info_box = TestInfoBox()
        layout.addWidget(self.test_info_box, stretch=2)

        '''# Printer box (placeholder for now)
        self.printer_box = PlaceholderBox("Printer", "🖨️")
        layout.addWidget(self.printer_box, stretch=1)'''

        # Add Error box
        self.error_box = AddErrorBox()
        layout.addWidget(self.error_box, stretch=2)

        # Queue box
        self.queue_box = QueueBox()
        layout.addWidget(self.queue_box, stretch=2)

        return content

    def _connect_signals(self):
        """Connect all signals to their handlers."""
        # File browsers
        self.browse_data_btn.clicked.connect(self._browse_data_file)
        self.open_data_btn.clicked.connect(lambda: open_in_default_app(self.data_file_path))
        self.browse_cover_btn.clicked.connect(self._browse_cover_file)
        self.open_cover_btn.clicked.connect(lambda: open_in_default_app(self.cover_file_path))

        # Settings edit button
        self.edit_settings_btn.clicked.connect(self._open_settings_dialog)

        # Test info box signals
        self.test_info_box.printer_changed.connect(self._on_printer_changed)
        self.test_info_box.line_changed.connect(self._on_line_changed)
        self.test_info_box.load_requested.connect(self._load_line_data)

        # Error box signals
        self.error_box.error_added.connect(self._on_error_added)

        # Queue box signals
        self.queue_box.choose_path_btn.clicked.connect(self._choose_save_path)
        self.queue_box.save_covers_requested.connect(self._save_cover_sheets)
        self.queue_box.print_requested.connect(self._print_cover_sheets)
        self.queue_box.group_by_printer_changed.connect(
            lambda checked: self.config.set("group_by_printer", checked)
        )

    # ========== FILE HANDLING ==========

    def _browse_data_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "",
            "Excel Files (*.xlsx *.xlsm);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.data_file_path = file_path
            self.data_path_label.setText(truncate_path(file_path, 50))
            self.data_path_label.setToolTip(file_path)
            self.open_data_btn.setEnabled(True)
            self._load_data_file(file_path)

    def _browse_cover_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Sheet", "",
            "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        if file_path:
            self.cover_file_path = file_path
            self.cover_path_label.setText(truncate_path(file_path, 50))
            self.cover_path_label.setToolTip(file_path)
            self.open_cover_btn.setEnabled(True)

    def _load_data_file(self, file_path: str):
        try:
            logger.info(f"Loading data file: {file_path}")
            if file_path.lower().endswith('.csv'):
                self.data_df = pd.read_csv(file_path)
                self.sheet_names = []
            else:
                # Read sheet names and close file immediately to avoid locking
                with pd.ExcelFile(file_path) as xls:
                    self.sheet_names = xls.sheet_names
                logger.debug(f"Available sheets: {self.sheet_names}")

                # Clear sheet cache when loading new file
                self._sheet_cache.clear()

                # Load error categories from the first printer sheet
                self._load_error_categories()

                self._load_printer_sheet()
                
            # Save last used path to config
            self.config.set("last_data_path", file_path)
        except Exception as e:
            log_exception(e, f"Error loading file: {file_path}")
            self.data_df = None
            self.sheet_names = []

    def _load_error_categories(self):
        if not self.data_file_path or not self.sheet_names:
            return
        try:
            first_sheet = self.test_info_box.current_printer()
            if first_sheet not in self.sheet_names:
                first_sheet = self.sheet_names[0]

            # Read ONLY rows 8-9, starting at column AF
            # Open and close file immediately to avoid locking
            df_errors = pd.read_excel(
                self.data_file_path,
                sheet_name=first_sheet,
                header=None,
                skiprows=7,   # Skip rows 1-7, start at row 8
                nrows=2,      # Only read 2 rows: categories (row 8) + error names (row 9)
                usecols=lambda x: x >= 31
            )

            if df_errors.empty or len(df_errors) < 2:
                logger.warning("No error categories found in data file")
                return

            categories = {}
            for col_idx in range(len(df_errors.columns)):
                category_name = df_errors.iloc[0, col_idx]  # Row 8 = category
                error_name = df_errors.iloc[1, col_idx]     # Row 9 = error type

                if pd.notna(category_name) and str(category_name).strip():
                    category_name = str(category_name).strip()

                    if pd.notna(error_name) and str(error_name).strip():
                        error_name = str(error_name).strip()

                        # Append error to category's list
                        if category_name not in categories:
                            categories[category_name] = []
                        categories[category_name].append(error_name)

            self.error_box.set_error_categories(categories)

            logger.debug(f"Loaded {len(categories)} error categories")
            for cat, errs in categories.items():
                logger.debug(f"  {cat}: {errs}")

        except Exception as e:
            log_exception(e, "Error loading error categories")
            self.error_box.set_error_categories({})

    def _load_printer_sheet(self):
        if not self.data_file_path or not self.sheet_names:
            return

        selected_printer = self.test_info_box.current_printer()

        if selected_printer not in self.sheet_names:
            logger.warning(f"Sheet '{selected_printer}' not found in workbook")
            self.data_df = None
            self.test_info_box.clear_all_fields()
            return

        try:
            # Check cache first for optimization
            if selected_printer in self._sheet_cache:
                self.data_df = self._sheet_cache[selected_printer]
                logger.debug(f"Loaded '{selected_printer}' from cache")
            else:
                # Open and close file immediately to avoid locking
                self.data_df = pd.read_excel(
                    self.data_file_path,
                    sheet_name=selected_printer,
                    header=EXCEL_HEADER_ROW
                )
                # Cache the sheet for future use
                self._sheet_cache[selected_printer] = self.data_df
                logger.info(f"Loaded {len(self.data_df)} rows from '{selected_printer}'")
            
            self.test_info_box.set_max_lines(len(self.data_df))
            self.test_info_box.set_line(1)

            # Read page count from cell N6 using pandas
            self._load_page_count(selected_printer)

            self._load_line_data()
        except Exception as e:
            log_exception(e, f"Error loading sheet '{selected_printer}'")
            self.data_df = None

    def _load_page_count(self, sheet_name: str):
        """Load page count from cell N6 of the specified sheet using pandas (fast)."""
        try:
            # Read just row 6 (0-indexed row 5), no header, single row
            # Column N is index 13 (0-indexed)
            # Open and close file immediately to avoid locking
            df_row = pd.read_excel(
                self.data_file_path,
                sheet_name=sheet_name,
                header=None,
                skiprows=5,  # Skip rows 1-5 (0-indexed 0-4)
                nrows=1      # Read only 1 row (row 6)
            )

            # Column N = index 13
            if len(df_row.columns) > 13:
                page_count_value = df_row.iloc[0, 13]
                if pd.notna(page_count_value):
                    self.page_count = str(int(page_count_value) if isinstance(page_count_value, float) else page_count_value)
                    self.test_info_box.set_page_count(self.page_count)
                    logger.debug(f"Page count from N6: {self.page_count}")
                    return

            self.page_count = "—"
            self.test_info_box.set_page_count("—")
        except Exception as e:
            log_exception(e, f"Error reading page count from '{sheet_name}'")
            self.page_count = "—"
            self.test_info_box.set_page_count("—")

    # ========== DATA LOADING ==========

    def _on_printer_changed(self, printer_name: str):
        logger.info(f"Printer changed to: {printer_name}")
        if self.data_file_path and self.sheet_names:
            self._load_printer_sheet()

    def _on_line_changed(self, value: int):
        self._load_line_data()
        self._update_error_context()

    def _load_line_data(self):
        if self.data_df is None:
            return

        row_index = self.test_info_box.current_line() - 1
        if row_index < 0 or row_index >= len(self.data_df):
            self.test_info_box.clear_all_fields()
            return

        row = self.data_df.iloc[row_index]

        for field_name in self.test_info_box.get_all_field_names():
            columns = self.test_info_box.get_field_columns(field_name)

            if "_STORED_OPERATOR_" in columns:
                value = self.stored_operator if self.stored_operator else "—"
            else:
                value = "—"
                for col in columns:
                    if col in row.index and pd.notna(row[col]):
                        value = str(row[col])
                        break

            self.test_info_box.set_field_value(field_name, value)

    # ========== SETTINGS ==========

    def _open_settings_dialog(self):
        """Open the settings dialog to edit session values."""
        dialog = SettingsDialog(
            self,
            campaign=self.stored_campaign,
            operator=self.stored_operator,
            firmware=self.stored_firmware,
            phase=self.stored_phase
        )

        if dialog.exec():
            values = dialog.get_values()
            self._apply_settings(values)

    def _apply_settings(self, values: dict):
        """Apply settings from the dialog."""
        # Update stored values
        self.stored_campaign = values["campaign"]
        self.stored_operator = values["operator"]
        self.stored_firmware = values["firmware"]
        self.stored_phase = values["phase"]

        # Update display labels
        self.campaign_display.setText(self.stored_campaign if self.stored_campaign else "—")
        self.operator_display.setText(self.stored_operator if self.stored_operator else "—")
        self.firmware_display.setText(self.stored_firmware if self.stored_firmware else "—")
        self.phase_display.setText(self.stored_phase if self.stored_phase else "—")

        # Update test info if loaded
        if self.data_df is not None:
            if self.stored_operator:
                self.test_info_box.set_field_value("Operator", self.stored_operator)

        # Update error context
        self._update_error_context()
        
        # Save settings to config file for persistence
        self.config.save({
            "campaign": self.stored_campaign,
            "operator": self.stored_operator,
            "firmware": self.stored_firmware,
            "phase": self.stored_phase,
        })

        logger.info(f"Settings updated: Campaign={self.stored_campaign}, Op={self.stored_operator}, FW={self.stored_firmware}, Phase={self.stored_phase}")

    # ========== ERROR HANDLING ==========

    def _update_error_context(self):
        """Update the error box with current context including test info."""
        # Get test info values from the test info box
        test_values = self.test_info_box.get_all_values()

        # Use stored_phase if set, otherwise fall back to test_values
        phase_value = self.stored_phase if self.stored_phase else test_values.get("Phase", "")

        self.error_box.set_context(
            campaign=self.stored_campaign,
            operator=self.stored_operator,
            firmware=self.stored_firmware,
            line_number=self.test_info_box.current_line(),
            # Test info fields - map display names to context keys
            climate=test_values.get("Climate", ""),
            media=test_values.get("Media #", ""),
            script=test_values.get("Script #", ""),
            plexity=test_values.get("Plexity", ""),
            load=test_values.get("Load #", ""),
            run=test_values.get("Run #", ""),
            phase=phase_value,
        )

    def _on_error_added(self, entry):
        """Handle when an error is added from the error box."""
        self.queue_box.add_entry(entry)

    def _choose_save_path(self):
        """Open dialog to choose save path for cover sheets."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Choose Save Location for Cover Sheets",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.queue_box.set_save_path(path)
            self.config.set("last_save_dir", path)
            logger.info(f"Save path set to: {path}")

    def _save_cover_sheets(self, queue):
        """Generate and save cover sheets to the chosen path."""
        if not queue:
            logger.warning("No errors to save - queue is empty")
            return

        if not self.cover_file_path:
            logger.warning("No cover sheet template loaded")
            self._show_warning("No Cover Sheet", "Load a cover sheet template first.")
            return

        save_path = self.queue_box.get_save_path()
        if not save_path:
            logger.warning("No save path selected")
            self._show_warning("No Save Location", "Choose a save location first.")
            return

        logger.info(f"Saving {len(queue)} cover sheets to: {save_path}")
        
        # Create service and save files
        service = CoverSheetService(self.cover_file_path)

        total_saved = 0
        saved_files = []
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for entry in queue:
                files = service.save_from_entry(entry, save_path)
                saved_files.extend(files)
                total_saved += len(files)
        except Exception as e:
            log_exception(e, "Error saving cover sheets")
            QApplication.restoreOverrideCursor()
            self._show_warning(
                "Save Failed",
                f"Saved {total_saved} cover sheet(s) before an error occurred:\n{e}"
            )
            return
        QApplication.restoreOverrideCursor()

        logger.info(f"Saved {total_saved} cover sheets to: {save_path}")
        for f in saved_files:
            logger.debug(f"  Saved: {f}")

    def _print_cover_sheets(self, queue):
        """Generate and print cover sheets for queued errors."""
        if not queue:
            logger.warning("No errors to print - queue is empty")
            return

        if not self.cover_file_path:
            logger.warning("No cover sheet template loaded")
            self._show_warning("No Cover Sheet", "Load a cover sheet template first.")
            return

        group_by_printer = self.queue_box.group_by_printer()
        jobs = self._print_order(queue, group_by_printer)
        logger.info(
            f"Printing {len(jobs)} cover sheets from {len(queue)} queued items"
            f"{' (grouped by printer)' if group_by_printer else ''}..."
        )
        
        # Create service with the template (temp files deleted after printing)
        service = CoverSheetService(self.cover_file_path, keep_files=False)

        failed = []  # (entry, printer) pairs that did not print
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for entry, printer in jobs:
                try:
                    ok = service.print_entry_for_printer(entry, printer)
                except Exception as e:
                    log_exception(e, f"Error printing {entry.error_type} on {printer}")
                    ok = False
                if not ok:
                    failed.append((entry, printer))
        finally:
            QApplication.restoreOverrideCursor()

        total_printed = len(jobs) - len(failed)
        logger.info(f"Printed {total_printed} of {len(jobs)} cover sheets")
        
        if failed:
            # Keep only the sheets that did not print, so a retry doesn't reprint the rest
            remaining = []
            for entry in queue:
                failed_printers = [p for e, p in failed if e is entry]
                if failed_printers:
                    remaining.append(replace(entry, printers=failed_printers))
            self.queue_box.set_entries(remaining)
            self._show_warning(
                "Print Problem",
                f"Printed {total_printed} of {len(jobs)} cover sheet(s). "
                "The sheets that didn't print are still in the queue so you can try again.\n\n"
                "Check that Microsoft Excel is installed and a default printer is set."
            )
            return

        # Clear the queue after successful print
        self.queue_box.clear()
        logger.info("Queue cleared after printing")

    @staticmethod
    def _print_order(queue, group_by_printer: bool):
        """
        Return (entry, printer) pairs in print order.

        Default: queue order, each entry's printers together.
        Grouped: all sheets for the first printer (in PRINTERS order), then the
        next printer, keeping queue order within each printer.
        """
        if not group_by_printer:
            return [(entry, printer) for entry in queue for printer in entry.printers]

        def printer_rank(printer):
            return PRINTERS.index(printer) if printer in PRINTERS else len(PRINTERS)

        printers = sorted(
            {p for entry in queue for p in entry.printers},
            key=lambda p: (printer_rank(p), p)
        )
        return [(entry, printer) for printer in printers for entry in queue if printer in entry.printers]
    
    # ========== HELPER METHODS ==========

    def _show_warning(self, title: str, message: str):
        """Show a warning dialog, pointing to the log file for details."""
        QMessageBox.warning(self, title, f"{message}\n\nDetails are in the log file:\n{get_log_path()}")
    
    def _apply_loaded_settings(self):
        """Apply settings loaded from config to the UI."""
        self.queue_box.set_group_by_printer(bool(self.config.get("group_by_printer")))
        self.campaign_display.setText(self.stored_campaign if self.stored_campaign else "—")
        self.operator_display.setText(self.stored_operator if self.stored_operator else "—")
        self.firmware_display.setText(self.stored_firmware if self.stored_firmware else "—")
        self.phase_display.setText(self.stored_phase if self.stored_phase else "—")
        
        if any([self.stored_campaign, self.stored_operator, self.stored_firmware, self.stored_phase]):
            logger.info(f"Restored settings: Campaign={self.stored_campaign}, Op={self.stored_operator}")
