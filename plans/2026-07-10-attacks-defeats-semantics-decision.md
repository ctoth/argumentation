# `attacks` / `defeats` Semantics Decision Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Resolve the review's remaining semantic risk: naive semantics currently uses
`defeats`, while stage/admissibility and CF2-related paths may consult
`attacks` when a structured projection supplies both relations. Establish one
paper-backed relation policy per semantic and make it executable before deciding
whether production code is wrong.

This is initially an adjudication plan. It must not assume that either relation
is universally correct.

## Decision Questions

1. In a plain Dung AF, is `defeats` the sole extension-semantic relation, with
   `attacks` absent or identical by construction?
2. In an ASPIC/preference projection, which relation defines conflict-freeness,
   defense, range, and SCC decomposition?
3. Do naive, admissible, stage, and CF2 semantics intentionally use different
   relations under the cited definitions, or is the current split accidental?
4. If a semantic is not defined for a framework carrying distinct attack and
   defeat relations, should the API reject that input rather than choose
   silently?

## Paper Checkpoint

Read the exact checked-in page images defining:

- the Dung-style semantics implemented by `core/dung.py`;
- Modgil and Prakken's structured/preference attack-to-defeat treatment; and
- the Gaggl/CF2 SCC and conflict-free relation.

Record page-image paths and the relation used for each operation in the decision
table below. Extracted PDF text is not evidence.

## Required Decision Table

Complete this table before production edits:

| Framework kind | Semantic operation | Required relation | Paper image | Current owner | Verdict |
|---|---|---|---|---|---|
| Plain Dung | conflict-free / naive | TBD | TBD | TBD | TBD |
| Plain Dung | defense / admissible | TBD | TBD | TBD | TBD |
| Plain Dung | range / stage | TBD | TBD | TBD | TBD |
| Plain Dung | SCC decomposition / CF2 | TBD | TBD | TBD | TBD |
| Structured projection | conflict-free / naive | TBD | TBD | TBD | TBD |
| Structured projection | defense / admissible | TBD | TBD | TBD | TBD |
| Structured projection | range / stage | TBD | TBD | TBD | TBD |
| Structured projection | SCC decomposition / CF2 | TBD | TBD | TBD | TBD |

Allowed verdicts are `current behavior correct`, `implementation defect`, or
`unsupported input must be rejected`. Do not use “probably.”

## Phase 1: Current-Tree Inventory

1. Inventory every read of `framework.attacks` and `framework.defeats` in core
   semantics, structured projections, solvers, tests, and serializers.
2. Trace how a framework with distinct relations reaches naive, admissible,
   stage, and CF2 entrypoints.
3. Build the smallest concrete framework where `attacks != defeats` and record
   each current result.
4. Separate relation ownership from caching or representation details.

## Phase 2: Executable Policy Contracts

Before changing production code, add tests for every populated row of the
decision table:

- pure Dung behavior when only the canonical relation is supplied;
- structured behavior when an attack is defeated/blocked by preference;
- conflict-free, defense, range, and SCC outcomes on the distinguishing
  framework; and
- explicit rejection for any combination the papers and public API do not
  support.

The contracts must assert extension sets, not merely which attribute was read.
Attribute/route telemetry may supplement the semantic assertion.

## Phase 3: Verdict-Specific Action

### If current behavior is correct

Keep production unchanged, commit only the paper-backed contracts and completed
decision table, and close the review risk as validated.

### If an implementation defect is confirmed

1. Change the existing semantic owner to use the table's required relation.
2. Migrate direct callers if necessary.
3. Delete the inconsistent relation-selection path.
4. Do not create a relation adapter, facade, or compatibility property.
5. Keep each semantic family as a separate red/green Git slice if more than one
   policy is wrong.

### If the input is unsupported

Reject it at the earliest existing semantic boundary with a precise validation
error. Do not silently normalize or copy one relation into the other.

## Operational Contracts

For CF2/SCC and solver routes, assert deterministic route selection and bounded
relation reads on the distinguishing framework. If a relation-policy fix causes
a performance regression, profile the real solver/worker path before selecting
an optimization; do not change semantics to recover speed.

## Acceptance Gates

```powershell
uv run pytest -q tests -k "naive or admissible or stage or cf2 or aspic"
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Use exact current test paths during execution.

## Done When

- Every row in the decision table has a page-image citation and executable
  result contract.
- The current inconsistency is either proven intentional, corrected, or rejected
  as unsupported input.
- All semantics use their established relation without a silent fallback.
- No relation adapter or duplicate semantic path was introduced.
- The focused and full gates pass, and the verdict is committed repo-locally.
