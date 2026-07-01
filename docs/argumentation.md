# Argumentation

propstore uses formal argumentation to resolve disagreements between scientific claims. This document covers the reasoning backends, conflict detection, and belief tracking systems.

## Dung abstract argumentation

The external `argumentation.dung` kernel implements Dung's abstract argumentation framework AF = (Args, Defeats). Propstore builds those frameworks from active claims, stances, contexts, and preferences, then delegates extension computation through `argumentation.semantics`.

- **Grounded extension** — the unique minimal complete extension (skeptical reasoning)
- **Complete extensions** — every admissible set that contains all arguments it defends (Dung 1995 Def 10)
- **Preferred extensions** — maximal admissible sets (credulous reasoning)
- **Stable extensions** — conflict-free sets that defeat all external arguments

Two kernel backends are available through the external package: brute-force enumeration (`argumentation.dung`) and Z3 SAT encoding (`argumentation.dung_z3`) for scalability. `argumentation.semantics` provides the generic set-returning dispatch over Dung, bipolar, and partial-AF dataclasses; propstore keeps backend validation, projection, and rendering policy.

## Claim-graph bridge

The bridge layer (`claim_graph.py`) converts raw stances into a Dung AF:

1. Load stances between active claims with confidence above threshold
2. Undercutting and supersedes attacks always become defeats
3. Rebutting and undermining attacks become defeats only if the attacker is at least as strong as the target (elitist comparison) or the attacking set is at least as strong (democratic comparison)
4. Build the Dung AF from surviving defeats
5. Compute extensions under chosen semantics

propstore ships multiple reasoning backends at different abstraction levels. The **claim-graph** backend builds a Dung AF over active claim rows using heuristic metadata for preferences, then calls `argumentation.semantics`. The **structured-projection** and **aspic** backends use `propstore.aspic_bridge` to translate situated propstore claims as `ist(context, proposition)` literals into `argumentation.aspic` objects for full ASPIC+ argument construction (recursive PremiseArg/StrictArg/DefeasibleArg, three-type attack determination per Modgil & Prakken 2018 Def 8, last-link/weakest-link preference defeat per Defs 19-21). Context lifting decisions project as formal rules only when the decision is `lifted`; `blocked` and `unknown` decisions stay as provenance-bearing non-commitment records. See [Structured Argumentation](structured-argumentation.md) for full details. The **praf** backend keeps propstore opinion/calibration/provenance adapters, then calls the float-valued `argumentation.probabilistic` kernel for MC sampling (Li et al. 2012), exact enumeration, exact-DP, and DF-QuAD gradual semantics (Freedman et al. 2025). Optional COH enforcement over subjective opinions remains in propstore. See [Probabilistic Argumentation](probabilistic-argumentation.md) for full details. The **atms** backend provides label propagation and bounded replay over the active belief space (de Kleer 1986).

The package boundary for the reusable formal kernel is recorded in
[Argumentation Package Boundary](argumentation-package-boundary.md). The
execution workstream was
`plans/argumentation-package-extraction-workstream-2026-04-18.md`.

## Goal-directed queries

