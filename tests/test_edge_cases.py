"""
Edge-case tests: make sure the game handles "weird" inputs gracefully
instead of crashing or silently accepting them.

Three categories of edge-case input are covered:
  1. Negative numbers      (e.g. "-5")
  2. Decimals              (e.g. "42.5")
  3. Extremely large values (e.g. "99999999999999999999")

"Gracefully" means: parse_guess never raises, it returns a clean
(ok, value, error) tuple, and check_guess keeps working for every
integer the parser lets through.
"""

import pytest

from logic_utils import parse_guess, check_guess


# ---------------------------------------------------------------------------
# 1. Negative numbers
#
# A "-5" is a valid whole number, so parse_guess should accept it (the app's
# range check is what rejects it later). The key point: it must NOT crash.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [("-5", -5), ("-1", -1), ("-100", -100)])
def test_parse_accepts_negative_whole_numbers(raw, expected):
    ok, value, err = parse_guess(raw)
    assert ok is True
    assert value == expected
    assert err is None


def test_check_guess_handles_negative_guess():
    # Negative guess below a positive secret -> "Too Low", no exception.
    outcome, _ = check_guess(-5, 10)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# 2. Decimals
#
# "42.5" is not a whole number. parse_guess must reject it cleanly with a
# helpful message rather than crashing or rounding it down to a winning 42.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["42.5", "42.0", "0.1", "-3.7", "1e3"])
def test_parse_rejects_decimals(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "Enter a whole number."


# ---------------------------------------------------------------------------
# 3. Extremely large values
#
# Python ints are unbounded, so a huge value should parse without overflow,
# and comparisons in check_guess should still work.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["99999999999999999999", "10000000000", "12345678901234567890"])
def test_parse_accepts_extremely_large_values(raw):
    ok, value, err = parse_guess(raw)
    assert ok is True
    assert value == int(raw)
    assert err is None


def test_check_guess_handles_extremely_large_guess():
    outcome, _ = check_guess(10**50, 50)
    assert outcome == "Too High"


# ---------------------------------------------------------------------------
# Bonus: other malformed inputs should also fail gracefully (no crash).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["abc", "  ", "12abc", "++5", "None"])
def test_parse_rejects_non_numeric_text(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "Enter a whole number."


@pytest.mark.parametrize("raw", [None, ""])
def test_parse_handles_missing_input(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."
