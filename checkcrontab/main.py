#!/usr/bin/env python3
"""
Main entry point for checkcrontab
"""

import argparse
import logging
import os
import platform
import re
import sys
import tempfile
import traceback
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    # Use as python3 -m checkcrontab
    from . import __description__ as DESCRIPTION
    from . import __version__ as VERSION
    from . import checker, logging_config
except ImportError:
    # Use as python3 checkcrontab/main.py
    try:
        from checkcrontab import __description__ as DESCRIPTION
        from checkcrontab import __version__ as VERSION
        from checkcrontab import (
            checker,  # type: ignore[import-not-found,no-redef]
            logging_config,  # type: ignore[import-not-found,no-redef]
        )
    except Exception as e:
        logging.warning(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        sys.exit(2)

logger = logging.getLogger(__name__)


def check_file(file_path: str, is_system_crontab: bool = False) -> Tuple[int, List[str]]:
    """
    Check crontab file line by line
    Returns: (checked_lines_count, errors_list)
    """
    errors = []
    checked_lines = 0

    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return 0, [f"Error reading file: {e}"]

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        line_number = i + 1

        # Handle multi-line commands
        if line.endswith("\\"):
            # Collect continuation lines
            full_line = line[:-1]  # Remove trailing backslash
            i += 1
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                continuation = lines[i].rstrip("\n")
                if continuation.endswith("\\"):
                    full_line += "\n" + continuation[:-1]
                    i += 1
                else:
                    full_line += "\n" + continuation
                    i += 1
                    break
            line = full_line
        else:
            i += 1

        # Skip continuation lines that were already processed
        if line.startswith((" ", "\t")) and not line.strip():
            continue

        # Skip empty lines and comments
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("#"):
            continue

        # This is a line to check
        checked_lines += 1

        # Check line using unified function with system crontab flag
        line_errors = checker.check_line(line, line_number, os.path.basename(file_path), file_path, is_system_crontab=is_system_crontab)

        # Output result immediately in order of processing
        line_content = checker.get_line_content(file_path, line_number) if file_path else line
        line_content = checker.clean_line_for_output(line_content)

        if line_errors:
            # Output all errors for this line
            for error in line_errors:
                logger.error(error)
            errors.extend(line_errors)
        elif logger.isEnabledFor(logging.DEBUG):
            # Output valid lines in debug mode
            logger.debug(f"{os.path.basename(file_path)} (Line {line_number}): {line_content} # valid")

    # Check if file ends with newline (RFC compliance)
    if lines and not lines[-1].endswith("\n"):
        error_msg = f"{os.path.basename(file_path)} (Line {len(lines) + 1}): File should end with newline"
        errors.append(error_msg)
        logger.error(error_msg)

    return checked_lines, errors


def find_user_crontab(username: str) -> Optional[str]:
    """Find user crontab file path or get content via crontab command"""
    # First try to find existing file
    possible_paths = [
        f"/var/spool/cron/crontabs/{username}",
        f"/var/spool/cron/{username}",
        f"/tmp/crontab.{username}",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If no file found, try to get via crontab command
    crontab_content = checker.get_crontab(username)
    if crontab_content:
        # Create temporary file with crontab content (context manager per SIM115)
        with tempfile.NamedTemporaryFile(mode="w", suffix=f".{username}", delete=False) as tmp:
            tmp.write(crontab_content)
            temp_path = tmp.name
        return temp_path
    return None


def main() -> int:
    """Main function"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
    %(prog)s                           # Check only system crontab (Linux) or no files
    %(prog)s /path/to/user/crontab     # Check system and file crontab
    %(prog)s username                  # Check system and user crontab
    %(prog)s file1 file2 username      # Check multiple files and user crontab
    %(prog)s -S system.cron -U user.cron  # Check with explicit type flags
    %(prog)s -u username1 -u username2  # Check specific usernames
        """,
    )

    parser.add_argument("arguments", nargs="*", help="Paths to crontab files or usernames")
    parser.add_argument("-S", "--system", action="append", help="System crontab files")
    parser.add_argument("-U", "--user", action="append", help="User crontab files")
    parser.add_argument("-u", "--username", action="append", help="Usernames to check")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION)
    parser.add_argument("-d", "--debug", action="store_true", help="Debug output")
    parser.add_argument("-n", "--no-colors", action="store_true", help="Disable colored output")

    args = parser.parse_args()

    # Setup logging
    logging_config.setup_logging(args.debug, args.no_colors)

    # Prepare list of files to check with their types
    file_list: List[Tuple[str, bool]] = []  # (file_path, is_system_crontab)
    temp_files: List[str] = []  # Track temporary files for cleanup

    # Add files with explicit flags
    if args.system:
        for file_path in args.system:
            file_list.append((file_path, True))

    if args.user:
        for file_path in args.user:
            file_list.append((file_path, False))

    # Add usernames with explicit flag
    if args.username:
        for username in args.username:
            crontab_path = find_user_crontab(username)
            if crontab_path:
                temp_files.append(crontab_path)
                file_list.append((crontab_path, False))  # User crontab
                logger.info(f"Found user crontab for {username}: {crontab_path}")
            else:
                logger.warning(f"User crontab not found for: {username}")

    # Add arguments with smart detection
    for arg in args.arguments:
        # First check if it's an existing file
        if os.path.exists(arg):
            # Determine type based on path or content
            is_system_crontab = arg == "/etc/crontab" or arg.startswith("/etc/cron.d") or "system" in os.path.basename(arg)
            file_list.append((arg, is_system_crontab))
        else:
            # If not a file, treat as username
            crontab_path = find_user_crontab(arg)
            if crontab_path:
                temp_files.append(crontab_path)
                file_list.append((crontab_path, False))  # User crontab
                logger.info(f"Found user crontab for {arg}: {crontab_path}")
            else:
                logger.warning(f"User crontab not found for: {arg}")

    # Add system crontab on Linux if not already included
    if platform.system().lower() == "linux":
        checker.check_daemon()
        checker.check_permissions()
        is_github = os.getenv("GITHUB_ACTIONS") == "true"
        if not is_github and not any(file_path == "/etc/crontab" for file_path, _ in file_list):
            file_list.insert(0, ("/etc/crontab", True))
    else:
        logger.info("Skipping checks on non-Linux system")

    # Remove duplicates while preserving order
    seen = set()
    unique_file_list: List[Tuple[str, bool]] = []
    for file_path, is_system in file_list:
        if file_path not in seen:
            seen.add(file_path)
            unique_file_list.append((file_path, is_system))
    file_list = unique_file_list

    total_checked_lines = 0
    total_errors = 0
    all_errors: List[str] = []

    for file_path, is_system_crontab in file_list:
        if os.path.exists(file_path):
            checked_lines, file_errors = check_file(file_path, is_system_crontab=is_system_crontab)
            total_checked_lines += checked_lines
            total_errors += len(file_errors)
            all_errors.extend(file_errors)
            unique_error_lines = set()
            for error in file_errors:
                if "File should end with newline" in error:
                    continue
                match = re.search(r"Line (\d+)", error)
                if match:
                    unique_error_lines.add(int(match.group(1)))
            lines_with_errors = len(unique_error_lines)
            if file_errors:
                logger.error(f"{file_path}: {lines_with_errors}/{checked_lines} lines with errors. Total {len(file_errors)} errors.")
            else:
                logger.info(f"{file_path}: 0/{checked_lines} lines without errors. No errors.")
        else:
            logger.warning(f"File {file_path} does not exist")

    if total_errors == 0:
        logger.info("All checks passed successfully!")
    else:
        unique_error_lines = set()
        for error in all_errors:
            if "File should end with newline" in error:
                continue
            match = re.search(r"Line (\d+)", error)
            if match:
                unique_error_lines.add(int(match.group(1)))
        lines_with_errors = len(unique_error_lines)
        logger.error(f"Total: {lines_with_errors} lines with errors found in {total_checked_lines} checked lines")

    # Clean up temporary files
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except Exception as e:
            logger.debug(f"Failed to remove temporary file {temp_file}: {e}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
