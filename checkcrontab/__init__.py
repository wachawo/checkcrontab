#!/usr/bin/env python3
"""
Checkcrontab package
"""

__version__ = "0.0.12"
__description__ = "A Python script for checking syntax of crontab files"
__author__ = "Aleksandr Pimenov"
__email__ = "wachawo@gmail.com"
__url__ = "https://github.com/wachawo/checkcrontab"

# Import main functions
from . import checker, logger, main

__all__ = [
    "main",
    "checker",
    "logger",
    "__version__",
    "__description__",
    "__author__",
    "__email__",
]
