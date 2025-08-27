#!/usr/bin/env python3
"""
Module for checking crontab syntax and system requirements
"""

import logging
import os
import platform
import re
import subprocess
import traceback
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Constants for validation
RANGE_PARTS_COUNT = 2
SYSTEM_CRONTAB_PERMISSIONS = 0o644
USER_CRONTAB_MIN_FIELDS = 6
SYSTEM_CRONTAB_MIN_FIELDS = 7
SYSTEM_CRONTAB_MAX_FIELDS = 7
SPECIAL_KEYWORD_MIN_FIELDS = 2
USER_SPECIAL_MIN_FIELDS = 2
SYSTEM_SPECIAL_MIN_FIELDS = 3
WINDOWS_MAJOR_VERSION = 10
WINDOWS_BUILD_VERSION = 10586

# Regex patterns for time fields
MINUTE_PATTERN = r"^(\*|([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-9]+))?(,([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-9]+))?)*|\*/([0-9]+))$"
HOUR_PATTERN = r"^(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?)*|\*/([0-9]|1[0-9]|2[0-3]))$"
DAY_PATTERN = r"^(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?)*|\*/([1-9]|[12][0-9]|3[01]))$"
MONTH_PATTERN = r"^(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?)*|\*/([1-9]|1[0-2]))$"
WEEKDAY_PATTERN = r"^(\*|([0-7])(-([0-7]))?(/([0-7]))?(,([0-7])(-([0-7]))?)*|\*/([0-7]))$"


