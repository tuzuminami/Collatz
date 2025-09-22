"""Utility functions for working with the Collatz sequence.

The Collatz sequence (also known as the 3n + 1 problem) starts from any
positive integer :math:`n`. If :math:`n` is even, the next term is
:math:`n / 2`; if :math:`n` is odd, the next term is :math:`3n + 1`. The
sequence repeats this process until it reaches ``1``.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Iterable, List


def collatz_sequence(start: int) -> List[int]:
    """Return the Collatz sequence that begins with ``start``.

    Parameters
    ----------
    start:
        A positive integer from which to start the sequence.

    Returns
    -------
    list[int]
        The sequence of numbers produced by repeatedly applying the
        Collatz rules until reaching ``1`` (inclusive).

    Raises
    ------
    ValueError
        If ``start`` is not a positive integer.
    """

    if not isinstance(start, int) or start <= 0:
        raise ValueError("start must be a positive integer")

    sequence = [start]
    current = start
    while current != 1:
        if current % 2 == 0:
            current //= 2
        else:
            current = 3 * current + 1
        sequence.append(current)
    return sequence


def main(argv: Iterable[str] | None = None) -> None:
    """Command-line entry point that prints the Collatz sequence."""

    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "start",
        type=int,
        help="positive integer from which to start the Collatz sequence",
    )
    args = parser.parse_args(argv)
    sequence = collatz_sequence(args.start)
    print(" ".join(str(term) for term in sequence))


if __name__ == "__main__":
    main()
