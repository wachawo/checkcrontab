#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functional tests for checkcrontab package
"""
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock


# Add the checkcrontab directory to the path so we can import main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
checkcrontab_dir = os.path.join(current_dir, 'checkcrontab')

# Import the main module directly
if checkcrontab_dir not in sys.path:
    sys.path.insert(0, checkcrontab_dir)

import main as main_module

# Import all needed functions
from main import (
    parse_cron_line,
    validate_cron_entry,
    validate_time_field,
    check_cron_daemon,
    check_system_crontab_permissions,
    system_cron_entry,
    user_cron_entry,
    check_crontab_file,
)


def test_parse_cron_line_standard_user():
    """Test parsing standard user crontab line"""
    errors = []
    line = "0 2 * * * /usr/bin/backup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is not None
    assert entry.minute == "0"
    assert entry.hour == "2"
    assert entry.day == "*"
    assert entry.month == "*"
    assert entry.weekday == "*"
    assert entry.command == "/usr/bin/backup.sh"
    assert len(errors) == 0


def test_parse_cron_line_standard_system():
    """Test parsing standard system crontab line"""
    errors = []
    line = "0 2 * * * root /usr/bin/backup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=True)

    assert entry is not None
    assert entry.minute == "0"
    assert entry.hour == "2"
    assert entry.day == "*"
    assert entry.month == "*"
    assert entry.weekday == "*"
    assert entry.user == "root"
    assert entry.command == "/usr/bin/backup.sh"
    assert len(errors) == 0


def test_parse_cron_line_special_keyword_user():
    """Test parsing special keyword in user crontab"""
    errors = []
    line = "@reboot /usr/bin/startup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is not None
    assert entry.minute == "@reboot"
    assert entry.command == "/usr/bin/startup.sh"
    assert len(errors) == 0


def test_parse_cron_line_special_keyword_system():
    """Test parsing special keyword in system crontab"""
    errors = []
    line = "@reboot root /usr/bin/startup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=True)

    assert entry is not None
    assert entry.minute == "@reboot"
    assert entry.user == "root"
    assert entry.command == "/usr/bin/startup.sh"
    assert len(errors) == 0


def test_parse_cron_line_invalid_special_keyword():
    """Test parsing invalid special keyword"""
    errors = []
    line = "@invalid root /usr/bin/script.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=True)

    assert entry is None
    assert len(errors) == 1
    assert "invalid special keyword" in errors[0]


def test_parse_cron_line_insufficient_fields_user():
    """Test parsing user crontab with insufficient fields"""
    errors = []
    line = "0 2 * * /usr/bin/backup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is None
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_parse_cron_line_insufficient_fields_system():
    """Test parsing system crontab with insufficient fields"""
    errors = []
    line = "0 2 * * * /usr/bin/backup.sh"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=True)

    assert entry is None
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_parse_cron_line_comment():
    """Test parsing comment line"""
    errors = []
    line = "# This is a comment"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is None
    assert len(errors) == 0


def test_parse_cron_line_empty():
    """Test parsing empty line"""
    errors = []
    line = ""
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is None
    assert len(errors) == 0


def test_parse_cron_line_environment_variable():
    """Test parsing environment variable line"""
    errors = []
    line = "PATH=/usr/bin:/usr/local/bin"
    entry = parse_cron_line(line, 1, "test.txt", errors, is_system_crontab=False)

    assert entry is None
    assert len(errors) == 0


def test_validate_time_field_valid():
    """Test validating valid time fields"""
    valid_fields = [
        ("0", "minutes", r'^(\*|([0-5]?[0-9])(-([0-5]?[0-9]))?(,([0-5]?[0-9])(-([0-5]?[0-9]))?)*|\*/([0-5]?[0-9]))$'),
        ("*", "hours", r'^(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?)*|\*/([0-9]|1[0-9]|2[0-3]))$'),
        ("1-5", "day of month", r'^(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?)*|\*/([1-9]|[12][0-9]|3[01]))$'),
        ("1,3,5", "month", r'^(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?)*|\*/([1-9]|1[0-2]))$'),
        ("*/2", "day of week", r'^(\*|([0-7])(-([0-7]))?(,([0-7])(-([0-7]))?)*|\*/([0-7]))$'),
    ]

    for value, field_name, pattern in valid_fields:
        errors = []
        result = validate_time_field(value, field_name, pattern, 1, "test.txt", errors)
        assert result, f"Field {field_name} with value '{value}' should be valid"
        assert len(errors) == 0


def test_validate_time_field_invalid():
    """Test validating invalid time fields"""
    invalid_fields = [
        ("60", "minutes", r'^(\*|([0-5]?[0-9])(-([0-5]?[0-9]))?(,([0-5]?[0-9])(-([0-5]?[0-9]))?)*|\*/([0-5]?[0-9]))$'),
        ("25", "hours", r'^(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?)*|\*/([0-9]|1[0-9]|2[0-3]))$'),
        ("32", "day of month", r'^(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?)*|\*/([1-9]|[12][0-9]|3[01]))$'),
        ("13", "month", r'^(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?)*|\*/([1-9]|1[0-2]))$'),
        ("8", "day of week", r'^(\*|([0-7])(-([0-7]))?(,([0-7])(-([0-7]))?)*|\*/([0-7]))$'),
    ]

    for value, field_name, pattern in invalid_fields:
        errors = []
        result = validate_time_field(value, field_name, pattern, 1, "test.txt", errors)
        assert not result, f"Field {field_name} with value '{value}' should be invalid"
        assert len(errors) == 1
        assert f"invalid {field_name} format" in errors[0]


def test_validate_cron_entry_standard_user_valid():
    """Test validating valid standard user crontab entry"""
    errors = []
    entry = user_cron_entry(
        minute="0", hour="2", day="*", month="*", weekday="*",
        command="/usr/bin/backup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert result
    assert len(errors) == 0


def test_validate_cron_entry_standard_system_valid():
    """Test validating valid standard system crontab entry"""
    errors = []
    entry = system_cron_entry(
        minute="0", hour="2", day="*", month="*", weekday="*",
        user="root", command="/usr/bin/backup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert result
    assert len(errors) == 0


def test_validate_cron_entry_special_keyword_user():
    """Test validating special keyword in user crontab"""
    errors = []
    entry = user_cron_entry(
        minute="@reboot", hour="*", day="*", month="*", weekday="*",
        command="/usr/bin/startup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert result
    assert len(errors) == 0


def test_validate_cron_entry_special_keyword_system():
    """Test validating special keyword in system crontab"""
    errors = []
    entry = system_cron_entry(
        minute="@reboot", hour="*", day="*", month="*", weekday="*",
        user="root", command="/usr/bin/startup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert result
    assert len(errors) == 0


def test_validate_cron_entry_invalid_time_fields():
    """Test validating crontab entry with invalid time fields"""
    errors = []
    entry = user_cron_entry(
        minute="60", hour="25", day="32", month="13", weekday="8",
        command="/usr/bin/backup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert not result
    assert len(errors) > 0


def test_validate_cron_entry_missing_user_system():
    """Test validating system crontab entry with missing user"""
    errors = []
    entry = system_cron_entry(
        minute="0", hour="2", day="*", month="*", weekday="*",
        user="", command="/usr/bin/backup.sh", line_number=1, file_name="test.txt"
    )

    result = validate_cron_entry(entry, errors)
    assert not result
    assert len(errors) == 1
    assert "missing user" in errors[0]


@patch.object(main_module, 'subprocess')
@patch.object(main_module, 'platform')
def test_check_cron_daemon_active(mock_platform, mock_subprocess):
    """Test checking active cron daemon"""
    mock_platform.system.return_value = 'Linux'
    mock_subprocess.run.return_value.returncode = 0

    result = check_cron_daemon()
    assert result
    mock_subprocess.run.assert_called_with(['systemctl', 'is-active', '--quiet', 'cron'],
                                           capture_output=True, text=True)


@patch.object(main_module, 'subprocess')
@patch.object(main_module, 'platform')
def test_check_cron_daemon_inactive(mock_platform, mock_subprocess):
    """Test checking inactive cron daemon"""
    mock_platform.system.return_value = 'Linux'
    # First call returns non-zero (cron inactive), second call returns 0 (crond active)
    mock_subprocess.run.side_effect = [
        MagicMock(returncode=1),
        MagicMock(returncode=0)
    ]

    result = check_cron_daemon()
    assert result
    assert mock_subprocess.run.call_count == 2


@patch.object(main_module, 'subprocess')
@patch.object(main_module, 'platform')
def test_check_cron_daemon_both_inactive(mock_platform, mock_subprocess):
    """Test checking when both cron daemons are inactive"""
    mock_platform.system.return_value = 'Linux'
    mock_subprocess.run.side_effect = [
        MagicMock(returncode=1),
        MagicMock(returncode=1)
    ]

    result = check_cron_daemon()
    assert not result


@patch.object(main_module, 'subprocess')
@patch.object(main_module, 'platform')
def test_check_cron_daemon_file_not_found(mock_platform, mock_subprocess):
    """Test checking cron daemon when systemctl not found"""
    mock_platform.system.return_value = 'Linux'
    mock_subprocess.run.side_effect = FileNotFoundError()

    result = check_cron_daemon()
    assert not result


@patch.object(main_module, 'subprocess')
@patch.object(main_module, 'platform')
def test_check_cron_daemon_non_linux(mock_platform, mock_subprocess):
    """Test checking cron daemon on non-Linux system"""
    mock_platform.system.return_value = 'Windows'

    result = check_cron_daemon()
    assert result
    # Should not call systemctl on non-Linux systems
    mock_subprocess.run.assert_not_called()


@patch.object(main_module, 'os')
def test_check_system_crontab_permissions_correct(mock_os):
    """Test checking system crontab with correct permissions"""
    mock_os.path.exists.return_value = True
    mock_os.access.return_value = True
    mock_os.stat.return_value.st_mode = 0o100644  # 644 permissions

    result = check_system_crontab_permissions()
    assert result


@patch.object(main_module, 'os')
def test_check_system_crontab_not_exists(mock_os):
    """Test checking system crontab that doesn't exist"""
    mock_os.path.exists.return_value = False

    result = check_system_crontab_permissions()
    assert result  # Now returns True (warning instead of error)


