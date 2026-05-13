"""Tests for the flat-ABA preprocessing layer (Wave C2a).

Structural invariants of ``simplify_aba`` plus oracle-equivalence: solving on the
simplified residual and lifting back must equal both the brute-force ``aba.py``
reference and the unsimplified SAT solver, for every gated semantics, on a hand
battery plus random flat ABA instances, for enumeration and acceptance.
"""

from __future__ import annotations

import random

import pytest

from argumentation import aba as native_aba
from argumentation import aba_sat
from argumentation.aba import ABAFramework, ABAPlusFramework
from argumentation.aba_preprocessing import (
    GROUNDED_REDUCT_ABA_SEMANTICS,
    grounded_assumption_set_via_supports,
    simplify_aba,
)
from argumentation.aba_asp import solve_aba_with_backend
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


# ---------------------------------------------------------------------------
# Hand battery
# ---------------------------------------------------------------------------

def battery() -> list[ABAFramework]:
    a, b, c, d = (lit(x) for x in ("a", "b", "c", "d"))
    ca, cb, cc, cd = (lit(x) for x in ("ca", "cb", "cc", "cd"))
    p, q, r = (lit(x) for x in ("p", "q", "r"))
    frameworks: list[ABAFramework] = []

    # 1. Trivial: no rules at all, contraries never derivable -> grounded = all
    #    assumptions, fixed_out empty. (Actually fixed_in == all assumptions here,
    #    so it is *not* trivial; the residual is empty.)
    frameworks.append(
        _framework(assumptions={a, b}, contrary={a: ca, b: cb}, rules=[])
    )

    # 2. Empty grounded set: a and b attack each other -> grounded = {} -> trivial.
    frameworks.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), cb, "strict"), Rule((b,), ca, "strict")],
        )
    )

    # 3. Non-trivial well-founded set + derivable contrary: a is unattacked, and a
    #    derives cb (so b is fixed_out).
    frameworks.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), cb, "strict")],
        )
    )

    # 4. Self-attacking assumption b (b derives cb) with unattacked a.
    frameworks.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((b,), cb, "strict")],
        )
    )

    # 5. Chain: a unattacked, a -> p -> cb, so b fixed_out via a 2-step derivation.
    frameworks.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), p, "strict"), Rule((p,), cb, "strict")],
        )
    )

    # 6. Three assumptions, layered: a unattacked, a derives cb; c attacks a? no --
    #    c derives ca only if c selected. b is out, c stays.
    frameworks.append(
        _framework(
            assumptions={a, b, c},
            contrary={a: ca, b: cb, c: cc},
            rules=[Rule((a,), cb, "strict"), Rule((c,), ca, "strict")],
        )
    )

    # 7. Flat attack-only mutual + a dominator: d unattacked, d -> ca and d -> cb;
    #    c attacks d (c -> cd) but c is then attacked back? no rule. So d, then
    #    a,b out, c stays (c attacks d though -> c not conflict free? c->cd, cd is
    #    contrary of d not c). Keep it; the oracle decides.
    frameworks.append(
        _framework(
            assumptions={a, b, c, d},
            contrary={a: ca, b: cb, c: cc, d: cd},
            rules=[Rule((d,), ca, "strict"), Rule((d,), cb, "strict"), Rule((c,), cd, "strict")],
        )
    )

    # 8. Pure flat attack chain a1 -> a2 -> a3 (attack), encoded with contraries.
    a1, a2, a3 = (lit(x) for x in ("x1", "x2", "x3"))
    c1, c2, c3 = (lit(x) for x in ("y1", "y2", "y3"))
    frameworks.append(
        _framework(
            assumptions={a1, a2, a3},
            contrary={a1: c1, a2: c2, a3: c3},
            rules=[Rule((a1,), c2, "strict"), Rule((a2,), c3, "strict")],
        )
    )

    # 9. With irrelevant rule literals and a derived sentence not a contrary.
    frameworks.append(
        _framework(
            assumptions={a, b},
            contrary={a: ca, b: cb},
            rules=[Rule((a,), q, "strict"), Rule((q,), r, "strict"), Rule((a,), cb, "strict")],
            extra_language=[r],
        )
    )

    # 10. Conjunctive rule body: a and b together derive cc; neither attacked.
    frameworks.append(
        _framework(
            assumptions={a, b, c},
            contrary={a: ca, b: cb, c: cc},
            rules=[Rule((a, b), cc, "strict")],
        )
    )

    return frameworks