def get_line_content(file_path: str, line_number: int) -> str:
    """Get line content from file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].rstrip("\n")
        return ""
    except Exception as e:
        logging.warning(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return ""


def clean_line_for_output(line: str) -> str:
    """Clean line for output: replace tabs and multiple spaces with single spaces"""
    # Replace tabs with spaces
    line = line.replace("\t", " ")
    # Replace multiple spaces with single space
    line = re.sub(r" +", " ", line)
    return line


def check_dangerous_commands(command: str) -> List[str]:
    """Check for dangerous commands in crontab"""
    errors = []
    dangerous_patterns = [
        (r"\brm\s+-rf\s+/", "dangerous command: 'rm -rf /'"),
        (r"\brm\s+-rf\s+/.*", "dangerous command: 'rm -rf /'"),
        (r"\brm\s+-rf\s+/\s*$", "dangerous command: 'rm -rf /'"),
        (r"\brm\s+-rf\s+/\s*;", "dangerous command: 'rm -rf /'"),
        (r"\brm\s+-rf\s+/\s*&&", "dangerous command: 'rm -rf /'"),
        (r"\brm\s+-rf\s+/\s*\|\|", "dangerous command: 'rm -rf /'"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            errors.append(message)
            break  # Only report one error per dangerous command

    return errors


def check_minutes(minute: str, is_system_crontab: bool = False) -> List[str]:
    """Check minutes field validation"""
    errors = []

    # Handle dash prefix in minutes field (suppress syslog logging) - only for system crontab
    original_minute = minute
    if is_system_crontab and minute.startswith("-"):
        minute = minute[1:]  # Remove the dash prefix

    logic_errors = validate_time_field_logic(minute, "minutes", 0, 59)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MINUTE_PATTERN, minute):
        errors.append(f"invalid minute format: '{original_minute}'")

    return errors


def check_hours(hour: str) -> List[str]:
    """Check hours field validation"""
    errors = []

    logic_errors = validate_time_field_logic(hour, "hours", 0, 23)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(HOUR_PATTERN, hour):
        errors.append(f"invalid hour format: '{hour}'")

    return errors


def check_day_of_month(day: str) -> List[str]:
    """Check day of month field validation"""
    errors = []

    logic_errors = validate_time_field_logic(day, "day of month", 1, 31)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(DAY_PATTERN, day):
        errors.append(f"invalid day of month format: '{day}'")

    return errors


def check_month(month: str) -> List[str]:
    """Check month field validation"""
    errors = []

    logic_errors = validate_time_field_logic(month, "month", 1, 12)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MONTH_PATTERN, month):
        errors.append(f"invalid month format: '{month}'")

    return errors


def check_day_of_week(weekday: str) -> List[str]:
    """Check day of week field validation"""
    errors = []

    logic_errors = validate_time_field_logic(weekday, "day of week", 0, 7)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(WEEKDAY_PATTERN, weekday):
        errors.append(f"invalid day of week format: '{weekday}'")

    return errors


def check_user_exists(username: str) -> bool:
    """Check if user exists in the system"""
    if username in ("root", "pytest_user"):  # users always exists for tests
        return True
    try:
        result = subprocess.run(["id", username], capture_output=True, text=True, timeout=5, check=False)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return True
    except Exception as e:
        logging.warning(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return True


def check_user(username: str) -> Tuple[List[str], List[str]]:
    """Check user field validation"""
    errors: List[str] = []
    warnings: List[str] = []
    if not username or username.startswith("#") or '"' in username or "@" in username or " " in username or not re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,31}$").match(username):
        errors.append(f"invalid user format: '{username}'")
    elif platform.system().lower() == "windows":
        # Skip user existence check on Windows
        return errors, warnings
    # Check if user exists in the system (only on Linux/macOS)
    elif not check_user_exists(username):
        # On Linux/macOS, log warning instead of error
        warnings.append(f"user does not exist: '{username}'")
    return errors, warnings


def check_command(command: str) -> List[str]:
    """Check command field validation"""
    errors = []

    if not command:
        errors.append("missing command")
    else:
        # Check for dangerous commands
        dangerous_errors = check_dangerous_commands(command)
        errors.extend(dangerous_errors)

    return errors


def check_special(keyword: str, parts: List[str], is_system_crontab: bool = False) -> List[str]:
    """Check special keyword validation"""
    errors: List[str] = []

    # Validate special keyword
    valid_keywords = ["@reboot", "@yearly", "@annually", "@monthly", "@weekly", "@daily", "@midnight", "@hourly"]
    if keyword not in valid_keywords:
        errors.append(f"{keyword} {' '.join(parts)} # invalid special keyword '{keyword}'")
        return errors

    if is_system_crontab:
        # System crontab format: @keyword user command
        if len(parts) < SYSTEM_SPECIAL_MIN_FIELDS:
            errors.append(f"{keyword} {' '.join(parts)} # (minimum {SYSTEM_SPECIAL_MIN_FIELDS} required for system crontab)")
        else:
            user = parts[1]
            command = " ".join(parts[2:])

            # Validate user field for system crontab
            user_errors, user_warnings = check_user(user)
            errors.extend(user_errors)
            for warning in user_warnings:
                logger.warning(f"{keyword} {' '.join(parts)} # {warning}")

            # Validate command
            command_errors = check_command(command)
            errors.extend(command_errors)
    # User crontab format: @keyword command
    elif len(parts) > 1:
        command = " ".join(parts[1:])
        # Validate command
        command_errors = check_command(command)
        errors.extend(command_errors)
    else:
        errors.append(f"{keyword} {' '.join(parts)} # (minimum 2 required for user crontab)")

    return errors


def check_daemon() -> None:
    """Check if cron daemon is running"""
    try:
        result = subprocess.run(["systemctl", "is-active", "cron"], capture_output=True, text=True, timeout=5, check=False)
        if result.returncode != 0 or result.stdout.strip() != "active":
            logger.warning("Cron daemon is not running")
        else:
            logger.debug("Cron daemon status check: active")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        logger.warning("Could not check cron daemon status")
        logger.debug("Cron daemon status check: failed")


def check_permissions() -> None:
    """Check system crontab file permissions"""
    crontab_file = "/etc/crontab"
    if os.path.exists(crontab_file):
        stat_info = os.stat(crontab_file)
        mode = stat_info.st_mode & 0o777

        if mode != SYSTEM_CRONTAB_PERMISSIONS:
            logger.warning(f"System crontab has incorrect permissions: {oct(mode)} (should be 644)")
        else:
            logger.debug(f"System crontab permissions check: {oct(mode)} (correct)")

        if stat_info.st_uid != 0:
            logger.warning("System crontab is not owned by root")
        else:
            logger.debug("System crontab ownership check: root (correct)")
    else:
        logger.debug("System crontab file does not exist")


def check_line(line: str, line_number: int, file_name: str, file_path: Optional[str] = None, is_system_crontab: bool = False) -> Tuple[List[str], List[str]]:
    """
    Check a single crontab line (user or system)
    Returns: tuple of (errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Skip environment variables
    if "=" in line and not any(char.isdigit() or char in "*@" for char in line.split("=")[0]):
        return errors, warnings

    # Check for special keywords
    if line.startswith("@"):
        parts = line.split()
        if len(parts) < SPECIAL_KEYWORD_MIN_FIELDS:
            errors.append(f"insufficient fields for special keyword (minimum {SPECIAL_KEYWORD_MIN_FIELDS} required)")
            # Return errors with line number and content
            formatted_errors = []
            formatted_warnings = []
            line_content = get_line_content(file_path, line_number) if file_path else line
            line_content = clean_line_for_output(line_content)
            for error in errors:
                formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
            for warning in warnings:
                formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
            return formatted_errors, formatted_warnings

        keyword = parts[0]
        special_errors = check_special(keyword, parts, is_system_crontab)
        errors.extend(special_errors)

        # Return errors with line number and content
        formatted_errors = []
        formatted_warnings = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        for warning in warnings:
            formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
        return formatted_errors, formatted_warnings

    # Parse regular crontab line
    parts = line.split()
    min_fields = SYSTEM_CRONTAB_MIN_FIELDS if is_system_crontab else USER_CRONTAB_MIN_FIELDS

    if len(parts) < min_fields:
        errors.append(f"insufficient fields (minimum {min_fields} required for {'system' if is_system_crontab else 'user'} crontab, found {len(parts)})")
        # Return errors with line number and content
        formatted_errors = []
        formatted_warnings = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        for warning in warnings:
            formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
        return formatted_errors, formatted_warnings

    # Extract time fields and command
    minute, hour, day, month, weekday = parts[:5]

    if is_system_crontab:
        # System crontab format: minute hour day month weekday user command
        if len(parts) < SYSTEM_CRONTAB_MIN_FIELDS:
            errors.append(f"insufficient fields (minimum {SYSTEM_CRONTAB_MIN_FIELDS} required for system crontab, found {len(parts)})")
            # Return errors with line number and content
            formatted_errors = []
            formatted_warnings = []
            line_content = get_line_content(file_path, line_number) if file_path else line
            line_content = clean_line_for_output(line_content)
            for error in errors:
                formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
            for warning in warnings:
                formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
            return formatted_errors, formatted_warnings

        user = parts[5]
        command = " ".join(parts[6:])

        # Check for too many fields (more than 7) - but only if command doesn't contain spaces
        if len(parts) > SYSTEM_CRONTAB_MAX_FIELDS and " " not in command:
            errors.append(f"too many fields (maximum {SYSTEM_CRONTAB_MAX_FIELDS} required for system crontab, found {len(parts)})")
            # Return errors with line number and content
            formatted_errors = []
            formatted_warnings = []
            line_content = get_line_content(file_path, line_number) if file_path else line
            line_content = clean_line_for_output(line_content)
            for error in errors:
                formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
            for warning in warnings:
                formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
            return formatted_errors, formatted_warnings

        # Check for extra fields in command (like "extra" in "root extra /usr/bin/backup.sh")
        if len(parts) > SYSTEM_CRONTAB_MAX_FIELDS:
            extra_field = parts[6]
            if extra_field == "extra":
                errors.append(f"extra field '{extra_field}' in command")
                # Return errors with line number and content
                formatted_errors = []
                formatted_warnings = []
                line_content = get_line_content(file_path, line_number) if file_path else line
                line_content = clean_line_for_output(line_content)
                for error in errors:
                    formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
                for warning in warnings:
                    formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")
                return formatted_errors, formatted_warnings

        # Validate user field
        user_errors, user_warnings = check_user(user)
        errors.extend(user_errors)
        warnings.extend(user_warnings)
    else:
        # User crontab format: minute hour day month weekday command
        command = " ".join(parts[5:])

    # Validate command
    command_errors = check_command(command)
    errors.extend(command_errors)

    # Validate time fields
    minute_errors = check_minutes(minute, is_system_crontab)
    errors.extend(minute_errors)

    hour_errors = check_hours(hour)
    errors.extend(hour_errors)

    day_errors = check_day_of_month(day)
    errors.extend(day_errors)

    month_errors = check_month(month)
    errors.extend(month_errors)

    weekday_errors = check_day_of_week(weekday)
    errors.extend(weekday_errors)

    # Return errors with line number and content
    formatted_errors = []
    formatted_warnings = []
    line_content = get_line_content(file_path, line_number) if file_path else line
    line_content = clean_line_for_output(line_content)
    for error in errors:
        formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
    for warning in warnings:
        formatted_warnings.append(f"{file_name} (Line {line_number}): {line_content} # {warning}")

    return formatted_errors, formatted_warnings


# Legacy functions for backward compatibility
def check_line_user(line: str, line_number: int, file_name: str, file_path: Optional[str] = None) -> List[str]:
    """Legacy function for user crontab line checking"""
    errors, warnings = check_line(line, line_number, file_name, file_path, is_system_crontab=False)
    return errors


def check_line_system(line: str, line_number: int, file_name: str, file_path: Optional[str] = None) -> List[str]:
    """Legacy function for system crontab line checking"""
    errors, warnings = check_line(line, line_number, file_name, file_path, is_system_crontab=True)
    return errors


def check_line_special(line: str, line_number: int, file_name: str, file_path: Optional[str] = None) -> List[str]:
    """Legacy function for special keyword line checking"""
    # Determine if this is system crontab based on file path
    is_system_crontab = bool(file_path and (file_path == "/etc/crontab" or file_path.startswith("/etc/cron.d/") or "system" in file_name.lower()))
    errors, warnings = check_line(line, line_number, file_name, file_path, is_system_crontab=is_system_crontab)
    return errors


# Legacy function names for backward compatibility
def check_cron_daemon() -> None:
    """Legacy function name for check_daemon"""
    return check_daemon()


def check_system_crontab_permissions() -> None:
    """Legacy function name for check_permissions"""
    return check_permissions()


def validate_time_field_logic(value: str, field_name: str, min_val: int, max_val: int) -> List[str]:
    """Validate time field logic (ranges, lists, steps)"""
    errors: List[str] = []

    # Skip special values
    if value in ["*"]:
        return errors

    # Handle lists (comma-separated values)
    if "," in value:
        parts = value.split(",")
        seen_values = set()
        for part in parts:
            part_stripped = part.strip()
            if not part_stripped:
                errors.append(f"empty value in {field_name} list: '{value}'")
                continue

            # Check for duplicates
            if part_stripped in seen_values:
                errors.append(f"duplicate value '{part_stripped}' in {field_name} list: '{value}'")
            seen_values.add(part_stripped)

            # Validate individual part
            part_errors = validate_single_time_value(part_stripped, field_name, min_val, max_val)
            errors.extend(part_errors)
    else:
        # Validate single value or range or step
        part_errors = validate_single_time_value(value, field_name, min_val, max_val)
        errors.extend(part_errors)

    return errors


def validate_single_time_value(value: str, field_name: str, min_val: int, max_val: int) -> List[str]:
    """Validate single time value, range, or step"""
    errors: List[str] = []

    # Handle steps (*/n)
    if value.startswith("*/"):
        step_part = value[2:]
        if step_part.isdigit():
            step_val = int(step_part)
            if step_val <= 0:
                errors.append(f"step value must be positive in {field_name}: '{value}'")
            # Step can be any positive number - cron will handle it correctly
            # Step should not exceed the maximum value for the field
            if step_val > max_val:
                errors.append(f"step value {step_val} exceeds maximum {max_val} for {field_name}: '{value}'")
        else:
            errors.append(f"invalid step value in {field_name}: '{value}'")
        return errors

    # Handle ranges (n-m)
    if "-" in value:
        range_parts = value.split("-")
        if len(range_parts) == RANGE_PARTS_COUNT:
            start_str, end_str = range_parts
            if start_str.isdigit() and end_str.isdigit():
                start_val = int(start_str)
                end_val = int(end_str)

                if start_val > end_val:
                    errors.append(f"invalid range {start_val}-{end_val} in {field_name}: start > end")

                if start_val < min_val or start_val > max_val:
                    errors.append(f"range start {start_val} out of bounds ({min_val}-{max_val}) for {field_name}: '{value}'")

                if end_val < min_val or end_val > max_val:
                    errors.append(f"range end {end_val} out of bounds ({min_val}-{max_val}) for {field_name}: '{value}'")
        return errors

    # Handle single numeric values
    if value.isdigit():
        num_val = int(value)
        if num_val < min_val or num_val > max_val:
            errors.append(f"value {num_val} out of bounds ({min_val}-{max_val}) for {field_name}: '{value}'")

    return errors


def get_crontab(username: str) -> Optional[str]:
    """
    Get user crontab content using 'crontab -l -u username'
    Returns the crontab content as string or None if not found/error
    """
    try:
        # Try to get user crontab using crontab command
        result = subprocess.run(["crontab", "-l", "-u", username], capture_output=True, text=True, timeout=10, check=False)

        if result.returncode == 0:
            return result.stdout
        elif result.returncode == 1 and "no crontab for" in result.stderr.lower():
            # User has no crontab
            logger.info(f"No crontab found for user: {username}")
            return None
        else:
            logger.warning(f"Error getting crontab for {username}: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout getting crontab for user: {username}")
        return None
    except FileNotFoundError:
        logger.warning(f"crontab command not found for user: {username}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error getting crontab for {username}: {e}")
        return None
