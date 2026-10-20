"""
File utility functions for Lab Cover Sheet Tool
"""

import os
import platform
import subprocess

from .logger import logger, log_exception

# Only these file types may be handed to the OS to open, so a mistaken
# "All Files" pick (e.g. an .exe or .bat) is never launched
OPENABLE_EXTENSIONS = {".xlsx", ".xlsm", ".csv"}


def truncate_path(path: str, max_length: int = 50) -> str:
    """Truncate path for display, keeping filename visible."""
    if len(path) <= max_length:
        return path
    
    filename = os.path.basename(path)
    if len(filename) >= max_length - 5:
        return "..." + filename[-(max_length - 3):]
    
    remaining = max_length - len(filename) - 4  # 4 for ".../"
    return path[:remaining] + ".../" + filename


def open_in_default_app(file_path: str) -> bool:
    """
    Open the specified file in the system's default application.
    Returns True on success, False on failure.
    """
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"Cannot open file - path invalid or missing: {file_path}")
        return False

    if os.path.splitext(file_path)[1].lower() not in OPENABLE_EXTENSIONS:
        logger.warning(f"Refusing to open non-spreadsheet file: {file_path}")
        return False

    try:
        logger.debug(f"Opening file in default app: {file_path}")
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        else:  # Linux
            subprocess.run(["xdg-open", file_path], check=True)
        logger.info(f"Opened file: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        log_exception(e, f"Error opening file: {file_path}")
        return False
