#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for checking syntax and correctness of crontab files
Usage: python3 -m checkcrontab [path_to_user_crontab]
"""
import copy
import sys
import os
import re
import subprocess
import argparse
import logging
import platform
import traceback
from typing import List, Optional
from collections import namedtuple

# Named tuples for representing crontab entries
system_cron_entry = namedtuple('system_cron_entry', [
    'minute', 'hour', 'day', 'month', 'weekday',
    'user', 'command', 'line_number', 'file_name'
])

user_cron_entry = namedtuple('user_cron_entry', [
    'minute', 'hour', 'day', 'month', 'weekday',
    'command', 'line_number', 'file_name'
])

# Regular expressions for time field validation
# Updated to support combinations of ranges and steps
MINUTE_PATTERN = r'^(\*|([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-5]?[0-9]))?(,([0-5]?[0-9])(-([0-5]?[0-9]))?(/([0-5]?[0-9]))?)*|\*/([0-5]?[0-9]))$'
HOUR_PATTERN = r'^(\*|([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?(,([0-9]|1[0-9]|2[0-3])(-([0-9]|1[0-9]|2[0-3]))?(/([0-9]|1[0-9]|2[0-3]))?)*|\*/([0-9]|1[0-9]|2[0-3]))$'
DAY_PATTERN = r'^(\*|([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?(,([1-9]|[12][0-9]|3[01])(-([1-9]|[12][0-9]|3[01]))?(/([1-9]|[12][0-9]|3[01]))?)*|\*/([1-9]|[12][0-9]|3[01]))$'
MONTH_PATTERN = r'^(\*|([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?(,([1-9]|1[0-2])(-([1-9]|1[0-2]))?(/([1-9]|1[0-2]))?)*|\*/([1-9]|1[0-2]))$'
WEEKDAY_PATTERN = r'^(\*|([0-7])(-([0-7]))?(/([0-7]))?(,([0-7])(-([0-7]))?(/([0-7]))?)*|\*/([0-7]))$'


class ColoredFormatter(logging.Formatter):
    """Enhanced colored formatter with Windows support"""

    def __init__(self, fmt: str = None, **kwargs) -> None:
        super().__init__(fmt, **kwargs)
        self._use_color = self._get_color_compatibility()
        self.COLORS = {
            "DEBUG": "\033[0;36m",     # CYAN
            "INFO": "\033[0;32m",      # GREEN
            "WARNING": "\033[0;33m",   # YELLOW
            "ERROR": "\033[0;31m",     # RED
            "CRITICAL": "\033[0;37;41m",  # WHITE ON RED
            "RESET": "\033[0m",        # RESET COLOR
        }

    @classmethod
    def _get_color_compatibility(cls) -> bool:
        """Check if system supports ANSI colors"""
        # Always use colors on Unix-like systems
        if platform.system().lower() != "windows":
            return True

        # Check Windows version for ANSI support
        try:
            win = sys.getwindowsversion()
            # Windows 10 version 1511+ supports ANSI colors
            if win.major >= 10 and win.build >= 10586:
                return True
        except Exception:
            pass

        return False

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors if supported"""
        if not self._use_color:
            return super().format(record)

        # Create a copy to avoid modifying the original record
        colored_record = copy.copy(record)
        levelname = colored_record.levelname

        # Apply color to levelname
        color_seq = self.COLORS.get(levelname, self.COLORS["RESET"])
        colored_record.levelname = f"{color_seq}{levelname}{self.COLORS['RESET']}"

        return super().format(colored_record)


