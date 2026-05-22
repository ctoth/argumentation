"""Tests for the incremental multi-shot clingo CEGAR solver for flat ABA (Wave C2b).

Oracle equivalence: the multi-shot solver (Lehtonen-Wallner-Jaervisalo TPLP 2021
Algorithm 1 / Algorithm 4, ``encodings/aba_com_incremental.lp`` = Listing 1) must
agree with

* the brute-force ``aba.py`` reference (powerset enumeration), and
* the existing ``aba_sat.support_extensions`` support-mask reference, and
* the legacy subprocess-clingo ``aba_asp`` enumerate-then-filter path
  (``backend="clingo_subprocess"``)

on a hand battery plus random flat ABA instances, for ``complete`` / ``stable`` /
``preferred`` / ``grounded`` enumeration, credulous (DC), and skeptical-preferred
(DS-PR, the ASPforABA reproduction). Also asserts the CEGAR loop actually iterates
(refinement clauses accumulate) via :class:`IncrementalTelemetry`, and the
``simplify=False`` opt-out.
"""

from __future__ import annotations

import random

import pytest

from argumentation import aba as native_aba
from argumentation import aba_asp
from argumentation import aba_sat
from argumentation.aba import ABAFramework, AssumptionSet, derives
from argumentation.aba_asp import solve_aba_with_backend
from argumentation.aba_incremental import (
    AbaIncrementalSolver,
    ClingoSolveTimeout,
    IncrementalTelemetry,
)
from argumentation.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _framework(*, assumptions, contrary, rules, extra_language=()) -> ABAFramework:
    language = (
        frozenset(assumptions)
        | frozenset(contrary.values())
        | frozenset(extra_language)
        | frozenset(r.consequent for r in rules)
        | frozenset(a for r in rules for a in r.antecedents)
    )
    return ABAFramework(
        language=language,
        rules=frozenset(rules),
        assumptions=frozenset(assumptions),
        contrary=dict(contrary),
    )


def _show(extensions) -> list[list[str]]:
    return sorted(sorted(map(repr, extension)) for extension in extensions)


# ---------------------------------------------------------------------------
# Batteries
# ---------------------------------------------------------------------------

def battery() -> list[ABAFramework]:
    a, b, c, d = (lit(x) for x in ("a", "b", "c", "d"))
    ca, cb, cc, cd = (lit(x) for x in ("ca", "cb", "cc", "cd"))
    s0, s1, s2 = (lit(x) for x in ("s0", "s1", "s2"))
    out: list[ABAFramework] = []

    # No rules: grounded = all assumptions; only extension = {a, b}.
    out.append(_framework(assumptions={a, b}, contrary={a: ca, b: cb}, rules=[]))

    # Mutual attack a <-> b: preferred = {{a}, {b}}, grounded = {}.
    out.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), cb, "strict"), Rule((b,), ca, "strict")],
        )
    )

    # a defeats b unconditionally (a -> cb); grounded = {a}, b out.
    out.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), cb, "strict")],
        )
    )

    # Three-cycle-ish with derived sentences.
    out.append(
        _framework(
            assumptions={a, b, c},
            contrary={a: ca, b: cb, c: cc},
            rules=[
                Rule((a,), cb, "strict"),
                Rule((b,), cc, "strict"),
                Rule((c,), ca, "strict"),
            ],
        )
    )

    # Self-attacking assumption d -> cd.
    out.append(
        _framework(
            assumptions={a, b, d},
            contrary={a: ca, b: cb, d: cd},
            rules=[Rule((d,), cd, "strict"), Rule((a,), cb, "strict")],
        )
    )

    # Conjunctive bodies and derived sentences.
    out.append(
        _framework(
            assumptions={a, b, c},
            contrary={a: ca, b: cb, c: cc},
            rules=[
                Rule((a, b), s0, "strict"),
                Rule((s0,), cc, "strict"),
                Rule((c,), ca, "strict"),
            ],
            extra_language=(s0,),
        )
    )

    # The found random instance needing >=2 outer CEGAR iterations for DS-PR.
    a0, a1, a2 = (lit(x) for x in ("a0", "a1", "a2"))
    c0, c1, c2 = (lit(x) for x in ("c0", "c1", "c2"))
    sa, sb, sc = (lit(x) for x in ("s0", "s1", "s2"))
    out.append(
        _framework(
            assumptions={a0, a1, a2},
            contrary={a0: c0, a1: c1, a2: c2},
            rules=[
                Rule((a0,), sb, "strict", "r2"),
                Rule((a1, a2), c0, "strict", "r5"),
                Rule((a1, sb), sc, "strict", "r1"),
                Rule((a1,), sa, "strict", "r4"),
                Rule((sb, sa), c2, "strict", "r7"),
                Rule((sc, a0, a1), c0, "strict", "r3"),
                Rule((sc,), c1, "strict", "r8"),
            ],
            extra_language=(sa, sb, sc),
        )
    )

    # The found random instance with refinement_clauses == 3 for DS-PR(a4) -> NO.
    a3, a4 = (lit(x) for x in ("a3", "a4"))
    c3, c4 = (lit(x) for x in ("c3", "c4"))
    out.append(
        _framework(
            assumptions={a0, a1, a2, a3, a4},
            contrary={a0: c0, a1: c1, a2: c2, a3: c3, a4: c4},
            rules=[
                Rule((a0, a2, sb), c1, "strict", "r13"),
                Rule((a1, sa, a3), c4, "strict", "r4"),
                Rule((a1,), c0, "strict", "r7"),
                Rule((a1,), sb, "strict", "r1"),
                Rule((a2, sa, sc), c0, "strict", "r3"),
                Rule((a3, a1), c4, "strict", "r11"),
                Rule((a3, sa), c0, "strict", "r9"),
                Rule((a3,), c0, "strict", "r6"),
                Rule((a4,), c3, "strict", "r5"),
                Rule((sb, a0), sa, "strict", "r10"),
                Rule((sb, sa, a3), sc, "strict", "r2"),
                Rule((sb,), c0, "strict", "r0"),
                Rule((sc, a0, a1), c4, "strict", "r8"),
                Rule((sc, a3), c0, "strict", "r12"),
            ],
            extra_language=(sa, sb, sc),
        )
    )

    return out


