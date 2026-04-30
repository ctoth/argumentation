# Citations

## `argumentation.dung.stable_extensions`

Stable extensions follow Dung 1995 Definition 12 for the base abstract
argumentation framework: a stable extension is conflict-free and must defeat
every argument outside the extension.

When an `ArgumentationFramework` includes both `attacks` and `defeats`, this
package uses the Modgil and Prakken preference-aware split: stable extensions
are attack-conflict-free over the pre-preference `attacks` relation, and they
defeat every argument outside the extension through the post-preference
`defeats` relation.

## `argumentation.probabilistic` strategy `exact_dp`

`compute_probabilistic_acceptance(strategy="exact_dp", ...)` reuses the tree
decomposition setup of Popescu and Wallner (2024) but the executable dynamic
programme is an adapted grounded-acceptance edge-tracking backend, not their
full I/O/U witness-table algorithm. It currently supports only credulous
grounded acceptance on defeat-only worlds (no support relations,
`attacks == defeats`); calling it on richer queries raises.

Its current tables key on full edge sets and forgotten arguments, so the
asymptotic complexity is not better than brute-force enumeration; the backend
is effective in practice for primal-graph treewidth ≤ ~15.

The paper-faithful Popescu and Wallner Algorithm 1 is exposed separately as
strategy `paper_td`, which is opt-in and answers `extension_probability`
queries only.
