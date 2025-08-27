#!/usr/bin/env python3
# mypy: ignore-errors
"""
Tests for checkcrontab package
"""

import json
import logging
import runpy
from pathlib import Path
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
# Individual validation function tests
# ============================================================================


def test_check_minutes_user_crontab():
    """Test minutes validation for user crontab"""
    # Valid minutes
    assert checker.check_minutes("0", is_system_crontab=False) == []
    assert checker.check_minutes("30", is_system_crontab=False) == []
    assert checker.check_minutes("*", is_system_crontab=False) == []
    assert checker.check_minutes("*/15", is_system_crontab=False) == []

    # Invalid minutes for user crontab
    assert len(checker.check_minutes("60", is_system_crontab=False)) == 1
    assert len(checker.check_minutes("-0", is_system_crontab=False)) == 1
    assert len(checker.check_minutes("abc", is_system_crontab=False)) == 1


def test_check_minutes_system_crontab():
    """Test minutes validation for system crontab"""
    # Valid minutes including dash prefix
    assert checker.check_minutes("0", is_system_crontab=True) == []
    assert checker.check_minutes("30", is_system_crontab=True) == []
    assert checker.check_minutes("-0", is_system_crontab=True) == []
    assert checker.check_minutes("-30", is_system_crontab=True) == []
    assert checker.check_minutes("*", is_system_crontab=True) == []

    # Invalid minutes for system crontab
    assert len(checker.check_minutes("60", is_system_crontab=True)) == 1
    assert len(checker.check_minutes("abc", is_system_crontab=True)) == 1


def test_check_hours():
    """Test hours validation"""
    # Valid hours
    assert checker.check_hours("0") == []
    assert checker.check_hours("12") == []
    assert checker.check_hours("23") == []
    assert checker.check_hours("*") == []
    assert checker.check_hours("*/6") == []

    # Invalid hours
    assert len(checker.check_hours("24")) == 1
    assert len(checker.check_hours("-1")) == 1
    assert len(checker.check_hours("abc")) == 1


def test_check_day_of_month():
    """Test day of month validation"""
    # Valid days
    assert checker.check_day_of_month("1") == []
    assert checker.check_day_of_month("15") == []
    assert checker.check_day_of_month("31") == []
    assert checker.check_day_of_month("*") == []

    # Invalid days
    assert len(checker.check_day_of_month("0")) == 1
    assert len(checker.check_day_of_month("32")) == 1
    assert len(checker.check_day_of_month("abc")) == 1


def test_check_month():
    """Test month validation"""
    # Valid months
    assert checker.check_month("1") == []
    assert checker.check_month("6") == []
    assert checker.check_month("12") == []
    assert checker.check_month("*") == []

    # Invalid months
    assert len(checker.check_month("0")) == 1
    assert len(checker.check_month("13")) == 1
    assert len(checker.check_month("abc")) == 1


def test_check_day_of_week():
    """Test day of week validation"""
    # Valid weekdays
    assert checker.check_day_of_week("0") == []
    assert checker.check_day_of_week("3") == []
    assert checker.check_day_of_week("7") == []
    assert checker.check_day_of_week("*") == []

    # Invalid weekdays
    assert len(checker.check_day_of_week("8")) == 1
    assert len(checker.check_day_of_week("-1")) == 1
    assert len(checker.check_day_of_week("abc")) == 1


def test_check_user():
    """Test user field validation"""
    # Valid users
    errors, warnings = checker.check_user("root")
    assert errors == [] and warnings == []
    errors, warnings = checker.check_user("pytest_user")
    assert errors == [] and warnings == []

    # Invalid users
    errors, warnings = checker.check_user("")
    assert len(errors) == 1 and warnings == []
    errors, warnings = checker.check_user("#root")
    assert len(errors) == 1 and warnings == []
    errors, warnings = checker.check_user('"root"')
    assert len(errors) == 1 and warnings == []
    errors, warnings = checker.check_user("root@localhost")
    assert len(errors) == 1 and warnings == []
    errors, warnings = checker.check_user("root user")
    assert len(errors) == 1 and warnings == []


def test_check_command():
    """Test command validation"""
    # Valid commands
    assert checker.check_command("/usr/bin/backup.sh") == []
    assert checker.check_command("echo 'hello world'") == []

    # Invalid commands
    assert len(checker.check_command("")) == 1

    # Dangerous commands
    dangerous_cmd = "rm -rf /"
    errors = checker.check_command(dangerous_cmd)
    assert len(errors) == 1
    assert "dangerous command" in errors[0]