def random_framework(rng: random.Random) -> ABAFramework:
    n = rng.randint(1, 5)
    assumptions = [lit(f"a{i}") for i in range(n)]
    contrary = {assumptions[i]: lit(f"c{i}") for i in range(n)}
    aux = [lit(f"p{i}") for i in range(rng.randint(0, 3))]
    heads = list(contrary.values()) + aux
    candidate_body = assumptions + aux
    rules: list[Rule] = []
    for i in range(rng.randint(0, 3 * n)):
        body_size = rng.randint(1, min(3, len(candidate_body)))
        body = tuple(rng.sample(candidate_body, body_size))
        head = rng.choice(heads)
        if head in body:
            continue
        rules.append(Rule(body, head, "strict", f"r{i}"))
    return _framework(
        assumptions=set(assumptions), contrary=contrary, rules=rules, extra_language=aux
    )


ALL = battery()
RANDOM = [random_framework(random.Random(seed)) for seed in range(120)]


def _intersection(extensions):
    extensions = list(extensions)
    if not extensions:
        return frozenset()
    common = set(extensions[0])
    for e in extensions[1:]:
        common &= set(e)
    return frozenset(common)


def _query_pool(framework: ABAFramework):
    return sorted(framework.assumptions, key=repr) + sorted(framework.contrary.values(), key=repr) + [
        lit("p0"),
        lit("s1"),
        lit("missing_sentence"),
    ]


# ---------------------------------------------------------------------------
# Enumeration: multi-shot == native == support-reference == subprocess
# ---------------------------------------------------------------------------

NATIVE = {
    "complete": native_aba.complete_extensions,
    "stable": native_aba.stable_extensions,
    "preferred": native_aba.preferred_extensions,
    "grounded": lambda f: (native_aba.grounded_extension(f),),
}


