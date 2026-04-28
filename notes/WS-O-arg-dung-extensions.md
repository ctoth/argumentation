# WS-O-arg-dung-extensions Step 0 Inventory

## Source inventory

- `src/argumentation/labelling.py` was a passive value object before this workstream: it exposed `Label`, `Labelling.from_statuses`, and `Labelling.from_extension`, but no legally-in/out predicates and no operational complete, grounded, preferred, stable, semi-stable, eager, or stage2 labelling solvers.
- `src/argumentation/dung_z3.py` exported `z3_stable_extensions`, `z3_complete_extensions`, `z3_preferred_extensions`, and a `solve_with_z3` dispatcher. Its callers were `src/argumentation/dung.py`, `src/argumentation/solver.py`, `tests/test_dung_z3.py`, and `tests/test_dung_backend_differential.py`.
- `src/argumentation/dung.py` selected a Dung extension backend with `_AUTO_BACKEND_MAX_ARGS`, `backend="auto"`, `backend="brute"`, and `backend="z3"`. That is the old dual-path surface to delete.
- `src/argumentation/bipolar.py` already had Cayrol-style derived defeats, d/s/c admissibility, d/s/c preferred extensions, and stable extensions. It lacked grounded and complete entry points.

## Paper-derived implementation targets

- Caminada 2006, p. 3: reinstatement labelling labels an argument `in` iff all its defeaters are `out`, and labels an argument `out` iff it has an `in` defeater.
- Caminada 2006, pp. 3-4: `Ext2Lab` / `Lab2Ext` give the bridge between complete extensions and reinstatement labellings.
- Caminada 2006, p. 4: reinstatement labellings correspond exactly to complete extensions; stable labellings are the reinstatement labellings with no undecided arguments.
- Caminada 2006, p. 5: preferred labellings maximize `in`; grounded labelling maximizes `undec` and equivalently minimizes `in`.
- Caminada 2006, pp. 6-7: semi-stable labellings minimize `undec`; when stable extensions exist, semi-stable and stable coincide.
- Caminada 2006, p. 8: the floating argument example has mutual attacks between `A` and `B`, both attacking `C`, and `C` attacking `D`; preferred semantics keeps the two decisive labellings and rules out all-undec.
- Baroni and Giacomin 2007, pp. 12-13: prudent semantics excludes indirect conflicts; an indirect attack is an odd-length attack path.
- Baroni and Giacomin 2007, pp. 13-14: semi-stable, prudent, and CF2 satisfy/fail distinct principle rows; these are standing property-test targets.
- Gaggl and Woltran 2013, pp. 927-929: SCC-recursive semantics decompose an AF into strongly connected components and propagate component-defeated arguments.
- Gaggl and Woltran 2013, p. 927: stage semantics selects conflict-free sets with maximal range.
- Gaggl and Woltran 2013, p. 937: CF2 can be characterized by SCC-local maximal conflict-free choices after recursively component-defeated arguments are removed; stage2 follows the same SCC-recursive shape with stage as the base.
- Cayrol and Lagasquie-Schiex 2005, pp. 383-386: BAF reasoning uses set-defeat derived from supported and indirect defeat; conflict-free, defence, d-admissibility, and stable extensions are defined over set-defeat.
- Cayrol and Lagasquie-Schiex 2005, p. 380 and p. 385: grounding can be understood by instantiating Dung's characteristic-function construction over the set-defeat relation.
- Amgoud et al. 2008, pp. 22-23: supported defeat and support closure are distinct BAF design axes; this workstream keeps Cayrol's abstract set-defeat semantics and documents richer support modes as deferred.
- Coste-Marquis, Devred, and Marquis 2005, p. 1: prudent semantics prevents two arguments from sharing an extension when one indirectly attacks the other; the paper's Example 1 is the acceptance cautionary case. The local collection lacks `Coste-Marquis_2005_PrudentSemantics/notes.md`; I used the paper PDF available from CiteSeerX for this Step 0 fact and did not treat the adjacent `Coste-Marquis_2005_SymmetricArgumentationFrameworks` notes as a substitute.
