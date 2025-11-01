#!/usr/bin/env python3

import logging
import platform
import sys
from unittest.mock import MagicMock, patch

import pytest
from checkcrontab.logger import ColoredFormatter, setup_logging

# Mock the getwindowsversion function if it doesn't exist (i.e., on non-Windows platforms)
if not hasattr(sys, "getwindowsversion"):

    class MockWindowsVersion:
        def __init__(self, major, build):
            self.major = major
            self.build = build

    sys.getwindowsversion = MagicMock(return_value=MockWindowsVersion(10, 10586))


class TestColoredFormatter:
    @pytest.fixture
    def log_record(self):
        return logging.LogRecord(
            "test", logging.INFO, "/test", 1, "test message", None, None
        )

    def test_formatter_no_color(self, log_record):
        formatter = ColoredFormatter(fmt="%(message)s", use_colors=False)
        formatted_message = formatter.format(log_record)
        assert formatted_message == "test message"
        assert "\033" not in formatted_message

    def test_formatter_with_color(self, log_record):
        formatter = ColoredFormatter(fmt="%(levelname)s: %(message)s", use_colors=True)
        with patch("platform.system", return_value="Linux"):
            formatted_message = formatter.format(log_record)
            assert "test message" in formatted_message
            assert "\033[0;32mINFO\033[0m" in formatted_message

    @patch("platform.system", return_value="Windows")
    def test_windows_color_compatibility_supported(self, mock_system, log_record):
        with patch(
            "sys.getwindowsversion",
            return_value=MagicMock(major=10, build=10586),
        ):
            formatter = ColoredFormatter(
                fmt="%(levelname)s: %(message)s", use_colors=True
            )
            assert formatter._get_color_compatibility() is True
            formatted_message = formatter.format(log_record)
            assert "\033[0;32mINFO\033[0m" in formatted_message

    @patch("platform.system", return_value="Windows")
    def test_windows_color_compatibility_not_supported(self, mock_system, log_record):
        with patch(
            "sys.getwindowsversion",
            return_value=MagicMock(major=10, build=10000),
        ):
            formatter = ColoredFormatter(fmt="%(message)s", use_colors=True)
            assert formatter._get_color_compatibility() is False
            formatted_message = formatter.format(log_record)
            assert "\033" not in formatted_message

    @patch("platform.system", return_value="Windows")
    def test_windows_color_compatibility_exception(self, mock_system, log_record):
        with patch("sys.getwindowsversion", side_effect=Exception()):
            formatter = ColoredFormatter(fmt="%(message)s", use_colors=True)
            assert formatter._get_color_compatibility() is False
            formatted_message = formatter.format(log_record)
            assert "\033" not in formatted_message


class TestSetupLogging:
    @patch("logging.basicConfig")
    def test_setup_logging_debug(self, mock_basic_config):
        setup_logging(debug=True)
        mock_basic_config.assert_called_once()
        assert mock_basic_config.call_args[1]["level"] == logging.DEBUG

    @patch("logging.basicConfig")
    def test_setup_logging_info(self, mock_basic_config):
        setup_logging(debug=False)
        mock_basic_config.assert_called_once()
        assert mock_basic_config.call_args[1]["level"] == logging.INFO

    @patch("logging.StreamHandler", MagicMock())
    @patch("logging.basicConfig")
    def test_setup_logging_stderr(self, mock_basic_config):
        with patch("sys.stderr") as mock_stderr:
            setup_logging(use_stderr=True)
            logging.StreamHandler.assert_called_with(mock_stderr)

    @patch("logging.StreamHandler", MagicMock())
    @patch("logging.basicConfig")
    def test_setup_logging_stdout(self, mock_basic_config):
        with patch("sys.stdout") as mock_stdout:
            setup_logging(use_stderr=False)
            logging.StreamHandler.assert_called_with(mock_stdout)
