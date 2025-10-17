#!/usr/bin/env python3
"""
Main entry point for checkcrontab
"""

import argparse
import glob
import json
import logging
import os
import platform
import re
import sys
import tempfile
import traceback
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    # Use as python3 -m checkcrontab  # type: ignore
    from . import __description__ as DESCRIPTION  # type: ignore
    from . import __url__ as REPO_URL  # type: ignore
    from . import __version__ as VERSION  # type: ignore
    from . import checker  # type: ignore
    from . import logger as log
except ImportError:
    # Use as python3 checkcrontab/main.py
    try:
        from checkcrontab import __description__ as DESCRIPTION
        from checkcrontab import __url__ as REPO_URL
        from checkcrontab import __version__ as VERSION
        from checkcrontab import (
            checker,  # type: ignore[import-not-found,no-redef]
        )
        from checkcrontab import (
            logger as log,  # type: ignore[import-not-found,no-redef]
        )
    except Exception as e:
        logging.warning(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
        sys.exit(2)

logger = logging.getLogger(__name__)

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"


def check_file(file_path: str, is_system_crontab: bool = False) -> Tuple[int, List[str]]:
    """
    Check crontab file line by line
    Returns: (rows_checked_count, errors_list)
    """
    errors = []
    rows_checked = 0

    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception as e:
        logging.warning(f"{type(e).__name__} {str(e)}\n{traceback.format_exc()}")
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
        rows_checked += 1

        # Check line using unified function with system crontab flag
        line_errors, line_warnings = checker.check_line(line, line_number, os.path.basename(file_path), file_path, is_system_crontab=is_system_crontab)

        # Output result immediately in order of processing
        line_content = checker.get_line_content(file_path, line_number) if file_path else line
        line_content = checker.clean_line_for_output(line_content)

        if line_errors:
            # Output all errors for this line
            for error in line_errors:
                logger.error(error)
            errors.extend(line_errors)

        if line_warnings:
            # Output all warnings for this line
            for warning in line_warnings:
                logger.warning(warning)
        if logger.isEnabledFor(logging.DEBUG) and not line_errors and not line_warnings:
            # Output valid lines in debug mode
            logger.debug(f"{os.path.basename(file_path)} (Line {line_number}): {line_content} # valid")

    # Check if file ends with newline (RFC compliance)
    if lines and not lines[-1].endswith("\n"):
        error_msg = f"{os.path.basename(file_path)} (Line {len(lines) + 1}): File should end with newline"
        errors.append(error_msg)
        logger.error(error_msg)

    return rows_checked, errors


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


def gen_sarif_output(files_data: List[Dict[str, Any]], total_errors: int, total_warnings: int = 0) -> Dict[str, Any]:
    """Generate SARIF format output"""
    results = []

    for file_data in files_data:
        file_path = file_data["file"]
        errors = file_data.get("errors", [])

        for error in errors:
            # Parse error message to extract line number and message
            line_match = re.search(r"Line (\d+):", error)
            line_number = int(line_match.group(1)) if line_match else 1

            # Extract the actual error message
            message_match = re.search(r"# (.+)$", error)
            message = message_match.group(1) if message_match else error

            result = {
                "ruleId": "crontab-syntax-error",
                "level": "error",
                "message": {"text": message},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": file_path}, "region": {"startLine": line_number, "startColumn": 1}}}],
            }
            results.append(result)

    sarif_output = {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "checkcrontab",
                        "version": VERSION,
                        "informationUri": REPO_URL,
                    }
                },
                "results": results,
            }
        ],
    }

    return sarif_output


def get_files(path: str) -> Tuple[List[str], List[str]]:
    """Get list of files from path (file or directory)"""
    files = []
    errors = []
    if not os.path.exists(path):
        # Path does not exist; no files to add.
        pass
    elif os.path.isfile(path):
        files.append(path)
    elif os.path.isdir(path):
        for file in glob.glob(os.path.join(path, "*")):
            if os.path.isfile(file):
                base = os.path.basename(file)
                errors = checker.check_filename(base)
                if not errors:
                    files.append(file)
                for error in errors:
                    errors.append(error)
    return files, errors