@pytest.mark.parametrize("framework", ALL + RANDOM)
@pytest.mark.parametrize("semantics", ["complete", "stable", "preferred", "grounded"])
def test_multishot_enumeration_matches_native_and_support_reference(framework, semantics) -> None:
    expected = _show(NATIVE[semantics](framework))
    solver = AbaIncrementalSolver(framework)
    if semantics == "complete":
        got = solver.enumerate_complete()
    elif semantics == "stable":
        got = solver.enumerate_stable()
    elif semantics == "preferred":
        got = solver.enumerate_preferred()
    else:
        got = (solver.grounded_extension(),)
    assert _show(got) == expected
    # via the wired backend (simplify on and off)
    on = solve_aba_with_backend(framework, backend="asp", semantics=semantics)
    off = solve_aba_with_backend(framework, backend="asp", semantics=semantics, simplify=False)
    assert on.status == "success" and off.status == "success"
    assert _show(on.extensions) == expected
    assert _show(off.extensions) == expected
    # support-mask reference
    if semantics in {"complete", "stable", "preferred"}:
        assert _show(aba_sat.support_extensions(framework, semantics)) == expected


@pytest.mark.parametrize("framework", ALL + RANDOM[:40])
@pytest.mark.parametrize("semantics", ["complete", "stable", "preferred", "grounded"])
def test_multishot_enumeration_matches_subprocess_clingo(framework, semantics) -> None:
    subprocess = solve_aba_with_backend(
        framework, backend="clingo_subprocess", semantics=semantics, simplify=False
    )
    if subprocess.status != "success":
        pytest.skip(f"subprocess clingo unavailable: {subprocess.metadata.get('reason')}")
    multishot = solve_aba_with_backend(
        framework, backend="asp", semantics=semantics, simplify=False
    )
    assert _show(multishot.extensions) == _show(subprocess.extensions)


def test_preferred_single_extension_uses_limited_multishot_witness(monkeypatch) -> None:
    framework = ALL[0]
    limits: list[int | None] = []
    original = AbaIncrementalSolver.enumerate_preferred

    def spy_enumerate_preferred(self, *, telemetry=None, limit=None):
        limits.append(limit)
        return original(self, telemetry=telemetry, limit=limit)

    monkeypatch.setattr(AbaIncrementalSolver, "enumerate_preferred", spy_enumerate_preferred)

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="preferred",
        task="single-extension",
        simplify=False,
    )

    assert result.status == "success"
    assert result.extensions
    assert limits == [1]


def test_stable_single_extension_avoids_full_multishot_enumeration(monkeypatch) -> None:
    framework = ALL[0]

    def forbidden_enumeration(*args, **kwargs):
        raise AssertionError("single stable witness should not enumerate every stable extension")

    monkeypatch.setattr(AbaIncrementalSolver, "enumerate_stable", forbidden_enumeration)

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="stable",
        task="single-extension",
        simplify=False,
    )

    assert result.status == "success"
    assert result.extensions


def test_multishot_asp_does_not_materialize_support_facts(monkeypatch) -> None:
    framework = ALL[0]

    def forbidden_minimal_supports(*args, **kwargs):
        raise AssertionError("multishot ASP should use lean ABA facts")

    monkeypatch.setattr(aba_asp, "_minimal_supports", forbidden_minimal_supports)

    result = solve_aba_with_backend(
        framework,
        backend="asp",
        semantics="preferred",
        task="single-extension",
        simplify=False,
    )

    assert result.status == "success"
    assert result.extensions
    assert result.metadata["encoding"] == "flat_aba_core_facts"


# ---------------------------------------------------------------------------
# DS-PR (skeptical preferred) -- Algorithm 1
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("framework", ALL + RANDOM)
def test_ds_pr_matches_brute_force(framework) -> None:
    prefs = native_aba.preferred_extensions(framework)
    solver = AbaIncrementalSolver(framework)
    for q in _query_pool(framework):
        expected = all(derives(framework, e, q) for e in prefs) if prefs else True
        answer, counterexample = solver.is_skeptically_accepted_preferred(q)
        assert answer == expected, (framework, q, answer, expected)
        if not answer:
            assert counterexample is not None
            assert not derives(framework, counterexample, q)
            assert any(set(counterexample) == set(e) for e in prefs)
        # via the wired backend (simplify on and off)
        on = solve_aba_with_backend(
            framework, backend="asp", semantics="preferred", task="skeptical", query=q
        )
        off = solve_aba_with_backend(
            framework, backend="asp", semantics="preferred", task="skeptical", query=q, simplify=False
        )
        assert on.answer == expected
        assert off.answer == expected
        # DS-PR routes through Algorithm 1 with simplify on and off.
        assert on.metadata.get("algorithm") == "L21-TPLP-Alg1"
        assert off.metadata.get("algorithm") == "L21-TPLP-Alg1"


