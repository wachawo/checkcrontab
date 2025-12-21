#!/usr/bin/env python3
# mypy: ignore-errors
"""
Tests for checkcrontab package.

This module contains comprehensive unit tests for the checkcrontab package,
testing functionality such as:
- Crontab line validation (user and system formats)
- Special keyword handling
- System-level checks (daemon, permissions)
- File validation and error handling
- Output formats (JSON, SARIF)
- Command-line argument parsing
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

# ============================================================================
# Module Import Setup
# ============================================================================

# Dynamically import the checkcrontab package from parent directory
PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "checkcrontab"

# Create module specification and load the package
package_spec = importlib.util.spec_from_file_location(
    "checkcrontab",
    PACKAGE_ROOT / "__init__.py",
    submodule_search_locations=[str(PACKAGE_ROOT)]
)
checkcrontab_pkg = importlib.util.module_from_spec(package_spec)
sys.modules["checkcrontab"] = checkcrontab_pkg
package_spec.loader.exec_module(checkcrontab_pkg)

# Import specific modules for testing
check_crontab = importlib.import_module("checkcrontab.main")
checker = importlib.import_module("checkcrontab.checker")
setup_logging = importlib.import_module("checkcrontab.logger").setup_logging


# ============================================================================
# Helper Functions
# ============================================================================

def run_main_with_args(args):
    """Helper to run main() with specific command-line arguments."""
    with patch("sys.argv", ["checkcrontab", *args]):
        return check_crontab.main()


def run_main(args):
    """Helper to run main() with arguments (no 'checkcrontab' prefix)."""
    with patch("sys.argv", ["checkcrontab", *args]):
        return check_crontab.main()


# ============================================================================
# Logging Tests
# ============================================================================

def test_setup_logging():
    """Test logging setup with various configurations."""
    # Should not raise any exceptions with different debug/color settings
    setup_logging(debug=False, no_colors=False)
    setup_logging(debug=True, no_colors=True)


# ============================================================================
# User Crontab Line Checking Tests
# ============================================================================

def test_valid_user_crontab_line():
    """Test validation of a correctly formatted user crontab line."""
    line = "0 2 * * * /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


def test_invalid_user_crontab_line_insufficient_fields():
    """Test user crontab line with insufficient fields (missing command)."""
    line = "0 2 * * *"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_missing_command():
    """Test user crontab line with trailing space but no command."""
    line = "0 2 * * * "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_user_crontab_line_invalid_minute():
    """Test user crontab line with invalid minute value (out of range)."""
    line = "60 2 * * * /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "value 60 out of bounds" in errors[0]


def test_valid_user_crontab_line_with_special_keyword():
    """Test valid user crontab line using @reboot special keyword."""
    line = "@reboot /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


def test_environment_variable_skipped():
    """Test that environment variable assignments are skipped (not validated)."""
    line = "MAILTO=user@example.com"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


# ============================================================================
# System Crontab Line Checking Tests
# ============================================================================

def test_valid_system_crontab_line():
    """Test validation of a correctly formatted system crontab line (includes user)."""
    line = "0 2 * * * root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_valid_system_crontab_line_with_dash_prefix():
    """Test system crontab line with dash prefix in minutes field."""
    line = "-0 2 * * * root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_invalid_system_crontab_line_insufficient_fields():
    """Test system crontab line with insufficient fields (user but no command)."""
    line = "0 2 * * * root"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_missing_command():
    """Test system crontab line with user but trailing space (no command)."""
    line = "0 2 * * * root "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_system_crontab_line_invalid_user():
    """Test system crontab line with invalid user format (contains comment character)."""
    line = "0 2 * * * #root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert len(errors) == 1
    assert warnings == []
    assert "invalid user format" in errors[0]


# ============================================================================
# Special Keyword Line Checking Tests
# ============================================================================

def test_valid_user_special_keyword_line():
    """Test valid special keyword line in user crontab format."""
    line = "@reboot /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert errors == []
    assert warnings == []


def test_valid_system_special_keyword_line():
    """Test valid special keyword line in system crontab format (includes user)."""
    line = "@reboot root /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=True)
    assert errors == []
    assert warnings == []


def test_invalid_special_keyword_line_insufficient_fields():
    """Test special keyword line with insufficient fields (no command)."""
    line = "@reboot"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_missing_command():
    """Test special keyword line with trailing space but no command."""
    line = "@reboot "
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "insufficient fields" in errors[0]


def test_invalid_special_keyword_line_invalid_keyword():
    """Test special keyword line with invalid/unrecognized keyword."""
    line = "@invalid /usr/bin/backup.sh"
    errors, warnings = checker.check_line(line, 1, "test.txt", is_system_crontab=False)
    assert len(errors) == 1
    assert warnings == []
    assert "invalid special keyword" in errors[0]


# ============================================================================
# System-Level Checks Tests
# ============================================================================

@patch("checkcrontab.checker.subprocess.run")
def test_check_cron_daemon_running(mock_run):
    """Test cron daemon check when daemon is running (systemctl returns active)."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "active\n"
    
    # Should not raise any exceptions when daemon is running
    checker.check_daemon()


