"""Tests for calculator.py. Run with `python test_calculator.py` or `pytest`."""

from calculator import calculate, format_number


def test_basic_arithmetic() -> None:
    assert calculate(2, "+", 3) == 5
    assert calculate(2, "-", 3) == -1
    assert calculate(2, "*", 3) == 6
    assert calculate(3, "/", 2) == 1.5


def test_negative_and_float_operands() -> None:
    assert calculate(-2.5, "+", 0.5) == -2.0
    assert calculate(-4, "*", -3) == 12


def test_divide_by_zero_raises() -> None:
    try:
        calculate(1, "/", 0)
    except ZeroDivisionError:
        return
    raise AssertionError("dividing by zero should raise ZeroDivisionError")


def test_invalid_operation_raises() -> None:
    try:
        calculate(1, "^", 2)
    except ValueError:
        return
    raise AssertionError("an unsupported operation should raise ValueError")


def test_format_number_drops_trailing_zero() -> None:
    assert format_number(5.0) == "5"
    assert format_number(-2.5) == "-2.5"


def test_format_number_keeps_large_numbers_exact() -> None:
    # The old "%g" default truncated this to 1e+07, hiding the addition.
    assert format_number(10000001.0) == "10000001"


def test_format_number_hides_float_noise() -> None:
    assert format_number(0.1 + 0.2) == "0.3"


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} passed")