@pytest.mark.parametrize("framework", ALL + RANDOM[:40])
def test_ds_pr_matches_subprocess_clingo(framework) -> None:
    for q in _query_pool(framework):
        subprocess = solve_aba_with_backend(
            framework,
            backend="clingo_subprocess",
            semantics="preferred",
            task="skeptical",
            query=q,
            simplify=False,
        )
        if subprocess.status != "success":
            pytest.skip(f"subprocess clingo unavailable: {subprocess.metadata.get('reason')}")
        multishot = solve_aba_with_backend(
            framework, backend="asp", semantics="preferred", task="skeptical", query=q, simplify=False
        )
        assert multishot.answer == subprocess.answer


# ---------------------------------------------------------------------------
# DC (credulous) -- complete and preferred coincide for derivable sentences
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("framework", ALL + RANDOM)
def test_dc_matches_brute_force(framework) -> None:
    complete = native_aba.complete_extensions(framework)
    solver = AbaIncrementalSolver(framework)
    for q in _query_pool(framework):
        expected = any(derives(framework, e, q) for e in complete)
        answer_co, witness_co = solver.is_credulously_accepted_complete(q)
        assert answer_co == expected
        if answer_co:
            assert witness_co is not None
            assert derives(framework, witness_co, q)
        # stable credulous: derivable from some stable set
        stable = native_aba.stable_extensions(framework)
        expected_st = any(derives(framework, e, q) for e in stable)
        answer_st, witness_st = solver.is_credulously_accepted_stable(q)
        assert answer_st == expected_st
        # via the wired backend
        on = solve_aba_with_backend(
            framework, backend="asp", semantics="complete", task="credulous", query=q
        )
        assert on.answer == expected


# ---------------------------------------------------------------------------
# The CEGAR loop actually iterates
# ---------------------------------------------------------------------------

def test_cegar_loop_accumulates_refinement_clauses() -> None:
    # ALL[-1] = the 5-assumption framework where DS-PR(a4) needs >=2 refinement
    # clauses (a counterexample is found only after the inner growth loop adds
    # several constr(out(I)) clauses).
    framework = ALL[-1]
    solver = AbaIncrementalSolver(framework)
    telemetry = IncrementalTelemetry()
    answer, counterexample = solver.is_skeptically_accepted_preferred(lit("a4"), telemetry=telemetry)
    assert answer is False
    assert counterexample is not None
    assert telemetry.refinement_clauses >= 2
    assert telemetry.solver_calls >= 3


def test_cegar_loop_multiple_outer_iterations() -> None:
    # ALL[-2] = the 3-assumption framework where DS-PR(a1) returns YES only after
    # >=2 outer iterations (a maximal-not-deriving complete set gets dominated by
    # a deriving superset, so the loop returns to Line 2).
    framework = ALL[-2]
    solver = AbaIncrementalSolver(framework)
    telemetry = IncrementalTelemetry()
    answer, _ = solver.is_skeptically_accepted_preferred(lit("a1"), telemetry=telemetry)
    prefs = native_aba.preferred_extensions(framework)
    assert answer == all(derives(framework, e, lit("a1")) for e in prefs)
    assert telemetry.outer_iterations >= 2


def test_enumerate_preferred_telemetry_iterates() -> None:
    framework = ALL[3]  # the three-cycle: two preferred sets, several rounds
    solver = AbaIncrementalSolver(framework)
    telemetry = IncrementalTelemetry()
    extensions = solver.enumerate_preferred(telemetry=telemetry)
    assert _show(extensions) == _show(native_aba.preferred_extensions(framework))
    assert telemetry.outer_iterations >= 2
    assert telemetry.refinement_clauses >= 1


