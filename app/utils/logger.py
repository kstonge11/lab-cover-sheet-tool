"""
Debug logging for Lab Cover Sheet Tool.

Logs to both console and a rotating file in the user's home directory.
Log files are kept for troubleshooting and rotate at 5MB.

Usage:
    from app.utils.logger import logger, log_exception

    logger.debug("Detailed info for troubleshooting")
    logger.info("Normal operation messages")
    logger.warning("Something unexpected but recoverable")
    logger.error("Something failed")

    try:
        risky_operation()
    except Exception as e:
        log_exception(e, "Failed during risky operation")
"""

import logging
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ========== LOG DIRECTORY SETUP ==========

LOG_DIR = Path.home() / ".lab_cover_logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file named with date for easy identification
LOG_FILE = LOG_DIR / f"lab_cover_{datetime.now():%Y%m%d}.log"


# ========== LOGGER CONFIGURATION ==========

logger = logging.getLogger("lab_cover")
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers if module is reloaded
if not logger.handlers:
    # Console handler - INFO and above (less verbose)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        "[%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_fmt)

    # File handler - DEBUG and above (full detail)
    # Rotates at 5MB, keeps 5 backup files
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# ========== HELPER FUNCTIONS ==========

def log_exception(exc: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        exc: The exception that was caught
        context: Optional description of what was happening when the error occurred
    """
    tb = traceback.format_exc()
    if context:
        logger.error(f"{context}: {type(exc).__name__}: {exc}\n{tb}")
    else:
        logger.error(f"{type(exc).__name__}: {exc}\n{tb}")


def get_log_path() -> Path:
    """Return the current log file path for user reference."""
    return LOG_FILE


def get_log_dir() -> Path:
    """Return the log directory path for user reference."""
    return LOG_DIR


# Log startup
logger.info(f"Lab Cover Sheet Tool logger initialized. Log file: {LOG_FILE}")
