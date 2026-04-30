# ICCMA Solver Adapter Workstream

## Goal

Replace the current minimal subprocess wrapper with a protocol-conformant
ICCMA adapter for official input, invocation, and output behavior.

## Primary Sources

- Jarvisalo, Lehtonen, and Niskanen (2025), ICCMA 2023 report, especially input
  formats, output formats, witness checking, and IPAFAIR sections.
- ICCMA competition web pages and solver-call specifications for the target
  year.
- Solver documentation for at least one real ICCMA-compatible backend.

Reread page images or primary web pages before encoding a command-line,
problem-code, or output-format assumption.

## Current State

- `argumentation.solver_adapters.iccma_af` writes numeric `p af n` input and
  uses the ICCMA 2023 `solver -p <task> -f <file> [-a <query>]` protocol.
- It parses typed DC/DS/SE outputs including `YES`, `NO`, witnesses,
  counterexamples, and no-extension SE output.
- Optional real-solver smoke coverage is gated by `ICCMA_AF_SOLVER`.

## Execution Mode

Use TDD:

1. Reread the source page defining the protocol feature.
2. Add a failing fixture or Hypothesis property derived from that page.
3. Implement one protocol behavior.
4. Test against fixture-only mocked solvers first, then at least one real solver
   when available.

Generated properties must encode official format guarantees, not local
convenience assumptions.

## Phases

### Phase 1: Output Parser Conformance

- Implement a typed output model for DC, DS, and SE tasks.
- Parse `YES`, `NO`, and `w ...` witness/counterexample lines according to the
  ICCMA report.
- Represent no-extension output for single-extension tasks.
- Preserve raw stdout/stderr for diagnosis.

Paper-derived properties:

- DC accepted output with `YES` and a witness contains the query in the witness
  for main/no-limits tracks.
- DS rejected output with `NO` and a counterexample omits the query from the
  counterexample for main/no-limits tracks.
- SE output is either one witness line or `NO` when no extension exists.
- Approximate/ABA track variants that require only `YES`/`NO` must not be
  parsed as if witnesses are mandatory.

Acceptance criteria:
- Parser fixtures cover every output form listed in the ICCMA report section.
- Malformed witness lines produce structured errors, not silent empty results.

### Phase 2: Invocation Model

- Determine the official invocation contract for the selected solver family.
- Replace `[binary, problem, path]` if the official contract uses flags,
  argument order, or stdin differently.
- Keep backend-specific wrappers separate from the protocol parser.

Source-derived properties:

- For a mock solver implementing the official CLI, the adapter sends exactly
  the expected task code and input path/stdin.
- Timeout and nonzero return code handling preserve enough context to debug the
  failing solver.

Acceptance criteria:
- At least one mocked backend fixture proves the official command shape.
- The adapter API states which ICCMA year/protocol it supports.

### Phase 3: Input Format Compatibility

- Reuse `argumentation.iccma.write_af` for official `p af n` files.
- Add property tests for parse/write round-trip over generated numeric AFs.
- Reject non-numeric or non-contiguous arguments before solver invocation with a
  clear error.

Paper-derived properties:

- Numeric AF files use arguments indexed consecutively from `1` to `n`.
- Attack lines contain exactly two numeric IDs in range.
- Comment handling matches the official grammar.

Acceptance criteria:
- Adapter never writes APX predicates when the selected protocol expects
  numeric `p af n`.

### Phase 4: Real Solver Smoke Test

- Select one installable solver that can be obtained without local path pins.
- Add an optional integration test gated by executable availability.
- Compare solver output against package-native semantics on small generated AFs.

Paper/source-derived properties:

- Witnesses returned for SE tasks satisfy the requested semantics.
- DC/DS answers agree with package-native semantics on small AFs.

Acceptance criteria:
- Optional integration tests skip cleanly when the solver is unavailable.
- No dependency metadata points to a local path.

## Tests

Targeted commands:

```powershell
uv run pytest tests\test_solver_adapters.py tests\test_iccma.py -q
```

Full verification:

```powershell
uv run pytest -q --timeout=600
uv run pyright src
git diff --check
```

## Completion Criteria

- The adapter states the exact ICCMA protocol year it implements.
- Output parsing covers DC, DS, and SE official forms.
- Invocation behavior is validated by tests, not assumed.
- At least one optional real-solver smoke test exists.

## Known Traps

- A `w` line alone is not the whole protocol for DC/DS tasks.
- Do not generalize one solver's CLI into "ICCMA" without primary-source
  support.
- Do not commit local executable paths, local dependency pins, or machine-local
  solver locations.