# Logging configuration
logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stderr)],
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Apply colored formatter
colored_formatter = ColoredFormatter(
    fmt='%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(colored_formatter)

logger = logging.getLogger(__name__)
# logger.propagate = False


def check_cron_daemon() -> bool:
    """Check cron daemon activity"""
    # Skip on non-Linux systems
    if platform.system().lower() != "linux":
        logger.info("Skipping cron daemon check on non-Linux system")
        return True

    try:
        # Check cron daemon
        result = subprocess.run(['systemctl', 'is-active', '--quiet', 'cron'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Cron daemon is active")
            return True

        # Check crond daemon
        result = subprocess.run(['systemctl', 'is-active', '--quiet', 'crond'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Crond daemon is active")
            return True

        logger.warning("Cron daemon is not active")
        return False

    except FileNotFoundError:
        logger.warning("Failed to check cron daemon status")
        return False


def check_system_crontab_permissions() -> bool:
    """Check system crontab permissions"""
    crontab_file = "/etc/crontab"

    if not os.path.exists(crontab_file):
        logger.warning(f"File {crontab_file} does not exist")
        return True  # Don't treat as error, just warn

    if not os.access(crontab_file, os.R_OK):
        logger.warning(f"File {crontab_file} is not readable")
        return True  # Don't treat as error, just warn

    try:
        stat_info = os.stat(crontab_file)
        permissions = oct(stat_info.st_mode)[-3:]

        if permissions != "644":
            logger.warning("System crontab: permissions {} (recommended 644)".format(permissions))
        else:
            logger.info("System crontab: permissions are correct")

        return True

    except Exception as e:
        logger.warning(f"Error checking permissions: {e}")
        return True  # Don't treat as error, just warn


def parse_cron_line(line: str, line_number: int, file_name: str, errors: List[str], is_system_crontab: bool = False):
    """Parse crontab line"""
    # Remove comments
    line = re.sub(r'#.*$', '', line).strip()

    if not line:
        return None

    # Skip environment variables
    if '=' in line and not line.startswith('#'):
        return None

    # Split line into fields
    parts = line.split()

    # Check for special keywords (@reboot, @yearly, @monthly, @weekly, @daily, @hourly)
    if parts and parts[0].startswith('@'):
        special_keyword = parts[0]
        valid_keywords = ['@reboot', '@yearly', '@monthly', '@weekly', '@daily', '@hourly']

        if special_keyword not in valid_keywords:
            errors.append(f"Line {line_number} in {file_name} - "
                          f"invalid special keyword: '{special_keyword}'")
            return None

        # For special keywords, the format depends on whether it's system or user crontab
        if is_system_crontab:
            # System crontab: @keyword user command
            if len(parts) < 3:
                errors.append(f"Line {line_number} in {file_name} - insufficient fields "
                              f"for special keyword (minimum 3 required: @keyword user command, found {len(parts)})")
                return None

            user = parts[1]
            command = ' '.join(parts[2:])

            if not command:
                errors.append(f"Line {line_number} in {file_name} - missing command")
                return None

            # Create a special entry with the keyword as the "minute" field for compatibility
            return system_cron_entry(
                minute=special_keyword,  # Store the special keyword here
                hour='*',               # Placeholder values for time fields
                day='*',
                month='*',
                weekday='*',
                user=user,
                command=command,
                line_number=line_number,
                file_name=file_name
            )
        else:
            # User crontab: @keyword command
            if len(parts) < 2:
                errors.append(f"Line {line_number} in {file_name} - insufficient fields "
                              f"for special keyword (minimum 2 required: @keyword command, found {len(parts)})")
                return None

            command = ' '.join(parts[1:])

            if not command:
                errors.append(f"Line {line_number} in {file_name} - missing command")
                return None

            # Create a special entry with the keyword as the "minute" field for compatibility
            return user_cron_entry(
                minute=special_keyword,  # Store the special keyword here
                hour='*',               # Placeholder values for time fields
                day='*',
                month='*',
                weekday='*',
                command=command,
                line_number=line_number,
                file_name=file_name
            )

    # Standard time-based crontab entries
    if is_system_crontab:
        # System crontab: 7 fields (including user)
        if len(parts) < 7:
            errors.append(f"Line {line_number} in {file_name} - insufficient fields "
                          f"(minimum 7 required for system crontab, found {len(parts)})")
            return None

        # Extract time fields, user and command
        minute, hour, day, month, weekday, user = parts[:6]
        command = ' '.join(parts[6:])

        if not command:
            errors.append(f"Line {line_number} in {file_name} - missing command")
            return None

        return system_cron_entry(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            weekday=weekday,
            user=user,
            command=command,
            line_number=line_number,
            file_name=file_name
        )
    else:
        # User crontab: 6 fields
        if len(parts) < 6:
            errors.append(f"Line {line_number} in {file_name} - insufficient fields "
                          f"(minimum 6 required for user crontab, found {len(parts)})")
            return None

        # Extract time fields and command
        minute, hour, day, month, weekday = parts[:5]
        command = ' '.join(parts[5:])

        if not command:
            errors.append(f"Line {line_number} in {file_name} - missing command")
            return None

        return user_cron_entry(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            weekday=weekday,
            command=command,
            line_number=line_number,
            file_name=file_name
        )


def validate_time_field(value: str, field_name: str, pattern: str,
                        line_number: int, file_name: str, errors: List[str]) -> bool:
    """Validate time field"""
    if not re.match(pattern, value):
        errors.append(f"Line {line_number} in {file_name} - "
                      f"invalid {field_name} format: '{value}'")
        return False
    return True


def validate_cron_entry(entry, errors: List[str]) -> bool:
    """Validate crontab entry"""
    is_valid = True

    # Check if this is a special keyword entry
    if entry.minute.startswith('@'):
        # For special keywords, skip time field validation
        # Only validate user field for system crontab
        if hasattr(entry, 'user'):
            if not entry.user or entry.user.strip() == '':
                errors.append(f"Line {entry.line_number} in {entry.file_name} - "
                              f"missing user")
                is_valid = False
        return is_valid

    # Validate each time field for standard crontab entries
    if not validate_time_field(entry.minute, "minutes", MINUTE_PATTERN,
                               entry.line_number, entry.file_name, errors):
        is_valid = False

    if not validate_time_field(entry.hour, "hours", HOUR_PATTERN,
                               entry.line_number, entry.file_name, errors):
        is_valid = False

    if not validate_time_field(entry.day, "day of month", DAY_PATTERN,
                               entry.line_number, entry.file_name, errors):
        is_valid = False

    if not validate_time_field(entry.month, "month", MONTH_PATTERN,
                               entry.line_number, entry.file_name, errors):
        is_valid = False

    if not validate_time_field(entry.weekday, "day of week", WEEKDAY_PATTERN,
                               entry.line_number, entry.file_name, errors):
        is_valid = False

    # Check user for system crontab
    if hasattr(entry, 'user'):
        if not entry.user or entry.user.strip() == '':
            errors.append(f"Line {entry.line_number} in {entry.file_name} - "
                          f"missing user")
            is_valid = False

    return is_valid


def check_crontab_file(file_path: str, errors: List[str], is_system_crontab: bool = False) -> int:
    """Check crontab file"""
    file_name = os.path.basename(file_path)
    total_errors = 0
    total_entries = 0

    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} does not exist")
        return 0  # Don't treat as error, just warn

    if not os.access(file_path, os.R_OK):
        logger.warning(f"File {file_path} is not readable")
        return 0  # Don't treat as error, just warn

    # Check if file ends with newline
    try:
        with open(file_path, 'rb') as f:
            f.seek(-1, 2)
            last_byte = f.read(1)
            if last_byte != b'\n':
                logger.error(f"{file_path}: does not end with newline")
                total_errors += 1
    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        pass

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split content into lines, but handle multi-line commands properly
        lines = content.split('\n')
        line_number = 0
        i = 0

        while i < len(lines):
            line = lines[i]
            line_number = i + 1

            # Skip empty lines and comments
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith('#'):
                i += 1
                continue

            # Check if this line is a continuation of a previous command
            # (starts with whitespace and doesn't look like a cron entry)
            if line.startswith(' ') or line.startswith('\t'):
                # This is a continuation line, skip it
                i += 1
                continue

            # Check if this looks like a cron entry (starts with time fields)
            parts = stripped_line.split()
            if len(parts) >= 5 and all(part.replace('*', '').replace(',', '').replace('-', '').replace('/', '').isdigit()
                                       or part in ['*', '@reboot', '@yearly', '@monthly', '@weekly', '@daily', '@hourly'] for part in parts[:5]):
                # This looks like a cron entry, process it
                entry = parse_cron_line(line, line_number, file_name, errors, is_system_crontab)
                if entry:
                    total_entries += 1
                    if not validate_cron_entry(entry, errors):
                        total_errors += 1
            else:
                # This doesn't look like a cron entry, skip it
                pass

            i += 1

    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return 1

    # Output results
    if total_errors == 0:
        logger.info(f"{file_path}: {total_entries}/{total_entries} lines are correct")
    else:
        logger.error(f"{file_path}: {total_entries - total_errors}/{total_entries} lines are correct")

    return total_errors


def get_line_content(file_name: str, line_number: int) -> Optional[str]:
    """Get line content from file"""
    try:
        # Try to find file in current directory
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 1 <= line_number <= len(lines):
                    return lines[line_number - 1].strip()

        # Try system crontab
        if file_name == "crontab" and os.path.exists("/etc/crontab"):
            with open("/etc/crontab", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 1 <= line_number <= len(lines):
                    return lines[line_number - 1].strip()

        return None

    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return None


def print_errors(errors: List[str]) -> None:
    """Print errors with line quoting"""
    logger.error("Found errors:")

    for error in errors:
        # Parse error message
        parts = error.split(" - ", 1)
        if len(parts) >= 2:
            location = parts[0]  # "Line X in file.txt"
            description = " - ".join(parts[1:])  # error description

            # Extract line number and file name
            match = re.search(r'Line (\d+) in (.+)', location)
            if match:
                line_num = int(match.group(1))
                file_name = match.group(2)
                line_content = get_line_content(file_name, line_num)

                if line_content:
                    # Replace tabs with spaces and remove duplication in description
                    clean_line = line_content.replace('\t', ' ')
                    # Remove comment from line as error description already contains needed information
                    clean_line = re.sub(r'\s+#.*$', '', clean_line)
                    logger.error(f"{file_name} (Line {line_num}): {clean_line} - {description}")
                else:
                    logger.error(f"{file_name} (Line {line_num}): {description}")
        else:
            logger.error(f"  {error}")


def get_user_crontab_path(username: str) -> Optional[str]:
    """Get user crontab path"""
    try:
        # Check if user exists
        result = subprocess.run(['id', username], capture_output=True, text=True)
        if result.returncode != 0:
            return None

        # Get user crontab path
        crontab_path = f"/var/spool/cron/crontabs/{username}"
        if os.path.exists(crontab_path):
            return crontab_path

        # Alternative path for some systems
        crontab_path = f"/var/spool/cron/{username}"
        if os.path.exists(crontab_path):
            return crontab_path

        return None

    except Exception as e:
        logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        return None


def check_user_crontab(username: str, errors: List[str]) -> int:
    """Check user crontab by username"""
    try:
        # Check if user exists
        result = subprocess.run(['id', username], capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"User '{username}' not found")
            return 0  # Don't treat as error, just warn

        # Try to get crontab content using 'crontab -l' command
        # This works even if the user doesn't have direct file access
        if username == os.getenv('USER') or username == os.getenv('LOGNAME'):
            # Current user - use 'crontab -l'
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode != 0:
                if "no crontab" in result.stderr.lower():
                    logger.warning(f"User '{username}' has no crontab")
                    return 0  # Don't treat as error, just warn
                else:
                    logger.warning(f"Failed to read crontab for user '{username}': {result.stderr.strip()}")
                    return 0  # Don't treat as error, just warn
            crontab_content = result.stdout
        else:
            # Other user - try to use 'sudo crontab -u username -l'
            result = subprocess.run(['sudo', 'crontab', '-u', username, '-l'],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                if "no crontab" in result.stderr.lower():
                    logger.warning(f"User '{username}' has no crontab")
                    return 0  # Don't treat as error, just warn
                else:
                    logger.warning(f"Failed to read crontab for user '{username}': {result.stderr.strip()}")
                    return 0  # Don't treat as error, just warn
            crontab_content = result.stdout

        # Create a temporary file with the crontab content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.crontab', delete=False) as temp_file:
            temp_file.write(crontab_content)
            temp_file_path = temp_file.name

        try:
            # Check the temporary file
            total_errors = check_crontab_file(temp_file_path, errors, is_system_crontab=False)
            return total_errors
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
                pass

    except Exception as e:
        logger.error(f"Error checking crontab for user '{username}': {e}")
        return 1


def validate_crontab_files(system_crontab: str, user_input: Optional[str]) -> int:
    """Validate crontab files"""
    errors = []
    total_errors = 0

    # Check system crontab
    system_errors = check_crontab_file(system_crontab, errors, is_system_crontab=True)
    total_errors += system_errors

    # Check user crontab if specified
    if user_input:
        # Check if it looks like a file path (contains '/' or '.' or has extension)
        looks_like_file = '/' in user_input or '.' in user_input or user_input.endswith(('.txt', '.cron', '.crontab'))

        if looks_like_file:
            # Treat as file path
            if os.path.exists(user_input):
                # This is an existing file path
                if os.path.abspath(user_input) == os.path.abspath(system_crontab):
                    logger.warning(f"{user_input}: already checked as system crontab")
                else:
                    user_errors = check_crontab_file(user_input, errors, is_system_crontab=False)
                    total_errors += user_errors
            else:
                # File doesn't exist, warn but don't treat as error
                logger.warning(f"File {user_input} does not exist")
        else:
            # Treat as username
            user_errors = check_user_crontab(user_input, errors)
            total_errors += user_errors

    # Print all errors
    if errors:
        print_errors(errors)

    return total_errors


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Check syntax and correctness of crontab files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
    %(prog)s                           # Check only system crontab
    %(prog)s /path/to/user/crontab     # Check system and file crontab
    %(prog)s username                  # Check system and user crontab
        """,
    )

    parser.add_argument('user_input', nargs='?', help='Path to crontab file or username')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Check cron daemon (only on Linux systems)
    if platform.system().lower() == "linux":
        check_cron_daemon()
    else:
        logger.info("Skipping cron daemon check on non-Linux system")

    # Check system crontab permissions
    check_system_crontab_permissions()

    # Validate crontab files
    total_errors = validate_crontab_files("/etc/crontab", args.user_input)

    # Final result
    if total_errors == 0:
        logger.info("All checks passed successfully!")
        return 0
    else:
        logger.error(f"Found errors: {total_errors}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
