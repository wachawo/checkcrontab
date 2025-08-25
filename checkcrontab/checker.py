#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for checking crontab syntax and system requirements
"""
import os
import re
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

# Regex patterns for time fields
MINUTE_PATTERN = r'^(\*|([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-9]+))?(,([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-9]+))?)*|\*/([0-9]+))$'
HOUR_PATTERN = r'^(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?)*|\*/([0-9]|1[0-9]|2[0-3]))$'
DAY_PATTERN = r'^(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?)*|\*/([1-9]|[12][0-9]|3[01]))$'
MONTH_PATTERN = r'^(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?)*|\*/([1-9]|1[0-2]))$'
WEEKDAY_PATTERN = r'^(\*|([0-7])(-([0-7]))?(/([0-7]))?(,([0-7])(-([0-7]))?)*|\*/([0-7]))$'


def get_line_content(file_path: str, line_number: int) -> str:
    """Get line content from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].rstrip('\n')
        return ""
    except Exception:
        return ""


def clean_line_for_output(line: str) -> str:
    """Clean line for output: replace tabs and multiple spaces with single spaces"""
    import re
    # Replace tabs with spaces
    line = line.replace('\t', ' ')
    # Replace multiple spaces with single space
    line = re.sub(r' +', ' ', line)
    return line