def random_framework(rng: random.Random) -> ABAFramework:
    n = rng.randint(1, 5)
    assumptions = [lit(f"a{i}") for i in range(n)]
    contrary = {assumptions[i]: lit(f"c{i}") for i in range(n)}
    aux = [lit(f"p{i}") for i in range(rng.randint(0, 2))]
    heads = list(contrary.values()) + aux
    candidate_body = assumptions + aux
    rules: list[Rule] = []
    for _ in range(rng.randint(0, n + 3)):
        body_size = rng.randint(1, min(2, len(candidate_body)))
        body = tuple(rng.sample(candidate_body, body_size))
        head = rng.choice(heads)
        if head in body:
            continue
        rules.append(Rule(body, head, "strict"))
    return _framework(
        assumptions=set(assumptions), contrary=contrary, rules=rules, extra_language=aux
    )


ALL = battery()


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("framework", ALL)
def test_simplify_structural_invariants(framework: ABAFramework) -> None:
    s = simplify_aba(framework, semantics="complete")
    assert s.fixed_in == native_aba.grounded_extension(framework)
    assert s.fixed_in == grounded_assumption_set_via_supports(framework)
    assert s.fixed_in.isdisjoint(s.fixed_out)
    survivors = s.residual.assumptions
    assert survivors.isdisjoint(s.fixed_in)
    assert survivors.isdisjoint(s.fixed_out)
    assert s.fixed_in | s.fixed_out | survivors == framework.assumptions
    assert s.lift(frozenset()) == s.fixed_in
    assert s.lift_all([frozenset(), frozenset(), survivors]) == (
        [s.fixed_in] if not survivors else [s.fixed_in, survivors | s.fixed_in]
    )
    if s.is_trivial:
        assert s.residual is framework


def test_grounded_via_supports_matches_native_on_random() -> None:
    rng = random.Random(20260512)
    for _ in range(200):
        framework = random_framework(rng)
        assert grounded_assumption_set_via_supports(framework) == native_aba.grounded_extension(
            framework
        )


def test_aba_plus_is_no_op() -> None:
    a, b = lit("a"), lit("b")
    ca, cb = lit("ca"), lit("cb")
    base = _framework(
        assumptions={a, b}, contrary={a: ca, b: cb}, rules=[Rule((a,), cb, "strict")]
    )
    plus = ABAPlusFramework(framework=base, preference_order=frozenset({(b, a)}))
    s = simplify_aba(plus, semantics="preferred")
    assert s.is_trivial
    assert s.residual is base
    assert s.fixed_in == frozenset()
    assert s.fixed_out == frozenset()


def test_ungated_semantics_no_op() -> None:
    a, b = lit("a"), lit("b")
    ca, cb = lit("ca"), lit("cb")
    framework = _framework(
        assumptions={a, b}, contrary={a: ca, b: cb}, rules=[Rule((a,), cb, "strict")]
    )
    s = simplify_aba(framework, semantics="admissible")
    assert s.is_trivial


def test_constant_is_frozenset() -> None:
    assert GROUNDED_REDUCT_ABA_SEMANTICS == frozenset(
        {"grounded", "complete", "preferred", "stable", "ideal"}
    )


# ---------------------------------------------------------------------------
# Oracle equivalence -- enumeration
# ---------------------------------------------------------------------------

def _native_extensions(framework: ABAFramework, semantics: str):
    fn = {
        "grounded": lambda f: (native_aba.grounded_extension(f),),
        "complete": native_aba.complete_extensions,
        "preferred": native_aba.preferred_extensions,
        "stable": native_aba.stable_extensions,
        "ideal": lambda f: (native_aba.ideal_extension(f),),
    }[semantics]
    return frozenset(frozenset(e) for e in fn(framework))


def _residual_extensions_via_simplify(framework: ABAFramework, semantics: str):
    s = simplify_aba(framework, semantics=semantics)
    residual = s.residual
    if semantics == "grounded":
        residual_exts = (native_aba.grounded_extension(residual),)
    elif semantics == "ideal":
        residual_exts = (native_aba.ideal_extension(residual),)
    elif semantics in {"complete", "preferred"}:
        residual_exts = aba_sat.support_extensions(residual, semantics)
    elif semantics == "stable":
        residual_exts = aba_sat.support_extensions(residual, "stable")
    else:
        raise AssertionError(semantics)
    return frozenset(s.lift_all(residual_exts))


