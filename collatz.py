"""Simple Flask backend for visualizing the Collatz sequence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from flask import Flask, render_template, request

app = Flask(__name__)

MAX_STEPS = 1000


@dataclass
class CollatzStep:
    """Represents a single step in the Collatz sequence."""

    step: int
    value: int
    operation: str


def collatz_sequence(start: int, *, max_steps: int = MAX_STEPS) -> Tuple[List[CollatzStep], bool]:
    """Generate the Collatz sequence for ``start``.

    Args:
        start: Positive integer to begin the sequence.
        max_steps: Maximum number of operations to perform to avoid infinite loops.

    Returns:
        A tuple of ``(steps, truncated)``. ``steps`` contains the detailed progression
        from the starting value to 1 (or until the maximum number of steps is reached).
        ``truncated`` is ``True`` when the computation stopped because ``max_steps`` was
        exceeded.
    """

    if start <= 0:
        raise ValueError("start must be a positive integer")

    steps: List[CollatzStep] = [CollatzStep(step=0, value=start, operation="開始値")]
    current = start
    step_index = 0

    while current != 1 and step_index < max_steps:
        if current % 2 == 0:
            next_value = current // 2
            operation = f"{current} は偶数なので 2 で割って {next_value}"
        else:
            next_value = current * 3 + 1
            operation = f"{current} は奇数なので 3×{current} + 1 = {next_value}"

        step_index += 1
        current = next_value
        steps.append(CollatzStep(step=step_index, value=current, operation=operation))

    truncated = current != 1
    return steps, truncated


@app.route("/", methods=["GET", "POST"])
def index():
    number_input = ""
    steps: List[CollatzStep] | None = None
    error_message: str | None = None
    truncated = False

    if request.method == "POST":
        number_input = request.form.get("number", "").strip()
        if not number_input:
            error_message = "値を入力してください。"
        else:
            try:
                number = int(number_input)
                steps, truncated = collatz_sequence(number)
            except ValueError:
                error_message = "1 以上の整数を入力してください。"

    max_value = max((step.value for step in steps), default=None) if steps else None

    return render_template(
        "index.html",
        number_input=number_input,
        steps=steps,
        truncated=truncated,
        max_value=max_value,
        max_steps=MAX_STEPS,
        error_message=error_message,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