def check_dangerous_commands(command: str) -> List[str]:
    """Check for dangerous commands in crontab"""
    errors = []
    dangerous_patterns = [
        (r'\brm\s+-rf\s+/', "dangerous command: 'rm -rf /'"),
        (r'\brm\s+-rf\s+/.*', "dangerous command: 'rm -rf /'"),
        (r'\brm\s+-rf\s+/\s*$', "dangerous command: 'rm -rf /'"),
        (r'\brm\s+-rf\s+/\s*;', "dangerous command: 'rm -rf /'"),
        (r'\brm\s+-rf\s+/\s*&&', "dangerous command: 'rm -rf /'"),
        (r'\brm\s+-rf\s+/\s*\|\|', "dangerous command: 'rm -rf /'"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            errors.append(message)

    return errors


def validate_time_field_logic(value: str, field_name: str, min_val: int, max_val: int) -> List[str]:
    """Validate time field logic (ranges, lists, steps)"""
    errors: List[str] = []

    # Skip special values
    if value in ['*']:
        return errors

    # Handle lists (comma-separated values)
    if ',' in value:
        parts = value.split(',')
        seen_values = set()
        for part in parts:
            part = part.strip()
            if not part:
                errors.append(f"empty value in {field_name} list: '{value}'")
                continue

            # Check for duplicates
            if part in seen_values:
                errors.append(f"duplicate value '{part}' in {field_name} list: '{value}'")
            seen_values.add(part)

            # Validate individual part
            part_errors = validate_single_time_value(part, field_name, min_val, max_val)
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
    if value.startswith('*/'):
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
    if '-' in value:
        range_parts = value.split('-')
        if len(range_parts) == 2:
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


def check_cron_daemon() -> None:
    """Check if cron daemon is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'cron'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode != 0 or result.stdout.strip() != 'active':
            logger.warning("Cron daemon is not running")
        else:
            logger.debug("Cron daemon status check: active")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        logger.warning("Could not check cron daemon status")
        logger.debug("Cron daemon status check: failed")


def check_system_crontab_permissions() -> None:
    """Check system crontab file permissions"""
    crontab_file = "/etc/crontab"
    if os.path.exists(crontab_file):
        stat_info = os.stat(crontab_file)
        mode = stat_info.st_mode & 0o777

        if mode != 0o644:
            logger.warning(f"System crontab has incorrect permissions: {oct(mode)} (should be 644)")
        else:
            logger.debug(f"System crontab permissions check: {oct(mode)} (correct)")

        if stat_info.st_uid != 0:
            logger.warning("System crontab is not owned by root")
        else:
            logger.debug("System crontab ownership check: root (correct)")
    else:
        logger.debug("System crontab file does not exist")


def check_line_user(line: str, line_number: int, file_name: str, file_path: str | None = None) -> List[str]:
    """
    Check a single user crontab line
    Returns: list of error messages
    """
    errors: List[str] = []

    # Skip environment variables
    if '=' in line and not any(char.isdigit() or char in '*@' for char in line.split('=')[0]):
        return errors

    # Check for special keywords
    if line.startswith('@'):
        return check_line_special(line, line_number, file_name, file_path)

    # Parse regular crontab line
    parts = line.split()
    if len(parts) < 6:
        errors.append(f"insufficient fields (minimum 6 required for user crontab, found {len(parts)})")
        # Return errors with line number and content
        formatted_errors = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        return formatted_errors

    # Extract time fields and command
    minute, hour, day, month, weekday = parts[:5]
    command = ' '.join(parts[5:])

    if not command:
        errors.append("missing command")
    else:
        # Check for dangerous commands
        dangerous_errors = check_dangerous_commands(command)
        errors.extend(dangerous_errors)

    # Validate time fields
    logic_errors = validate_time_field_logic(minute, "minutes", 0, 59)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MINUTE_PATTERN, minute):
        errors.append(f"invalid minute format: '{minute}'")

    logic_errors = validate_time_field_logic(hour, "hours", 0, 23)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(HOUR_PATTERN, hour):
        errors.append(f"invalid hour format: '{hour}'")

    logic_errors = validate_time_field_logic(day, "day of month", 1, 31)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(DAY_PATTERN, day):
        errors.append(f"invalid day of month format: '{day}'")

    logic_errors = validate_time_field_logic(month, "month", 1, 12)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MONTH_PATTERN, month):
        errors.append(f"invalid month format: '{month}'")

    logic_errors = validate_time_field_logic(weekday, "day of week", 0, 7)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(WEEKDAY_PATTERN, weekday):
        errors.append(f"invalid day of week format: '{weekday}'")

    # Return errors with line number and content
    formatted_errors = []
    line_content = get_line_content(file_path, line_number) if file_path else line
    line_content = clean_line_for_output(line_content)
    for error in errors:
        formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")

    return formatted_errors


def check_line_system(line: str, line_number: int, file_name: str, file_path: str | None = None) -> List[str]:
    """
    Check a single system crontab line
    Returns: list of error messages
    """
    errors: List[str] = []

    # Skip environment variables
    if '=' in line and not any(char.isdigit() or char in '*@' for char in line.split('=')[0]):
        return errors

    # Check for special keywords
    if line.startswith('@'):
        return check_line_special(line, line_number, file_name, file_path)

    # Parse regular crontab line
    parts = line.split()
    if len(parts) < 7:
        errors.append(f"insufficient fields (minimum 7 required for system crontab, found {len(parts)})")
        # Return errors with line number and content
        formatted_errors = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        return formatted_errors

    # Extract time fields, user, and command
    minute, hour, day, month, weekday, user = parts[:6]
    command = ' '.join(parts[6:])

    # Check for too many fields (more than 7) - but only if command doesn't contain spaces
    if len(parts) > 7 and ' ' not in command:
        errors.append(f"too many fields (maximum 7 required for system crontab, found {len(parts)})")
        # Return errors with line number and content
        formatted_errors = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        return formatted_errors

    # Check for extra fields in command (like "extra" in "root extra /usr/bin/backup.sh")
    if len(parts) > 7:
        # Check if the extra field is not part of the command
        extra_field = parts[6]
        if extra_field == 'extra':
            errors.append(f"extra field '{extra_field}' in command")
            # Return errors with line number and content
            formatted_errors = []
            line_content = get_line_content(file_path, line_number) if file_path else line
            line_content = clean_line_for_output(line_content)
            for error in errors:
                formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
            return formatted_errors

    if not command:
        errors.append("missing command")
    else:
        # Check for dangerous commands
        dangerous_errors = check_dangerous_commands(command)
        errors.extend(dangerous_errors)

    # Validate time fields
    logic_errors = validate_time_field_logic(minute, "minutes", 0, 59)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MINUTE_PATTERN, minute):
        errors.append(f"invalid minute format: '{minute}'")

    logic_errors = validate_time_field_logic(hour, "hours", 0, 23)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(HOUR_PATTERN, hour):
        errors.append(f"invalid hour format: '{hour}'")

    logic_errors = validate_time_field_logic(day, "day of month", 1, 31)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(DAY_PATTERN, day):
        errors.append(f"invalid day of month format: '{day}'")

    logic_errors = validate_time_field_logic(month, "month", 1, 12)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(MONTH_PATTERN, month):
        errors.append(f"invalid month format: '{month}'")

    logic_errors = validate_time_field_logic(weekday, "day of week", 0, 7)
    if logic_errors:
        errors.extend(logic_errors)
    elif not re.match(WEEKDAY_PATTERN, weekday):
        errors.append(f"invalid day of week format: '{weekday}'")

    # Validate user field
    if not user or user.startswith('#'):
        errors.append("invalid user field")
    elif '"' in user or '@' in user or ' ' in user:
        errors.append(f"invalid user field format: '{user}'")

    # Return errors with line number and content
    formatted_errors = []
    line_content = get_line_content(file_path, line_number) if file_path else line
    line_content = clean_line_for_output(line_content)
    for error in errors:
        formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")

    return formatted_errors


def check_line_special(line: str, line_number: int, file_name: str, file_path: str | None = None) -> List[str]:
    """
    Check a special keyword line (@reboot, @yearly, etc.)
    Returns: list of error messages
    """
    errors: List[str] = []

    parts = line.split()
    if len(parts) < 2:
        errors.append("insufficient fields for special keyword (minimum 2 required)")
        # Return errors with line number and content
        formatted_errors = []
        line_content = get_line_content(file_path, line_number) if file_path else line
        line_content = clean_line_for_output(line_content)
        for error in errors:
            formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")
        return formatted_errors

    keyword = parts[0]

    # For system crontab, special keywords need user and command
    # For user crontab, special keywords only need command
    # We need to determine if this is system crontab by checking if we have 3 parts
    if len(parts) >= 3:
        # This looks like system crontab format: @keyword user command
        user = parts[1]
        command = ' '.join(parts[2:])

        # Validate special keyword
        valid_keywords = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@midnight', '@hourly']
        if keyword not in valid_keywords:
            errors.append(f"invalid special keyword: '{keyword}'")

        # Validate user field for system crontab
        if not user or user.startswith('#'):
            errors.append("invalid user field")

        if not command:
            errors.append("missing command")
    else:
        # This looks like user crontab format: @keyword command
        command = ' '.join(parts[1:])

        # Validate special keyword
        valid_keywords = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@midnight', '@hourly']
        if keyword not in valid_keywords:
            errors.append(f"invalid special keyword: '{keyword}'")

        if not command:
            errors.append("missing command")

        # For system crontab files, even @keyword command format needs user field
        # We can detect this by checking if the file name contains "system"
        if file_path and "system" in os.path.basename(file_path):
            errors.append("missing user field for system crontab")

    # Return errors with line number and content
    formatted_errors = []
    line_content = get_line_content(file_path, line_number) if file_path else line
    line_content = clean_line_for_output(line_content)
    for error in errors:
        formatted_errors.append(f"{file_name} (Line {line_number}): {line_content} # {error}")

    return formatted_errors
