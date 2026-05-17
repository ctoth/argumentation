# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
#   "z3-solver>=4.12",
# ]
# ///
"""PEP 723 benchmark entrypoint for the dialectical chess sidecar."""

from __future__ import annotations

from dialectical_chess.bench import main


if __name__ == "__main__":
    raise SystemExit(main())
