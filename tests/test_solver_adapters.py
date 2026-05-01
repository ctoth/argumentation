from __future__ import annotations

import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest
from hypothesis import given, settings, strategies as st

import argumentation.solver as solver_module
from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule
from argumentation.dung import ArgumentationFramework
from argumentation.dung import stable_extensions as native_stable_extensions
from argumentation.iccma import parse_aba
from argumentation.solver_adapters import iccma_af, iccma_aba
from argumentation.solver_adapters.iccma_aba import (
    ICCMAABAOutputKind,
    ICCMAABAOutputParseError,
    ICCMAABASolverProtocolError,
    ICCMAABASolverSuccess,
    parse_iccma_aba_output,
    solve_aba_acceptance as solve_iccma_aba_acceptance,
    solve_aba_extensions as solve_iccma_aba_extensions,
)
from argumentation.solver_adapters.iccma_af import (
    ICCMAOutputKind,
    ICCMAOutputParseError,
    ICCMASolverProtocolError,
    ICCMASolverError,
    ICCMASolverSuccess,
    ICCMASolverUnavailable,
    parse_iccma_output,
    parse_extension_witnesses,
    solve_af_acceptance,
    solve_af_extensions,
)
from argumentation.solver_results import SolverUnavailable


def af(args: set[str], defeats: set[tuple[str, str]]) -> ArgumentationFramework:
    return ArgumentationFramework(arguments=frozenset(args), defeats=frozenset(defeats))


def aba_framework(
    size: int,
    attacks: frozenset[tuple[int, int]] = frozenset(),
) -> ABAFramework:
    assumptions = {literal(f"a{index}") for index in range(1, size + 1)}
    contraries = {literal(f"c{index}") for index in range(1, size + 1)}
    assumption_by_index = {
        index: literal(f"a{index}") for index in range(1, size + 1)
    }
    contrary_by_index = {
        index: literal(f"c{index}") for index in range(1, size + 1)
    }
    return ABAFramework(
        language=frozenset(assumptions | contraries),
        rules=frozenset(
            Rule((assumption_by_index[attacker],), contrary_by_index[target], "strict")
            for attacker, target in attacks
        ),
        assumptions=frozenset(assumptions),
        contrary={
            assumption_by_index[index]: contrary_by_index[index]
            for index in range(1, size + 1)
        },
    )


def literal(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_parse_iccma_witness_output() -> None:
    assert parse_extension_witnesses("w 1 3\nw 2\n") == (
        frozenset({"1", "3"}),
        frozenset({"2"}),
    )


def test_parse_iccma_2023_dc_yes_requires_query_in_certificate() -> None:
    output = parse_iccma_output("DC-CO", "YES\nw 1 3\n", query="1")

    assert output.kind is ICCMAOutputKind.DECISION
    assert output.answer is True
    assert output.witness == frozenset({"1", "3"})


def test_parse_iccma_2023_dc_yes_rejects_certificate_missing_query() -> None:
    with pytest.raises(ICCMAOutputParseError, match="must contain query"):
        parse_iccma_output("DC-CO", "YES\nw 2\n", query="1")


def test_parse_iccma_2023_dc_no_has_no_certificate() -> None:
    output = parse_iccma_output("DC-CO", "NO\n", query="1")

    assert output.answer is False
    assert output.witness is None


def test_parse_iccma_2023_ds_no_counterexample_omits_query() -> None:
    output = parse_iccma_output("DS-PR", "NO\nw 2 3\n", query="1")

    assert output.answer is False
    assert output.witness == frozenset({"2", "3"})


def test_parse_iccma_2023_ds_no_rejects_counterexample_containing_query() -> None:
    with pytest.raises(ICCMAOutputParseError, match="must omit query"):
        parse_iccma_output("DS-PR", "NO\nw 1 2\n", query="1")


def test_parse_iccma_2023_ds_yes_has_no_certificate() -> None:
    output = parse_iccma_output("DS-PR", "YES\n", query="1")

    assert output.answer is True
    assert output.witness is None


def test_parse_iccma_2023_se_output_is_witness_or_no_extension() -> None:
    witness = parse_iccma_output("SE-ST", "w 1\n")
    no_extension = parse_iccma_output("SE-ST", "NO\n")

    assert witness.kind is ICCMAOutputKind.SINGLE_EXTENSION
    assert witness.extensions == (frozenset({"1"}),)
    assert no_extension.extensions == ()
    assert no_extension.no_extension is True


def test_parse_iccma_2023_approximate_decision_outputs_need_no_witness() -> None:
    output = parse_iccma_output("DC-CO", "YES\n", query="1", certificate_required=False)

    assert output.answer is True
    assert output.witness is None


def test_parse_iccma_output_rejects_malformed_witness_line() -> None:
    with pytest.raises(ICCMAOutputParseError, match="witness"):
        parse_iccma_output("SE-ST", "w 1 nope\n")


def test_iccma_af_adapter_invokes_official_2023_cli_for_single_extension(monkeypatch) -> None:
    framework = af({"1", "2"}, {("1", "2")})
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        input_path = command[-1]
        assert command[:-1] == ["fake-iccma-solver", "-p", "SE-ST", "-f"]
        assert input_path.endswith(".af")
        return SimpleNamespace(returncode=0, stdout="w 1\n", stderr="")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        fake_run,
    )

    result = solve_af_extensions(
        framework,
        semantics="stable",
        binary="fake-iccma-solver",
        timeout_seconds=5.0,
    )

    assert isinstance(result, ICCMASolverSuccess)
    assert result.extensions == (frozenset({"1"}),)
    assert calls and calls[0][1:4] == ["-p", "SE-ST", "-f"]


