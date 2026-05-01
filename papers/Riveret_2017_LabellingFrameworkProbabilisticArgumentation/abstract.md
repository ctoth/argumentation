---
paper: Riveret_2017_LabellingFrameworkProbabilisticArgumentation
---

## Verbatim Abstract

The combination of argumentation and probability paves the way to new accounts of qualitative and quantitative uncertainty, thereby offering new theoretical and applicative opportunities. Due to a variety of interests, probabilistic argumentation is approached in the literature with different frameworks, pertaining to structured and abstract argumentation, and with respect to diverse types of uncertainty, in particular the uncertainty on the credibility of the premises, the uncertainty about which arguments to consider, and the uncertainty on the acceptance status of arguments or statements. Towards a general framework for probabilistic argumentation, we investigate a labelling-oriented framework encompassing a basic setting for rule-based argumentation and its (semi-) abstract account, along with diverse types of uncertainty. Our framework provides a systematic treatment of various kinds of uncertainty and of their relationships and allows us to back or question assertions from the literature.

## Interpretation

The paper tackles a real fragmentation problem in probabilistic argumentation: different communities use different probability spaces for different kinds of uncertainty (structural vs. acceptance vs. epistemic), making comparison difficult. The solution is elegant — extend the labelling alphabet from {IN, OUT, UN} to include ON/OFF for "is this argument even in play?", then define probability distributions over the full labelling space. This creates a hierarchy of probabilistic frames (PTF for theories, PGF for graphs, PLF for labellings) where each subsumes the previous. The PLF level is expressive enough to capture both the constellations approach (probability over which arguments exist) and the epistemic approach (probability over which arguments are accepted) as special cases, plus their combination. The statement-level extension (probabilistic labelling of literals) is particularly valuable for practical systems that need to reason about conclusion-level uncertainty rather than just argument-level.