For querying the argumentation status of a single claim without building the full CSAF, use `query_claim()` from `propstore/aspic_bridge.py`. This uses backward chaining to construct only the arguments relevant to a specific conclusion. See [Structured Argumentation — Goal-Directed Query](structured-argumentation.md#goal-directed-query-backward-chaining) for details.

## Conflict detection

See [Conflict Detection](conflict-detection.md) for full details.

When two claims bind to the same concept, the conflict detector classifies them:

| Class | Meaning |
|-------|---------|
| `COMPATIBLE` | Values consistent (within tolerance or overlapping ranges). Not reported. |
| `PHI_NODE` | Values differ, conditions fully disjoint (Z3-verified). Not a conflict — they describe different regimes. |
| `CONFLICT` | Values differ, conditions identical or both unconditional. Genuine disagreement. |
| `OVERLAP` | Values differ, conditions partially overlapping. Needs investigation. |
| `PARAM_CONFLICT` | Conflict detected via parameterization chain: claim A and claim B individually consistent, but deriving through a shared formula produces contradictory outputs. |

Condition disjointness is checked via Z3 satisfiability. Category concepts get EnumSorts, quantity concepts get Reals, boolean concepts get Bools. Condition pairs are first grouped into equivalence classes by structural similarity, so Z3 is only called once per unique condition pattern.

## Semantic axes

- `reasoning_backend` selects the argumentation backend used when a render policy asks for argumentation-based conflict resolution.
- `claim_graph` remains the default backend and preserves the current claim-row projection and behavior.
- `aspic` is the canonical structured-argument backend over active claims plus exact support metadata.
- `atms` is a global label/nogood propagation backend over the active belief space. It is an ATMS-style engine pass, not a full de Kleer runtime manager, not AGM entrenchment, and not full ASPIC+.
- Formal belief-set revision operators live in the external `belief_set` package. Formal AF revision lives in `argumentation.af_revision`. `propstore.support_revision` is only an operational support-incision adapter for scoped worldline capture; argumentation consumers do not treat it as AGM or AF-revision semantics.
- `resolution_strategy` selects how to pick a winner when a conflicted concept still has multiple active claims after belief-space reasoning.
- `comparison` selects the preference-comparison rule used inside the claim-graph argumentation backend.

## ATMS backend

The ATMS (Assumption-based Truth Maintenance System) backend provides label propagation and nogood pruning over the active belief space. It tracks exact support only — which assumptions justify each claim. See [ATMS](atms.md) for full details.

The `atms` backend does not expose Dung extensions. `pks world extensions --backend atms` is rejected by design. Use the ATMS-native commands instead:

```bash
# Show ATMS status, support quality, and essential support
pks world atms status domain=argumentation

# Show which exactly supported claims hold in the current bound environment
pks world atms context domain=argumentation

# Run ATMS label self-checks
pks world atms verify domain=argumentation

# Show bounded future environments for a claim or concept
pks world atms futures claim_id domain=argumentation --queryable framework=general

# Explain whether an OUT status is missing support or nogood-pruned
pks world atms why-out claim_id domain=argumentation --queryable framework=general

# Show bounded stability and witness futures
pks world atms stability claim_id domain=argumentation --queryable framework=general

# Show which queryables matter, with witness flips
pks world atms relevance claim_id domain=argumentation --queryable framework=general

# Show bounded additive intervention plans over declared queryables
pks world atms interventions claim_id domain=argumentation --target-status IN --queryable framework=general

# Show next-query suggestions derived from actual minimal intervention plans
pks world atms next-query claim_id domain=argumentation --target-status IN --queryable framework=general
```

### Capabilities by layer

The labelled core and `atms` backend track exact support only. Semantically compatible Z3 activation and context visibility are preserved for activity, but not upgraded into exact labels or unconditional support by fiat.

- **Label propagation** — `TRUE`, `IN`, and `OUT` statuses exposed directly from propagated labels
- **Essential support** — shared core across compatible supporting environments
- **Justification traces** — nogood provenance exposed for inspection
- **Future analysis** — bounded candidate environments that could activate or block exact support; `OUT` statuses distinguish missing support from nogood-pruned
- **Stability and relevance** — whether a claim keeps the same status across all bounded consistent future replays, and which declared queryables can flip it
- **Intervention planning** — minimal bounded additive queryable sets that reach a requested target status; next-query suggestions derived from actual minimal plans

These remain bounded replay over admitted future queryables. This is not AGM revision, entrenchment maintenance, or full structured-argument dynamics. Formal revision operators live in `belief_set`; support-incision capture lives in `propstore.support_revision`.

## Extensions CLI

```bash
# Show the grounded extension (claims that survive all attacks)
pks world extensions --semantics grounded

# Preferred extensions under condition bindings
pks world extensions domain=argumentation --semantics preferred

# Stable extensions with democratic set comparison
pks world extensions --semantics stable --set-comparison democratic
```

The grounded extension is unique and represents the skeptically justified claims. Preferred extensions are maximal admissible sets — each represents a credulous position. Stable extensions (when they exist) are the strongest: conflict-free sets that defeat every non-member.

## Bipolar argumentation

The bipolar kernel (`argumentation.bipolar`) implements Cayrol 2005: support relations create derived defeat paths via fixpoint computation. Propstore's claim-graph and PrAF adapters decide which claim relations become support or defeat inputs. See [Bipolar Argumentation](bipolar-argumentation.md) for full details.

## Partial AFs and AF revision

Repository semantic merge uses `argumentation.partial_af` for the formal partial-AF partition, completion enumeration, skeptical/credulous completion queries, and Sum/Max/Leximax merge operators. Propstore storage code owns branch comparison, emitted merge arguments, and two-parent merge commits.

AF-level revision operators live in `argumentation.af_revision`; propstore worldline and support-revision modules only adapt active support state into those formal inputs.

## Subjective logic and calibration

See [Subjective Logic and Calibration](subjective-logic.md) for full details.

The opinion algebra (`opinion.py`) implements Jøsang 2001: Opinion = (b,d,u,a) with negation, conjunction, disjunction, consensus fusion, discounting, ordering, and uncertainty maximization. `calibrate.py` provides temperature scaling (Guo et al. 2017), corpus CDF calibration, evidence-to-opinion mapping (Sensoy et al. 2018), and ECE computation.

Decision criteria at render time: pignistic (default), Hurwicz, lower bound, upper bound — per Denoeux 2019. Interval dominance not yet implemented.

## Future work

Claim/context AGM-style revision semantics are consumed from `belief_set`. Remaining future work is warrant-level revision, plus extended Jøsang operators (deduction, comultiplication, abduction) and interval dominance (Denoeux 2019).