def main() -> int:
    """Main function"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
    %(prog)s                                  # Check system crontab
    %(prog)s filename                         # Check system and file crontab
    %(prog)s username                         # Check system and user crontab
    %(prog)s file1 file2 username             # Check multiple files and user crontab
    %(prog)s -S file1 -U file2 -u username    # Check crontab with type flags
    %(prog)s -u username1 -u username2        # Check specific usernames
    %(prog)s filename -j | jq '.total_errors' # Check crontab and return JSON
        """,
    )

    parser.add_argument("arguments", nargs="*", help="Paths to crontab files or usernames")
    parser.add_argument("-S", "--system", action="append", metavar="FILENAME", help="System crontab files")
    parser.add_argument("-U", "--user", action="append", metavar="FILENAME", help="User crontab files")
    parser.add_argument("-u", "--username", action="append", metavar="USERNAME", help="Usernames to check")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + VERSION)
    parser.add_argument("-d", "--debug", action="store_true", help="Debug output")
    parser.add_argument("-n", "--no-colors", action="store_true", help="Disable colored output")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text", help="Output format (default: text)")
    parser.add_argument("-j", dest="format", action="store_const", const="json", help="Shortcut for JSON output (same as --format json)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--exit-zero", action="store_true", help="Always exit with code 0")

    args = parser.parse_args()

    # Setup logging
    log.setup_logging(args.debug, args.no_colors, args.format in ["json", "sarif"])

    # Prepare list of files to check with their types
    files_list: List[Tuple[str, bool]] = []  # (file_path, is_system_crontab)
    files_temp: List[str] = []  # Track temporary files for cleanup

    # Add files with explicit flags
    if args.system:
        for path in args.system:
            if os.path.isdir(path):
                files, warnings = get_files(path)
                for warning in warnings:
                    logger.warning(warning)
                for file in files:
                    files_list.append((file, True))
            else:
                files_list.append((path, True))

    if args.user:
        for path in args.user:
            files_list.append((path, False))

    # Add usernames with explicit flag
    if args.username:
        for username in args.username:
            crontab_path = find_user_crontab(username)
            if crontab_path:
                files_temp.append(crontab_path)
                files_list.append((crontab_path, False))  # User crontab
                logger.info(f"Found user crontab for {username}: {crontab_path}")
            else:
                logger.warning(f"User crontab not found for: {username}")

    # Add arguments with smart detection
    for path in args.arguments:
        if os.path.isfile(path):
            # First check if it's an existing file
            full_path = os.path.abspath(path)
            is_system_crontab = bool(full_path == "/etc/crontab" or full_path.startswith("/etc/cron.d") or "system" in os.path.basename(full_path))
            files_list.append((full_path, is_system_crontab))
        elif os.path.isdir(path):
            # If directory, add all files inside as system crontabs
            files, warnings = get_files(path)
            for warning in warnings:
                logger.warning(warning)
            for file in files:
                full_path = os.path.abspath(file)
                is_system_crontab = bool(full_path == "/etc/crontab" or full_path.startswith("/etc/cron.d") or "system" in os.path.basename(full_path))
                files_list.append((full_path, is_system_crontab))
        elif re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,31}$").match(path):
            # If not a file, treat as username
            crontab_path = find_user_crontab(path)
            if crontab_path:
                files_temp.append(crontab_path)
                files_list.append((crontab_path, False))  # User crontab
                logger.info(f"{path} user found: {crontab_path}")
            else:
                logger.warning(f"{path} user not found or has no crontab")
        else:
            logger.warning(f"{path} File not found and is not a valid username")

    # Add system crontab on Linux if not already included
    if platform.system().lower() == "linux":
        is_github = os.getenv("GITHUB_ACTIONS") == "true"
        # Only check daemon and permissions on Linux and not in GitHub Actions
        if not is_github:
            for w in checker.check_daemon():
                logger.warning(w)
        # if not any(file_path == "/etc/crontab" for file_path, _ in files_list):
        #    files_list.insert(0, ("/etc/crontab", True))
    else:
        logger.info("Skipping system checks on non-Linux system")

    if len(files_list) == 0:
        logger.warning("No files to check.")

    # Remove duplicates while preserving order
    seen = set()
    unique_file_list: List[Tuple[str, bool]] = []
    for path, is_system in files_list:
        if path not in seen:
            seen.add(path)
            unique_file_list.append((path, is_system))
    files_list = unique_file_list

    total_rows = 0
    total_rows_errors = 0
    total_errors = 0
    total_warnings = 0
    all_errors: List[str] = []
    # all_warnings: List[str] = []

    # Prepare output structure if needed
    output_data: Dict[str, Any] = {"success": True, "total_files": len(files_list), "total_rows": 0, "total_rows_errors": 0, "total_errors": 0, "total_warnings": 0, "files": []}

    for path, is_system_crontab in files_list:
        if os.path.exists(path):
            if path not in files_temp:
                base = os.path.basename(path)
                name_errors = checker.check_filename(base)
                if name_errors:
                    msg = f"{path}: invalid cron filename: {'; '.join(name_errors)}"
                    file_info = {
                        "file": path,
                        "is_system_crontab": is_system_crontab,
                        "rows": 0,
                        "rows_warnings": 0,
                        "warnings_count": 0,
                        "rows_errors": 1,
                        "errors_count": 1,
                        "errors": [f"{os.path.basename(path)} (Line 0): {msg}"],
                        "success": False,
                    }
                    output_data["files"].append(file_info)
                    all_errors.append(f"{os.path.basename(path)} (Line 0): {msg}")
                    total_errors += 1
                    if args.format == "text":
                        logger.error(msg)
                    continue
            file_level_errors: List[str] = []
            if platform.system().lower() == "linux" and is_system_crontab:
                errors = checker.check_owner_and_permissions(path)
                for err in errors:
                    err_msg = f"{os.path.basename(path)} (Line 0): {err}"
                    logger.error(err_msg)
                    file_level_errors.append(err_msg)

            rows_checked, file_errors = check_file(path, is_system_crontab=is_system_crontab)

            if file_level_errors:
                file_errors = file_errors + file_level_errors

            total_rows += rows_checked
            total_errors += len(file_errors)
            all_errors.extend(file_errors)
            # Note: warnings are logged directly in check_file, so we don't need to track them here
            unique_error_lines = set()
            for error in file_errors:
                if "File should end with newline" in error:
                    continue
                match = re.search(r"Line (\d+)", error)
                if match:
                    unique_error_lines.add(int(match.group(1)))
            rows_errors = len(unique_error_lines)
            total_rows_errors += rows_errors
            # Add file info to output structure
            file_info = {
                "file": path,
                "is_system_crontab": is_system_crontab,
                "rows": rows_checked,
                "rows_warnings": 0,
                "warnings_count": 0,
                "rows_errors": rows_errors,
                "errors_count": len(file_errors),
                "errors": file_errors,
                "success": len(file_errors) == 0,
            }
            output_data["files"].append(file_info)
            # Standard output
            if args.format == "text" and len(file_errors) > 0:
                logger.error(f"{path}: {rows_errors}/{rows_checked} lines with errors. Total {len(file_errors)} errors.")
            elif args.format == "text":
                logger.info(f"{path}: 0/{rows_checked} lines without errors. No errors.")
        else:
            file_info = {
                "file": path,
                "is_system_crontab": is_system_crontab,
                "rows": 0,
                "rows_warnings": 0,
                "warnings_count": 0,
                "rows_errors": 0,
                "errors_count": 1,
                "errors": [f"File {path} does not exist"],
                "success": False,
            }
            output_data["files"].append(file_info)
            if args.format == "text":
                logger.warning(f"File {path} does not exist")

    # Update output structure and generate final output
    output_data["total_rows"] = total_rows
    output_data["total_rows_errors"] = total_rows_errors
    output_data["total_errors"] = total_errors
    output_data["total_warnings"] = total_warnings
    output_data["success"] = total_errors == 0

    # Calculate unique error lines
    unique_error_lines = set()
    for error in all_errors:
        if "File should end with newline" in error:
            continue
        match = re.search(r"Line (\d+)", error)
        if match:
            unique_error_lines.add(int(match.group(1)))
    output_data["rows_errors"] = len(unique_error_lines)

    # Generate output based on format
    if args.format == "json":
        print(json.dumps(output_data, indent=2))
    elif args.format == "sarif":
        sarif_output = gen_sarif_output(output_data["files"], total_errors)
        print(json.dumps(sarif_output, indent=2))
    # Standard output
    elif total_errors == 0:
        logger.info("All checks passed successfully!")
    else:
        unique_error_lines = set()
        for error in all_errors:
            if "File should end with newline" in error:
                continue
            match = re.search(r"Line (\d+)", error)
            if match:
                unique_error_lines.add(int(match.group(1)))
        rows_errors = len(unique_error_lines)
        logger.error(f"Total: {rows_errors} lines with errors found in {total_rows} checked lines")

    # Clean up temporary files
    for temp_file in files_temp:
        try:
            os.unlink(temp_file)
        except Exception as e:
            logger.debug(f"Failed to remove temporary file {temp_file}: {e}")

    # Determine exit code based on flags and results
    if args.exit_zero:
        return 0

    # Count warnings if in strict mode
    total_issues = total_errors
    if args.strict:
        total_issues += total_warnings

    if total_issues == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