def test_incremental_solver_passes_diagnostic_control_args(monkeypatch) -> None:
    framework = battery()[0]
    seen_args = []

    class FakeResult:
        satisfiable = False

    class FakeControl:
        def __init__(self, args):
            seen_args.append(tuple(args))
            self.statistics = {}

        def add(self, *args, **kwargs):
            return None

        def ground(self, *args, **kwargs):
            return None

        def solve(self, *args, **kwargs):
            return FakeResult()

    class FakeClingo:
        Control = FakeControl

    monkeypatch.setattr("argumentation.aba_incremental._load_clingo", lambda: FakeClingo)

    solver = AbaIncrementalSolver(framework, control_args=("--configuration=frumpy",))
    telemetry = IncrementalTelemetry()

    assert solver.find_stable_extension(telemetry=telemetry) is None
    assert seen_args == [("--models=0", "--warn=none", "--configuration=frumpy")]
    assert telemetry.clingo_control_args == (
        "--models=0",
        "--warn=none",
        "--configuration=frumpy",
    )
    assert telemetry.clingo_statistics is None


def test_incremental_solver_collects_sanitized_clingo_statistics(monkeypatch) -> None:
    framework = battery()[0]

    class FakeResult:
        satisfiable = False

    class FakeControl:
        def __init__(self, args):
            self.statistics = {
                "summary": {"times": {"solve": 1.25}},
                "solving": {"solvers": {"choices": 7.0, "conflicts": 3.0, "restarts": 2.0}},
            }

        def add(self, *args, **kwargs):
            return None

        def ground(self, *args, **kwargs):
            return None

        def solve(self, *args, **kwargs):
            return FakeResult()

    class FakeClingo:
        Control = FakeControl

    monkeypatch.setattr("argumentation.aba_incremental._load_clingo", lambda: FakeClingo)

    solver = AbaIncrementalSolver(framework, collect_statistics=True)
    telemetry = IncrementalTelemetry()

    assert solver.find_stable_extension(telemetry=telemetry) is None
    assert telemetry.clingo_control_args == ("--models=0", "--warn=none")
    assert telemetry.clingo_statistics == {
        "summary": {"times": {"solve": 1.25}},
        "solving": {"solvers": {"choices": 7.0, "conflicts": 3.0, "restarts": 2.0}},
    }


def test_incremental_solver_interrupts_solve_at_diagnostic_timeout(monkeypatch) -> None:
    framework = battery()[0]

    class FakeHandle:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def wait(self, timeout):
            assert timeout == 0.25
            return False

        def cancel(self):
            return None

        def get(self):
            class FakeResult:
                satisfiable = False
                interrupted = True

            return FakeResult()

    class FakeControl:
        def __init__(self, args):
            self.statistics = {
                "summary": {"times": {"solve": 0.25}},
                "solving": {"solvers": {"choices": 11.0}},
            }

        def add(self, *args, **kwargs):
            return None

        def ground(self, *args, **kwargs):
            return None

        def solve(self, *args, **kwargs):
            assert kwargs["async_"] is True
            return FakeHandle()

    class FakeClingo:
        Control = FakeControl

    monkeypatch.setattr("argumentation.aba_incremental._load_clingo", lambda: FakeClingo)

    solver = AbaIncrementalSolver(
        framework,
        collect_statistics=True,
        solve_timeout_seconds=0.25,
    )
    telemetry = IncrementalTelemetry()

    with pytest.raises(ClingoSolveTimeout):
        solver.find_stable_extension(telemetry=telemetry)

    assert telemetry.clingo_timeout_seconds == 0.25
    assert telemetry.clingo_interrupted is True
    assert telemetry.clingo_statistics == {
        "summary": {"times": {"solve": 0.25}},
        "solving": {"solvers": {"choices": 11.0}},
    }


def test_incremental_solver_default_does_not_collect_statistics(monkeypatch) -> None:
    framework = battery()[0]

    class FakeResult:
        satisfiable = False

    class FakeControl:
        def __init__(self, args):
            self.statistics = {"summary": {"times": {"solve": 1.25}}}

        def add(self, *args, **kwargs):
            return None

        def ground(self, *args, **kwargs):
            return None

        def solve(self, *args, **kwargs):
            return FakeResult()

    class FakeClingo:
        Control = FakeControl

    monkeypatch.setattr("argumentation.aba_incremental._load_clingo", lambda: FakeClingo)

    solver = AbaIncrementalSolver(framework)
    telemetry = IncrementalTelemetry()

    assert solver.find_stable_extension(telemetry=telemetry) is None
    assert telemetry.clingo_control_args == ("--models=0", "--warn=none")
    assert telemetry.clingo_statistics is None


