"""Probabilistic argumentation over primitive relation worlds.

This module keeps uncertainty on primitive arguments, attacks, and supports,
then realizes semantic AFs per sampled world. Direct defeats are primitive
semantic relations; Cayrol derived defeats are world-derived consequences.

Monte Carlo uses Agresti-Coull stopping per Li et al. (2012, Algorithm 1).
Connected component decomposition follows Hunter & Thimm (2017, Prop 18)
over the primitive semantic dependency graph.
"""

from __future__ import annotations

import math
import random as _random_mod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from argumentation.probabilistic_components import connected_components

_Z_SCORES = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
_DETERMINISTIC_EPSILON = 1e-12
_UNSET = object()
_ALLOWED_STRATEGIES = frozenset({
    "auto",
    "deterministic",
    "mc",
    "exact",
    "exact_enum",
    "exact_dp",
    "paper_td",
    "dfquad",
    "dfquad_quad",
    "dfquad_baf",
})
_STRATEGY_ALIASES = {
    "exact": "exact_enum",
}


def _z_for_confidence(confidence: float) -> float:
    """Z-score for two-tailed confidence interval."""
    if confidence in _Z_SCORES:
        return _Z_SCORES[confidence]
    if not 0.0 < confidence < 1.0:
        raise ValueError(f"mc_confidence must be in (0,1), got {confidence}")
    p = 1.0 - (1.0 - confidence) / 2.0
    return _inverse_standard_normal_cdf(p)


def _inverse_standard_normal_cdf(p: float) -> float:
    """Acklam inverse-normal CDF approximation for dependency-free z scores."""
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )
    low = 0.02425
    high = 1.0 - low
    if p < low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q) + 1.0
        )
    if p > high:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q) + 1.0
        )
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
        (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r) + 1.0
    )


def _normalize_strategy(strategy: str) -> tuple[str, str]:
    """Normalize public strategy aliases and reject unsupported values."""
    requested = str(strategy)
    if requested not in _ALLOWED_STRATEGIES:
        supported = ", ".join(sorted(_ALLOWED_STRATEGIES))
        raise ValueError(f"Unknown strategy: {requested}. Supported strategies: {supported}")
    return _STRATEGY_ALIASES.get(requested, requested), requested

from argumentation.dung import (
    ArgumentationFramework,
    complete_extensions,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)


ProbabilityValue = float


def _validate_probability(value: ProbabilityValue, name: str) -> float:
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"{name} must be in [0,1], got {probability}")
    return probability


def _normalize_relation(
    name: str,
    relation: frozenset[tuple[str, str]],
    arguments: frozenset[str],
) -> frozenset[tuple[str, str]]:
    normalized = frozenset((str(source), str(target)) for source, target in relation)
    unknown = sorted(
        (source, target)
        for source, target in normalized
        if source not in arguments or target not in arguments
    )
    if unknown:
        raise ValueError(
            f"{name} must only contain pairs over framework arguments: {unknown!r}"
        )
    return normalized


def _validate_probability_keys(
    name: str,
    probabilities: Mapping[tuple[str, str], ProbabilityValue],
    relation: frozenset[tuple[str, str]],
) -> None:
    extra = sorted(edge for edge in probabilities if edge not in relation)
    if extra:
        raise ValueError(f"{name} contains undeclared relation pairs: {extra!r}")


def _expectation(value: ProbabilityValue | None) -> float:
    if value is None:
        return 1.0
    return float(value)

@dataclass(frozen=True)
class ProbabilisticAF:
    """Probabilistic AF with primitive-relation uncertainty.

    framework: the semantic AF envelope used for deterministic evaluation.
    p_args: P_A per argument.
    p_defeats: direct defeat probabilities.
    p_attacks: optional primitive attack probabilities when attacks and defeats differ.
    supports / p_supports: optional primitive support relations with existence probabilities.
    base_defeats: optional direct defeats before Cayrol closure; defaults to framework.defeats.
    """

    framework: ArgumentationFramework
    p_args: Mapping[str, ProbabilityValue]
    p_defeats: Mapping[tuple[str, str], ProbabilityValue]
    p_attacks: Mapping[tuple[str, str], ProbabilityValue] | None = None
    supports: frozenset[tuple[str, str]] = frozenset()
    p_supports: Mapping[tuple[str, str], ProbabilityValue] | None = None
    base_defeats: frozenset[tuple[str, str]] | None = None

    def __post_init__(self) -> None:
        framework_args = frozenset(self.framework.arguments)
        supports = _normalize_relation("supports", self.supports, framework_args)
        object.__setattr__(self, "supports", supports)

        if self.base_defeats is not None:
            base_defeats = _normalize_relation(
                "base_defeats",
                self.base_defeats,
                framework_args,
            )
            primitive_attacks = _primitive_attacks(self)
            extra_base_defeats = sorted(
                edge for edge in base_defeats if edge not in primitive_attacks
            )
            if extra_base_defeats:
                raise ValueError(
                    "base_defeats must be a subset of primitive attacks: "
                    f"{extra_base_defeats!r}"
                )
            object.__setattr__(self, "base_defeats", base_defeats)

        object.__setattr__(
            self,
            "p_args",
            {str(arg): _validate_probability(probability, f"p_args[{arg!r}]") for arg, probability in self.p_args.items()},
        )
        p_arg_keys = set(self.p_args)
        if p_arg_keys != set(framework_args):
            missing = sorted(framework_args - p_arg_keys)
            extra = sorted(p_arg_keys - framework_args)
            details: list[str] = []
            if missing:
                details.append(f"missing={missing!r}")
            if extra:
                details.append(f"extra={extra!r}")
            raise ValueError(
                "p_args must contain exactly the framework arguments"
                f": {', '.join(details)}"
            )

        object.__setattr__(
            self,
            "p_defeats",
            {
                (str(src), str(tgt)): _validate_probability(probability, f"p_defeats[{(src, tgt)!r}]")
                for (src, tgt), probability in self.p_defeats.items()
            },
        )
        _validate_probability_keys("p_defeats", self.p_defeats, _direct_defeats(self))
        if self.p_attacks is not None:
            object.__setattr__(
                self,
                "p_attacks",
                {
                    (str(src), str(tgt)): _validate_probability(probability, f"p_attacks[{(src, tgt)!r}]")
                    for (src, tgt), probability in self.p_attacks.items()
                },
            )
            _validate_probability_keys(
                "p_attacks",
                self.p_attacks,
                _primitive_attacks(self),
            )
        if self.p_supports is not None:
            object.__setattr__(
                self,
                "p_supports",
                {
                    (str(src), str(tgt)): _validate_probability(probability, f"p_supports[{(src, tgt)!r}]")
                    for (src, tgt), probability in self.p_supports.items()
                },
            )
            _validate_probability_keys("p_supports", self.p_supports, self.supports)

    @property
    def argument_probabilities(self) -> Mapping[str, ProbabilityValue]:
        return self.p_args

    @property
    def direct_defeat_probabilities(self) -> Mapping[tuple[str, str], ProbabilityValue]:
        return self.p_defeats

    @property
    def attack_probabilities(self) -> Mapping[tuple[str, str], ProbabilityValue] | None:
        return self.p_attacks

    @property
    def support_probabilities(self) -> Mapping[tuple[str, str], ProbabilityValue] | None:
        return self.p_supports


