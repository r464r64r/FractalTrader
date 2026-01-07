"""Centralized logging configuration for FractalTrader.

This module provides a unified logging setup function that configures both file
and console logging with rotation support.

Usage:
    from live.logging_config import setup_logging

    # Basic setup
    setup_logging()

    # Custom log level and file
    setup_logging(log_level="DEBUG", log_file="/custom/path.log")

    # Console only (no file)
    setup_logging(log_file=None)
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "/tmp/bot_v2.log",
    console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure application-wide logging.

    Sets up logging handlers for both file and console output with consistent
    formatting across all modules. Uses rotating file handler to prevent
    unbounded log file growth.

    Args:
        log_level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_file: Path to log file. None disables file logging.
        console: Enable console (stdout) logging
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Example:
        >>> setup_logging(log_level="DEBUG", log_file="/tmp/myapp.log")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Clear existing handlers to prevent duplicates
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    # Standard format with timestamp, module name, level, and message
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Capture everything to file
        root_logger.addHandler(file_handler)

    # Console handler (stdout)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)
