"""Round-1 triage probe: stable-first shortcut for SE-PR single-extension.

Reusable, read-only diagnostic for the ICCMA 2023 ABA campaign (Round 1). It
does NOT modify any solver code and does NOT implement the shortcut; it only
measures, on a single dev instance, whether the recommended "try the stable
extension first and hand it back as the preferred witness" experiment can survive
its own probe (scout report `reports/iccma-round1-probe-scout-20260711.md`, P4/P5).

For the dev instance it establishes, from live APIs:

  1. flatness and the current auto-route backend the runner would pick;
  2. stable single-extension status / elapsed / witness under a 5 s solve cap;
  3. INDEPENDENT preferred-extension validity of that exact witness, using a
     self-contained polynomial verifier (`horn_closure` only) -- NOT the clingo
     stable solver that produced it, and NOT the exponential `aba.py` reference
     kernel (which enumerates the 2**|assumptions| powerset and is intractable at
     600 assumptions);
  4. the current preferred single-extension path's telemetry (solver_calls,
     outer_iterations, refinement_clauses, inner_iterations), status, and elapsed
     under a 15 s solve cap -- i.e. the work a stable-first success would skip.

The py-spy real-worker profile (probe item 5) is run separately through the
existing harness runner (`tools/iccma2025_run_native.py`), not from this script;
its raw profile path is recorded in the experiment record.

INDEPENDENT PREFERRED VERIFIER -- soundness note.
For flat ABA, with cl(X) = horn_closure(X, rules) (least fixpoint, polynomial):
  * "X attacks assumption a"  <=>  contrary[a] in cl(X)   (Horn closure is
    monotone, so a subset of X derives contrary[a] iff cl(X) does).
  * conflict-free(S)          <=>  no a in S has contrary[a] in cl(S).
  * S defends each of its members: let U = assumptions NOT attacked by S
    (contrary[c] not in cl(S)); U is the largest attacker set S cannot
    counter-attack, so S defends a  <=>  contrary[a] not in cl(U). Hence
    admissible(S) <=> conflict-free(S) AND for all a in S: contrary[a] not in cl(U).
  * maximal-conflict-free(S): for every outside assumption a, S|{a} is not
    conflict-free. Since a not in S is attacked by a stable S (contrary[a] in
    cl(S) subset of cl(S|{a})), S|{a} is not conflict-free -- so this reduces to
    "every outside assumption is attacked by S".
Theorem used: if S is admissible AND maximal-conflict-free then S is preferred
(any admissible T strictly containing S would be a conflict-free proper superset,
contradicting maximality). This is SOUND for accepting the witness as preferred
(it is a sufficient condition; a stable extension always satisfies it). All checks
are two Horn closures plus set work -- fully tractable at 600 assumptions.
"""

from __future__ import annotations

import time
from pathlib import Path

from argumentation.interop.iccma import parse_aba
from argumentation.structured.aba._closure import horn_closure
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aba.aba_asp import ABAQueryResult, solve_aba_with_backend
from argumentation.structured.aba.aba_route_policy import (
    _is_flat_aba,
    large_dense_flat_aba_shape,
    sparse_narrow_native_sat_shape,
)
from argumentation.solving.solver import _auto_aba_backend_for_framework

DEV_INSTANCE = Path(
    "data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_1.aba"
)
STABLE_CAP_SECONDS = 5.0
PREFERRED_CAP_SECONDS = 15.0
STABLE_SURVIVE_SECONDS = 2.0  # survive criterion: stable must return within 2 s


def _witness(result: ABAQueryResult) -> frozenset | None:
    """The single-extension witness assumption set from a solve result."""
    assert result.status == "success", f"solve did not succeed: {result.status}"
    assert len(result.extensions) <= 1, result.extensions
    if not result.extensions:
        assert not result.accepted_assumptions
        return None
    witness = frozenset(result.extensions[0])
    assert result.accepted_assumptions == witness
    return witness


