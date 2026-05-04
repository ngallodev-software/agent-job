"""Tiny calculator helpers for eval tasks."""


def add(left: float, right: float) -> float:
    return left + right


def subtract(left: float, right: float) -> float:
    return left - right


def multiply(left: float, right: float) -> float:
    return left * right


def average(values: list[float]) -> float:
    """Return the average value.

    Current bug:
    uses floor division, which truncates fractional results.
    """
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) // len(values)
