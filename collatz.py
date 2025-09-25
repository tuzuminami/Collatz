"""Simple Flask backend for visualizing the Collatz sequence."""
from __future__ import annotations

import argparse
import errno
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

MAX_STEPS = 1000
INVALID_INPUT_MESSAGE = "1 以上の整数を入力してください。"


@dataclass(slots=True)
class CollatzStep:
    """Represents a single step in the Collatz sequence."""

    step: int
    value: int
    operation: str

    def to_dict(self) -> dict[str, int | str]:
        """Return the step as a JSON-serialisable dictionary."""

        return {"step": self.step, "value": self.value, "operation": self.operation}


@dataclass(slots=True)
class CollatzResult:
    """Container for the computed Collatz sequence."""

    steps: list[CollatzStep]
    truncated: bool

    def to_response_payload(self, *, max_steps: int) -> dict[str, Any]:
        """Convert the result to a payload suited for the API response."""

        return {
            "steps": [step.to_dict() for step in self.steps],
            "truncated": self.truncated,
            "max_steps": max_steps,
        }


def collatz_sequence(start: int, *, max_steps: int = MAX_STEPS) -> CollatzResult:
    """Generate the Collatz sequence for ``start``.

    Args:
        start: Positive integer to begin the sequence.
        max_steps: Maximum number of operations to perform to avoid infinite loops.

    Returns:
        A :class:`CollatzResult` instance containing the detailed progression from the
        starting value to 1 (or until the maximum number of steps is reached).

    Raises:
        ValueError: If ``start`` is not a positive integer.
    """

    if start <= 0:
        raise ValueError("start must be a positive integer")

    steps: list[CollatzStep] = [CollatzStep(step=0, value=start, operation="開始値")]
    current = start

    for step_index in range(1, max_steps + 1):
        if current == 1:
            break

        is_even = current % 2 == 0
        if is_even:
            next_value = current // 2
            operation = f"{current} は偶数なので 2 で割って {next_value}"
        else:
            next_value = current * 3 + 1
            operation = f"{current} は奇数なので 3×{current} + 1 = {next_value}"

        current = next_value
        steps.append(CollatzStep(step=step_index, value=current, operation=operation))

    truncated = current != 1
    return CollatzResult(steps=steps, truncated=truncated)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", max_steps=MAX_STEPS)


def _json_error(message: str, status_code: int = 400):
    """Return a Flask JSON response with the given error message."""

    return jsonify({"error": message}), status_code


def _parse_positive_int(value: Any) -> int:
    """Parse ``value`` into a positive integer.

    Raises:
        ValueError: If ``value`` cannot be parsed into a positive integer.
    """

    number = int(value)
    if number < 1:
        raise ValueError
    return number


@app.post("/api/collatz")
def collatz_api():
    payload = request.get_json(silent=True) or {}
    raw_number = payload.get("number")

    try:
        number = _parse_positive_int(raw_number)
    except (TypeError, ValueError):
        return _json_error(INVALID_INPUT_MESSAGE)

    try:
        result = collatz_sequence(number)
    except ValueError:
        return _json_error(INVALID_INPUT_MESSAGE)

    return jsonify(result.to_response_payload(max_steps=MAX_STEPS))
def parse_args() -> argparse.Namespace:
    """Parse command line arguments for configuring the Flask server."""

    parser = argparse.ArgumentParser(description="Collatz 可視化アプリのサーバーを起動します。")
    parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="待ち受けるホスト名。デフォルトは 0.0.0.0 です。",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "5000")),
        help="使用するポート番号。デフォルトは 5000 です。",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Flask のデバッグモードを有効にします (デフォルト)。",
    )
    parser.add_argument(
        "--no-debug",
        dest="debug",
        action="store_false",
        help="Flask のデバッグモードを無効にします。",
    )
    parser.set_defaults(debug=True)
    return parser.parse_args()


def main() -> None:
    """Entrypoint for running the Flask development server."""

    args = parse_args()

    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except OSError as exc:  # pragma: no cover - depends on environment
        if exc.errno == errno.EADDRINUSE:
            print(
                f"Port {args.port} is already in use. "
                "Specify a different port with --port or the PORT environment variable."
            )
            raise SystemExit(1) from exc
        raise


if __name__ == "__main__":
    main()