@patch.object(main_module, 'os')
def test_check_system_crontab_not_readable(mock_os):
    """Test checking system crontab that's not readable"""
    mock_os.path.exists.return_value = True
    mock_os.access.return_value = False

    result = check_system_crontab_permissions()
    assert result  # Now returns True (warning instead of error)


def test_check_crontab_file_with_valid_file():
    """Test checking crontab file with valid content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("0 2 * * * /usr/bin/backup.sh\n")
        temp_file.write("@reboot /usr/bin/startup.sh\n")
        temp_file_path = temp_file.name

    try:
        errors = []
        result = check_crontab_file(temp_file_path, errors, is_system_crontab=False)
        assert result == 0
        assert len(errors) == 0
    finally:
        os.unlink(temp_file_path)


def test_check_crontab_file_with_invalid_file():
    """Test checking crontab file with invalid content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("0 2 * * * /usr/bin/backup.sh\n")  # Valid line
        temp_file.write("60 25 32 13 8 /usr/bin/invalid.sh\n")  # Invalid time fields
        temp_file_path = temp_file.name

    try:
        errors = []
        result = check_crontab_file(temp_file_path, errors, is_system_crontab=False)
        assert result > 0
        assert len(errors) > 0
    finally:
        os.unlink(temp_file_path)


