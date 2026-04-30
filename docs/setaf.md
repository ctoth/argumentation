# SETAF Semantics and I/O

This package models finite SETAFs as pairs `(A, R)` where `A` is a finite set
of arguments and each collective attack in `R` is a pair `(T, h)` with nonempty
tail `T` and head `h`.

The implemented core semantics follow the SETAF definitions reread from the
splitting paper page images:

- A set `S` attacks argument `a` iff there is an attack `(T, a)` with `T <= S`.
- `S` is conflict-free iff no active attack targets an argument in `S`.
- `S` defends `a` iff, for every attacking tail `T` that attacks `a`, `S`
  attacks at least one member of `T`.
- Complete extensions are admissible fixed points of the characteristic
  function; grounded is the subset-minimal complete extension; preferred
  extensions are inclusion-maximal admissible sets; stable extensions are
  conflict-free sets whose SETAF range is all arguments.

## I/O Formats

`argumentation.setaf_io` supports the ASPARTIX SETAF fact format documented by
TU Wien:

```prolog
arg(a).
arg(b).
arg(c).
att(r1,c).
mem(r1,a).
mem(r1,b).
```

The parser and writer use only `arg/1`, `att/2`, and `mem/2` facts. Attack
names identify collective attacks; `att(Name, Target)` gives the head and
`mem(Name, Argument)` facts give the nonempty tail.

The compact `p setaf` format is retained only as a package-local helper through
`parse_compact_setaf` and `write_compact_setaf`. It is not documented or exposed
as an ICCMA SETAF format. The checked ICCMA 2023 rules document AF and ABA input
formats, not a SETAF/collective-attack track format.

## Splitting

The current surface is core SETAF semantics plus SETAF I/O. It does not
implement the splitting algorithms from the splitting paper, and callers should
not infer splitting support from the core SETAF semantics.
