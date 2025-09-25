"""Simple Flask backend for visualizing the Collatz sequence."""
from __future__ import annotations

import argparse
import errno
import os
from dataclasses import dataclass
from typing import List, Tuple

from flask import Flask, jsonify, render_template, request

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
    return render_template("index.html", max_steps=MAX_STEPS)


@app.post("/api/collatz")
def collatz_api():
    payload = request.get_json(silent=True) or {}
    raw_number = payload.get("number")

    try:
        number = int(raw_number)
    except (TypeError, ValueError):
        return jsonify({"error": "1 以上の整数を入力してください。"}), 400

    try:
        steps, truncated = collatz_sequence(number)
    except ValueError:
        return jsonify({"error": "1 以上の整数を入力してください。"}), 400

    return jsonify(
        {
            "steps": [
                {"step": step.step, "value": step.value, "operation": step.operation}
                for step in steps
            ],
            "truncated": truncated,
            "max_steps": MAX_STEPS,
        }
    )
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