def test_check_crontab_file_with_system_crontab():
    """Test checking system crontab file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write("0 2 * * * root /usr/bin/backup.sh\n")
        temp_file_path = temp_file.name

    try:
        errors = []
        result = check_crontab_file(temp_file_path, errors, is_system_crontab=True)
        assert result == 0
        assert len(errors) == 0
    finally:
        os.unlink(temp_file_path)


def test_check_crontab_file_nonexistent():
    """Test checking nonexistent crontab file"""
    errors = []
    result = check_crontab_file("/nonexistent/file.txt", errors, is_system_crontab=False)
    assert result == 0  # Should return 0 for nonexistent files (just warning)


# Test runner function
def run_all_tests():
    """Run all functional tests"""
    test_functions = [
        test_parse_cron_line_standard_user,
        test_parse_cron_line_standard_system,
        test_parse_cron_line_special_keyword_user,
        test_parse_cron_line_special_keyword_system,
        test_parse_cron_line_invalid_special_keyword,
        test_parse_cron_line_insufficient_fields_user,
        test_parse_cron_line_insufficient_fields_system,
        test_parse_cron_line_comment,
        test_parse_cron_line_empty,
        test_parse_cron_line_environment_variable,
        test_validate_time_field_valid,
        test_validate_time_field_invalid,
        test_validate_cron_entry_standard_user_valid,
        test_validate_cron_entry_standard_system_valid,
        test_validate_cron_entry_special_keyword_user,
        test_validate_cron_entry_special_keyword_system,
        test_validate_cron_entry_invalid_time_fields,
        test_validate_cron_entry_missing_user_system,
        test_check_cron_daemon_active,
        test_check_cron_daemon_inactive,
        test_check_cron_daemon_both_inactive,
        test_check_cron_daemon_file_not_found,
        test_check_cron_daemon_non_linux,
        test_check_system_crontab_permissions_correct,
        test_check_system_crontab_not_exists,
        test_check_system_crontab_not_readable,
        test_check_crontab_file_with_valid_file,
        test_check_crontab_file_with_invalid_file,
        test_check_crontab_file_with_system_crontab,
        test_check_crontab_file_nonexistent,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASSED: {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAILED: {test_func.__name__} - {e}")
            failed += 1

    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