def test_iccma_af_adapter_invokes_official_2023_cli_for_acceptance(monkeypatch) -> None:
    framework = af({"1", "2"}, {("1", "2")})
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert command[:4] == ["fake-iccma-solver", "-p", "DC-ST", "-f"]
        assert command[4].endswith(".af")
        assert command[5:] == ["-a", "1"]
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        return SimpleNamespace(returncode=0, stdout="YES\nw 1\n", stderr="")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        fake_run,
    )

    result = solve_af_acceptance(
        framework,
        semantics="stable",
        task="credulous",
        query="1",
        binary="fake-iccma-solver",
        timeout_seconds=5.0,
    )

    assert isinstance(result, ICCMASolverSuccess)
    assert result.answer is True
    assert result.witness == frozenset({"1"})
    assert calls and calls[0][-2:] == ["-a", "1"]


def test_iccma_af_adapter_reports_missing_binary(monkeypatch) -> None:
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: None,
    )

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="grounded",
        binary="missing-solver",
    )

    assert isinstance(result, ICCMASolverUnavailable)
    assert result.backend == "missing-solver"


def test_iccma_af_adapter_reports_solver_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="bad input"),
    )

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="stable",
        binary="fake-iccma-solver",
    )

    assert isinstance(result, ICCMASolverError)
    assert result.returncode == 2
    assert result.stderr == "bad input"


def test_iccma_af_adapter_reports_protocol_error(monkeypatch) -> None:
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="maybe\n", stderr=""),
    )

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="stable",
        binary="fake-iccma-solver",
    )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.stdout == "maybe\n"


OFFICIAL_ICCMA_2023_MAIN_AF_PROBLEMS = {
    ("DC", "complete"),
    ("DC", "stable"),
    ("DC", "semi-stable"),
    ("DC", "stage"),
    ("DS", "preferred"),
    ("DS", "stable"),
    ("DS", "semi-stable"),
    ("DS", "stage"),
    ("SE", "preferred"),
    ("SE", "stable"),
    ("SE", "semi-stable"),
    ("SE", "stage"),
    ("SE", "ideal"),
}


@given(
    st.sampled_from(["DC", "DS", "SE"]),
    st.sampled_from(
        [
            "complete",
            "grounded",
            "preferred",
            "stable",
            "semi-stable",
            "stage",
            "ideal",
            "cf2",
        ]
    ),
)
@settings(deadline=10000, max_examples=60)
def test_iccma_af_capability_table_matches_official_2023_main_track(
    task: str,
    semantics: str,
) -> None:
    assert iccma_af.supports_af_problem(task, semantics) is (
        (task, semantics) in OFFICIAL_ICCMA_2023_MAIN_AF_PROBLEMS
    )


def test_iccma_af_rejects_unsupported_se_without_subprocess(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="w 1\n", stderr="")

    monkeypatch.setattr("argumentation.solver_adapters.iccma_af.subprocess.run", fake_run)

    result = solve_af_extensions(
        af({"1"}, set()),
        semantics="complete",
        binary="fake-iccma-solver",
    )

    assert isinstance(result, SolverUnavailable)
    assert result.reason == "unsupported ICCMA 2023 AF problem: SE-CO"
    assert calls == []


def test_iccma_af_rejects_unsupported_acceptance_without_subprocess(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_af.shutil.which",
        lambda binary: binary,
    )

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="YES\nw 1\n", stderr="")

    monkeypatch.setattr("argumentation.solver_adapters.iccma_af.subprocess.run", fake_run)

    result = solve_af_acceptance(
        af({"1"}, set()),
        semantics="preferred",
        task="credulous",
        query="1",
        binary="fake-iccma-solver",
    )

    assert isinstance(result, SolverUnavailable)
    assert result.reason == "unsupported ICCMA 2023 AF problem: DC-PR"
    assert calls == []


