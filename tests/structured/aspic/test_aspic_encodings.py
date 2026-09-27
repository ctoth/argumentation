from __future__ import annotations

import re
from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from argumentation.structured.aspic.aspic import (
    ArgumentationSystem,
    ContrarinessFn,
    GroundAtom,
    KnowledgeBase,
    Literal,
    PreferenceConfig,
    Rule,
    build_abstract_framework,
    conc,
)
from argumentation.structured.aspic.aspic_encoding import (
    ASPICQueryStatus,
    encode_aspic_theory,
    solve_aspic_grounded,
    solve_aspic_with_backend,
)
from argumentation.core.dung import grounded_extension


ASP_CONSTANT_RE = re.compile(r"^[a-z][A-Za-z0-9_]*$")


def test_aspic_encoding_assigns_deterministic_facts_and_signature() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    not_q = q.contrary
    strict = Rule((p,), q, "strict")
    defeasible = Rule((q,), not_q, "defeasible", "d_not_q")
    system = ArgumentationSystem(
        language=frozenset({not_q, q, p}),
        contrariness=ContrarinessFn(contradictories=frozenset({(q, not_q)})),
        strict_rules=frozenset({strict}),
        defeasible_rules=frozenset({defeasible}),
    )
    kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset({q}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    first = encode_aspic_theory(system, kb, pref)
    second = encode_aspic_theory(system, kb, pref)

    assert first.facts == second.facts
    assert first.signature == second.signature
    assert first.facts == tuple(sorted(first.facts))
    assert "axiom(p)." in first.facts
    assert "premise(q)." in first.facts
    assert "s_head(s_0,q)." in first.facts
    assert "s_body(s_0,p)." in first.facts
    assert "d_head(d_not_q,n_q)." in first.facts
    assert "d_body(d_not_q,q)." in first.facts
    assert "contrary(q,n_q)." in first.facts


def test_aspic_encoding_signature_is_stable_under_input_set_ordering() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    d1 = Rule((p,), q, "defeasible", "d1")
    d2 = Rule((q,), r, "defeasible", "d2")
    first_system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d1, d2}),
    )
    second_system = ArgumentationSystem(
        language=frozenset({r, q, p}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({d2, d1}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({q, p}))
    pref = PreferenceConfig(
        rule_order=frozenset({(d1, d2)}),
        premise_order=frozenset(),
        comparison="democratic",
        link="last",
    )

    first = encode_aspic_theory(first_system, kb, pref)
    second = encode_aspic_theory(second_system, kb, pref)

    assert first.signature == second.signature
    assert first.facts == second.facts
    assert "preferred(d2,d1)." in first.facts
    assert first.metadata["comparison"] == "democratic"
    assert first.metadata["link"] == "last"


def test_solve_aspic_grounded_returns_accepted_conclusions() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    rule = Rule((p,), q, "defeasible", "d_q")
    system = ArgumentationSystem(
        language=frozenset({p, q}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({rule}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    result = solve_aspic_grounded(system, kb, pref)

    assert result.status is ASPICQueryStatus.SUCCESS
    assert result.semantics == "grounded"
    assert result.accepted_conclusions == frozenset({p, q})
    assert result.backend == "materialized_reference"


def test_solve_aspic_grounded_matches_materialized_pipeline() -> None:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    not_q = q.contrary
    rule_q = Rule((p,), q, "defeasible", "d_q")
    system = ArgumentationSystem(
        language=frozenset({p, q, not_q}),
        contrariness=ContrarinessFn(contradictories=frozenset({(q, not_q)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({rule_q}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p, not_q}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    projection = build_abstract_framework(system, kb, pref)
    grounded_ids = grounded_extension(projection.framework)
    expected = frozenset(
        conc(projection.id_to_argument[arg_id]) for arg_id in grounded_ids
    )

    result = solve_aspic_grounded(system, kb, pref)

    assert result.accepted_conclusions == expected
    assert result.accepted_argument_ids == grounded_ids


def test_optional_aspic_backend_absence_is_typed() -> None:
    p = Literal(GroundAtom("p"))
    system = ArgumentationSystem(
        language=frozenset({p}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    result = solve_aspic_with_backend(system, kb, pref, backend="missing-test-backend")

    assert result.status is ASPICQueryStatus.UNAVAILABLE_BACKEND
    assert result.backend == "missing-test-backend"
    assert result.accepted_argument_ids == frozenset()
    assert result.metadata["reason"] == "backend is not installed or registered"


def test_clingo_backend_invokes_solver_and_parses_grounded_answer_set(
    monkeypatch,
) -> None:
    system, kb, pref = simple_aspic_theory()
    expected = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="asp",
        semantics="grounded",
    )
    accepted_ids = " ".join(
        f"accepted_arg({arg_id})" for arg_id in expected.extensions[0]
    )
    accepted_lits = " ".join(
        f"accepted_lit({literal_id})"
        for literal_id, literal in expected.encoding.literal_by_id.items()
        if literal in expected.accepted_conclusions
    )
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert command[0] == "fake-clingo"
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        return SimpleNamespace(
            returncode=0,
            stdout=f"Answer: 1\n{accepted_ids} {accepted_lits}\nSATISFIABLE\n",
            stderr="",
        )

    monkeypatch.setattr("argumentation.solver_adapters.clingo.subprocess.run", fake_run)

    result = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="clingo",
        semantics="grounded",
        binary="fake-clingo",
        timeout_seconds=5.0,
    )

    assert result.status is ASPICQueryStatus.SUCCESS
    assert result.backend == "clingo"
    assert result.accepted_conclusions == frozenset(
        {Literal(GroundAtom("p")), Literal(GroundAtom("q"))}
    )
    assert result.accepted_argument_ids == expected.extensions[0]
    assert calls


def test_clingo_backend_missing_binary_is_typed(monkeypatch) -> None:
    system, kb, pref = simple_aspic_theory()
    calls = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.shutil.which",
        lambda binary: None,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.subprocess.run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="clingo",
        semantics="grounded",
        binary="missing-clingo",
    )

    assert result.status is ASPICQueryStatus.UNAVAILABLE_BACKEND
    assert result.backend == "clingo"
    assert result.metadata["reason"] == "binary not found on PATH"
    assert calls == []


def test_clingo_backend_process_failure_is_backend_error(monkeypatch) -> None:
    system, kb, pref = simple_aspic_theory()

    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2,
            stdout="solver stdout",
            stderr="solver stderr",
        ),
    )

    result = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="clingo",
        semantics="grounded",
        binary="fake-clingo",
    )

    assert result.status is ASPICQueryStatus.BACKEND_ERROR
    assert result.metadata["stdout"] == "solver stdout"
    assert result.metadata["stderr"] == "solver stderr"


def test_clingo_backend_malformed_answer_set_is_protocol_error(monkeypatch) -> None:
    system, kb, pref = simple_aspic_theory()

    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="Answer: 1\naccepted_arg(unknown)\nSATISFIABLE\n",
            stderr="protocol stderr",
        ),
    )

    result = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="clingo",
        semantics="grounded",
        binary="fake-clingo",
    )

    assert result.status is ASPICQueryStatus.PROTOCOL_ERROR
    assert result.metadata["reason"] == "accepted argument id is not in the encoding"
    assert (
        result.metadata["stdout"] == "Answer: 1\naccepted_arg(unknown)\nSATISFIABLE\n"
    )
    assert result.metadata["stderr"] == "protocol stderr"


def test_clingo_backend_missing_binary_for_stable_is_typed(
    monkeypatch,
) -> None:
    system, kb, pref = simple_aspic_theory()
    calls = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.clingo.subprocess.run",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="clingo",
        semantics="stable",
        binary="fake-clingo",
    )

    assert result.status is ASPICQueryStatus.UNAVAILABLE_BACKEND
    assert result.metadata["reason"] == "binary not found on PATH"
    assert calls == []


@st.composite
def simple_aspic_theories(draw):
    size = draw(st.integers(min_value=1, max_value=4))
    literals = [Literal(GroundAtom(f"p{index}")) for index in range(size)]
    rule_count = draw(st.integers(min_value=0, max_value=max(0, size - 1)))
    rules = frozenset(
        Rule((literals[index],), literals[index + 1], "defeasible", f"d_{index}")
        for index in range(rule_count)
    )
    system = ArgumentationSystem(
        language=frozenset(literals),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=rules,
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({literals[0]}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )
    return system, kb, pref


@given(simple_aspic_theories())
@settings(deadline=10000, max_examples=25)
def test_clingo_grounded_success_matches_reference_on_generated_simple_theories(
    theory,
) -> None:
    system, kb, pref = theory
    expected = solve_aspic_with_backend(
        system,
        kb,
        pref,
        backend="asp",
        semantics="grounded",
    )
    accepted_ids = " ".join(
        f"accepted_arg({arg_id})" for arg_id in expected.extensions[0]
    )
    accepted_lits = " ".join(
        f"accepted_lit({literal_id})"
        for literal_id, literal in expected.encoding.literal_by_id.items()
        if literal in expected.accepted_conclusions
    )

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.clingo.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.clingo.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout=f"Answer: 1\n{accepted_ids} {accepted_lits}\nSATISFIABLE\n",
                stderr="",
            ),
        )

        result = solve_aspic_with_backend(
            system,
            kb,
            pref,
            backend="clingo",
            semantics="grounded",
            binary="fake-clingo",
        )

    assert result.status is ASPICQueryStatus.SUCCESS
    assert result.accepted_conclusions == expected.accepted_conclusions


