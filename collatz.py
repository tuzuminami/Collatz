"""Compute Collatz sequences from the command line."""
from __future__ import annotations

import argparse
from typing import Iterable


def collatz_sequence(start: int) -> list[int]:
    """Return the Collatz sequence starting from ``start``.

    Args:
        start: Positive integer to begin the sequence.

    Returns:
        A list containing each value in the progression until it reaches 1.

    Raises:
        ValueError: If ``start`` is not a positive integer.
    """

    if start <= 0:
        raise ValueError("start must be a positive integer")

    sequence = [start]
    current = start

    while current != 1:
        if current % 2 == 0:
            current //= 2
        else:
            current = current * 3 + 1
        sequence.append(current)

    return sequence


def format_sequence(sequence: Iterable[int]) -> str:
    """Format the sequence for human-friendly output."""

    steps = []
    for index, value in enumerate(sequence):
        steps.append(f"Step {index:>2}: {value}")
    return "\n".join(steps)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Compute the Collatz sequence for a positive integer.",
    )
    parser.add_argument(
        "number",
        type=int,
        help="Starting positive integer for the sequence.",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint for the script."""

    args = parse_args()
    sequence = collatz_sequence(args.number)
    print(format_sequence(sequence))


if __name__ == "__main__":
    main()