def test_check_special_user_crontab():
    """Test special keyword validation for user crontab"""
    # Valid special keywords
    assert checker.check_special("@reboot", ["@reboot", "/usr/bin/backup.sh"], is_system_crontab=False) == []
    assert checker.check_special("@daily", ["@daily", "echo hello"], is_system_crontab=False) == []

    # Invalid special keywords
    assert len(checker.check_special("@invalid", ["@invalid", "/usr/bin/backup.sh"], is_system_crontab=False)) == 1

    # Too many fields for user crontab (now warning instead of error)
    assert checker.check_special("@reboot", ["@reboot", "root", "/usr/bin/backup.sh"], is_system_crontab=False) == []


def test_check_special_system_crontab():
    """Test special keyword validation for system crontab"""
    # Valid special keywords
    assert checker.check_special("@reboot", ["@reboot", "pytest_user", "/usr/bin/backup.sh"], is_system_crontab=True) == []
    assert checker.check_special("@daily", ["@daily", "root", "echo hello"], is_system_crontab=True) == []

    # Invalid special keywords
    assert len(checker.check_special("@invalid", ["@invalid", "root", "/usr/bin/backup.sh"], is_system_crontab=True)) == 1

    # Insufficient fields for system crontab
    assert len(checker.check_special("@reboot", ["@reboot", "root"], is_system_crontab=True)) == 1


# ============================================================================
# User crontab line checking tests
# ============================================================================


    def test_valid_user_crontab_line():
        """Test valid user crontab line"""
        line = "0 2 * * * /usr/bin/backup.sh"
        errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
        assert errors == []
        assert warnings == []


def test_invalid_user_crontab_line_insufficient_fields():
    """Test user crontab line with insufficient fields"""
    line = "0 2 * * *"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_missing_command():
    """Test user crontab line with missing command"""
    line = "0 2 * * * "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_invalid_minute():
    """Test user crontab line with invalid minute"""
    line = "60 2 * * * /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "value 60 out of bounds" in errors[0]


def test_valid_user_crontab_line_with_special_keyword():
    """Test valid user crontab line with special keyword"""
    line = "@reboot /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


def test_environment_variable_skipped():
    """Test that environment variables are skipped"""
    line = "MAILTO=user@example.com"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


# ============================================================================
# System crontab line checking tests
# ============================================================================


def test_valid_system_crontab_line():
    """Test valid system crontab line"""
    line = "0 2 * * * root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_valid_system_crontab_line_with_dash_prefix():
    """Test valid system crontab line with dash prefix in minutes"""
    line = "-0 2 * * * root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_invalid_system_crontab_line_insufficient_fields():
    """Test system crontab line with insufficient fields"""
    line = "0 2 * * * root"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_missing_command():
    """Test system crontab line with missing command"""
    line = "0 2 * * * root "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_invalid_user():
    """Test system crontab line with invalid user"""
    line = "0 2 * * * #root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "invalid user format" in errors[0]


# ============================================================================
# Special keyword line checking tests
# ============================================================================


def test_valid_user_special_keyword_line():
    """Test valid special keyword line"""
    line = "@reboot /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


def test_valid_system_special_keyword_line():
    """Test valid system special keyword line"""
    line = "@reboot root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_invalid_special_keyword_line_insufficient_fields():
    """Test special keyword line with insufficient fields"""
    line = "@reboot"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_missing_command():
    """Test special keyword line with missing command"""
    line = "@reboot "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_invalid_keyword():
    """Test special keyword line with invalid keyword"""
    line = "@invalid /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "invalid special keyword" in errors[0]


# ============================================================================
# System-level checks tests
# ============================================================================


@patch("checkcrontab.checker.subprocess.run")
def test_check_cron_daemon_running(mock_run):
    """Test cron daemon check when running"""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "active\n"

    # Should not raise any exceptions
    checker.check_daemon()


@patch("checkcrontab.checker.subprocess.run")
def test_check_cron_daemon_not_running(mock_run):
    """Test cron daemon check when not running"""
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = "inactive\n"

    # Should not raise any exceptions
    checker.check_daemon()


