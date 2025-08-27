#!/usr/bin/env python3
"""
Main entry point for checkcrontab
"""

import argparse
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
    from . import checker, logging_config  # type: ignore
except ImportError:
    # Use as python3 checkcrontab/main.py
    try:
        from checkcrontab import __description__ as DESCRIPTION
        from checkcrontab import __url__ as REPO_URL
        from checkcrontab import __version__ as VERSION
        from checkcrontab import (
            checker,  # type: ignore[import-not-found,no-redef]
            logging_config,  # type: ignore[import-not-found,no-redef]
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


def generate_sarif_output(files_data: List[Dict[str, Any]], total_errors: int, total_warnings: int = 0) -> Dict[str, Any]:
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


def main() -> int:
    """Main function"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
    %(prog)s                           # Check only system crontab (Linux) or no files
    %(prog)s /etc/crontab              # Check system and file crontab
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
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text", help="Output format (default: text)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--exit-zero", action="store_true", help="Always exit with code 0")

    args = parser.parse_args()

    # Setup logging
    logging_config.setup_logging(args.debug, args.no_colors, args.format == "text")

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
        elif re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,31}$").match(arg):
            # If not a file, treat as username
            crontab_path = find_user_crontab(arg)
            if crontab_path:
                temp_files.append(crontab_path)
                file_list.append((crontab_path, False))  # User crontab
                logger.info(f"{arg} user found: {crontab_path}")
            else:
                logger.warning(f"{arg} user not found or has no crontab")
        else:
            logger.warning(f"{arg} File not found and is not a valid username")

    # Add system crontab on Linux if not already included
    if platform.system().lower() == "linux":
        is_github = os.getenv("GITHUB_ACTIONS") == "true"
        # Only check daemon and permissions on Linux and not in GitHub Actions
        if not is_github:
            checker.check_daemon()
            checker.check_permissions()
        # Add system crontab if not in GitHub Actions and not already included
        if not is_github and not any(file_path == "/etc/crontab" for file_path, _ in file_list):
            file_list.insert(0, ("/etc/crontab", True))
    else:
        logger.info("Skipping system checks on non-Linux system")

    # Remove duplicates while preserving order
    seen = set()
    unique_file_list: List[Tuple[str, bool]] = []
    for file_path, is_system in file_list:
        if file_path not in seen:
            seen.add(file_path)
            unique_file_list.append((file_path, is_system))
    file_list = unique_file_list

    total_rows = 0
    total_rows_errors = 0
    total_errors = 0
    # total_warnings = 0
    all_errors: List[str] = []
    # all_warnings: List[str] = []

    # Prepare output structure if needed
    output_data = None
    if args.format in ["json", "sarif"]:
        output_data = {"success": True, "total_files": len(file_list), "total_rows": 0, "total_rows_errors": 0, "total_errors": 0, "files": []}

    for file_path, is_system_crontab in file_list:
        if os.path.exists(file_path):
            rows_checked, file_errors = check_file(file_path, is_system_crontab=is_system_crontab)
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
            if output_data:
                # Add file info to output structure
                file_info = {
                    "file": file_path,
                    "is_system_crontab": is_system_crontab,
                    "rows": rows_checked,
                    "rows_errors": rows_errors,
                    "errors_count": len(file_errors),
                    "errors": file_errors,
                    "success": len(file_errors) == 0,
                }
                output_data["files"].append(file_info)  # type: ignore
            # Standard output
            elif file_errors:
                logger.error(f"{file_path}: {rows_errors}/{rows_checked} lines with errors. Total {len(file_errors)} errors.")
            else:
                logger.info(f"{file_path}: 0/{rows_checked} lines without errors. No errors.")
        elif output_data:
            file_info = {
                "file": file_path,
                "is_system_crontab": is_system_crontab,
                "rows": 0,
                "rows_errors": 0,
                "errors_count": 1,
                "errors": [f"File {file_path} does not exist"],
                "success": False,
            }
            output_data["files"].append(file_info)  # type: ignore
        else:
            logger.warning(f"File {file_path} does not exist")

    # Update output structure and generate final output
    if output_data:
        output_data["total_rows"] = total_rows  # type: ignore
        output_data["total_rows_errors"] = total_rows_errors  # type: ignore
        output_data["total_errors"] = total_errors  # type: ignore
        output_data["success"] = total_errors == 0  # type: ignore

        # Calculate unique error lines
        unique_error_lines = set()
        for error in all_errors:
            if "File should end with newline" in error:
                continue
            match = re.search(r"Line (\d+)", error)
            if match:
                unique_error_lines.add(int(match.group(1)))
        output_data["rows_errors"] = len(unique_error_lines)  # type: ignore

        # Generate output based on format
        if args.format == "json":
            print(json.dumps(output_data, indent=2))
        elif args.format == "sarif":
            sarif_output = generate_sarif_output(output_data["files"], total_errors)  # type: ignore
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
    for temp_file in temp_files:
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
        # In strict mode, warnings are treated as errors
        # We need to count warnings from the checker
        # For now, we'll just use errors, but this could be enhanced
        # TODO: Implement proper warning counting
        pass

    if total_issues == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
