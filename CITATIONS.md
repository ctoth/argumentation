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
