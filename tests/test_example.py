#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest -q tests/test_example.py::test_valid_minute
"""
from __future__ import annotations

import importlib
import io
import logging
import os
import sys
import pytest
import re
# import subprocess
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from typing import List, Tuple, Dict, Any, cast
from unittest.mock import patch

# MODULE_CHECKER = importlib.import_module("checkcrontab.checker")
MODULE_MAIN = importlib.import_module("checkcrontab.main")

def run_main(args: list[str]) -> tuple[int, str, str]:
    out_buf, err_buf = io.StringIO(), io.StringIO()
    with patch("sys.argv", ["checkcrontab", *args]), redirect_stdout(out_buf), redirect_stderr(err_buf):
        try:
            code = MODULE_MAIN.main()
        except SystemExit as e:
            code = int(e.code) if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, out_buf.getvalue(), err_buf.getvalue()

def run_line(line: str, filename: str = 'crontab') -> tuple[int, str, str]:
    base = "/dev/shm/"
    os.makedirs(base, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as tmpdir:
        fpath = os.path.join(tmpdir, filename)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(line if line.endswith("\n") else line + "\n")
        code, stdout, stderr = run_main([fpath])
        return code, stdout, stderr

VALID_MINUTE_CASES = [
    {"id": "min_0",             "line": "0 * * * * /bin/true\n",              "rx": r"(?s).*"},
    {"id": "min_59",            "line": "59 * * * * /bin/true\n",             "rx": r"(?s).*"},
    {"id": "min_step_15",       "line": "*/15 * * * * /bin/true\n",           "rx": r"(?s).*"},
    {"id": "min_range_full",    "line": "0-59 * * * * /bin/true\n",           "rx": r"(?s).*"},
    {"id": "min_list_quarters", "line": "0,15,30,45 * * * * /bin/true\n",     "rx": r"(?s).*"},
    {"id": "min_range_step",    "line": "1-10/3 * * * * /bin/true\n",         "rx": r"(?s).*"},
]
@pytest.mark.skipif("linux" not in sys.platform, reason="Linux-only")  # type: ignore[misc]
@pytest.mark.parametrize("case", VALID_MINUTE_CASES, ids=[c["id"] for c in VALID_MINUTE_CASES])  # type: ignore[misc]
def test_valid_minute(case: Dict[str, str], caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)
    code, stdout, stderr = run_line(case["line"])
    combined = (stdout or "") + (stderr or "") + caplog.text
    assert code == 0, f"{case['id']}: expected exit 0, got {code}\nSTDOUT:{stdout}\nSTDERR:{stderr}\nLOGS:{caplog.text}"
    assert re.search(case["rx"], combined) is not None, (
        f"{case['id']}: pattern {case['rx']!r} not found in combined output.\n"
        f"STDOUT:{stdout}\nSTDERR:{stderr}\nLOGS:{caplog.text}"
    )

INVALID_MINUTE_CASES = [
    {"id": "min_60",               "line": "60 * * * * /bin/true\n",          "rx": r"(?is).*minute.*"},
    {"id": "min_step_60",          "line": "*/60 * * * * /bin/true\n",        "rx": r"(?is).*minute.*"},
    {"id": "min_negative",         "line": "-1 * * * * /bin/true\n",          "rx": r"(?is).*minute.*"},
    {"id": "min_range_overflow",   "line": "0-60 * * * * /bin/true\n",        "rx": r"(?is).*minute.*"},
    {"id": "min_descending_range", "line": "10-5 * * * * /bin/true\n",        "rx": r"(?is).*minute.*"},
    {"id": "min_step_zero",        "line": "*/0 * * * * /bin/true\n",         "rx": r"(?is).*minute.*"},
    {"id": "min_list_empty_item",  "line": "0,,15 * * * * /bin/true\n",       "rx": r"(?is).*minute.*"},
    {"id": "min_non_numeric",      "line": "A * * * * /bin/true\n",           "rx": r"(?is).*minute.*"},
]
@pytest.mark.skipif("linux" not in sys.platform, reason="Linux-only")  # type: ignore[misc]
@pytest.mark.parametrize("case", INVALID_MINUTE_CASES, ids=[c["id"] for c in INVALID_MINUTE_CASES]) # type: ignore[misc]
def test_invalid_minute(case: Dict[str, str], caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.ERROR)
    code, stdout, stderr = run_line(case["line"])
    combined = (stdout or "") + (stderr or "") + caplog.text
    assert code != 0, f"{case['id']}: expected non-zero exit, got 0\nSTDOUT:{stdout}\nSTDERR:{stderr}\nLOGS:{caplog.text}"
    assert re.search(case["rx"], combined) is not None, (
        f"{case['id']}: pattern {case['rx']!r} not found in combined output.\n"
        f"STDOUT:{stdout}\nSTDERR:{stderr}\nLOGS:{caplog.text}"
    )

def main() -> None:
    pass

if __name__ == '__main__':
    main()
