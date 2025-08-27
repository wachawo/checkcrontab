#!/usr/bin/env python3
"""
Module for logging configuration and colored output
"""

import copy
import logging
import platform
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Windows version constants
WINDOWS_MAJOR_VERSION = 10
WINDOWS_BUILD_VERSION = 10586


class ColoredFormatter(logging.Formatter):
    """Enhanced colored formatter with Windows support"""

    def __init__(self, fmt: Optional[str] = None, use_colors: bool = True, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(fmt, **kwargs)
        self._use_color = use_colors and self._get_color_compatibility()
        self.COLORS = {
            "DEBUG": "\033[0;36m",  # CYAN
            "INFO": "\033[0;32m",  # GREEN
            "WARNING": "\033[0;33m",  # YELLOW
            "ERROR": "\033[0;31m",  # RED
            "CRITICAL": "\033[0;37;41m",  # WHITE ON RED
            "RESET": "\033[0m",  # RESET COLOR
        }

    @classmethod
    def _get_color_compatibility(cls) -> bool:
        """Check if system supports ANSI colors"""
        # Always use colors on Unix-like systems
        if platform.system().lower() != "windows":
            return True

        # Check Windows version for ANSI support
        try:
            if hasattr(sys, "getwindowsversion"):
                win = sys.getwindowsversion()
                # Windows 10 version 1511+ supports ANSI colors
                if win.major >= WINDOWS_MAJOR_VERSION and win.build >= WINDOWS_BUILD_VERSION:
                    return True
        except Exception:
            pass

        return False

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors if supported"""
        if not self._use_color:
            return super().format(record)

        # Create a copy to avoid modifying the original record
        colored_record = copy.copy(record)
        levelname = colored_record.levelname

        # Apply color to levelname
        color_seq = self.COLORS.get(levelname, self.COLORS["RESET"])
        colored_record.levelname = f"{color_seq}{levelname}{self.COLORS['RESET']}"

        return super().format(colored_record)


def setup_logging(debug: bool = False, no_colors: bool = False, use_stderr: bool = True) -> None:
    """Setup logging configuration with colored formatter"""
    # Set logging level
    level = logging.DEBUG if debug else logging.INFO

    # Choose output stream
    stream = sys.stderr if use_stderr else sys.stdout

    # Configure logging
    logging.basicConfig(handlers=[logging.StreamHandler(stream)], level=level, format="%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Apply colored formatter
    colored_formatter = ColoredFormatter(fmt="%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", use_colors=not no_colors)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(colored_formatter)