@given(st.integers(min_value=1, max_value=5))
@settings(deadline=10000, max_examples=20)
def test_iccma_se_witness_must_be_native_extension(size: int) -> None:
    # ICCMA witness checking requires SE witnesses to be extensions.
    framework = af({str(index) for index in range(1, size + 1)}, set())
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout="w\n",
                stderr="",
            ),
        )

        result = solve_af_extensions(
            framework,
            semantics="stable",
            binary="fake-iccma-solver",
        )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.stdout == "w\n"


@given(st.integers(min_value=2, max_value=5))
@settings(deadline=10000, max_examples=20)
def test_iccma_dc_yes_witness_must_be_native_extension(size: int) -> None:
    # ICCMA DC YES certificates must contain the query and be extensions.
    framework = af({str(index) for index in range(1, size + 1)}, set())
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout="YES\nw 1\n",
                stderr="",
            ),
        )

        result = solve_af_acceptance(
            framework,
            semantics="stable",
            task="credulous",
            query="1",
            binary="fake-iccma-solver",
        )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.stdout == "YES\nw 1\n"


@given(st.integers(min_value=2, max_value=5))
@settings(deadline=10000, max_examples=20)
def test_iccma_ds_no_counterexample_must_be_native_extension(size: int) -> None:
    # ICCMA DS NO certificates must omit the query and be extensions.
    framework = af({str(index) for index in range(1, size + 1)}, set())
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout="NO\nw 2\n",
                stderr="",
            ),
        )

        result = solve_af_acceptance(
            framework,
            semantics="stable",
            task="skeptical",
            query="1",
            binary="fake-iccma-solver",
        )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.stdout == "NO\nw 2\n"


def test_iccma_backend_failures_use_shared_solver_result_classes() -> None:
    assert ICCMASolverUnavailable is solver_module.SolverBackendUnavailable
    assert ICCMASolverError is solver_module.SolverBackendError
    assert ICCMASolverProtocolError is solver_module.SolverProtocolError


@given(st.from_regex(r"[A-Za-z_]{1,12}", fullmatch=True))
@settings(deadline=10000, max_examples=30)
def test_iccma_source_derived_malformed_witnesses_are_protocol_errors(
    bad_argument: str,
) -> None:
    # ICCMA 2023 AF witness lines use indexed positive-integer arguments.
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_af.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout=f"w 1 {bad_argument}\n",
                stderr="protocol stderr",
            ),
        )

        result = solve_af_extensions(
            af({"1"}, set()),
            semantics="stable",
            binary="fake-iccma-solver",
        )

    assert isinstance(result, ICCMASolverProtocolError)
    assert result.problem == "SE-ST"
    assert result.stdout == f"w 1 {bad_argument}\n"
    assert result.stderr == "protocol stderr"


def test_optional_real_iccma_af_solver_smoke() -> None:
    binary = os.environ.get("ICCMA_AF_SOLVER")
    if not binary or (shutil.which(binary) is None and not Path(binary).exists()):
        pytest.skip("set ICCMA_AF_SOLVER to an ICCMA 2023 AF solver executable")

    framework = af({"1", "2"}, {("1", "2")})
    result = solve_af_extensions(framework, semantics="stable", binary=binary)

    assert isinstance(result, ICCMASolverSuccess)
    assert set(result.extensions) <= set(native_stable_extensions(framework))


def test_parse_iccma_aba_2023_se_output_maps_numeric_assumption_ids() -> None:
    framework = aba_framework(2)

    output = parse_iccma_aba_output("SE-ST", "w 1 2\n", framework=framework)

    assert output.kind is ICCMAABAOutputKind.SINGLE_EXTENSION
    assert output.witness == frozenset({literal("a1"), literal("a2")})


def test_parse_iccma_aba_2023_decision_output_has_no_certificate() -> None:
    framework = aba_framework(1)

    dc = parse_iccma_aba_output(
        "DC-CO",
        "YES\n",
        framework=framework,
        query=literal("a1"),
    )
    ds = parse_iccma_aba_output(
        "DS-ST",
        "NO\n",
        framework=framework,
        query=literal("a1"),
    )

    assert dc.kind is ICCMAABAOutputKind.DECISION
    assert dc.answer is True
    assert dc.witness is None
    assert ds.answer is False
    assert ds.witness is None


def test_parse_iccma_aba_2023_decision_output_rejects_certificates() -> None:
    with pytest.raises(ICCMAABAOutputParseError, match="YES or NO"):
        parse_iccma_aba_output(
            "DC-ST",
            "YES\nw 1\n",
            framework=aba_framework(1),
            query=literal("a1"),
        )


OFFICIAL_ASPFORABA_ICCMA_2023_PROBLEMS = {
    ("DC", "complete"),
    ("DC", "stable"),
    ("DS", "preferred"),
    ("DS", "stable"),
    ("SE", "preferred"),
    ("SE", "stable"),
}


