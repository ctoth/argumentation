# Architecture

`argumentation` owns finite formal argumentation objects and algorithms. It is
not a propstore adapter layer.

## Kernel Boundary

The package includes:

- Dung abstract argumentation frameworks and extension semantics.
- ASPIC+ literals, rules, arguments, attacks, defeats, and CSAF construction.
- Cayrol-style bipolar argumentation frameworks and semantics.
- Optional Z3-backed Dung extension enumeration.
- Generic preference helpers when they do not depend on propstore claim rows.

The package excludes:

- Scientific-claim storage and compilation.
- Source, stance, context, provenance, sidecar, worldline, and CLI workflows.
- CEL condition solving and propstore-specific policy.
- Compatibility shims for old propstore import paths.

## Backend Policy

Pure Python algorithms are the reference implementations. Optional solver
backends must produce the same formal results as the reference implementation
on the same finite framework, except when the solver explicitly reports
unknown.

Optional backends must keep solver-result plumbing local to this package. They
must not import propstore CEL or sidecar modules.

## Z3 Backend

`argumentation.dung_z3` provides SAT-backed enumeration for complete,
preferred, and stable extensions. It uses the local `argumentation.solver`
result wrappers:

- `SolverSat`
- `SolverUnsat`
- `SolverUnknown`
- `Z3UnknownError`

`z3-solver` is an optional package dependency and a development dependency for
the test suite.