@patch("checkcrontab.checker.subprocess.run")
def test_check_cron_daemon_not_running(mock_run):
    """Test cron daemon check when daemon is not running (systemctl returns inactive)."""
    mock_run.return_value.returncode = 1
    mock_run.return_value.stdout = "inactive\n"
    
    # Should not raise any exceptions when daemon is not running
    checker.check_daemon()


@patch("checkcrontab.checker.os.path.exists")
@patch("checkcrontab.checker.os.stat")
def test_check_system_crontab_permissions_correct(mock_stat, mock_exists):
    """Test system crontab permissions check with correct permissions (0o644, root-owned)."""
    mock_exists.return_value = True
    mock_stat_info = MagicMock()
    mock_stat_info.st_mode = 0o644  # Correct permissions
    mock_stat_info.st_uid = 0  # Root ownership
    mock_stat.return_value = mock_stat_info
    
    # Should not raise any exceptions with correct permissions
    checker.check_owner_and_permissions('/etc/crontab')


@patch("checkcrontab.checker.os.path.exists")
def test_check_system_crontab_permissions_file_not_exists(mock_exists):
    """Test system crontab permissions check when file doesn't exist."""
    mock_exists.return_value = False
    
    # Should not raise any exceptions for non-existent file
    checker.check_owner_and_permissions('/etc/crontab')


# ============================================================================
# File Validation Tests (Integration)
# ============================================================================

@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_valid_file_returns_zero(mock_permissions, mock_daemon, mock_exists, mock_env, 
                                         mock_platform, monkeypatch):
    """Test that a valid system crontab file returns exit code 0 (no errors)."""
    mock_platform.return_value = "Linux"
    
    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default
    mock_env.side_effect = mock_env_side_effect
    
    mock_exists.return_value = True
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    if hasattr(os, "getuid"):
        monkeypatch.setenv("CRONTAB_OWNER_UID", str(os.getuid()))

    with patch("sys.argv", ["checkcrontab", "examples/system_valid"]):
        exit_code = check_crontab.main()
        assert exit_code == 0


@patch("checkcrontab.main.platform.system")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.main.os.path.exists")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_incorrect_file_returns_non_zero(mock_permissions, mock_daemon, mock_exists, 
                                                 mock_env, mock_platform, monkeypatch):
    """Test that an invalid system crontab file returns exit code 1 (has errors)."""
    mock_platform.return_value = "Linux"
    
    def mock_env_side_effect(key, default=None):
        if key == "GITHUB_ACTIONS":
            return "true"
        return default
    mock_env.side_effect = mock_env_side_effect
    
    mock_exists.return_value = True
    mock_daemon.return_value = []
    mock_permissions.return_value = []

    if hasattr(os, "getuid"):
        monkeypatch.setenv("CRONTAB_OWNER_UID", str(os.getuid()))

    with patch("sys.argv", ["checkcrontab", "examples/system_incorrect"]):
        exit_code = check_crontab.main()
        assert exit_code == 1


