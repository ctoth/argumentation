"""Profile WHY simplify_aba(stable) hangs on aba_2000_0.1_5_5_1 (exp 4B).

Decomposes the simplify_aba pipeline on the named frontier-v1 SE-ST rows:

1. the cheap bail-out forward closures (aba_preprocessing.py:265) — expected fast;
2. the current hot path `_SupportState.from_framework` (minimal-support
   enumeration, aba_support_model.py:108) — run in a SUBPROCESS with a hard
   timeout because the hypothesis is that it never finishes;
3. a closure-based grounded fixpoint prototype (candidate fix): iterate the def
   operator using two horn closures per round instead of minimal supports —
   expected milliseconds;
4. equivalence check: on sibling instances where the CURRENT implementation
   completes, prototype == grounded_assumption_set_via_closures.

Usage:
    uv run scripts/profile_aba_simplify_stable.py
    uv run scripts/profile_aba_simplify_stable.py --mode supports --instance <path>
        (internal: subprocess target for the timeout-guarded stage)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from argumentation.interop.iccma import parse_aba
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_preprocessing import (
    _forward_closure,
    grounded_assumption_set_via_closures,
)

DATA_ROOT = Path(
    r"C:\Users\Q\code\argumentation\data\iccma\2025\extracted\instances\ABAs"
)
NAMED_ROWS = ("aba_2000_0.1_5_5_1.aba", "aba_2000_0.1_5_5_6.aba")
# Small instances where the CURRENT implementation is expected to finish, for the
# equivalence check (the 2000-atom siblings may hit the same blow-up when the
# simplify_aba bail-out is bypassed, so they cannot serve as oracles here).
EQUIVALENCE_ROWS = (
    "aba_100_0.1_10_10_6.aba",
    "aba_100_0.1_10_10_7.aba",
    "aba_100_0.1_10_5_7.aba",
)
SUPPORTS_TIMEOUT_SECONDS = 60.0


def _load(path: Path) -> ABAFramework:
    return parse_aba(path.read_text(encoding="utf-8"))


def closure_grounded_prototype(framework: ABAFramework) -> frozenset:
    """Candidate fix: def-operator fixpoint via horn closures, no minimal supports."""
    assumptions = framework.assumptions
    selected: frozenset = frozenset()
    while True:
        closure_of_selected = _forward_closure(framework, selected)
        attacked = frozenset(
            assumption
            for assumption in assumptions
            if framework.contrary[assumption] in closure_of_selected
        )
        survivor_closure = _forward_closure(framework, assumptions - attacked)
        defended = frozenset(
            assumption
            for assumption in assumptions
            if framework.contrary[assumption] not in survivor_closure
        )
        next_selected = selected | defended
        if next_selected == selected:
            return selected
        selected = next_selected


def run_supports_mode(instance: Path) -> None:
    from argumentation.structured.aba.aba_support_model import _SupportState

    framework = _load(instance)
    started = time.perf_counter()
    state = _SupportState.from_framework(framework)
    elapsed = time.perf_counter() - started
    print(f"supports built in {elapsed:.3f}s ({len(state.supports)} literals)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("profile", "supports"), default="profile")
    parser.add_argument("--instance", type=Path, default=None)
    args = parser.parse_args()

    if args.mode == "supports":
        assert args.instance is not None
        run_supports_mode(args.instance)
        return

    for name in NAMED_ROWS:
        path = DATA_ROOT / name
        framework = _load(path)
        print(
            f"== {name}: atoms={len(framework.language)} "
            f"asms={len(framework.assumptions)} rules={len(framework.rules)}"
        )

        started = time.perf_counter()
        fact_closure = _forward_closure(framework, frozenset())
        all_closure = _forward_closure(framework, framework.assumptions)
        bailout_all = all(
            framework.contrary[a] in all_closure for a in framework.assumptions
        )
        bailout_fact = any(
            framework.contrary[a] in fact_closure for a in framework.assumptions
        )
        print(
            f"  bail-out closures: {time.perf_counter() - started:.3f}s "
            f"(all-contraries-derivable={bailout_all}, "
            f"contrary-is-fact={bailout_fact}, "
            f"bails-out={bailout_all and not bailout_fact})"
        )

        started = time.perf_counter()
        grounded = closure_grounded_prototype(framework)
        print(
            f"  closure-based grounded prototype: "
            f"{time.perf_counter() - started:.3f}s |grounded|={len(grounded)}"
        )

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    __file__,
                    "--mode",
                    "supports",
                    "--instance",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=SUPPORTS_TIMEOUT_SECONDS,
            )
            print(
                f"  _SupportState.from_framework: "
                f"{completed.stdout.strip()} rc={completed.returncode}"
            )
        except subprocess.TimeoutExpired:
            print(
                f"  _SupportState.from_framework: TIMEOUT "
                f">{SUPPORTS_TIMEOUT_SECONDS:.0f}s "
                f"(killed after {time.perf_counter() - started:.1f}s)"
            )

    for name in EQUIVALENCE_ROWS:
        path = DATA_ROOT / name
        framework = _load(path)
        started = time.perf_counter()
        current = grounded_assumption_set_via_closures(framework)
        current_elapsed = time.perf_counter() - started
        started = time.perf_counter()
        prototype = closure_grounded_prototype(framework)
        prototype_elapsed = time.perf_counter() - started
        print(
            f"== {name}: current={current_elapsed:.3f}s "
            f"prototype={prototype_elapsed:.3f}s "
            f"equal={current == prototype} |grounded|={len(current)}"
        )


if __name__ == "__main__":
    main()
