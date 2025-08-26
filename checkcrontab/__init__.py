#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkcrontab package
"""

__version__ = "0.0.2"
__description__ = "A Python script for checking syntax of crontab files"
__author__ = 'Aleksandr Pimenov'
__email__ = 'wachawo@gmail.com'

# Import main functions
from . import main
from . import checker
from . import logging_config

__all__ = [
    "main",
    "checker",
    "logging_config",
    "__version__",
    "__description__",
    "__author__",
    "__email__",
]