ProbabilisticArgumentationFramework = ProbabilisticAF


@dataclass(frozen=True)
class PrAFResult:
    """Result of probabilistic extension computation.

    `query_kind` and `inference_mode` make the queried object explicit:
    argument-acceptance vs exact-set extension probability, and credulous
    vs skeptical singleton acceptance for multi-extension semantics.
    """

    acceptance_probs: dict[str, float] | None = None
    extension_probability: float | None = None
    strategy_used: str = ""
    strategy_requested: str | None = None
    downgraded_from: str | None = None
    samples: int | None = None
    confidence_interval_half: float | None = None
    semantics: str = "grounded"
    query_kind: str = "argument_acceptance"
    inference_mode: str | None = "credulous"
    queried_set: tuple[str, ...] | None = None
    strategy_metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.strategy_requested is None:
            object.__setattr__(self, "strategy_requested", self.strategy_used)
        if self.queried_set is not None:
            object.__setattr__(
                self,
                "queried_set",
                tuple(sorted(dict.fromkeys(str(arg) for arg in self.queried_set))),
            )


def _is_deterministic_opinion(opinion: ProbabilityValue | None) -> bool:
    if opinion is None:
        return True
    expectation = _expectation(opinion)
    return (
        expectation >= 1.0 - _DETERMINISTIC_EPSILON
        or expectation <= _DETERMINISTIC_EPSILON
    )


def _edge_is_present(opinion: ProbabilityValue | None) -> bool:
    if opinion is None:
        return True
    return _expectation(opinion) >= 1.0 - _DETERMINISTIC_EPSILON


def _primitive_attacks(praf: ProbabilisticAF) -> frozenset[tuple[str, str]]:
    if praf.framework.attacks is not None:
        return praf.framework.attacks
    return praf.framework.defeats


def _direct_defeats(praf: ProbabilisticAF) -> frozenset[tuple[str, str]]:
    if praf.base_defeats is not None:
        return praf.base_defeats
    return praf.framework.defeats


def _attack_opinion(
    praf: ProbabilisticAF,
    edge: tuple[str, str],
) -> ProbabilityValue | None:
    if praf.p_attacks is not None and edge in praf.p_attacks:
        return praf.p_attacks[edge]
    if edge in _direct_defeats(praf) and edge in praf.p_defeats:
        return praf.p_defeats[edge]
    return None


def _support_opinion(
    praf: ProbabilisticAF,
    edge: tuple[str, str],
) -> ProbabilityValue | None:
    if praf.p_supports is not None and edge in praf.p_supports:
        return praf.p_supports[edge]
    return None


def _sample_edge(
    rng: _random_mod.Random,
    opinion: ProbabilityValue | None,
) -> bool:
    if opinion is None:
        return True
    return rng.random() < _expectation(opinion)


def _supports_structure(praf: ProbabilisticAF) -> bool:
    return bool(praf.supports)


def _uses_attack_only_conflicts(praf: ProbabilisticAF) -> bool:
    return (
        praf.framework.attacks is not None
        and praf.framework.attacks != praf.framework.defeats
    )


def _requires_relation_rich_worlds(praf: ProbabilisticAF) -> bool:
    return _supports_structure(praf) or _uses_attack_only_conflicts(praf)


def _all_structure_deterministic(praf: ProbabilisticAF) -> bool:
    if not all(_is_deterministic_opinion(p) for p in praf.p_args.values()):
        return False
    for edge in _primitive_attacks(praf):
        opinion = _attack_opinion(praf, edge)
        if not _is_deterministic_opinion(opinion):
            return False
    for edge in praf.supports:
        opinion = _support_opinion(praf, edge)
        if not _is_deterministic_opinion(opinion):
            return False
    return True