# ============================================================================
# Multi-line Command Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_multiline_command_user_crontab(mock_exists, mock_env, mock_platform, tmp_path):
    """Test handling of multi-line commands with continuation backslashes in user crontab."""
    content = "0 2 * * * echo part1 \\\n    part2\n"
    f = tmp_path / "multiline_cron"
    f.write_text(content)
    code = run_main_with_args([str(f)])
    assert code == 0


# ============================================================================
# Duplicate File Handling Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_duplicate_files_processed_once(mock_exists, mock_env, mock_platform, tmp_path):
    """Test that duplicate file arguments are processed only once."""
    f = tmp_path / "dup_cron"
    f.write_text("0 1 * * * echo hi\n")
    calls = []

    def fake_check_file(path, is_system_crontab=False):
        calls.append((path, is_system_crontab))
        return 1, []

    with patch("checkcrontab.main.check_file", side_effect=fake_check_file):
        code = run_main_with_args([str(f), str(f), str(f)])
    assert code == 0
    # Only one call for the file despite duplicates
    assert len(calls) == 1


# ============================================================================
# Username Resolution Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_username_resolution(mock_exists, mock_getenv, mock_platform, monkeypatch, 
                             tmp_path, capsys):
    """Test that usernames are resolved to user crontab files."""
    user_file = tmp_path / "user_pytest_user"
    user_file.write_text("0 3 * * * echo user\n")

    def fake_find_user_crontab(username):
        assert username == "pytest_user"
        return str(user_file)

    monkeypatch.setattr(check_crontab, "find_user_crontab", fake_find_user_crontab)

    def exists_side_effect(path):
        if path == "pytest_user":
            return False  # Not a file, should be treated as username
        return True
    mock_exists.side_effect = exists_side_effect

    code = run_main(["--format", "json", "pytest_user"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 1
    assert data["files"][0]["success"] is True


# ============================================================================
# Cross-Platform Compatibility Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Windows")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.main.os.getenv", return_value="true")
def test_non_linux_skips_system(mock_env, mock_exists, mock_platform, tmp_path):
    """Test that system crontab checks are skipped on non-Linux systems."""
    f = tmp_path / "user_cron"
    f.write_text("0 4 * * * echo hi\n")
    code = run_main_with_args([str(f)])
    assert code == 0


@patch("checkcrontab.main.platform.system", return_value="Darwin")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_non_linux_message(mock_exists, mock_env, mock_platform, caplog, tmp_path):
    """Test appropriate message is logged when skipping system checks on non-Linux."""
    caplog.set_level("INFO")
    f = tmp_path / "user_cron"
    f.write_text("0 1 * * * echo mac\n")
    code = run_main([str(f)])
    assert code == 0
    assert any("Skipping system checks on non-Linux" in r.getMessage() 
               for r in caplog.records)


# ============================================================================
# File Existence and Error Handling Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_file_not_exists_warning(mock_exists, mock_env, mock_platform, caplog):
    """Test that missing files generate warnings but don't cause failure."""
    caplog.set_level(logging.DEBUG)
    code = run_main_with_args(["/tmp/does_not_exist_cron"])
    assert code == 0  # Warning, but no errors -> exit 0
    assert any("not found" in r.getMessage() for r in caplog.records)


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_debug_mode_outputs_valid(mock_exists, mock_env, mock_platform, tmp_path, caplog):
    """Test that debug mode outputs additional validation information."""
    f = tmp_path / "debug_cron"
    f.write_text("0 5 * * * echo hi\n")
    caplog.set_level(logging.DEBUG)
    with patch("sys.argv", ["checkcrontab", "--debug", str(f)]):
        code = check_crontab.main()
    assert code == 0
    assert any("# valid" in r.getMessage() 
               for r in caplog.records if r.levelname == "DEBUG")


# ============================================================================
# JSON Output Format Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_valid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    """Test JSON output format for a valid crontab file."""
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
    """Test JSON output format for an invalid crontab file."""
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


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_json_multiple_files_mixed(mock_perm, mock_daemon, mock_env, mock_platform, 
                                   tmp_path, capsys):
    """Test JSON output format with multiple files (some valid, some invalid)."""
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


# ============================================================================
# SARIF Output Format Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_sarif_valid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    """Test SARIF output format for a valid file."""
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
    # No errors means empty results
    assert len(data["runs"][0]["results"]) == 0


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_sarif_invalid_file(mock_perm, mock_daemon, mock_env, mock_platform, capsys):
    """Test SARIF output format for an invalid file."""
    mock_env.side_effect = lambda k, d=None: "true" if k == "GITHUB_ACTIONS" else d
    code = run_main(["--format", "sarif", "examples/system_incorrect"])
    assert code == 1
    out = capsys.readouterr().out
    data = json.loads(out)
    # Check SARIF structure
    assert data["version"] == "2.1.0"
    assert "runs" in data
    assert len(data["runs"]) == 1
    # Should have errors
    assert len(data["runs"][0]["results"]) > 0
    # Check result structure
    result = data["runs"][0]["results"][0]
    assert "ruleId" in result
    assert "message" in result
    assert "locations" in result


# ============================================================================
# Strict Mode Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_strict_mode_with_errors(mock_perm, mock_daemon, mock_exists, mock_env, 
                                 mock_platform, tmp_path):
    """Test that --strict flag correctly treats errors as failures."""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--strict", str(f)])
    assert code == 1


# ============================================================================
# Exit-Zero Mode Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_exit_zero_with_errors(mock_perm, mock_daemon, mock_exists, mock_env, 
                               mock_platform, tmp_path):
    """Test that --exit-zero returns 0 even with validation errors."""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--exit-zero", str(f)])
    assert code == 0  # Should return 0 despite errors


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_exit_zero_with_strict_and_errors(mock_perm, mock_daemon, mock_exists, mock_env, 
                                          mock_platform, tmp_path):
    """Test that --exit-zero overrides --strict flag."""
    f = tmp_path / "invalid_cron"
    f.write_text("61 1 * * * root echo bad\n")  # Invalid minute
    code = run_main(["--strict", "--exit-zero", str(f)])
    assert code == 0  # --exit-zero should override everything


