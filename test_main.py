#!/usr/bin/env python3
# mypy: ignore-errors
"""
Tests for checkcrontab package
"""
from unittest.mock import MagicMock, patch

from checkcrontab import checker
from checkcrontab import main as check_crontab
from checkcrontab.logging_config import setup_logging

# ============================================================================
# Logging tests
# ============================================================================


def test_setup_logging():
    """Test logging setup"""
    # Should not raise any exceptions
    setup_logging(debug=False, no_colors=False)
    setup_logging(debug=True, no_colors=True)

# ============================================================================
# User crontab line checking tests
# ============================================================================


def test_valid_user_crontab_line():
    """Test valid user crontab line"""
    line = "0 2 * * * /usr/bin/backup.sh"
    errors = checker.check_line_user(line, 1, "test.txt")
    assert errors == []


def test_invalid_user_crontab_line_insufficient_fields():
    """Test user crontab line with insufficient fields"""
    line = "0 2 * * *"
    errors = checker.check_line_user(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_missing_command():
    """Test user crontab line with missing command"""
    line = "0 2 * * * "
    errors = checker.check_line_user(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_invalid_minute():
    """Test user crontab line with invalid minute"""
    line = "60 2 * * * /usr/bin/backup.sh"
    errors = checker.check_line_user(line, 1, "test.txt")
    assert len(errors) == 1
    assert "value 60 out of bounds" in errors[0]


def test_valid_user_crontab_line_with_special_keyword():
    """Test valid user crontab line with special keyword"""
    line = "@reboot /usr/bin/backup.sh"
    errors = checker.check_line_user(line, 1, "test.txt")
    assert errors == []


def test_environment_variable_skipped():
    """Test that environment variables are skipped"""
    line = "MAILTO=user@example.com"
    errors = checker.check_line_user(line, 1, "test.txt")
    assert errors == []


# ============================================================================
# System crontab line checking tests
# ============================================================================

def test_valid_system_crontab_line():
    """Test valid system crontab line"""
    line = "0 2 * * * root /usr/bin/backup.sh"
    errors = checker.check_line_system(line, 1, "test.txt")
    assert errors == []


def test_invalid_system_crontab_line_insufficient_fields():
    """Test system crontab line with insufficient fields"""
    line = "0 2 * * * root"
    errors = checker.check_line_system(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_missing_command():
    """Test system crontab line with missing command"""
    line = "0 2 * * * root "
    errors = checker.check_line_system(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_invalid_user():
    """Test system crontab line with invalid user"""
    line = "0 2 * * * #root /usr/bin/backup.sh"
    errors = checker.check_line_system(line, 1, "test.txt")
    assert len(errors) == 1
    assert "invalid user field" in errors[0]


# ============================================================================
# Special keyword line checking tests
# ============================================================================

def test_valid_user_special_keyword_line():
    """Test valid special keyword line"""
    line = "@reboot /usr/bin/backup.sh"
    errors = checker.check_line_special(line, 1, "test.txt")
    assert errors == []


def test_valid_system_special_keyword_line():
    """Test valid special keyword line"""
    line = "@reboot root /usr/bin/backup.sh"
    errors = checker.check_line_special(line, 1, "test.txt")
    assert errors == []


def test_invalid_special_keyword_line_insufficient_fields():
    """Test special keyword line with insufficient fields"""
    line = "@reboot"
    errors = checker.check_line_special(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_missing_command():
    """Test special keyword line with missing command"""
    line = "@reboot "
    errors = checker.check_line_special(line, 1, "test.txt")
    assert len(errors) == 1
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_invalid_keyword():
    """Test special keyword line with invalid keyword"""
    line = "@invalid /usr/bin/backup.sh"
    errors = checker.check_line_special(line, 1, "test.txt")
    assert len(errors) == 1
    assert "invalid special keyword" in errors[0]


# ============================================================================
# System-level checks tests
# ============================================================================

@patch('checkcrontab.checker.subprocess.run')
def test_check_cron_daemon_running(mock_run):
    """Test cron daemon check when running"""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "active\n"

    # Should not raise any exceptions
    checker.check_cron_daemon()


@patch('checkcrontab.checker.subprocess.run')
def test_check_cron_daemon_not_running(mock_run):
    """Test cron daemon check when not running"""
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = "inactive\n"

    # Should not raise any exceptions
    checker.check_cron_daemon()


@patch('checkcrontab.checker.os.path.exists')
@patch('checkcrontab.checker.os.stat')
def test_check_system_crontab_permissions_correct(mock_stat, mock_exists):
    """Test system crontab permissions check with correct permissions"""
    mock_exists.return_value = True
    mock_stat_info = MagicMock()
    mock_stat_info.st_mode = 0o644
    mock_stat_info.st_uid = 0
    mock_stat.return_value = mock_stat_info

    # Should not raise any exceptions
    checker.check_system_crontab_permissions()


@patch('checkcrontab.checker.os.path.exists')
def test_check_system_crontab_permissions_file_not_exists(mock_exists):
    """Test system crontab permissions check when file doesn't exist"""
    mock_exists.return_value = False

    # Should not raise any exceptions
    checker.check_system_crontab_permissions()

# ============================================================================
# File validation tests
# ============================================================================


@patch('checkcrontab.main.platform.system')
@patch('checkcrontab.main.os.getenv')
@patch('checkcrontab.main.os.path.exists')
@patch('checkcrontab.checker.check_cron_daemon')
@patch('checkcrontab.checker.check_system_crontab_permissions')
def test_system_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that system_valid.txt returns exit code 0 (no errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == 'GITHUB_ACTIONS':
            return 'true'
        return default
    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with system_valid.txt
    with patch('sys.argv', ['checkcrontab', 'examples/system_valid.txt']):
        exit_code = check_crontab.main()
        assert exit_code == 0


@patch('checkcrontab.main.platform.system')
@patch('checkcrontab.main.os.getenv')
@patch('checkcrontab.main.os.path.exists')
@patch('checkcrontab.checker.check_cron_daemon')
@patch('checkcrontab.checker.check_system_crontab_permissions')
def test_system_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that system_incorrect.txt returns exit code 1 (has errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == 'GITHUB_ACTIONS':
            return 'true'
        return default
    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with system_incorrect.txt
    with patch('sys.argv', ['checkcrontab', 'examples/system_incorrect.txt']):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch('checkcrontab.main.platform.system')
@patch('checkcrontab.main.os.getenv')
@patch('checkcrontab.main.os.path.exists')
@patch('checkcrontab.checker.check_cron_daemon')
@patch('checkcrontab.checker.check_system_crontab_permissions')
def test_user_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_incorrect.txt returns exit code 1 (has errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == 'GITHUB_ACTIONS':
            return 'true'
        return default
    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with user_incorrect.txt
    with patch('sys.argv', ['checkcrontab', 'examples/user_incorrect.txt']):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch('checkcrontab.main.platform.system')
@patch('checkcrontab.main.os.getenv')
@patch('checkcrontab.main.os.path.exists')
@patch('checkcrontab.checker.check_cron_daemon')
@patch('checkcrontab.checker.check_system_crontab_permissions')
def test_user_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_valid.txt returns exit code 0 (no errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == 'GITHUB_ACTIONS':
            return 'true'
        return default
    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with user_valid.txt
    with patch('sys.argv', ['checkcrontab', 'examples/user_valid.txt']):
        exit_code = check_crontab.main()
        assert exit_code == 0
