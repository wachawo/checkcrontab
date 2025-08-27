#!/usr/bin/env python3
"""
Checkcrontab package
"""

__version__ = "0.0.8"
__description__ = "A Python script for checking syntax of crontab files"
__author__ = "Aleksandr Pimenov"
__email__ = "wachawo@gmail.com"
__url__ = "https://github.com/wachawo/checkcrontab"

# Import main functions
from . import checker, logging_config, main

__all__ = [
    "main",
    "checker",
    "logging_config",
    "__version__",
    "__description__",
    "__author__",
    "__email__",
]