# ============================================================================
# Directory Handling Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.main.os.path.isdir")
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_system_flag_with_directory(mock_perm, mock_daemon, mock_isdir, mock_exists, 
                                     mock_env, mock_platform, tmp_path, capsys):
    """Test -S flag with directory containing multiple cron files."""
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
            return [str(cron_dir / "job1"), str(cron_dir / "job2"), 
                    str(cron_dir / "job3")], []
        return [], []

    with patch("checkcrontab.main.get_files", side_effect=mock_get_files):
        code = run_main(["--format", "json", "-S", str(cron_dir)])

    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 3
    assert all(f["is_system_crontab"] for f in data["files"])


# ============================================================================
# Multiple Usernames Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_multiple_usernames(mock_perm, mock_daemon, mock_exists, mock_env, 
                            mock_platform, tmp_path, capsys, monkeypatch):
    """Test -u flag with multiple usernames."""
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


# ============================================================================
# Combined Flags Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
@patch("checkcrontab.checker.check_daemon")
@patch("checkcrontab.checker.check_owner_and_permissions")
def test_combined_system_user_and_username_flags(mock_perm, mock_daemon, mock_exists, 
                                                  mock_env, mock_platform, tmp_path, 
                                                  capsys, monkeypatch):
    """Test combining -S, -U, and -u flags together."""
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

    code = run_main(["--format", "json", "-S", str(system_file), "-U", str(user_file), 
                     "-u", "testuser"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["total_files"] == 3
    # Check that system file is marked correctly
    system_entries = [f for f in data["files"] if f["is_system_crontab"]]
    user_entries = [f for f in data["files"] if not f["is_system_crontab"]]
    assert len(system_entries) == 1
    assert len(user_entries) == 2


# ============================================================================
# Helper Function Tests
# ============================================================================

@patch("checkcrontab.main.os.path.exists")
def test_find_user_crontab_from_var_spool_crontabs(mock_exists):
    """Test find_user_crontab finding file in /var/spool/cron/crontabs/."""
    def exists_side_effect(path):
        return path == "/var/spool/cron/crontabs/testuser"
    mock_exists.side_effect = exists_side_effect
    
    result = check_crontab.find_user_crontab("testuser")
    assert result == "/var/spool/cron/crontabs/testuser"


@patch("checkcrontab.main.checker.get_crontab")
@patch("checkcrontab.main.os.path.exists", return_value=False)
def test_find_user_crontab_via_command(mock_exists, mock_get_crontab, tmp_path):
    """Test find_user_crontab getting crontab via command execution."""
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


def test_get_files_with_directory(tmp_path):
    """Test get_files with directory containing valid and invalid files."""
    cron_dir = tmp_path / "cron.d"
    cron_dir.mkdir()

    # Valid files
    (cron_dir / "valid-job").write_text("0 * * * * root echo valid\n")
    (cron_dir / "another_job").write_text("0 * * * * root echo another\n")

    # Invalid files (should be filtered out)
    (cron_dir / ".hidden").write_text("0 * * * * root echo hidden\n")  # starts with dot
    (cron_dir / "backup~").write_text("0 * * * * root echo backup\n")  # ends with tilde

    files, errors = check_crontab.get_files(str(cron_dir))

    # Should only return valid files
    assert len(files) == 2
    assert any("valid-job" in f for f in files)
    assert any("another_job" in f for f in files)

    # Should have errors for invalid files
    assert len(errors) >= 2


# ============================================================================
# Error Handling Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_check_file_read_error(mock_exists, mock_env, mock_platform, tmp_path):
    """Test check_file handling of read errors (e.g., permission denied)."""
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


# ============================================================================
# SARIF Output Generation Tests
# ============================================================================

def test_gen_sarif_output_structure():
    """Test gen_sarif_output creates proper SARIF structure."""
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
    """Test gen_sarif_output with no errors."""
    files_data = [{"file": "test.cron", "errors": []}]

    sarif = check_crontab.gen_sarif_output(files_data, total_errors=0, total_warnings=0)

    # Should have empty results
    assert len(sarif["runs"][0]["results"]) == 0


# ============================================================================
# Edge Case Tests
# ============================================================================

@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_check_file_multiline_continuation_with_backslash(mock_exists, mock_env, 
                                                           mock_platform, tmp_path):
    """Test check_file with multiline command continuation with backslash."""
    f = tmp_path / "multiline_cron"
    content = """# Test multiline
0 2 * * * root echo line1 \\
    && echo line2 \\
    && echo line3
"""
    f.write_text(content)
    rows, errors = check_crontab.check_file(str(f), is_system_crontab=True)
    assert rows == 1  # Should count as 1 line
    assert errors == []


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
@patch("checkcrontab.main.os.path.exists", return_value=True)
def test_main_check_daemon_warnings_on_linux(mock_exists, mock_env, mock_platform, 
                                              tmp_path, caplog):
    """Test that check_daemon warnings are logged on Linux (not GitHub)."""
    # Mock check_daemon to return a warning
    with patch("checkcrontab.checker.check_daemon") as mock_check_daemon:
        mock_check_daemon.return_value = ["Cron daemon: systemctl not found"]

        f = tmp_path / "test_cron"
        f.write_text("0 1 * * * echo test\n")

        caplog.set_level(logging.WARNING)
        code = run_main([str(f)])
        assert code == 0
        # Should have logged the daemon warning
        assert any("systemctl not found" in r.getMessage() 
                   for r in caplog.records if r.levelname == "WARNING")


@patch("checkcrontab.main.platform.system", return_value="Linux")
@patch("checkcrontab.main.os.getenv", return_value="true")
def test_import_error_handling(mock_env, mock_platform):
    """Test that import errors are handled gracefully (module structure verification)."""
    # Verify the module structure exists
    assert hasattr(check_crontab, "logger")
    assert hasattr(check_crontab, "checker")