# ---------------------------------------------------------------------------
# Resource file is Listing 1
# ---------------------------------------------------------------------------

def test_com_module_resource_is_listing_one() -> None:
    from importlib import resources

    text = resources.files("argumentation.encodings").joinpath("aba_com_incremental.lp").read_text(
        encoding="utf-8"
    )
    for needle in (
        "in(X) :- assumption(X), not out(X).",
        "out(X) :- assumption(X), not in(X).",
        "supported(X) :- assumption(X), in(X).",
        "supported(X) :- head(R,X), triggered_by_in(R).",
        "triggered_by_in(R) :- head(R,_), supported(X) : body(R,X).",
        ":- in(X), contrary(X,Y), supported(Y).",
        "defeated(X) :- supported(Y), contrary(X,Y).",
        "derived_from_undefeated(X) :- assumption(X), not defeated(X).",
        "derived_from_undefeated(X) :- head(R,X), triggered_by_undefeated(R).",
        "triggered_by_undefeated(R) :- head(R,_), derived_from_undefeated(X) : body(R,X).",
        "attacked_by_undefeated(X) :- contrary(X,Y), derived_from_undefeated(Y).",
        ":- in(X), attacked_by_undefeated(X).",
        ":- out(X), not attacked_by_undefeated(X).",
    ):
        assert needle in text


# ---------------------------------------------------------------------------
# Wave C4 regression: fact-contrary frameworks (the empty-attacker-set bug)
# ---------------------------------------------------------------------------

def _fact_contrary_frameworks() -> list[ABAFramework]:
    """Frameworks where some assumption's contrary is derivable from no premises.

    These are the analyst's Wave C3 repro family: an assumption attacked by the
    empty set must be out of every grounded/complete/admissible set.
    """
    a0, a1 = lit("a0"), lit("a1")
    p0, p1 = lit("p0"), lit("p1")
    out: list[ABAFramework] = []
    # The exact analyst repro: a0, contrary a0->p0, rule  p0 :- .
    out.append(_framework(assumptions={a0}, contrary={a0: p0}, rules=[Rule((), p0, "strict")]))
    # Two assumptions, one with a fact contrary, one free.
    out.append(
        _framework(
            assumptions={a0, a1},
            contrary={a0: p0, a1: p1},
            rules=[Rule((), p0, "strict")],
        )
    )
    # Fact contrary reached through a derived sentence.
    s0 = lit("s0")
    out.append(
        _framework(
            assumptions={a0},
            contrary={a0: p0},
            rules=[Rule((), s0, "strict"), Rule((s0,), p0, "strict")],
        )
    )
    return out


def _grounded_reference(framework: ABAFramework) -> AssumptionSet:
    """The grounded set = the unique least complete extension (flat ABA)."""
    complete = aba_sat.support_extensions(framework, "complete")
    assert complete, "flat ABA always has at least one complete extension"
    least = min(complete, key=len)
    # Sanity: it is contained in every complete extension.
    for ext in complete:
        assert least <= ext, (least, ext)
    return least


@pytest.mark.parametrize("framework", _fact_contrary_frameworks())
def test_grounded_fact_contrary_is_conflict_free(framework: ABAFramework) -> None:
    reference = _grounded_reference(framework)
    # Native primitive (aba._defends must consider the empty attacker set).
    native = native_aba.grounded_extension(framework)
    assert native_aba.conflict_free(framework, native), native
    assert _show([native]) == _show([reference])
    # Multi-shot solver path -- the C2b regression site.
    inc = AbaIncrementalSolver(framework)
    assert _show([inc.grounded_extension()]) == _show([reference])
    assert native_aba.conflict_free(framework, inc.grounded_extension())


@pytest.mark.parametrize("framework", _fact_contrary_frameworks())
@pytest.mark.parametrize("backend", ["asp", "clingo"])
def test_solve_aba_grounded_fact_contrary_via_backend(framework: ABAFramework, backend: str) -> None:
    pytest.importorskip("clingo")
    reference = _grounded_reference(framework)
    result = solve_aba_with_backend(
        framework, backend=backend, semantics="grounded", simplify=False
    ).extensions
    assert _show(result) == _show([reference])
    for ext in result:
        assert native_aba.conflict_free(framework, ext), ext
