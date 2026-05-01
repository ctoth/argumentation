# Citations

## Reference List

Atkinson, K., Holt, K., and Sherr, A. 1995. Foundations of AI and Law. Morgan Kaufmann.

Besnard, P., Garcia, A., Hunter, A., Modgil, S., Prakken, H., Simari, G., and Toni, F. 2014. Special issue on tutorials on structured argumentation. *Argument Comput.*, 5(1).

Brewka, G., and Eiter, T. 1999. Preferred answer sets for extended logic programs. *Artif. Intell.* 109(1-2):297-356.

Brown, V., Heckler, M., and Wellman, S. 2023. On the size complexity of grounding: tracking ASP-based benchmarks via systematic progress and traceoffs. In *ECAI*.

Caminada, M., and Schulz, C. 2017. On the equivalence between assumption-based argumentation and logic programming. *Journal of Artificial Intelligence Research* 665-739.

Calero, G., Calzaroga, R., and Okonkoy, A. 2021. 2B or not: A logic-based successor set for symbolic AI. *Salzburg: IA AAAI*.

Coste, R., and Toni, F. 2016. Argument graphs and assumption-based argumentation. *Artif. Intell.* 233:1-59.

Cyras, K., and Toni, F. 2016. ABA+ assumption-based argumentation with preferences. *KR 2016*.

Diller, M., Gaggl, S. A., and Goverza, P. 2021. First-order grounding in ASPIC+. And formal and heuristic approaches in structured argumentation. *Tech. Rep. AAAI 2021*.

Dung, P. M. 1995. On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77:321-357.

Fichte, J. K., Gaggl, S. A., and Rusovac, D. 2022. Rushing and strolling among answer sets — navigation made easy. In *Proc. AAAI*, volume 5467 of *Lecture Notes in Computer Science*. 5-20. Springer.

Gebser, M., Kaminski, R., Kaufmann, B., Lühne, P., and Schaub, T. 2015. *Abstract grunge: Theory and practice of logic programming.* 15(4-5):731-745.

Gebser, M., Kaminski, R., Kaufmann, B., Lifschitz, V., and Schaub, T. 2015. Abstract grunge: Theory and practice of logic programming. 15(4-5):731-745.

Gordon, T., and Walton, D. 2016. Formalizing balancing arguments. In *Proc. COMMA*, 327-338.

Hanisch, P., and Rauschenbach, F. 2025. ANGRY: A grounder for rule-based argumentation. https://doi.org/10.5281/zenodo.14677451.

Jordan, H., Scholz, B., and Subotic, P. 2016. Souffle: On synthesis of program analyzers. In *CAV*, volume 9980 of *Lecture Notes in Computer Science*, 422-430. Springer.

Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2021. Declarative algorithms and complexity results for assumption-based argumentation. *J. Artif. Intell. Res.* 71:265-318.

Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2022. ASP-based algorithms for the alternative-based and abstraction-based semantics for ASPIC+.

Lehtonen, T., Wallner, J. P., and Järvisalo, M. 2022. ASP-based algorithms for the alternative-based or abstraction-based semantics for ASPIC+. In *COMMA*, 225-236.

Mahmood, Y., Gabbay, D., and Oren, N. 2025. Advancing lazy grounding ASP solving techniques: restarts, phase-saving, backjumping, and more. *Theory Pract. Log. Programming* 25(3):609-624.

Matt, P.-A., and Toni, F. 2008. A game-theoretic measure of argument strength for abstract argumentation. In *JELIA*, volume 5293 of *Lecture Notes in Computer Science*, 285-297.

Modgil, S. and Prakken, H. 2018. Abstract rule-based argumentation. In Baroni, P., Gabbay, D., and Giacomin, M., eds., *Handbook of Formal Argumentation*. College Publications, 287-364.

Monk, V. W., and Truszczynski, M. 1999. Stable models and an alternative logic programming paradigm. *Artificial Intelligence Symposium*, 375-398.

Monterosso, G., Gaggl, S. A., Diller, M., Hanisch, P., and Rauschenbach, F. 2025. Benchmark instances for ANGRY: A grounder for rule-based argumentation.

Nute, D. 1987. Defeasible reasoning and decision support systems. *Decision Support Systems*, 4(1):97-110.

Nuter, T., Pan, R., Malik, B., Hantsch, L., Wu, Z., and Banerjee, J. 2013. REFINe: A Highly scalable RIF rule engine. In *RR'13*, volume 5437 of *Lecture Notes in Computer Science*. 7-20. Springer.

Oikarinen, E., and Woltran, S. 2011. Characterizing strong equivalence for argumentation frameworks. *Artificial Intelligence*, 175(14-15):1985-2009.

Okerlund, O., Lehtonen, T., Burg, A., Wallner, J. P., and Järvisalo, M. 2025. Assumption-based argumentation equipped with preferences and its application to decision making. In Marquis, P., Ortiz, M., and Pagnucco, M., eds., *KR 2025*. International Joint Conferences on Artificial Intelligence Organization.

Parsons, A., and Wallner, J. P. 2023. Reasoning in assumption-based argumentation using tree-decomposition. In *JELIA*, volume 14281 of *Lecture Notes in Computer Science*, 192-208. Springer.

Pollock, J. 2010. Defeasible reasoning and degrees of justification. *Argument and Computation*, 1:7-22.

Prakken, H. 2010. An abstract framework for argumentation with structured arguments. *Argument Comput.* 1(2):93-124.

Prakken, H., and Sartor, G. 2015. Law and logic: a review from an argumentation perspective. *Artificial Intelligence*, 227:214-245.

## Key Citations for Follow-up

- **Lehtonen, Wallner, Järvisalo 2021** — ASPforASPIC: the main comparison system. Declarative algorithms translating ASPIC+ to ASP. Directly relevant as the propositional ASPIC+ solver that ANGRY's grounding feeds into.
- **Modgil and Prakken 2018** — The canonical ASPIC+ reference. Handbook chapter defining the framework that this paper grounds. Already in propstore's collection.
- **Hanisch and Rauschenbach 2025** — ANGRY system paper. The actual implementation described in this paper. Essential for anyone wanting to use the prototype.
- **Gebser et al. 2015** — Clingo/gringo grounding infrastructure. The ASP grounding technology that ANGRY's Datalog approach is compared against and partially inspired by.
- **Jordan, Scholz, Subotic 2016** — Souffle Datalog engine. The high-performance Datalog engine that could serve as the back-end for ANGRY-style grounding in propstore.