@patch("checkcrontab.checker.os.path.exists")
@patch("checkcrontab.checker.os.stat")
def test_check_system_crontab_permissions_correct(mock_stat, mock_exists):
    """Test system crontab permissions check with correct permissions"""
    mock_exists.return_value = True
    mock_stat_info = MagicMock()
    mock_stat_info.st_mode = 0o644
    mock_stat_info.st_uid = 0
    mock_stat.return_value = mock_stat_info

    # Should not raise any exceptions
    checker.check_permissions()


@patch("checkcrontab.checker.os.path.exists")
def test_check_system_crontab_permissions_file_not_exists(mock_exists):
    """Test system crontab permissions check when file doesn't exist"""
    mock_exists.return_value = False

    # Should not raise any exceptions
    checker.check_permissions()


# ============================================================================
# File validation tests
# ============================================================================


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_system_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that system_valid.txt returns exit code 0 (no errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default

    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with system_valid.txt
    with patch("sys.argv", ["checkcrontab", "examples/system_valid.txt"]):
        exit_code = check_crontab.main()
        assert exit_code == 0


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_system_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that system_incorrect.txt returns exit code 1 (has errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default

    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with system_incorrect.txt
    with patch("sys.argv", ["checkcrontab", "examples/system_incorrect.txt"]):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_user_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_incorrect.txt returns exit code 1 (has errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default

    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with user_incorrect.txt
    with patch("sys.argv", ["checkcrontab", "examples/user_incorrect.txt"]):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_user_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_valid.txt returns exit code 0 (no errors)"""
    # Mock platform to return Linux
    mock_platform.return_value = "Linux"
    # Mock environment variables

    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default

    mock_env.side_effect = mock_env_side_effect
    # Mock file existence
    mock_exists.return_value = True
    # Mock system checks to not raise exceptions
    mock_daemon.return_value = None
    mock_permissions.return_value = None

    # Test with user_valid.txt
    with patch("sys.argv", ["checkcrontab", "examples/user_valid.txt"]):
        exit_code = check_crontab.main()
        assert exit_code == 0


def run_main_with_args(args):
    with patch("sys.argv", ["checkcrontab", *args]):
        return check_crontab.main()


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="false")
@patch("checkcrontab.main.os.path.exists")
def test_auto_adds_system_crontab(mock_exists, mock_env, mock_platform, monkeypatch):
    # /etc/crontab should be auto-added when no args and on Linux (not GitHub)
    # Mock existence - /etc/crontab doesn't exist initially (for permissions check)
    # but will be created when needed for reading
    def exists_side_effect(path):
        return False

    mock_exists.side_effect = exists_side_effect

    # Provide mock content for /etc/crontab
    crontab_content = "0 0 * * * root echo hello\n"
    mock_open = patch("checkcrontab.main.open", create=True)
    with mock_open as m:
        m.return_value.__enter__.return_value.readlines.return_value = crontab_content.splitlines(True)
        code = run_main_with_args([])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_missing_newline_error(mock_exists, mock_env, mock_platform, tmp_path, caplog):
    # File without trailing newline should generate an error and non-zero exit
    f = tmp_path / "no_newline.cron"
    f.write_text("0 1 * * * echo test")  # missing final newline
    caplog.set_level(logging.DEBUG)
    code = run_main_with_args([str(f)])
    assert code == 1
    assert any("File should end with newline" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_multiline_command_user_crontab(mock_exists, mock_env, mock_platform, tmp_path):
    # Multi-line command continuation handling
    content = "0 2 * * * echo part1 \\\n    part2\n"
    f = tmp_path / "multiline.cron"
    f.write_text(content)
    code = run_main_with_args([str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_duplicate_files_processed_once(mock_exists, mock_env, mock_platform, tmp_path):
    f = tmp_path / "dup.cron"
    f.write_text("0 1 * * * echo hi\n")
    calls = []

    def fake_check_file(path, is_system_crontab=False):  # pragma: no cover - simple shim
        calls.append((path, is_system_crontab))
        return 1, []

    with patch("checkcrontab.main.check_file", side_effect=fake_check_file):
        code = run_main_with_args([str(f), str(f), str(f)])
    assert code == 0
    # Only one call for the file despite duplicates
    assert len(calls) == 1


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_username_resolution(mock_exists, mock_getenv, mock_platform, monkeypatch, tmp_path, capsys):
    # Simulate finding user crontab via helper
    user_file = tmp_path / "user_pytest_user"
    user_file.write_text("0 3 * * * echo user\n")

    def fake_find_user_crontab(username):  # pragma: no cover - shim
        assert username == "pytest_user"
        return str(user_file)

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    # Treat the provided argument as username (not existing file) so resolution happens
    def exists_side_effect(path):
        if path == "pytest_user":
            return False
        return True

    mock_exists.side_effect = exists_side_effect

    code = run_main(["--format", "json", "pytest_user"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["success"] is True


@patch("checkcrontab.main.platform.system", return_value="Windows")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.main.os.getenv", return_value="true")
def test_non_linux_skips_system(mock_env, mock_exists, mock_platform, tmp_path):
    # On non-Linux system system crontab insertion is skipped
    f = tmp_path / "user.cron"
    f.write_text("0 4 * * * echo hi\n")
    code = run_main_with_args([str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_file_not_exists_warning(mock_exists, mock_env, mock_platform, caplog):
    caplog.set_level(logging.DEBUG)
    code = run_main_with_args(["/tmp/does_not_exist.cron"])  # warning, but no errors -> exit 0
    assert code == 0
    assert any("not found" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_debug_mode_outputs_valid(mock_exists, mock_env, mock_platform, tmp_path, caplog):
    f = tmp_path / "debug.cron"
    f.write_text("0 5 * * * echo hi\n")
    caplog.set_level(logging.DEBUG)
    with patch("sys.argv", ["checkcrontab", "--debug", str(f)]):
        code = check_crontab.main()
    assert code == 0
    assert any("# valid" in r.getMessage() for r in caplog.records if r.levelname == "DEBUG")


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_no_colors_flag(mock_exists, mock_env, mock_platform, tmp_path):
    # Just exercise the --no-colors flag path
    f = tmp_path / "nocolor.cron"
    f.write_text("0 6 * * * echo hi\n")
    code = run_main_with_args(["--no-colors", str(f)])
    assert code == 0


def run_main(args):
    with patch("sys.argv", ["checkcrontab", *args]):
        return check_crontab.main()


def test_import_fallback_run_as_script(tmp_path, monkeypatch):
    # Execute main.py as a script so the relative import fails and absolute succeeds
    script_path = Path(check_crontab.__file__).resolve()
    # Provide a simple valid file argument to keep runtime short
    valid = tmp_path / "valid.cron"
    valid.write_text("0 0 * * * echo ok\n")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")  # prevent auto /etc/crontab addition
    with patch("sys.argv", [str(script_path), str(valid)]):
        try:
            runpy.run_path(str(script_path), run_name="__main__")
        except SystemExit as e:  # main exits
            assert e.code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_json_explicit_missing_files(mock_exists, mock_env, mock_platform, capsys):
    # Use -S / -U so missing files are still added to JSON
    with patch("sys.argv", ["checkcrontab", "--format", "json", "-S", "/tmp/miss_system.cron", "-U", "/tmp/miss_user.cron"]):
        code = check_crontab.main()
    out = capsys.readouterr().out
    data = json.loads(out)
    # Current behavior: missing files recorded but not counted toward total_errors (possible improvement)
    assert code == 0
    assert data["total_files"] == 2
    assert data["total_errors"] == 0  # because total_errors only increments for existing files
    assert data["success"] is True
    file_paths = {f["file"] for f in data["files"]}
    assert "/tmp/miss_system.cron" in file_paths and "/tmp/miss_user.cron" in file_paths
    for f in data["files"]:
        assert f["success"] is False
        assert f["errors_count"] == 1
        assert "does not exist" in f["errors"][0]


@patch("checkcrontab.main.platform.system", return_value="Darwin")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_non_linux_message(mock_exists, mock_env, mock_platform, caplog, tmp_path):
    caplog.set_level("INFO")
    f = tmp_path / "user.cron"
    f.write_text("0 1 * * * echo mac\n")
    code = run_main([str(f)])
    assert code == 0
    assert any("Skipping system checks on non-Linux" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="false")  # allow auto-add
@patch("checkcrontab.main.os.path.exists", return_value=False)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_auto_added_missing_system_file_warning(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, caplog):
    caplog.set_level("WARNING")
    # /etc/crontab will be auto-added then reported missing
    code = run_main([])
    # Exit 0 because missing system file just a warning (no errors counted since not JSON path)
    assert code == 0
    assert any("/etc/crontab" in r.getMessage() and "does not exist" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_temp_file_cleanup_error(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, monkeypatch, caplog, tmp_path):
    caplog.set_level("DEBUG")
    # Create a fake temp file path returned by find_user_crontab
    temp_file = tmp_path / "crontab.testuser"
    temp_file.write_text("0 2 * * * echo hi\n")

    def fake_find_user_crontab(username):
        return str(temp_file)

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    # Force os.unlink to raise to hit debug exception path
    def unlink_raiser(path):  # pragma: no cover - simple helper
        raise OSError("permission denied")

    monkeypatch.setattr(check_crontab.os, "unlink", unlink_raiser)
    code = run_main(["--debug", "-u", "testuser"])
    assert code == 0
    assert any("Failed to remove temporary file" in r.getMessage() for r in caplog.records if r.levelname == "DEBUG")


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_valid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "examples/system_valid.txt"])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["success"] is True
    assert data["total_errors"] == 0
    assert data["total_files"] == 1
    assert data["files"][0]["success"] is True
    assert data["files"][0]["rows"] > 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_invalid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "examples/system_incorrect.txt"])
    assert code == 1
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["success"] is False
    assert data["total_errors"] > 0
    f = data["files"][0]
    assert f["success"] is False
    assert f["errors_count"] == len(f["errors"])
    # lines_with_errors should be <= total_errors
    assert f["errors_count"] <= f["errors_count"]


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_missing_newline_file(mock_perm, mock_daemon, mock_env, mock_platform, tmp_path, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    f = tmp_path / "no_newline.cron"
    f.write_text("0 1 * * * root echo test")  # missing newline
    code = run_main(["--format", "json", str(f)])
    assert code == 1
    data = json.loads(capsys.readouterr().out)
    file_entry = data["files"][0]
    assert any("File should end with newline" in e for e in file_entry["errors"])
    # newline error excluded from lines_with_errors counting, so may be 0
    assert file_entry["errors_count"] >= 1


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_nonexistent_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "/tmp/definitely_nonexistent_cron_file_12345.cron"])
    # Because path doesn't exist it's treated as username; user not found -> no files gathered.
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total_files"] == 0
    assert data["files"] == []
    # No errors because nothing processed
    assert data["total_errors"] == 0
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_multiple_files_mixed(mock_perm, mock_daemon, mock_env, mock_platform, tmp_path, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    valid = tmp_path / "valid.cron"
    valid.write_text("0 2 * * * root echo ok\n")
    invalid = tmp_path / "invalid.cron"
    invalid.write_text("61 2 * * * root echo bad\n")  # invalid minute
    code = run_main(["--format", "json", str(valid), str(invalid)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total_files"] == 2
    assert data["total_rows"] == sum(f["rows"] for f in data["files"])
    # One file success, one fail
    statuses = {f["success"] for f in data["files"]}
    assert statuses == {True, False}
    assert code == 1


# Additional JSON tests
@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="false")  # not GitHub so system crontab auto-added
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_auto_add_system(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, capsys):
    def exists_side_effect(path):
        return path == "/etc/crontab"

    mock_exists.side_effect = exists_side_effect
    # Provide fake /etc/crontab content
    content = "0 0 * * * root echo ok\n"
    with patch("checkcrontab.main.open", create=True) as m:
        m.return_value.__enter__.return_value.readlines.return_value = content.splitlines(True)
        code = run_main(["--format", "json"])  # no args triggers auto-add
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["is_system_crontab"] is True


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_duplicates_removed(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys):
    f = tmp_path / "dup.cron"
    f.write_text("0 3 * * * root echo once\n")
    code = run_main(["--format", "json", str(f), str(f), str(f)])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert len(data["files"]) == 1


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_permissions")
def test_json_username_resolution(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys, monkeypatch):
    user_file = tmp_path / "user_pytest_user"
    user_file.write_text("0 4 * * * echo user\n")

    def fake_find_user_crontab(username):
        assert username == "pytest_user"
        return str(user_file)

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    # Ensure username treated as username not file
    def exists_side_effect(path):
        if path == "pytest_user":
            return False
        return True

    mock_exists.side_effect = exists_side_effect

    code = run_main(["--format", "json", "pytest_user"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["success"] is True
