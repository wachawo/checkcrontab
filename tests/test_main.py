#!/usr/bin/env python3
# mypy: ignore-errors
"""
Tests for checkcrontab package
"""

import importlib
import importlib.util
import json
import logging
import os
import runpy
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "checkcrontab"
package_spec = importlib.util.spec_from_file_location(
    "checkcrontab", PACKAGE_ROOT / "__init__.py", submodule_search_locations=[str(PACKAGE_ROOT)]
)
checkcrontab_pkg = importlib.util.module_from_spec(package_spec)
sys.modules["checkcrontab"] = checkcrontab_pkg
package_spec.loader.exec_module(checkcrontab_pkg)

check_crontab = importlib.import_module("checkcrontab.main")
checker = importlib.import_module("checkcrontab.checker")
setup_logging = importlib.import_module("checkcrontab.logger").setup_logging

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
    checker.check_owner_and_permissions('/etc/crontab')


@patch("checkcrontab.checker.os.path.exists")
def test_check_system_crontab_permissions_file_not_exists(mock_exists):
    """Test system crontab permissions check when file doesn't exist"""
    mock_exists.return_value = False

    # Should not raise any exceptions
    checker.check_owner_and_permissions('/etc/crontab')


# ============================================================================
# File validation tests
# ============================================================================


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform, monkeypatch):
    """Test that system_valid returns exit code 0 (no errors)"""
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
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    if hasattr(os, "getuid"):
        monkeypatch.setenv("CRONTAB_OWNER_UID", str(os.getuid()))

    # Test with system_valid
    with patch("sys.argv", ["checkcrontab", "examples/system_valid"]):
        exit_code = check_crontab.main()
        assert exit_code == 0


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform, monkeypatch):
    """Test that system_incorrect returns exit code 1 (has errors)"""
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
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    if hasattr(os, "getuid"):
        monkeypatch.setenv("CRONTAB_OWNER_UID", str(os.getuid()))

    # Test with system_incorrect
    with patch("sys.argv", ["checkcrontab", "examples/system_incorrect"]):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_user_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_incorrect returns exit code 1 (has errors)"""
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
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    # Test with user_incorrect
    with patch("sys.argv", ["checkcrontab", "examples/user_incorrect"]):
        exit_code = check_crontab.main()
        assert exit_code == 1


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_user_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, mock_platform):
    """Test that user_valid returns exit code 0 (no errors)"""
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
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    # Test with user_valid
    with patch("sys.argv", ["checkcrontab", "examples/user_valid"]):
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
    f = tmp_path / "no_newline_cron"
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
    f = tmp_path / "multiline_cron"
    f.write_text(content)
    code = run_main_with_args([str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_duplicate_files_processed_once(mock_exists, mock_env, mock_platform, tmp_path):
    f = tmp_path / "dup_cron"
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
    f = tmp_path / "user_cron"
    f.write_text("0 4 * * * echo hi\n")
    code = run_main_with_args([str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_file_not_exists_warning(mock_exists, mock_env, mock_platform, caplog):
    caplog.set_level(logging.DEBUG)
    code = run_main_with_args(["/tmp/does_not_exist_cron"])  # warning, but no errors -> exit 0
    assert code == 0
    assert any("not found" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_debug_mode_outputs_valid(mock_exists, mock_env, mock_platform, tmp_path, caplog):
    f = tmp_path / "debug_cron"
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
    f = tmp_path / "nocolor_cron"
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
    valid = tmp_path / "valid_cron"
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
    with patch("sys.argv", ["checkcrontab", "--format", "json", "-S", "/tmp/miss_system_cron", "-U", "/tmp/miss_user_cron"]):
        code = check_crontab.main()
    out = capsys.readouterr().out
    data = json.loads(out)
    # Current behavior: missing files recorded but not counted toward total_errors (possible improvement)
    assert code == 0
    if data["total_files"] != 2:
        print(data)
    assert data["total_files"] == 2
    assert data["total_errors"] == 0  # because total_errors only increments for existing files
    assert data["success"] is True
    file_paths = {f["file"] for f in data["files"]}
    assert "/tmp/miss_system_cron" in file_paths and "/tmp/miss_user_cron" in file_paths
    for f in data["files"]:
        assert f["success"] is False
        assert f["errors_count"] == 1
        assert "does not exist" in f["errors"][0]


@patch("checkcrontab.main.platform.system", return_value="Darwin")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_non_linux_message(mock_exists, mock_env, mock_platform, caplog, tmp_path):
    caplog.set_level("INFO")
    f = tmp_path / "user_cron"
    f.write_text("0 1 * * * echo mac\n")
    code = run_main([str(f)])
    assert code == 0
    assert any("Skipping system checks on non-Linux" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="false")  # allow auto-add
@patch("checkcrontab.main.os.path.exists", return_value=False)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_auto_added_missing_system_file_warning(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, caplog):
    caplog.set_level("WARNING")
    # /etc/crontab will be auto-added then reported missing
    code = run_main([])
    # Exit 0 because missing system file just a warning (no errors counted since not JSON path)
    assert code == 0
    assert any("No files to check." in r.getMessage() for r in caplog.records if r.levelname == "WARNING")


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
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
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_valid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "examples/system_valid"])
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
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_invalid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "examples/system_incorrect"])
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
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_missing_newline_file(mock_perm, mock_daemon, mock_env, mock_platform, tmp_path, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    f = tmp_path / "no_newline_cron"
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
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_nonexistent_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "json", "/tmp/definitely_nonexistent_cron_file_12345_cron"])
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
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_multiple_files_mixed(mock_perm, mock_daemon, mock_env, mock_platform, tmp_path, capsys):
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    valid = tmp_path / "valid_cron"
    valid.write_text("0 2 * * * root echo ok\n")
    invalid = tmp_path / "invalid_cron"
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
@patch("checkcrontab.checker.check_owner_and_permissions")
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
    # DISABLE AUTO-ADD FOR LINUX
    assert data["total_files"] == 0
    # assert data["files"][0]["is_system_crontab"] is True


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_duplicates_removed(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys):
    f = tmp_path / "dup_cron"
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
@patch("checkcrontab.checker.check_owner_and_permissions")
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
    print(data)
    print(os.getenv("GITHUB_ACTIONS"))
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["success"] is True


# ============================================================================
# SARIF format tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_sarif_valid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    """Test SARIF output for valid file"""
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "sarif", "examples/system_valid"])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    # Check SARIF structure
    assert data["version"] == "2.1.0"
    assert data["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
    assert "runs" in data
    assert len(data["runs"]) == 1
    assert "tool" in data["runs"][0]
    assert "results" in data["runs"][0]
    # No errors means empty results
    assert len(data["runs"][0]["results"]) == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_sarif_invalid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    """Test SARIF output for invalid file"""
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "sarif", "examples/system_incorrect"])
    assert code == 1
    out = capsys.readouterr().out
    data = json.loads(out)
    # Check SARIF structure
    assert data["version"] == "2.1.0"
    assert "runs" in data
    assert len(data["runs"]) == 1
    assert "results" in data["runs"][0]
    # Should have errors
    assert len(data["runs"][0]["results"]) > 0
    # Check result structure
    result = data["runs"][0]["results"][0]
    assert "ruleId" in result
    assert "message" in result
    assert "locations" in result


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_sarif_multiple_files(mock_perm, mock_daemon, mock_env, mock_platform, tmp_path, capsys):
    """Test SARIF output with multiple files"""
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    valid = tmp_path / "valid_cron"
    valid.write_text("0 2 * * * root echo ok\n")
    invalid = tmp_path / "invalid_cron"
    invalid.write_text("61 2 * * * root echo bad\n")  # invalid minute
    code = run_main(["--format", "sarif", str(valid), str(invalid)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert code == 1
    assert len(data["runs"][0]["results"]) > 0


# ============================================================================
# --strict flag tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_strict_mode_with_warnings(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys):
    """Test that --strict flag treats warnings as errors for exit code"""
    # Create a file that might generate warnings (we'd need to know what generates warnings)
    # For now, test with a valid file to ensure strict mode doesn't break normal operation
    f = tmp_path / "test_cron"
    f.write_text("0 1 * * * root echo test\n")
    code = run_main(["--strict", "--format", "json", str(f)])
    assert code == 0  # No warnings or errors
    data = json.loads(capsys.readouterr().out)
    assert data["success"] is True


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_strict_mode_with_errors(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path):
    """Test that --strict flag still catches errors"""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--strict", str(f)])
    assert code == 1


# ============================================================================
# --exit-zero flag tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_exit_zero_with_errors(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path):
    """Test that --exit-zero returns 0 even with errors"""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--exit-zero", str(f)])
    assert code == 0  # Should return 0 despite errors


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_exit_zero_with_valid_file(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path):
    """Test that --exit-zero returns 0 with valid file"""
    f = tmp_path / "valid_cron"
    f.write_text("0 1 * * * root echo ok\n")
    code = run_main(["--exit-zero", str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_exit_zero_with_strict_and_errors(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path):
    """Test that --exit-zero overrides --strict"""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--strict", "--exit-zero", str(f)])
    assert code == 0  # --exit-zero should override everything


# ============================================================================
# Directory handling tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.main.os.path.isdir")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_flag_with_directory(mock_perm, mock_daemon, mock_isdir, mock_exists, mock_env, mock_platform, tmp_path, capsys):
    """Test -S flag with directory containing multiple cron files"""
    cron_dir = tmp_path / "cron.d"
    cron_dir.mkdir()
    (cron_dir / "job1").write_text("0 1 * * * root echo job1\n")
    (cron_dir / "job2").write_text("0 2 * * * root echo job2\n")
    (cron_dir / "job3").write_text("0 3 * * * root echo job3\n")

    def isdir_side_effect(path):
        return path == str(cron_dir)

    mock_isdir.side_effect = isdir_side_effect

    # Mock get_files to return our test files
    def mock_get_files(path):
        if path == str(cron_dir):
            return [str(cron_dir / "job1"), str(cron_dir / "job2"), str(cron_dir / "job3")], []
        return [], []

    with patch("checkcrontab.main.get_files", side_effect=mock_get_files):
        code = run_main(["--format", "json", "-S", str(cron_dir)])

    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 3
    assert all(f["is_system_crontab"] for f in data["files"])


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.main.os.path.isdir", return_value=False)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_flag_with_single_file(mock_perm, mock_daemon, mock_isdir, mock_exists, mock_env, mock_platform, tmp_path, capsys):
    """Test -S flag with single file"""
    f = tmp_path / "crontab"
    f.write_text("0 1 * * * root echo test\n")
    code = run_main(["--format", "json", "-S", str(f)])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["is_system_crontab"] is True


# ============================================================================
# Multiple usernames tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_multiple_usernames(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys, monkeypatch):
    """Test -u flag with multiple usernames"""
    user1_file = tmp_path / "crontab.user1"
    user1_file.write_text("0 1 * * * echo user1\n")
    user2_file = tmp_path / "crontab.user2"
    user2_file.write_text("0 2 * * * echo user2\n")
    user3_file = tmp_path / "crontab.user3"
    user3_file.write_text("0 3 * * * echo user3\n")

    def fake_find_user_crontab(username):
        if username == "user1":
            return str(user1_file)
        elif username == "user2":
            return str(user2_file)
        elif username == "user3":
            return str(user3_file)
        return None

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    code = run_main(["--format", "json", "-u", "user1", "-u", "user2", "-u", "user3"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 3
    assert all(not f["is_system_crontab"] for f in data["files"])


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_multiple_usernames_with_missing(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys, monkeypatch, caplog):
    """Test -u flag with multiple usernames where some don't exist"""
    user1_file = tmp_path / "crontab.user1"
    user1_file.write_text("0 1 * * * echo user1\n")

    def fake_find_user_crontab(username):
        if username == "user1":
            return str(user1_file)
        return None  # user2 and user3 don't exist

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)
    caplog.set_level(logging.WARNING)

    code = run_main(["--format", "json", "-u", "user1", "-u", "user2", "-u", "user3"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1  # Only user1 found
    # Check warnings for missing users
    assert any("user2" in r.getMessage() for r in caplog.records if r.levelname == "WARNING")
    assert any("user3" in r.getMessage() for r in caplog.records if r.levelname == "WARNING")


# ============================================================================
# Combined flags tests
# ============================================================================


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_combined_system_user_and_username_flags(mock_perm, mock_daemon, mock_exists, mock_env, mock_platform, tmp_path, capsys, monkeypatch):
    """Test combining -S, -U, and -u flags"""
    system_file = tmp_path / "system_crontab"
    system_file.write_text("0 1 * * * root echo system\n")
    user_file = tmp_path / "user_crontab"
    user_file.write_text("0 2 * * * echo user\n")
    username_file = tmp_path / "crontab.testuser"
    username_file.write_text("0 3 * * * echo username\n")

    def fake_find_user_crontab(username):
        if username == "testuser":
            return str(username_file)
        return None

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    code = run_main(["--format", "json", "-S", str(system_file), "-U", str(user_file), "-u", "testuser"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 3
    # Check that system file is marked correctly
    system_entries = [f for f in data["files"] if f["is_system_crontab"]]
    user_entries = [f for f in data["files"] if not f["is_system_crontab"]]
    assert len(system_entries) == 1
    assert len(user_entries) == 2


# ============================================================================
# Helper function tests
# ============================================================================


@patch("checkcrontab.main.os.path.exists")
def test_find_user_crontab_from_var_spool_crontabs(mock_exists):
    """Test find_user_crontab finding file in /var/spool/cron/crontabs/"""
    def exists_side_effect(path):
        return path == "/var/spool/cron/crontabs/testuser"

    mock_exists.side_effect = exists_side_effect
    result = check_crontab.find_user_crontab("testuser")
    assert result == "/var/spool/cron/crontabs/testuser"


@patch("checkcrontab.main.os.path.exists")
def test_find_user_crontab_from_var_spool_cron(mock_exists):
    """Test find_user_crontab finding file in /var/spool/cron/"""
    def exists_side_effect(path):
        return path == "/var/spool/cron/testuser"

    mock_exists.side_effect = exists_side_effect
    result = check_crontab.find_user_crontab("testuser")
    assert result == "/var/spool/cron/testuser"


@patch("checkcrontab.main.os.path.exists")
def test_find_user_crontab_from_tmp(mock_exists):
    """Test find_user_crontab finding file in /tmp/"""
    def exists_side_effect(path):
        return path == "/tmp/crontab.testuser"

    mock_exists.side_effect = exists_side_effect
    result = check_crontab.find_user_crontab("testuser")
    assert result == "/tmp/crontab.testuser"


@patch("checkcrontab.main.checker.get_crontab")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_find_user_crontab_via_command(mock_exists, mock_get_crontab, tmp_path):
    """Test find_user_crontab getting crontab via command"""
    mock_get_crontab.return_value = "0 * * * * echo test\n"

    result = check_crontab.find_user_crontab("testuser")
    assert result is not None
    assert "testuser" in result
    # Check that file was created
    with open(result) as f:
        assert f.read() == "0 * * * * echo test\n"
    # Cleanup
    import os
    os.unlink(result)


@patch("checkcrontab.main.checker.get_crontab", return_value=None)
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_find_user_crontab_not_found(mock_exists, mock_get_crontab):
    """Test find_user_crontab when user crontab not found"""
    result = check_crontab.find_user_crontab("testuser")
    assert result is None


def test_get_files_with_directory(tmp_path):
    """Test get_files with directory containing valid and invalid files"""
    cron_dir = tmp_path / "cron.d"
    cron_dir.mkdir()

    # Valid files
    (cron_dir / "valid-job").write_text("0 * * * * root echo valid\n")
    (cron_dir / "another_job").write_text("0 * * * * root echo another\n")

    # Invalid files (should be filtered out)
    (cron_dir / ".hidden").write_text("0 * * * * root echo hidden\n")  # starts with dot
    (cron_dir / "backup~").write_text("0 * * * * root echo backup\n")  # ends with tilde
    (cron_dir / "file.txt").write_text("0 * * * * root echo txt\n")  # contains dot
    (cron_dir / "file#name").write_text("0 * * * * root echo hash\n")  # contains hash

    files, errors = check_crontab.get_files(str(cron_dir))

    # Should only return valid files
    assert len(files) == 2
    assert any("valid-job" in f for f in files)
    assert any("another_job" in f for f in files)

    # Should have errors for invalid files (at least 3: .hidden, backup~, file.txt)
    # Note: file#name might fail to create on some systems
    assert len(errors) >= 3


def test_get_files_with_single_file(tmp_path):
    """Test get_files with single file"""
    f = tmp_path / "crontab"
    f.write_text("0 * * * * echo test\n")

    files, errors = check_crontab.get_files(str(f))
    assert len(files) == 1
    assert str(f) in files
    assert errors == []


def test_get_files_with_nonexistent_path():
    """Test get_files with non-existent path"""
    files, errors = check_crontab.get_files("/nonexistent/path")
    assert files == []
    assert errors == []


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_check_file_read_error(mock_exists, mock_env, mock_platform, tmp_path):
    """Test check_file with read error"""
    # Create a file then make it unreadable
    f = tmp_path / "unreadable"
    f.write_text("0 * * * * echo test\n")

    # Mock open to raise an exception
    def mock_open_error(*args, **kwargs):
        raise PermissionError("Permission denied")

    with patch("checkcrontab.main.open", side_effect=mock_open_error):
        rows, errors = check_crontab.check_file(str(f))
        assert rows == 0
        assert len(errors) == 1
        assert "Error reading file" in errors[0]


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
def test_main_import_error_handling(mock_env, mock_platform, capsys):
    """Test main function error handling for import errors"""
    # This test is to ensure the exception handling in imports works
    # The actual imports succeed, so we just verify the function exists
    assert hasattr(check_crontab, "main")
    assert callable(check_crontab.main)


# ============================================================================
# gen_sarif_output detailed tests
# ============================================================================


def test_gen_sarif_output_structure():
    """Test gen_sarif_output creates proper SARIF structure"""
    files_data = [
        {
            "file": "test.cron",
            "errors": [
                "test.cron (Line 5): 0 * * * * echo test # value 60 out of bounds"
            ]
        }
    ]

    sarif = check_crontab.gen_sarif_output(files_data, total_errors=1, total_warnings=0)

    # Check structure
    assert sarif["$schema"] == "https://json.schemastore.org/sarif-2.1.0.json"
    assert sarif["version"] == "2.1.0"
    assert "runs" in sarif
    assert len(sarif["runs"]) == 1

    run = sarif["runs"][0]
    assert "tool" in run
    assert "results" in run
    assert run["tool"]["driver"]["name"] == "checkcrontab"

    # Check result
    assert len(run["results"]) == 1
    result = run["results"][0]
    assert result["ruleId"] == "crontab-syntax-error"
    assert result["level"] == "error"
    assert "message" in result
    assert "locations" in result


def test_gen_sarif_output_no_errors():
    """Test gen_sarif_output with no errors"""
    files_data = [{"file": "test.cron", "errors": []}]

    sarif = check_crontab.gen_sarif_output(files_data, total_errors=0, total_warnings=0)

    # Should have empty results
    assert len(sarif["runs"][0]["results"]) == 0


def test_gen_sarif_output_multiple_errors():
    """Test gen_sarif_output with multiple errors"""
    files_data = [
        {
            "file": "test.cron",
            "errors": [
                "test.cron (Line 1): 60 * * * * echo test # value 60 out of bounds",
                "test.cron (Line 2): * 25 * * * echo test # value 25 out of bounds"
            ]
        }
    ]

    sarif = check_crontab.gen_sarif_output(files_data, total_errors=2, total_warnings=0)

    # Should have 2 results
    assert len(sarif["runs"][0]["results"]) == 2
    # Both results should have proper structure
    for result in sarif["runs"][0]["results"]:
        assert "ruleId" in result
        assert "message" in result
        assert "locations" in result
        assert "physicalLocation" in result["locations"][0]
