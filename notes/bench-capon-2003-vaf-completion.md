# Bench-Capon 2003 VAF completion obligations

Source: Trevor J. M. Bench-Capon, "Persuasion in Practical Argument Using
Value-based Argumentation Frameworks", Journal of Logic and Computation 13(3),
2003, printed pp. 438-447.

This note records the surfaces implemented by WS-O-arg-vaf-completion. It uses
the paper's printed page numbers.

## Printed p. 438

- Definition 6.3 defines an argument chain as a same-value sequence where the
  first argument has no attacker in the chain and every later argument is
  attacked only by its predecessor in the chain.
- Same-value attacks always succeed, so acceptance alternates by one-based
  parity along the chain.
- Theorem 6.4 states that an AVAF with no single-valued cycles has a unique
  non-empty preferred extension.

## Printed p. 439

- Definition 6.5 defines a line of argument for a target argument as chains
  with distinct values.
- The target argument is the last argument of the first chain.
- The last argument of each later chain attacks the first argument of the
  previous chain.
- A line terminates when extending it would repeat a value.

## Printed pp. 440-441

- Theorem 6.6 applies only when there are no single-valued cycles and each
  argument has at most one attacker.
- Under those preconditions, a target is objectively acceptable when it is in
  an odd position in the first chain and there is no later odd-length chain.
- A target is indefensible when it is in an even position in the first chain
  and there is no later odd-length chain.
- A target is subjectively acceptable when a later chain has odd length.
- Corollary 6.7 characterizes two-value cycles by chain parity and the
  audience-preferred value.

## Printed pp. 444-447

- Factual arguments are represented by a special value ranked above every
  ordinary value for every reasonable audience.
- A factual argument can block a value dispute from defeating an accepted
  factual claim.
- Factual uncertainty can create multiple preferred extensions even for a
  fixed ordinary value ordering.
- Under uncertainty, fully persuasive objective status requires the argument
  in every preferred extension for every reasonable value ordering.