def _unsimplified_extensions(framework: ABAFramework, semantics: str):
    if semantics == "grounded":
        return frozenset({frozenset(native_aba.grounded_extension(framework))})
    if semantics == "ideal":
        return frozenset({frozenset(native_aba.ideal_extension(framework))})
    return frozenset(frozenset(e) for e in aba_sat.support_extensions(framework, semantics))


@pytest.mark.parametrize("semantics", ["grounded", "complete", "preferred", "stable", "ideal"])
@pytest.mark.parametrize("framework", ALL)
def test_oracle_equivalence_enumeration_battery(framework: ABAFramework, semantics: str) -> None:
    native = _native_extensions(framework, semantics)
    assert _residual_extensions_via_simplify(framework, semantics) == native
    assert _unsimplified_extensions(framework, semantics) == native


@pytest.mark.parametrize("semantics", ["grounded", "complete", "preferred", "stable"])
@pytest.mark.parametrize("framework", ALL)
def test_solve_aba_with_backend_simplify_matches_native(
    framework: ABAFramework, semantics: str
) -> None:
    on = solve_aba_with_backend(framework, backend="support_reference", semantics=semantics)
    off = solve_aba_with_backend(
        framework, backend="support_reference", semantics=semantics, simplify=False
    )
    assert on.status == "success"
    assert frozenset(frozenset(e) for e in on.extensions) == _native_extensions(framework, semantics)
    assert frozenset(frozenset(e) for e in off.extensions) == _native_extensions(framework, semantics)


def test_solve_aba_with_backend_acceptance_simplify() -> None:
    for framework in ALL:
        for query in _query_pool(framework):
            for semantics in ("complete", "stable"):
                for task in ("credulous", "skeptical"):
                    on = solve_aba_with_backend(
                        framework,
                        backend="support_reference",
                        semantics=semantics,
                        task=task,
                        query=query,
                    )
                    off = solve_aba_with_backend(
                        framework,
                        backend="support_reference",
                        semantics=semantics,
                        task=task,
                        query=query,
                        simplify=False,
                    )
                    assert on.answer == off.answer, (semantics, task, query, framework)


def test_oracle_equivalence_enumeration_random() -> None:
    rng = random.Random(424242)
    for _ in range(120):
        framework = random_framework(rng)
        for semantics in ("grounded", "complete", "preferred", "stable", "ideal"):
            native = _native_extensions(framework, semantics)
            assert _residual_extensions_via_simplify(framework, semantics) == native, (
                semantics,
                framework,
            )
            assert _unsimplified_extensions(framework, semantics) == native


# ---------------------------------------------------------------------------
# Oracle equivalence -- acceptance (DC / DS), via the wired Z3/SAT entry points
# ---------------------------------------------------------------------------

def _native_dc(framework: ABAFramework, semantics: str, query: Literal) -> bool:
    exts = _native_extensions(framework, semantics)
    return any(native_aba.derives(framework, e, query) for e in exts)


def _native_ds(framework: ABAFramework, semantics: str, query: Literal) -> bool:
    exts = _native_extensions(framework, semantics)
    return all(native_aba.derives(framework, e, query) for e in exts)


def _query_pool(framework: ABAFramework) -> list[Literal]:
    pool = list(framework.assumptions)
    for assumption in framework.assumptions:
        pool.append(framework.contrary[assumption])
    pool.extend(framework.language)
    seen: list[Literal] = []
    for q in pool:
        if q not in seen:
            seen.append(q)
    return seen


