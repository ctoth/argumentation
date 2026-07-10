# ABA Duplicate Contrary Declaration Plan

Date: 2026-07-10

Status: Active under the remediation master plan.

Parent: [`2026-07-10-codex-review-remediation-master.md`](2026-07-10-codex-review-remediation-master.md)

## Objective

Reject duplicate ABA contrary declarations in both supported ICCMA syntaxes
instead of silently replacing the earlier value in a dictionary.

## Input Contract

A contrary relation is functional per assumption. A source file that declares
the same assumption's contrary more than once is invalid, even when the repeated
right-hand side is textually identical. Rejecting identical duplicates keeps
the grammar deterministic and prevents hidden copy/paste errors.

If the checked-in format specification explicitly permits repeated identical
declarations, update this contract from the specification before editing code;
do not infer permission from current overwrite behavior.

## Red Contracts

Add parameterized parser tests covering both compact and numeric formats:

1. Duplicate assumption with two different contraries is rejected.
2. Duplicate assumption with the same contrary is rejected.
3. The error identifies the duplicated assumption and the later source line.
4. A single contrary per assumption continues to parse.
5. Different assumptions may have the same contrary when the format permits it.
6. Serializer output contains exactly one declaration per assumption and
   round-trips unchanged.

Commit the failing tests before production edits.

## Green Implementation

1. At each existing contrary parse site in
   `src/argumentation/interop/iccma.py`, check whether the assumption already has
   a declaration before assignment.
2. Raise the parser's existing precise format/validation exception with source
   location and assumption identity.
3. Do not add a generic declaration adapter or parser helper solely to combine
   two small syntax branches. Reuse an existing owner only if one already
   expresses this exact validation.
4. Preserve all other compact/numeric parsing and serialization behavior.

## Audit Boundary

Search the ABA parsers for any second path that builds the contrary map. Every
accepted input syntax must enforce the same uniqueness rule. Do not broaden the
slice to unrelated duplicate declarations unless a test proves that they share
the exact same functional-relation contract.

## Acceptance Gates

```powershell
uv run pytest -q tests/interop -k "aba and (contrary or parse or roundtrip)"
uv run pytest -q tests/aba
uv run pytest -q
uv run pyright src
uv run import-linter
git diff --check
```

Use exact current paths discovered during execution.

## Done When

- Neither compact nor numeric syntax can silently overwrite a contrary.
- Duplicate diagnostics identify the assumption and source location.
- Valid ABA round trips remain stable.
- No parallel parser or compatibility path was introduced.
- The fix is committed independently of every other remediation family.
