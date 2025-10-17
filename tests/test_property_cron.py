#!/usr/bin/env python3
"""Property-based tests for cron line parsing."""

from __future__ import annotations

from hypothesis import HealthCheck, given as hypothesis_given, settings, strategies as st
from typing import Any, Callable, cast

from checkcrontab.checker import check_line

Decorator = Callable[[Callable[..., Any]], Callable[..., Any]]
DecoratorFactory = Callable[..., Decorator]

COMMON_SETTINGS: Decorator = cast(
    Decorator,
    settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow]),
)
typed_given: DecoratorFactory = cast(DecoratorFactory, hypothesis_given)


def _valid_range(min_val: int, max_val: int) -> st.SearchStrategy[str]:
    return st.integers(min_val, max_val).flatmap(
        lambda start: st.integers(start, max_val).map(lambda end: f"{start}-{end}")
    )


def _valid_step(max_val: int) -> st.SearchStrategy[str]:
    return st.integers(1, max_val).map(lambda step: f"*/{step}")


def _valid_list(min_val: int, max_val: int) -> st.SearchStrategy[str]:
    return st.lists(st.integers(min_val, max_val), min_size=2, max_size=4, unique=True).map(
        lambda values: ",".join(str(value) for value in values)
    )


def _valid_field(min_val: int, max_val: int) -> st.SearchStrategy[str]:
    base_number = st.integers(min_val, max_val).map(str)
    return st.one_of(
        st.just("*"),
        base_number,
        _valid_range(min_val, max_val),
        _valid_step(max_val),
        _valid_list(min_val, max_val),
    )


def _invalid_range(min_val: int, max_val: int) -> st.SearchStrategy[str]:
    upper_min = min_val + 1
    return st.integers(upper_min, max_val).flatmap(
        lambda start: st.integers(min_val, start - 1).map(lambda end: f"{start}-{end}")
    )


def _invalid_step(max_val: int) -> st.SearchStrategy[str]:
    too_large = st.integers(max_val + 1, max_val * 4).map(lambda step: f"*/{step}")
    non_positive = st.integers(-4, 0).map(lambda step: f"*/{step}")
    return st.one_of(too_large, non_positive)


def _duplicate_list(min_val: int, max_val: int) -> st.SearchStrategy[str]:
    return st.integers(min_val, max_val).map(lambda value: f"{value},{value}")


def _safe_command() -> st.SearchStrategy[str]:
    word = st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=10)
    args = st.lists(word, min_size=0, max_size=3)
    return st.builds(
        lambda base, extra: "/usr/bin/" + base + (" " + " ".join(extra) if extra else ""),
        word,
        args,
    )


@COMMON_SETTINGS
@typed_given(
    minute=_valid_field(0, 59),
    hour=_valid_field(0, 23),
    day=_valid_field(1, 31),
    month=_valid_field(1, 12),
    weekday=_valid_field(0, 7),
)
def test_user_crontab_accepts_valid_fields(minute: str, hour: str, day: str, month: str, weekday: str) -> None:
    line = f"{minute} {hour} {day} {month} {weekday} /usr/bin/true"
    errors, warnings = check_line(line, 1, "property_cron", is_system_crontab=False)
    assert errors == []
    assert warnings == []


@COMMON_SETTINGS
@typed_given(
    minute=_valid_field(0, 59),
    hour=_valid_field(0, 23),
    day=_valid_field(1, 31),
    month=_valid_field(1, 12),
    weekday=_valid_field(0, 7),
)
def test_system_crontab_accepts_valid_fields(minute: str, hour: str, day: str, month: str, weekday: str) -> None:
    line = f"{minute} {hour} {day} {month} {weekday} root /usr/bin/true"
    errors, warnings = check_line(line, 1, "property_cron", is_system_crontab=True)
    assert errors == []
    assert warnings == []


@COMMON_SETTINGS
@typed_given(
    bad_minute=_invalid_range(0, 59),
    hour=_valid_field(0, 23),
    day=_valid_field(1, 31),
    month=_valid_field(1, 12),
    weekday=_valid_field(0, 7),
)
def test_invalid_range_is_reported(bad_minute: str, hour: str, day: str, month: str, weekday: str) -> None:
    line = f"{bad_minute} {hour} {day} {month} {weekday} /usr/bin/true"
    errors, _ = check_line(line, 1, "invalid-range_cron", is_system_crontab=False)
    assert errors
    assert any("invalid range" in error for error in errors)


@COMMON_SETTINGS
@typed_given(
    bad_step=_invalid_step(59),
    hour=_valid_field(0, 23),
    day=_valid_field(1, 31),
    month=_valid_field(1, 12),
    weekday=_valid_field(0, 7),
)
def test_invalid_steps_are_rejected(bad_step: str, hour: str, day: str, month: str, weekday: str) -> None:
    line = f"{bad_step} {hour} {day} {month} {weekday} /usr/bin/true"
    errors, _ = check_line(line, 1, "invalid-step_cron", is_system_crontab=False)
    assert errors
    assert any("step" in error for error in errors)


@COMMON_SETTINGS
@typed_given(
    duplicate_minute=_duplicate_list(0, 59),
    hour=_valid_field(0, 23),
    day=_valid_field(1, 31),
    month=_valid_field(1, 12),
    weekday=_valid_field(0, 7),
)
def test_duplicate_list_entries_are_detected(
    duplicate_minute: str,
    hour: str,
    day: str,
    month: str,
    weekday: str,
) -> None:
    line = f"{duplicate_minute} {hour} {day} {month} {weekday} /usr/bin/true"
    errors, _ = check_line(line, 1, "duplicate-list_cron", is_system_crontab=False)
    assert errors
    assert any("duplicate value" in error for error in errors)


SPECIAL_KEYWORDS = st.sampled_from(["@reboot", "@yearly", "@annually", "@monthly", "@weekly", "@daily", "@midnight", "@hourly"])


@COMMON_SETTINGS
@typed_given(keyword=SPECIAL_KEYWORDS, command=_safe_command())
def test_special_user_keywords(keyword: str, command: str) -> None:
    line = f"{keyword} {command}"
    errors, warnings = check_line(line, 1, "special-user_cron", is_system_crontab=False)
    assert errors == []
    assert warnings == []


@COMMON_SETTINGS
@typed_given(keyword=SPECIAL_KEYWORDS, command=_safe_command())
def test_special_system_keywords(keyword: str, command: str) -> None:
    line = f"{keyword} root {command}"
    errors, warnings = check_line(line, 1, "special-system_cron", is_system_crontab=True)
    assert errors == []
    assert warnings == []