def _telemetry_count(result: ABAQueryResult, key: str) -> int:
    """Read one integer counter from the live result metadata."""
    value = result.metadata.get(key)
    assert isinstance(value, int) and value >= 0, (key, value)
    return value


def verify_preferred_independent(fw: ABAFramework, witness: frozenset) -> dict:
    """Independent, polynomial, sound preferred-extension check for the witness.

    Uses only `horn_closure` and the contrary map -- no clingo, no powerset. See
    module docstring for the soundness argument. Returns a dict of the booleans
    and the derived sets so the caller can print the full picture.
    """
    assumptions = frozenset(fw.assumptions)
    contrary = fw.contrary
    rules = fw.rules

    cl_s = horn_closure(witness, rules)

    # (0) witness is a subset of assumptions and closed (trivially true for flat).
    subset_ok = witness <= assumptions
    closed_ok = (cl_s & assumptions) == witness

    # (1) conflict-free: no member's contrary is derivable from the witness.
    self_attacked = {a for a in witness if contrary[a] in cl_s}
    conflict_free = not self_attacked

    # (2) which outside assumptions the witness attacks.
    attacked = {c for c in assumptions if contrary[c] in cl_s}
    unattacked = assumptions - attacked  # U: largest attacker S cannot counter

    # (3) admissibility: S defends every member  <=>  contrary[a] not in cl(U).
    cl_u = horn_closure(unattacked, rules)
    undefended = {a for a in witness if contrary[a] in cl_u}
    defends = not undefended
    admissible = conflict_free and defends and closed_ok and subset_ok

    # (4) maximal-conflict-free: every outside assumption is attacked by S, so
    #     S|{a} is never conflict-free. Sufficient (with admissibility) for preferred.
    outside = assumptions - witness
    unattacked_outside = {a for a in outside if contrary[a] not in cl_s}
    maximal_conflict_free = not unattacked_outside

    preferred = admissible and maximal_conflict_free
    # For the record: is the witness also independently a STABLE extension?
    stable = conflict_free and closed_ok and not unattacked_outside

    return {
        "witness_size": len(witness),
        "subset_ok": subset_ok,
        "closed_ok": closed_ok,
        "conflict_free": conflict_free,
        "defends": defends,
        "admissible": admissible,
        "maximal_conflict_free": maximal_conflict_free,
        "preferred": preferred,
        "stable": stable,
        "num_attacked_outside": len(attacked - witness),
        "num_unattacked_outside": len(unattacked_outside),
    }