def _normalize_queried_set(
    queried_set: frozenset[str] | set[str] | tuple[str, ...] | list[str] | None,
) -> tuple[str, ...] | None:
    if queried_set is None:
        return None
    return tuple(sorted(dict.fromkeys(str(arg) for arg in queried_set)))


def _validate_query_contract(
    *,
    strategy: str,
    query_kind: object,
    inference_mode: object,
    queried_set: frozenset[str] | set[str] | tuple[str, ...] | list[str] | None,
) -> tuple[str, str | None, tuple[str, ...] | None]:
    """Validate explicit query selectors for PrAF acceptance queries."""
    if strategy in {"dfquad", "dfquad_quad", "dfquad_baf"}:
        return "gradual_strength", None, None

    if query_kind is _UNSET:
        if inference_mode is not _UNSET and inference_mode is not None:
            raise ValueError("inference_mode requires an explicit query_kind")
        return "argument_acceptance", "credulous", None

    query_kind_str = str(query_kind)
    normalized_queried_set = _normalize_queried_set(queried_set)

    if query_kind_str == "argument_acceptance":
        if inference_mode is _UNSET or inference_mode is None:
            raise ValueError(
                "argument_acceptance requires inference_mode='credulous' or 'skeptical'"
            )
        inference_mode_str = str(inference_mode)
        if inference_mode_str not in {"credulous", "skeptical"}:
            raise ValueError(
                "argument_acceptance requires inference_mode='credulous' or 'skeptical'"
            )
        if normalized_queried_set is not None:
            raise ValueError("argument_acceptance does not use queried_set")
        return query_kind_str, inference_mode_str, None

    if query_kind_str == "extension_probability":
        if inference_mode is not _UNSET and inference_mode is not None:
            raise ValueError("extension_probability does not use inference_mode")
        if normalized_queried_set is None:
            raise ValueError("extension_probability requires queried_set")
        return query_kind_str, None, normalized_queried_set

    raise ValueError(f"Unknown query_kind: {query_kind_str}")


def _exact_dp_supports_query(
    *,
    query_kind: str,
    inference_mode: str | None,
) -> bool:
    if query_kind == "argument_acceptance":
        return inference_mode == "credulous"
    return False