@pytest.mark.parametrize("framework", ALL)
def test_oracle_equivalence_acceptance_battery(framework: ABAFramework) -> None:
    for query in _query_pool(framework):
        for semantics in ("complete", "preferred"):
            dc_simpl, _ = aba_sat.sat_support_acceptance(
                framework, semantics=semantics, task="credulous", query=query
            )
            dc_off, _ = aba_sat.sat_support_acceptance(
                framework, semantics=semantics, task="credulous", query=query, simplify=False
            )
            assert dc_simpl == dc_off == _native_dc(framework, semantics, query), (
                semantics,
                query,
            )
            ds_simpl, _ = aba_sat.sat_support_acceptance(
                framework, semantics=semantics, task="skeptical", query=query
            )
            ds_off, _ = aba_sat.sat_support_acceptance(
                framework, semantics=semantics, task="skeptical", query=query, simplify=False
            )
            assert ds_simpl == ds_off == _native_ds(framework, semantics, query), (
                semantics,
                query,
            )
        # stable
        dc_simpl, _ = aba_sat.sat_stable_acceptance(framework, task="credulous", query=query)
        dc_off, _ = aba_sat.sat_stable_acceptance(
            framework, task="credulous", query=query, simplify=False
        )
        assert dc_simpl == dc_off == _native_dc(framework, "stable", query), query
        ds_simpl, _ = aba_sat.sat_stable_acceptance(framework, task="skeptical", query=query)
        ds_off, _ = aba_sat.sat_stable_acceptance(
            framework, task="skeptical", query=query, simplify=False
        )
        assert ds_simpl == ds_off == _native_ds(framework, "stable", query), query


def test_oracle_equivalence_acceptance_random() -> None:
    rng = random.Random(987654)
    for _ in range(60):
        framework = random_framework(rng)
        for query in _query_pool(framework):
            for semantics in ("complete", "preferred"):
                got, _ = aba_sat.sat_support_acceptance(
                    framework, semantics=semantics, task="credulous", query=query
                )
                assert got == _native_dc(framework, semantics, query), (semantics, query, framework)
                got, _ = aba_sat.sat_support_acceptance(
                    framework, semantics=semantics, task="skeptical", query=query
                )
                assert got == _native_ds(framework, semantics, query), (semantics, query, framework)
            got, _ = aba_sat.sat_stable_acceptance(framework, task="credulous", query=query)
            assert got == _native_dc(framework, "stable", query), (query, framework)
            got, _ = aba_sat.sat_stable_acceptance(framework, task="skeptical", query=query)
            assert got == _native_ds(framework, "stable", query), (query, framework)


# ---------------------------------------------------------------------------
# Single-extension membership (the wired finders)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("framework", ALL)
def test_single_extension_finders_are_valid(framework: ABAFramework) -> None:
    complete_ref = _native_extensions(framework, "complete")
    preferred_ref = _native_extensions(framework, "preferred")
    stable_ref = _native_extensions(framework, "stable")
    assert aba_sat.sat_support_extension(framework, "complete") in complete_ref
    assert aba_sat.sat_support_extension(framework, "preferred") in preferred_ref
    stable_witness = aba_sat.sat_stable_extension(framework)
    if stable_ref:
        assert stable_witness in stable_ref
    else:
        assert stable_witness is None


def test_single_extension_random() -> None:
    rng = random.Random(112233)
    for _ in range(120):
        framework = random_framework(rng)
        assert aba_sat.sat_support_extension(framework, "complete") in _native_extensions(
            framework, "complete"
        )
        pref = aba_sat.sat_support_extension(framework, "preferred")
        assert pref in _native_extensions(framework, "preferred"), framework
        stable_ref = _native_extensions(framework, "stable")
        sw = aba_sat.sat_stable_extension(framework)
        if stable_ref:
            assert sw in stable_ref
        else:
            assert sw is None


# ---------------------------------------------------------------------------
# §2.3a -- the refactored preferred CEGAR matches the admissible CEGAR helper
# ---------------------------------------------------------------------------

def test_preferred_cegar_matches_admissible_growth() -> None:
    rng = random.Random(55667788)
    for _ in range(80):
        framework = random_framework(rng)
        cegar = aba_sat._sat_preferred_cegar_extension(framework)
        preferred_ref = _native_extensions(framework, "preferred")
        assert cegar in preferred_ref, framework
        # The reused-solver class and the one-shot helper must each return an
        # admissible set of ``framework`` -- but NOT necessarily the *same* one:
        # admissible sets are not unique and Z3's model choice is not stable
        # across process state, so strict set-equality is not a sound invariant.
        reused = aba_sat._AdmissibleCegarSolver(framework).solve()
        oneshot = aba_sat._sat_admissible_cegar_extension(framework)
        # Both must succeed: the empty set is always admissible.
        assert reused is not None and oneshot is not None, framework
        assert native_aba.admissible(framework, reused), (framework, reused)
        assert native_aba.admissible(framework, oneshot), (framework, oneshot)
