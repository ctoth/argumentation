# `attacks` / `defeats` Semantics Decision Plan

Date: 2026-07-10

Status: Completed on 2026-07-10.

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
| Plain Dung | conflict-free / naive | canonical `defeats` relation (the paper's single `attacks` relation) | `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png` | `core/dung.py::naive_extensions` | current behavior correct |
| Plain Dung | defense / admissible | canonical `defeats` relation for both attack and counterattack | `papers/Dung_1995_AcceptabilityArguments/pngs/page-005.png` | `core/dung.py::admissible` | current behavior correct |
| Plain Dung | range / stage | canonical `defeats` relation for conflict-free candidates and range | `papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-002.png` | `core/dung.py::stage_extensions` | current behavior correct |
| Plain Dung | SCC decomposition / CF2 | canonical `defeats` relation for SCCs, component defeat, and naive base | `papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-003.png`; `page-004.png` | `core/dung.py::_is_scc_recursive_extension` | current behavior correct |
| Structured projection | conflict-free / naive | full pre-preference `attacks` relation | `papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-013.png` | `core/dung.py::naive_extensions` | implementation defect |
| Structured projection | defense / admissible | `attacks` for conflict-freedom; preference-filtered `defeats` for defense | `papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-011.png`; `page-013.png` | `core/dung.py::admissible` | current behavior correct |
| Structured projection | range / stage | no paper-defined mixed relation; Gaggl uses one `R`, and Modgil-Prakken's supported extension list omits stage | `papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-002.png`; `papers/Modgil_2018_GeneralAccountArgumentationPreferences/pngs/page-013.png` | `core/dung.py::stage_extensions` | unsupported input must be rejected |
| Structured projection | SCC decomposition / CF2 | no paper-defined mixed relation; Gaggl uses one `R` throughout SCC recursion and naive base | `papers/Gaggl_2013_CF2ArgumentationSemanticsRevisited/pngs/page-002.png`; `page-003.png`; `page-004.png` | `core/dung.py::cf2_extensions` | unsupported input must be rejected |

Allowed verdicts are `current behavior correct`, `implementation defect`, or
`unsupported input must be rejected`. Do not use “probably.”

### Pre-Remediation Distinguishing Result

For arguments `{a, b}`, full attacks `{(a, b)}`, and no surviving defeats,
current `main` returns:

- naive: `{a, b}`, because it incorrectly reads only `defeats`;
- admissible: `{}`, `{a}`, `{b}`, which correctly combines attack-based
  conflict-freedom with defeat-based defense;
- stage: `{a}` and `{b}`, a hybrid of attack-based candidates and
  defeat-based range that neither cited framework defines; and
- CF2: `{a, b}`, because SCC decomposition and its naive base read different
  effective relations.

The executable policy will preserve the admissible result, make naive maximal
over the attack-conflict-free sets, and reject distinct-relation stage, stage2,
and CF2 input before SCC/range computation. Frameworks with `attacks=None` or
`attacks == defeats` remain ordinary single-relation Dung frameworks.

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

## Execution Record

- Paper-backed decision table and RED policy contracts: `fffa976`.
- Structured naive correction: `c666720`.
- Mixed-relation stage rejection: `ebce2ee`.
- Mixed-relation CF2/stage2 rejection: `f928589`.
- The paper-reader skill found the Dung, Modgil-Prakken, and Gaggl paper
  artifacts already complete; the adjudication reread the cited page images
  directly and did not mutate paper artifacts.
- Pure Dung and identical-relation frameworks retain exact naive, admissible,
  stage, and CF2 extension sets on the distinguishing two-argument graph.
- Structured naive is now maximal over attack-conflict-free sets, while
  structured admissibility preserves attack-based conflict-freedom and
  defeat-based defense.
- Stage rejects distinct relations before range computation; stage2 and CF2
  reject before SCC decomposition. No relation is silently copied or selected.
- `uv run pytest -q tests -k "naive or admissible or stage or cf2 or aspic"`:
  208 passed, 2826 deselected.
- `uv run pyright src`: 0 errors, 0 warnings.
- `uv run lint-imports`: 2 contracts kept, 0 broken.
- Calibrated full gate: 3030 passed, 3 skipped, 1 xfailed in 293.23s.