def _extensions_for_semantics(
    af: ArgumentationFramework,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    if semantics == "grounded":
        return (grounded_extension(af),)
    if semantics == "preferred":
        return tuple(preferred_extensions(af, backend="brute"))
    if semantics == "stable":
        return tuple(stable_extensions(af, backend="brute"))
    if semantics == "complete":
        return tuple(complete_extensions(af, backend="brute"))
    raise ValueError(f"Unknown semantics: {semantics}")


def _accepted_arguments_from_extensions(
    extensions: tuple[frozenset[str], ...],
    *,
    inference_mode: str,
) -> frozenset[str]:
    if not extensions:
        return frozenset()
    if inference_mode == "credulous":
        accepted = set().union(*extensions)
        return frozenset(accepted)
    if inference_mode == "skeptical":
        accepted = set(extensions[0])
        for extension in extensions[1:]:
            accepted &= set(extension)
        return frozenset(accepted)
    raise ValueError(f"Unknown inference_mode: {inference_mode}")


def _evaluate_world_query(
    af: ArgumentationFramework,
    *,
    semantics: str,
    query_kind: str,
    inference_mode: str | None,
    queried_set: tuple[str, ...] | None,
) -> frozenset[str] | bool:
    extensions = _extensions_for_semantics(af, semantics)
    if query_kind == "argument_acceptance":
        assert inference_mode is not None
        return _accepted_arguments_from_extensions(
            extensions,
            inference_mode=inference_mode,
        )
    if query_kind == "extension_probability":
        target = frozenset(queried_set or ())
        return target in set(extensions)
    raise ValueError(f"Unknown query_kind: {query_kind}")


def _with_strategy_override(
    result: PrAFResult,
    *,
    strategy_requested: str,
    downgraded_from: str | None = None,
) -> PrAFResult:
    return PrAFResult(
        acceptance_probs=result.acceptance_probs,
        extension_probability=result.extension_probability,
        strategy_used=result.strategy_used,
        strategy_requested=strategy_requested,
        downgraded_from=downgraded_from,
        samples=result.samples,
        confidence_interval_half=result.confidence_interval_half,
        semantics=result.semantics,
        query_kind=result.query_kind,
        inference_mode=result.inference_mode,
        queried_set=result.queried_set,
    )


def _deterministic_world(
    praf: ProbabilisticAF,
    arg_subset: frozenset[str] | None = None,
) -> ArgumentationFramework:
    """Realize the unique deterministic world for a deterministic PrAF."""
    args_to_consider = arg_subset if arg_subset is not None else praf.framework.arguments
    sampled_args = frozenset(
        a for a in args_to_consider
        if _edge_is_present(praf.p_args[a])
    )
    sampled_attacks = frozenset(
        edge for edge in _primitive_attacks(praf)
        if edge[0] in sampled_args
        and edge[1] in sampled_args
        and _edge_is_present(_attack_opinion(praf, edge))
    )
    sampled_supports = frozenset(
        edge for edge in praf.supports
        if edge[0] in sampled_args
        and edge[1] in sampled_args
        and _edge_is_present(_support_opinion(praf, edge))
    )
    return _build_sampled_framework(praf, sampled_args, sampled_attacks, sampled_supports)


def _build_sampled_framework(
    praf: ProbabilisticAF,
    sampled_args: frozenset[str],
    sampled_attacks: frozenset[tuple[str, str]],
    sampled_supports: frozenset[tuple[str, str]],
) -> ArgumentationFramework:
    """Build one sampled world, deriving Cayrol defeats after sampling primitives."""
    direct_defeats = frozenset(
        edge for edge in sampled_attacks if edge in _direct_defeats(praf)
    )
    all_defeats = set(direct_defeats)
    if sampled_supports and direct_defeats:
        from argumentation.bipolar import cayrol_derived_defeats

        all_defeats |= set(cayrol_derived_defeats(frozenset(direct_defeats), frozenset(sampled_supports)))

    sampled_attacks_relation: frozenset[tuple[str, str]] | None = None
    if praf.framework.attacks is not None:
        sampled_attacks_relation = sampled_attacks

    return ArgumentationFramework(
        arguments=sampled_args,
        defeats=frozenset(all_defeats),
        attacks=sampled_attacks_relation,
    )


def _enumerate_worlds(
    praf: ProbabilisticAF,
    sampled_args: frozenset[str],
):
    """Enumerate all sampled worlds induced by a fixed argument subset."""
    deterministic_attacks: set[tuple[str, str]] = set()
    probabilistic_attacks: list[tuple[tuple[str, str], float]] = []
    for edge in sorted(_primitive_attacks(praf)):
        if edge[0] not in sampled_args or edge[1] not in sampled_args:
            continue
        opinion = _attack_opinion(praf, edge)
        if opinion is None:
            deterministic_attacks.add(edge)
        else:
            probabilistic_attacks.append((edge, _expectation(opinion)))

    deterministic_supports: set[tuple[str, str]] = set()
    probabilistic_supports: list[tuple[tuple[str, str], float]] = []
    for edge in sorted(praf.supports):
        if edge[0] not in sampled_args or edge[1] not in sampled_args:
            continue
        opinion = _support_opinion(praf, edge)
        if opinion is None:
            deterministic_supports.add(edge)
        else:
            probabilistic_supports.append((edge, _expectation(opinion)))

    n_prob_attacks = len(probabilistic_attacks)
    n_prob_supports = len(probabilistic_supports)

    for attack_mask in range(1 << n_prob_attacks):
        sampled_attacks = set(deterministic_attacks)
        p_attacks_config = 1.0
        for idx, (edge, p_edge) in enumerate(probabilistic_attacks):
            if attack_mask & (1 << idx):
                p_attacks_config *= p_edge
                sampled_attacks.add(edge)
            else:
                p_attacks_config *= (1.0 - p_edge)
        if p_attacks_config < 1e-15:
            continue

        for support_mask in range(1 << n_prob_supports):
            sampled_supports = set(deterministic_supports)
            p_supports_config = 1.0
            for idx, (edge, p_edge) in enumerate(probabilistic_supports):
                if support_mask & (1 << idx):
                    p_supports_config *= p_edge
                    sampled_supports.add(edge)
                else:
                    p_supports_config *= (1.0 - p_edge)

            total_prob = p_attacks_config * p_supports_config
            if total_prob < 1e-15:
                continue

            yield total_prob, _build_sampled_framework(
                praf,
                sampled_args,
                frozenset(sampled_attacks),
                frozenset(sampled_supports),
            )


def _compute_probabilistic_acceptance(
    praf: ProbabilisticAF,
    *,
    semantics: str = "grounded",
    strategy: str = "auto",
    query_kind: object = _UNSET,
    inference_mode: object = _UNSET,
    queried_set: frozenset[str] | set[str] | tuple[str, ...] | list[str] | None = None,
    tau: dict[str, float] | None = None,
    mc_epsilon: float = 0.01,
    mc_confidence: float = 0.95,
    treewidth_cutoff: int = 12,
    rng_seed: int | None = None,
) -> PrAFResult:
    """Main dispatch for PrAF acceptance computation.

    Per Li et al. (2012, Algorithm 1): MC sampler with Agresti-Coull stopping.
    Per Hunter & Thimm (2017, Prop 18): connected component decomposition.

    query_kind:
        "argument_acceptance" — per-argument acceptance probabilities.
        "extension_probability" — probability that the exact queried_set is an extension.

    inference_mode:
        Required only for argument_acceptance: "credulous" or "skeptical".
    """
    normalized_strategy, requested_strategy = _normalize_strategy(strategy)
    normalized_query_kind, normalized_inference_mode, normalized_queried_set = _validate_query_contract(
        strategy=normalized_strategy,
        query_kind=query_kind,
        inference_mode=inference_mode,
        queried_set=queried_set,
    )

    if normalized_strategy == "deterministic":
        result = _deterministic_fallback(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )
    if normalized_strategy == "mc":
        result = _compute_mc(
            praf,
            semantics,
            mc_epsilon,
            mc_confidence,
            rng_seed,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )
    if normalized_strategy == "exact_enum":
        result = _compute_exact_enumeration(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )
    if normalized_strategy == "exact_dp":
        from argumentation.probabilistic_treedecomp import supports_exact_dp

        if not _exact_dp_supports_query(
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
        ):
            raise ValueError(
                "exact_dp only supports credulous argument acceptance queries"
            )
        if not supports_exact_dp(praf, semantics):
            raise ValueError(
                "exact_dp only supports grounded semantics on defeat-only probabilistic frameworks"
            )
        result = _compute_exact_dp(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )
    if normalized_strategy == "paper_td":
        result = _compute_paper_td(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )
    if normalized_strategy == "dfquad":
        raise ValueError(
            "strategy='dfquad' is ambiguous; use 'dfquad_quad' or 'dfquad_baf'"
        )
    if normalized_strategy in {"dfquad_quad", "dfquad_baf"}:
        result = _compute_dfquad(
            praf,
            semantics,
            strategy=normalized_strategy,
            tau=tau,
        )
        return (
            _with_strategy_override(result, strategy_requested=requested_strategy)
            if requested_strategy != normalized_strategy else result
        )

    # Auto dispatch
    # Fast path: if all P_D expectations are ~1.0 and all P_A expectations are ~1.0,
    # this is a deterministic AF — no sampling needed.
    # Per Li (2012, p.2): PrAF with P_A=1, P_D=1 equals standard Dung evaluation.
    all_deterministic = _all_structure_deterministic(praf)
    if all_deterministic:
        return _deterministic_fallback(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )

    # Small AF: exact enumeration (Li 2012, p.8: exact beats MC below ~13 args)
    n_args = len(praf.framework.arguments)
    if n_args <= 13:
        return _compute_exact_enumeration(
            praf,
            semantics,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )

    # Relation-rich worlds currently require exact enumeration or MC.
    if _requires_relation_rich_worlds(praf):
        return _compute_mc(
            praf,
            semantics,
            mc_epsilon,
            mc_confidence,
            rng_seed,
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
            queried_set=normalized_queried_set,
        )

    # Medium AF with low treewidth: exact DP (Popescu & Wallner 2024)
    # Per plan Section 2.4: estimate treewidth, use DP if below cutoff.
    from argumentation.probabilistic_treedecomp import estimate_treewidth

    tw = estimate_treewidth(praf.framework)
    if (
        tw <= treewidth_cutoff
        and _exact_dp_supports_query(
            query_kind=normalized_query_kind,
            inference_mode=normalized_inference_mode,
        )
    ):
        from argumentation.probabilistic_treedecomp import supports_exact_dp

        if supports_exact_dp(praf, semantics):
            return _compute_exact_dp(
                praf,
                semantics,
                query_kind=normalized_query_kind,
                inference_mode=normalized_inference_mode,
            )

    # Default: MC
    return _compute_mc(
        praf,
        semantics,
        mc_epsilon,
        mc_confidence,
        rng_seed,
        query_kind=normalized_query_kind,
        inference_mode=normalized_inference_mode,
        queried_set=normalized_queried_set,
    )


def _deterministic_fallback(
    praf: ProbabilisticAF,
    semantics: str,
    *,
    query_kind: str,
    inference_mode: str | None,
    queried_set: tuple[str, ...] | None,
) -> PrAFResult:
    """All P_D ≈ 1.0 case: run standard Dung evaluation.

    Per Li (2012, p.2): PrAF with P_A=1, P_D=1 yields acceptance probabilities
    of exactly 0.0 or 1.0, matching standard Dung extension computation.
    """
    deterministic_af = _deterministic_world(praf)
    evaluation = _evaluate_world_query(
        deterministic_af,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=inference_mode,
        queried_set=queried_set,
    )

    if query_kind == "argument_acceptance":
        assert isinstance(evaluation, frozenset)
        acceptance: dict[str, float] = {}
        for arg in deterministic_af.arguments:
            acceptance[arg] = 1.0 if arg in evaluation else 0.0
        for arg in praf.framework.arguments - deterministic_af.arguments:
            acceptance[arg] = 0.0
        return PrAFResult(
            acceptance_probs=acceptance,
            extension_probability=None,
            strategy_used="deterministic",
            strategy_requested="deterministic",
            downgraded_from=None,
            samples=None,
            confidence_interval_half=None,
            semantics=semantics,
            query_kind=query_kind,
            inference_mode=inference_mode,
            queried_set=None,
        )

    assert isinstance(evaluation, bool)
    return PrAFResult(
        acceptance_probs=None,
        extension_probability=1.0 if evaluation else 0.0,
        strategy_used="deterministic",
        strategy_requested="deterministic",
        downgraded_from=None,
        samples=None,
        confidence_interval_half=None,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=None,
        queried_set=queried_set,
    )

def _sample_subgraph(
    praf: ProbabilisticAF,
    rng: _random_mod.Random,
    arg_subset: set[str] | None = None,
) -> ArgumentationFramework:
    """Sample one semantic AF world from primitive probabilistic relations.

    Per Li et al. (2012, Algorithm 1, p.5):
    1. For each argument a, include with probability P_A(a).expectation()
    2. For each primitive attack/support where both endpoints are included,
       sample existence from its opinion expectation
    3. Derive direct defeats from sampled attacks and direct-defeat policy
    4. Derive Cayrol defeats from sampled direct defeats and supports
    """
    args_to_sample = arg_subset if arg_subset is not None else praf.framework.arguments

    # Step 1: Sample arguments
    sampled_args: set[str] = set()
    for a in args_to_sample:
        p_a = _expectation(praf.p_args[a])
        if rng.random() < p_a:
            sampled_args.add(a)

    sampled_attacks: set[tuple[str, str]] = set()
    for edge in _primitive_attacks(praf):
        if edge[0] in sampled_args and edge[1] in sampled_args:
            if _sample_edge(rng, _attack_opinion(praf, edge)):
                sampled_attacks.add(edge)

    sampled_supports: set[tuple[str, str]] = set()
    for edge in praf.supports:
        if edge[0] in sampled_args and edge[1] in sampled_args:
            if _sample_edge(rng, _support_opinion(praf, edge)):
                sampled_supports.add(edge)

    return _build_sampled_framework(
        praf,
        frozenset(sampled_args),
        frozenset(sampled_attacks),
        frozenset(sampled_supports),
    )


def _compute_mc(
    praf: ProbabilisticAF,
    semantics: str,
    epsilon: float,
    confidence: float,
    seed: int | None,
    *,
    query_kind: str,
    inference_mode: str | None,
    queried_set: tuple[str, ...] | None,
) -> PrAFResult:
    """Monte Carlo sampler with per-argument acceptance and Agresti-Coull stopping.

    Per Li et al. (2012, Algorithm 1, p.5): sample DAFs, evaluate semantics,
    accumulate per-argument acceptance counts.

    Stopping criterion per Li et al. (2012, Eq. 5, p.7):
    N > 4 * p' * (1 - p') / epsilon^2 - 4
    where p' is the observed proportion for the argument with widest CI.

    Min 30 samples before convergence check.
    """
    rng = _random_mod.Random(seed)
    z = _z_for_confidence(confidence)

    if query_kind == "extension_probability":
        hits = 0
        n = 0
        min_samples = 30
        while True:
            n += 1
            sub_af = _sample_subgraph(praf, rng)
            evaluation = _evaluate_world_query(
                sub_af,
                semantics=semantics,
                query_kind=query_kind,
                inference_mode=inference_mode,
                queried_set=queried_set,
            )
            assert isinstance(evaluation, bool)
            if evaluation:
                hits += 1

            if n >= min_samples:
                adjusted_n = n + z * z
                adjusted_count = hits + (z * z) / 2.0
                adjusted_p = adjusted_count / adjusted_n
                ci_half = z * math.sqrt(
                    adjusted_p * (1.0 - adjusted_p) / adjusted_n
                )
                if ci_half <= epsilon:
                    break

            if n >= 100000:
                break

        adjusted_n = n + z * z
        adjusted_count = hits + (z * z) / 2.0
        adjusted_p = adjusted_count / adjusted_n
        ci_half = z * math.sqrt(
            adjusted_p * (1.0 - adjusted_p) / adjusted_n
        )
        return PrAFResult(
            acceptance_probs=None,
            extension_probability=hits / n if n > 0 else 0.0,
            strategy_used="mc",
            strategy_requested="mc",
            downgraded_from=None,
            samples=n,
            confidence_interval_half=ci_half,
            semantics=semantics,
            query_kind=query_kind,
            inference_mode=None,
            queried_set=queried_set,
        )

    # Decompose into connected components per Hunter & Thimm (2017, Prop 18)
    components = connected_components(praf)

    # Compute acceptance per component independently
    all_acceptance: dict[str, float] = {}
    total_samples = 0
    max_ci_half = 0.0

    for comp_args in components:
        # Build sub-PrAF for this component
        comp_defeats = frozenset(
            (f, t) for f, t in praf.framework.defeats
            if f in comp_args and t in comp_args
        )
        comp_attacks = None
        if praf.framework.attacks is not None:
            comp_attacks = frozenset(
                (f, t) for f, t in praf.framework.attacks
                if f in comp_args and t in comp_args
            )
        comp_supports = frozenset(
            (f, t) for f, t in praf.supports
            if f in comp_args and t in comp_args
        )
        comp_base_defeats = frozenset(
            (f, t) for f, t in _direct_defeats(praf)
            if f in comp_args and t in comp_args
        )

        comp_af = ArgumentationFramework(
            arguments=frozenset(comp_args),
            defeats=comp_defeats,
            attacks=comp_attacks,
        )
        comp_p_args = {a: praf.p_args[a] for a in comp_args}
        comp_p_defeats = {
            d: praf.p_defeats[d] for d in comp_defeats
            if d in praf.p_defeats
        }
        comp_p_attacks = None
        if praf.p_attacks is not None:
            comp_p_attacks = {
                d: praf.p_attacks[d] for d in comp_attacks or frozenset()
                if d in praf.p_attacks
            }
        comp_p_supports = None
        if praf.p_supports is not None:
            comp_p_supports = {
                d: praf.p_supports[d] for d in comp_supports
                if d in praf.p_supports
            }

        comp_praf = ProbabilisticAF(
            framework=comp_af,
            p_args=comp_p_args,
            p_defeats=comp_p_defeats,
            p_attacks=comp_p_attacks,
            supports=comp_supports,
            p_supports=comp_p_supports,
            base_defeats=comp_base_defeats,
        )

        # Check if this component is deterministic
        comp_all_det = _all_structure_deterministic(comp_praf)
        if comp_all_det:
            evaluation = _evaluate_world_query(
                _deterministic_world(comp_praf),
                semantics=semantics,
                query_kind=query_kind,
                inference_mode=inference_mode,
                queried_set=queried_set,
            )
            if query_kind == "argument_acceptance":
                assert isinstance(evaluation, frozenset)
                for arg in comp_args:
                    all_acceptance[arg] = 1.0 if arg in evaluation else 0.0
            continue

        # MC sampling for this component
        counts: dict[str, int] = {a: 0 for a in comp_args}
        n = 0
        min_samples = 30

        while True:
            n += 1
            sub_af = _sample_subgraph(comp_praf, rng, comp_args)
            evaluation = _evaluate_world_query(
                sub_af,
                semantics=semantics,
                query_kind=query_kind,
                inference_mode=inference_mode,
                queried_set=queried_set,
            )

            if query_kind == "argument_acceptance":
                assert isinstance(evaluation, frozenset)
                for a in comp_args:
                    if a in evaluation:
                        counts[a] += 1

            # Agresti-Coull stopping (Li 2012, Eq. 5, p.7)
            if n >= min_samples:
                converged = True
                for a in comp_args:
                    adjusted_n = n + z * z
                    adjusted_count = counts[a] + (z * z) / 2.0
                    adjusted_p = adjusted_count / adjusted_n
                    ci_half = z * math.sqrt(
                        adjusted_p * (1.0 - adjusted_p) / adjusted_n
                    )
                    if ci_half > epsilon:
                        converged = False
                        break
                if converged:
                    break

            # Safety cap to prevent infinite loops
            if n >= 100000:
                break

        for a in comp_args:
            all_acceptance[a] = counts[a] / n

        total_samples = max(total_samples, n)

        # Compute CI half-width for this component
        if n > 0:
            for a in comp_args:
                adjusted_n = n + z * z
                adjusted_count = counts[a] + (z * z) / 2.0
                adjusted_p = adjusted_count / adjusted_n
                ci = z * math.sqrt(
                    adjusted_p * (1.0 - adjusted_p) / adjusted_n
                )
                max_ci_half = max(max_ci_half, ci)

    return PrAFResult(
        acceptance_probs=all_acceptance,
        extension_probability=None,
        strategy_used="mc",
        strategy_requested="mc",
        downgraded_from=None,
        samples=total_samples,
        confidence_interval_half=max_ci_half,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=inference_mode,
        queried_set=queried_set,
    )


def _compute_exact_enumeration(
    praf: ProbabilisticAF,
    semantics: str,
    *,
    query_kind: str,
    inference_mode: str | None,
    queried_set: tuple[str, ...] | None,
) -> PrAFResult:
    """Brute-force exact computation for small AFs.

    Per Li et al. (2012, p.3-4): enumerate all inducible DAFs, compute
    P_PrAF(AF) for each, sum probabilities where argument is in extension.

    Complexity: O(2^(|A|+|D|)) — only feasible for small AFs.
    """
    args_list = sorted(praf.framework.arguments)
    n_args = len(args_list)

    acceptance: dict[str, float] = {a: 0.0 for a in args_list}
    extension_probability = 0.0

    # Enumerate all subsets of arguments
    for arg_mask in range(1 << n_args):
        sampled_args = frozenset(
            args_list[i] for i in range(n_args) if arg_mask & (1 << i)
        )

        # Compute probability of this argument subset
        p_args_present = 1.0
        for i, a in enumerate(args_list):
            p_a = _expectation(praf.p_args[a])
            if arg_mask & (1 << i):
                p_args_present *= p_a
            else:
                p_args_present *= (1.0 - p_a)

        if p_args_present < 1e-15:
            continue

        # Find valid defeats (both endpoints present)
        for p_world, sub_af in _enumerate_worlds(praf, sampled_args):
            total_prob = p_args_present * p_world
            if total_prob < 1e-15:
                continue
            evaluation = _evaluate_world_query(
                sub_af,
                semantics=semantics,
                query_kind=query_kind,
                inference_mode=inference_mode,
                queried_set=queried_set,
            )

            if query_kind == "argument_acceptance":
                assert isinstance(evaluation, frozenset)
                for a in sampled_args:
                    if a in evaluation:
                        acceptance[a] += total_prob
            else:
                assert isinstance(evaluation, bool)
                if evaluation:
                    extension_probability += total_prob

    return PrAFResult(
        acceptance_probs=acceptance if query_kind == "argument_acceptance" else None,
        extension_probability=None if query_kind == "argument_acceptance" else extension_probability,
        strategy_used="exact_enum",
        strategy_requested="exact_enum",
        downgraded_from=None,
        samples=None,
        confidence_interval_half=None,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=inference_mode,
        queried_set=queried_set,
    )


def _compute_exact_dp(
    praf: ProbabilisticAF,
    semantics: str,
    *,
    query_kind: str,
    inference_mode: str | None,
) -> PrAFResult:
    """Exact computation via tree-decomposition DP.

    Per Popescu & Wallner (2024): compute extension probabilities using
    dynamic programming on tree decompositions. Tractable for low-treewidth
    AFs (complexity O(3^k * n) where k is treewidth).
    """
    from argumentation.probabilistic_treedecomp import compute_exact_dp

    if query_kind != "argument_acceptance" or inference_mode != "credulous":
        raise ValueError("exact_dp currently only supports credulous argument acceptance")

    acceptance = compute_exact_dp(praf, semantics)

    return PrAFResult(
        acceptance_probs=acceptance,
        extension_probability=None,
        strategy_used="exact_dp",
        strategy_requested="exact_dp",
        downgraded_from=None,
        samples=None,
        confidence_interval_half=None,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=inference_mode,
        queried_set=None,
        strategy_metadata={
            "backend": "grounded_edge_tracking_td",
            "paper_conformance": "adapted_not_popescu_iou_witness_dp",
        },
    )


def _compute_paper_td(
    praf: ProbabilisticAF,
    semantics: str,
    *,
    query_kind: str,
    inference_mode: str | None,
    queried_set: tuple[str, ...] | None,
) -> PrAFResult:
    """Exact complete-extension probability via the paper-faithful TD backend."""
    if query_kind != "extension_probability" or inference_mode is not None:
        raise ValueError("paper_td currently only supports extension_probability queries")
    if queried_set is None:
        raise ValueError("paper_td requires queried_set")

    from argumentation.probabilistic_treedecomp import (
        compute_paper_exact_extension_probability,
    )

    result = compute_paper_exact_extension_probability(
        praf,
        queried_set=frozenset(queried_set),
        semantics=semantics,
    )
    return PrAFResult(
        acceptance_probs=None,
        extension_probability=result.extension_probability,
        strategy_used="paper_td",
        strategy_requested="paper_td",
        downgraded_from=None,
        samples=None,
        confidence_interval_half=None,
        semantics=semantics,
        query_kind=query_kind,
        inference_mode=None,
        queried_set=queried_set,
        strategy_metadata={
            "backend": result.backend,
            "paper_conformance": "popescu_wallner_2024_algorithm_1",
            "treewidth": result.treewidth,
            "node_count": result.node_count,
            "root_table_rows": result.root_table_rows,
            "root_probability_mass": result.root_probability_mass,
            "table_summaries": result.table_summaries,
            "argument_witnesses": result.argument_witnesses,
        },
    )


def summarize_defeat_relations(
    praf: ProbabilisticAF,
    *,
    include_derived: bool = True,
) -> dict[tuple[str, str], float]:
    """Compute exact defeat marginals as derived query results.

    This helper is explicit and potentially exponential. It is intended for
    explanation and diagnostics, not as an input to the semantic core.
    """
    args_list = sorted(praf.framework.arguments)
    n_args = len(args_list)
    acceptance: dict[tuple[str, str], float] = {}

    for arg_mask in range(1 << n_args):
        sampled_args = frozenset(
            args_list[i] for i in range(n_args) if arg_mask & (1 << i)
        )

        p_args_present = 1.0
        for i, a in enumerate(args_list):
            p_a = _expectation(praf.p_args[a])
            if arg_mask & (1 << i):
                p_args_present *= p_a
            else:
                p_args_present *= (1.0 - p_a)

        if p_args_present < 1e-15:
            continue

        for p_world, sub_af in _enumerate_worlds(praf, sampled_args):
            total_prob = p_args_present * p_world
            if total_prob < 1e-15:
                continue
            for defeat in sub_af.defeats:
                acceptance[defeat] = acceptance.get(defeat, 0.0) + total_prob

    direct_defeats = _direct_defeats(praf)
    return {
        edge: probability
        for edge, probability in sorted(acceptance.items())
        if include_derived or edge in direct_defeats
    }


def _compute_dfquad(
    praf: ProbabilisticAF,
    semantics: str,
    *,
    strategy: str,
    tau: dict[str, float] | None = None,
    supports: dict[tuple[str, str], float] | None = None,
) -> PrAFResult:
    """DF-QuAD gradual semantics for QBAFs.

    Per Freedman et al. (2025, p.3): computes continuous strengths in [0,1]
    by propagating base scores through attack and support relations.

    Complementary to PrAF MC/exact strategies which compute extension
    membership probabilities. DF-QuAD computes graded argument strengths.

    **Design note:** Li 2012's P_A (argument existence probability for MC sampling)
    is currently used as Rago 2016's τ (intrinsic strength for DF-QuAD gradual
    semantics). These are conceptually distinct: a rarely-existing argument is not
    the same as a weak argument. A principled separation would maintain P_A for
    sampling and τ as an independent parameter.
    """
    from argumentation.probabilistic_dfquad import (
        compute_dfquad_baf_strengths,
        compute_dfquad_quad_strengths,
    )

    if semantics != "grounded":
        raise ValueError(
            "DF-QuAD is a gradual semantics, not a Dung semantics label; "
            "leave semantics at the default or use the dedicated DF-QuAD result."
        )

    if supports is None:
        supports = {}
        for edge in praf.supports:
            opinion = _support_opinion(praf, edge)
            supports[edge] = _expectation(opinion)

    if strategy == "dfquad_quad":
        if tau is None:
            raise ValueError("dfquad_quad requires explicit tau")
        strengths = compute_dfquad_quad_strengths(
            praf,
            supports,
            tau=tau,
        )
    elif strategy == "dfquad_baf":
        if tau is not None:
            raise ValueError("dfquad_baf does not use tau")
        strengths = compute_dfquad_baf_strengths(
            praf,
            supports,
        )
    else:
        raise ValueError(
            "strategy='dfquad' is ambiguous; use 'dfquad_quad' or 'dfquad_baf'"
        )

    return PrAFResult(
        acceptance_probs=strengths,
        extension_probability=None,
        strategy_used=strategy,
        strategy_requested=strategy,
        downgraded_from=None,
        samples=None,
        confidence_interval_half=None,
        semantics=strategy,
        query_kind="gradual_strength",
        inference_mode=None,
        queried_set=None,
    )


def compute_probabilistic_acceptance(*args: Any, **kwargs: Any) -> PrAFResult:
    return _compute_probabilistic_acceptance(*args, **kwargs)


ProbabilisticResult = PrAFResult


__all__ = [
    "ProbabilityValue",
    "ProbabilisticAF",
    "ProbabilisticArgumentationFramework",
    "PrAFResult",
    "ProbabilisticResult",
    "compute_probabilistic_acceptance",
    "summarize_defeat_relations",
]
