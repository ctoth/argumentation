# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
# ]
# ///
"""CLI wrapper for the owned chess substrate."""

from __future__ import annotations

import argparse
import json

from dialectical_chess.board import START_FEN, OwnedBoard, command_payload, run_selftest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fen", nargs="?", default=START_FEN)
    parser.add_argument("--square")
    parser.add_argument("--pseudo-legal", action="store_true")
    parser.add_argument("--legal", action="store_true")
    parser.add_argument("--compare-oracle", action="store_true")
    parser.add_argument("--perft", type=int)
    parser.add_argument("--divide", type=int)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    board = OwnedBoard.from_fen(args.fen)
    print(json.dumps(command_payload(board, args), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