@given(
    st.sampled_from(["DC", "DS", "SE"]),
    st.sampled_from(
        [
            "complete",
            "grounded",
            "preferred",
            "stable",
            "semi-stable",
            "stage",
            "ideal",
            "cf2",
        ]
    ),
)
@settings(deadline=10000, max_examples=60)
def test_iccma_aba_capability_table_matches_aspforaba_iccma_2023_source(
    task: str,
    semantics: str,
) -> None:
    assert iccma_aba.supports_aba_problem(task, semantics) is (
        (task, semantics) in OFFICIAL_ASPFORABA_ICCMA_2023_PROBLEMS
    )


def test_iccma_aba_adapter_invokes_official_2023_cli_and_writes_numeric_aba(
    monkeypatch,
) -> None:
    framework = aba_framework(2)
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert command[:4] == ["fake-aspforaba", "-p", "SE-ST", "-f"]
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        parsed = parse_aba(Path(command[4]).read_text(encoding="utf-8"))
        assert parsed.assumptions == framework.assumptions
        return SimpleNamespace(returncode=0, stdout="w 1 2\n", stderr="")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.subprocess.run",
        fake_run,
    )

    result = solve_iccma_aba_extensions(
        framework,
        semantics="stable",
        binary="fake-aspforaba",
        timeout_seconds=5.0,
    )

    assert isinstance(result, ICCMAABASolverSuccess)
    assert result.extensions == (frozenset({literal("a1"), literal("a2")}),)
    assert calls and calls[0][1:4] == ["-p", "SE-ST", "-f"]


def test_iccma_aba_adapter_invokes_acceptance_with_query_atom(monkeypatch) -> None:
    framework = aba_framework(1)
    calls: list[list[str]] = []

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.shutil.which",
        lambda binary: binary,
    )

    def fake_run(command, *, capture_output, text, timeout, check):
        calls.append(command)
        assert command[:4] == ["fake-aspforaba", "-p", "DC-CO", "-f"]
        assert command[5:] == ["-a", "1"]
        assert capture_output is True
        assert text is True
        assert timeout == 5.0
        assert check is False
        return SimpleNamespace(returncode=0, stdout="YES\n", stderr="")

    monkeypatch.setattr(
        "argumentation.solver_adapters.iccma_aba.subprocess.run",
        fake_run,
    )

    result = solve_iccma_aba_acceptance(
        framework,
        semantics="complete",
        task="credulous",
        query=literal("a1"),
        binary="fake-aspforaba",
        timeout_seconds=5.0,
    )

    assert isinstance(result, ICCMAABASolverSuccess)
    assert result.answer is True
    assert calls and calls[0][-2:] == ["-a", "1"]


@given(st.integers(min_value=2, max_value=5))
@settings(deadline=10000, max_examples=20)
def test_iccma_aba_se_witness_must_be_native_extension(size: int) -> None:
    framework = aba_framework(size)
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_aba.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_aba.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout="w 1\n",
                stderr="",
            ),
        )

        result = solve_iccma_aba_extensions(
            framework,
            semantics="stable",
            binary="fake-aspforaba",
        )

    assert isinstance(result, ICCMAABASolverProtocolError)
    assert result.stdout == "w 1\n"


@given(st.from_regex(r"[A-Za-z_]{1,12}", fullmatch=True))
@settings(deadline=10000, max_examples=30)
def test_iccma_aba_malformed_witnesses_are_protocol_errors(
    bad_atom: str,
) -> None:
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_aba.shutil.which",
            lambda binary: binary,
        )
        monkeypatch.setattr(
            "argumentation.solver_adapters.iccma_aba.subprocess.run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0,
                stdout=f"w 1 {bad_atom}\n",
                stderr="protocol stderr",
            ),
        )

        result = solve_iccma_aba_extensions(
            aba_framework(1),
            semantics="stable",
            binary="fake-aspforaba",
        )

    assert isinstance(result, ICCMAABASolverProtocolError)
    assert result.problem == "SE-ST"
    assert result.stdout == f"w 1 {bad_atom}\n"
    assert result.stderr == "protocol stderr"


def test_optional_real_aspforaba_solver_smoke() -> None:
    binary = os.environ.get("ASPFORABA_SOLVER") or os.environ.get("ICCMA_ABA_SOLVER")
    if not binary or (shutil.which(binary) is None and not Path(binary).exists()):
        pytest.skip("set ASPFORABA_SOLVER or ICCMA_ABA_SOLVER to an ICCMA 2023 ABA solver")

    framework = aba_framework(2)
    result = solve_iccma_aba_extensions(framework, semantics="stable", binary=binary)

    assert isinstance(result, ICCMAABASolverSuccess)
    assert result.extensions == (framework.assumptions,)