def main() -> int:
    inst = DEV_INSTANCE
    print(f"# Probe: stable-first SE-PR shortcut  instance={inst}")
    assert inst.exists(), f"dev instance missing: {inst}"
    fw = parse_aba(inst.read_text())
    assert isinstance(fw, ABAFramework), type(fw)

    n_assume = len(fw.assumptions)
    n_rules = len(fw.rules)
    density = n_rules / n_assume if n_assume else 0.0

    # -- Item 1: flatness + current route predicates --------------------------
    flat = _is_flat_aba(fw)
    sat_shape = sparse_narrow_native_sat_shape(fw)
    dense_shape = large_dense_flat_aba_shape(fw)
    route_st = _auto_aba_backend_for_framework(
        "auto", "stable", task="single-extension", framework=fw
    )
    route_pr = _auto_aba_backend_for_framework(
        "auto", "preferred", task="single-extension", framework=fw
    )
    print("\n## 1. shape / route")
    print(f"assumptions={n_assume} rules={n_rules} density={density:.2f}")
    print(f"flat={flat} sat_shape={sat_shape} dense_shape={dense_shape}")
    print(f"auto_route SE-ST={route_st!r}  SE-PR={route_pr!r}")
    # ABAFramework enforces flatness at construction; belt-and-suspenders here.
    assert flat, "route-policy flatness disagrees with the parsed framework"
    assert not sat_shape, "instance routes to the N1-dead native SAT path"
    assert route_st == "asp" and route_pr == "asp", (route_st, route_pr)

    # -- Item 2: stable single-extension under a 5 s cap ----------------------
    t0 = time.perf_counter()
    st = solve_aba_with_backend(
        fw,
        backend="clingo",
        semantics="stable",
        task="single-extension",
        clingo_solve_timeout_seconds=STABLE_CAP_SECONDS,
    )
    st_elapsed = time.perf_counter() - t0
    st_witness = _witness(st)
    st_tel = {
        key: _telemetry_count(st, key)
        for key in (
            "solver_calls",
            "outer_iterations",
            "inner_iterations",
            "refinement_clauses",
        )
    }
    print("\n## 2. stable single-extension (cap 5 s)")
    print(
        f"status={st.status!r} elapsed={st_elapsed:.3f}s "
        f"witness_size={None if st_witness is None else len(st_witness)}"
    )
    print(f"witness={None if st_witness is None else sorted(st_witness, key=repr)!r}")
    print(f"telemetry={st_tel}")
    assert st.status == "success", f"stable solve did not succeed: {st.status}"
    assert st_elapsed <= STABLE_CAP_SECONDS, st_elapsed

    # -- Item 3: independent preferred validity of THAT witness ---------------
    if st_witness is None:
        v = {"witness_present": False, "preferred": False}
    else:
        v = verify_preferred_independent(fw, st_witness)
    print("\n## 3. independent preferred check of the stable witness")
    print(str(v))
    if st_witness is not None:
        assert v["subset_ok"] and v["closed_ok"], "witness not a closed assumption subset"

    # -- Item 4: current preferred single-extension path telemetry (cap 15 s) --
    t1 = time.perf_counter()
    pr = solve_aba_with_backend(
        fw,
        backend="clingo",
        semantics="preferred",
        task="single-extension",
        clingo_solve_timeout_seconds=PREFERRED_CAP_SECONDS,
    )
    pr_elapsed = time.perf_counter() - t1
    pr_tel = {
        k: _telemetry_count(pr, k)
        for k in (
            "solver_calls",
            "outer_iterations",
            "inner_iterations",
            "refinement_clauses",
        )
    }
    print("\n## 4. current preferred single-extension path (cap 15 s)")
    print(f"status={pr.status!r} elapsed={pr_elapsed:.3f}s")
    print(f"telemetry={pr_tel}")
    assert pr.status in {"success", "timeout"}, pr.status
    assert pr_elapsed <= PREFERRED_CAP_SECONDS, pr_elapsed

    # -- Verdict --------------------------------------------------------------
    solver_calls = pr_tel.get("solver_calls") or 0
    outer = pr_tel.get("outer_iterations") or 0
    # "SE-PR enters work a stable-first path skips": it either times out, or runs
    # the maximization loop (>1 solve / >=1 outer iteration) beyond the single
    # stable solve the shortcut would substitute.
    pr_does_extra_work = pr.status == "timeout" or solver_calls > 1 or outer >= 1

    c_flat_routed = flat and (not sat_shape) and route_pr == "asp"
    c_stable_fast = (
        st.status == "success"
        and st_witness is not None
        and st_elapsed <= STABLE_SURVIVE_SECONDS
    )
    c_preferred_ok = bool(v["preferred"])
    c_extra_work = bool(pr_does_extra_work)
    survive = c_flat_routed and c_stable_fast and c_preferred_ok and c_extra_work

    print("\n## VERDICT")
    print(f"  flat & clingo-routed .............. {c_flat_routed}")
    print(f"  stable <= 2 s ({st_elapsed:.3f}s) ......... {c_stable_fast}")
    print(f"  independent preferred accepts ..... {c_preferred_ok}")
    print(f"  current SE-PR does skippable work .. {c_extra_work}")
    print(f"  ==> CANDIDATE {'SURVIVES' if survive else 'KILLED'}")
    assert c_preferred_ok, "exact stable witness failed independent preferred verification"
    assert survive, "stable-first SE-PR candidate failed a survival criterion"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