def test_ws_o_arg_aspic_encoding_sanitises_literal_ids_for_asp() -> None:
    """Bug 2: encoded literal identifiers must be valid ASP constants."""
    p = Literal(GroundAtom("P", (1, 2)))
    not_p = p.contrary
    system = ArgumentationSystem(
        language=frozenset({p, not_p}),
        contrariness=ContrarinessFn(contradictories=frozenset({(p, not_p)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset(),
    )
    kb = KnowledgeBase(axioms=frozenset({not_p}), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    encoding = encode_aspic_theory(system, kb, pref)
    ids = {
        fact.removesuffix(").").split("(", 1)[1]
        for fact in encoding.facts
        if fact.startswith(("axiom(", "premise("))
    }

    assert ids
    assert all(ASP_CONSTANT_RE.fullmatch(identifier) for identifier in ids)
    assert encoding.literal_by_id
    assert set(encoding.literal_by_id) >= ids
    assert not any(
        "~" in fact or "(" in fact.split("(", 1)[1] for fact in encoding.facts
    )


def test_ws_o_arg_aspic_encoding_rejects_duplicate_defeasible_rule_names() -> None:
    """Bug 3: duplicate defeasible rule names must fail at encode time."""
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    first = Rule((p,), q, "defeasible", "dup")
    second = Rule((p,), r, "defeasible", "dup")
    system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({first, second}),
    )
    kb = KnowledgeBase(axioms=frozenset({p}), premises=frozenset())
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )

    with pytest.raises(ValueError, match="duplicate defeasible rule name: 'dup'"):
        encode_aspic_theory(system, kb, pref)


def simple_aspic_theory():
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    rule = Rule((p,), q, "defeasible", "d_q")
    system = ArgumentationSystem(
        language=frozenset({p, q}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({rule}),
    )
    kb = KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))
    pref = PreferenceConfig(
        rule_order=frozenset(),
        premise_order=frozenset(),
        comparison="elitist",
        link="last",
    )
    return system, kb, pref


NO_PREFERENCES = PreferenceConfig(
    rule_order=frozenset(),
    premise_order=frozenset(),
    comparison="elitist",
    link="last",
)


def _assert_asp_facts_parse(facts: tuple[str, ...]) -> None:
    clingo = pytest.importorskip("clingo")
    clingo.Control().add("base", [], "\n".join(facts))


def _assert_asp_backend_matches_reference(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
) -> frozenset[Literal]:
    pytest.importorskip("clingo")
    reference = solve_aspic_with_backend(
        system, kb, NO_PREFERENCES, backend="materialized_reference"
    )
    asp = solve_aspic_with_backend(system, kb, NO_PREFERENCES, backend="asp")

    assert asp.status is ASPICQueryStatus.SUCCESS, asp.metadata
    assert asp.accepted_conclusions == reference.accepted_conclusions
    return asp.accepted_conclusions


def _undercut_theory(rule_name: str) -> tuple[ArgumentationSystem, KnowledgeBase]:
    p = Literal(GroundAtom("p"))
    name = Literal(GroundAtom(rule_name))
    undercutter = Literal(GroundAtom("u"))
    system = ArgumentationSystem(
        language=frozenset({p, name, undercutter}),
        contrariness=ContrarinessFn(frozenset(), frozenset({(undercutter, name)})),
        strict_rules=frozenset(),
        defeasible_rules=frozenset({Rule((), p, "defeasible", rule_name)}),
    )
    return system, KnowledgeBase(axioms=frozenset({undercutter}), premises=frozenset())


def test_aspic_encoding_emits_valid_asp_for_arbitrary_rule_names() -> None:
    """Issue #52: rule names are encoded as ASP constants, not raw text.

    Lehtonen et al. 2020 encode each defeasible rule through its name
    ``n(r)``, a literal of L, so undercutting targets the same identifier
    as the rule. A legal name such as ``Rule 1`` must still produce parseable
    facts and the undercut must still land.
    """
    system, kb = _undercut_theory("Rule 1")

    encoding = encode_aspic_theory(system, kb, NO_PREFERENCES)

    _assert_asp_facts_parse(encoding.facts)
    assert Literal(GroundAtom("p")) not in _assert_asp_backend_matches_reference(
        system, kb
    )


def test_aspic_encoding_keeps_asp_safe_rule_names() -> None:
    """Issue #52 control: an already ASP-safe name is emitted unchanged."""
    system, kb = _undercut_theory("r1")

    encoding = encode_aspic_theory(system, kb, NO_PREFERENCES)

    assert "d_head(r1,p)." in encoding.facts
    _assert_asp_facts_parse(encoding.facts)
    _assert_asp_backend_matches_reference(system, kb)


def _repeated_antecedent_theory(
    antecedents: tuple[Literal, ...],
) -> tuple[ArgumentationSystem, KnowledgeBase]:
    p = Literal(GroundAtom("p"))
    q = Literal(GroundAtom("q"))
    r = Literal(GroundAtom("r"))
    system = ArgumentationSystem(
        language=frozenset({p, q, r}),
        contrariness=ContrarinessFn(frozenset()),
        strict_rules=frozenset({Rule(antecedents, q, "strict")}),
        defeasible_rules=frozenset({Rule(antecedents, r, "defeasible", "dr")}),
    )
    return system, KnowledgeBase(axioms=frozenset(), premises=frozenset({p}))


def test_source_asp_facts_count_distinct_rule_antecedents() -> None:
    """Issue #64: a body count must match the set of emitted body facts.

    The rule body is the set of antecedents that must be derived
    (Lehtonen et al. 2020, AT(T) body facts), so ``p, p -> q`` fires on
    ``p`` exactly as the materialized reference does.
    """
    from argumentation.structured.aspic.aspic_encoding import _source_aspic_facts

    p = Literal(GroundAtom("p"))
    system, kb = _repeated_antecedent_theory((p, p))
    encoding = encode_aspic_theory(system, kb, NO_PREFERENCES)

    facts, _element_ids = _source_aspic_facts(system, kb, NO_PREFERENCES, encoding)

    assert "s_body_count(s_0,1)." in facts
    assert "d_body_count(dr,1)." in facts
    assert _assert_asp_backend_matches_reference(system, kb) >= {
        Literal(GroundAtom("q")),
        Literal(GroundAtom("r")),
    }


def test_source_asp_facts_count_single_rule_antecedent() -> None:
    """Issue #64 control: an ordinary one-antecedent body."""
    system, kb = _repeated_antecedent_theory((Literal(GroundAtom("p")),))

    _assert_asp_backend_matches_reference(system, kb)


def _assert_asp_semantics_match_reference(
    system: ArgumentationSystem,
    kb: KnowledgeBase,
    semantics: str,
) -> None:
    pytest.importorskip("clingo")
    reference = solve_aspic_with_backend(
        system, kb, NO_PREFERENCES, backend="materialized_reference", semantics=semantics
    )
    asp = solve_aspic_with_backend(
        system, kb, NO_PREFERENCES, backend="asp", semantics=semantics
    )

    assert asp.status is ASPICQueryStatus.SUCCESS, asp.metadata
    assert set(asp.extension_conclusions) == set(reference.extension_conclusions)


def _rebutting_defeasible_facts(
    heads: tuple[Literal, ...],
) -> tuple[ArgumentationSystem, KnowledgeBase]:
    atoms = frozenset(Literal(head.atom) for head in heads)
    return (
        ArgumentationSystem(
            language=atoms | frozenset(atom.contrary for atom in atoms),
            contrariness=ContrarinessFn(
                frozenset((atom, atom.contrary) for atom in atoms)
            ),
            strict_rules=frozenset(),
            defeasible_rules=frozenset(
                Rule((), head, "defeasible", f"d{index}")
                for index, head in enumerate(heads)
            ),
        ),
        KnowledgeBase(axioms=frozenset(), premises=frozenset()),
    )


@pytest.mark.parametrize("semantics", ["grounded", "complete", "stable"])
def test_source_asp_backend_rebuts_defeasible_conclusions(semantics: str) -> None:
    """Issue #65: a defeasible rule is attacked by a contrary of its head.

    Lehtonen et al. 2020, Def 10: ``(P, D)`` attacks ``r`` in ``R_d`` if a
    contrary of the rule name *or of its head* is derivable. Equally
    preferred defeasible facts ``r`` and ``~r`` rebut each other, so the
    grounded extension accepts neither.
    """
    r = Literal(GroundAtom("r"))
    system, kb = _rebutting_defeasible_facts((r, r.contrary))

    _assert_asp_semantics_match_reference(system, kb, semantics)


@pytest.mark.parametrize("semantics", ["grounded", "complete", "stable"])
def test_source_asp_backend_accepts_unrebutted_defeasible_conclusion(
    semantics: str,
) -> None:
    """Issue #65 control: with no contrary conclusion, ``r`` is accepted."""
    system, kb = _rebutting_defeasible_facts((Literal(GroundAtom("r")),))

    _assert_asp_semantics_match_reference(system, kb, semantics)


@given(
    st.lists(
        st.sampled_from(
            [
                Literal(GroundAtom(atom), negated=negated)
                for atom in ("a", "b")
                for negated in (False, True)
            ]
        ),
        min_size=1,
        max_size=4,
    )
)
@settings(max_examples=15, deadline=None)
def test_source_asp_backend_matches_reference_on_rebutting_facts(
    heads: list[Literal],
) -> None:
    """Issue #65: differential check over small rebutting fact theories."""
    system, kb = _rebutting_defeasible_facts(tuple(heads))

    _assert_asp_semantics_match_reference(system, kb, "grounded")
