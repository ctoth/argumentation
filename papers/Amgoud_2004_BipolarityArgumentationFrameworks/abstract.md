# Abstract

## Original Text (Verbatim)

In this paper, we propose a survey of the use of bipolarity in argumentation frameworks, *i.e.* the presence of two kinds of entities (a *positive* entity and a *negative* entity). An argumentation process follows three steps: building the arguments and the interactions between them, valuating the arguments using or not the interactions and finally defining the acceptability of the arguments. This paper shows on various applications and with some formal definitions that bipolarity appears (in some cases since always) and can be used in each step of this process under different forms.

So, the purpose of this paper is to present *a survey* on the use of bipolarity in argumentation frameworks.

The first section is devoted to the background about abstract argumentation frameworks. Then, the outline of this paper follows the structure of the argumentation process which can be viewed under the form of three steps:

1. the *building of the arguments* and, using the structure of the arguments, the *definition of different interactions between arguments*. An argument can take different forms depending on the domain, but it is generally required to be a structured set of linked propositions or claims. This step has a bipolar aspect illustrated with some applications.
2. the *valuation of these arguments* which can be based only on the interactions between arguments, or can also take into account an intrinsic strength for each argument. The resulting valuation can be crisp or gradual. In this step, the bipolarity appears on the form of the interactions between arguments (support and defeat relations between arguments). We present different formal approaches which take into account this bipolar aspect.
3. the *selection of some arguments using the definition of the acceptability*. In this step, different classes of arguments can be distinguished with different levels of acceptability, and the valuation results can be used in order to define these levels. The bipolar aspect of this step is illustrated by some examples.

---

## Our Interpretation

The paper introduces *bipolarity* — the explicit, simultaneous presence of positive (support) and negative (attack/defeat) interactions — as a missing dimension of Dung-style abstract argumentation. It proposes an abstract bipolar AF `<A, R_def, R_sup>` extending Dung's `<A, R>`, lays out branch-based notions of direct/indirect defeaters/defenders/supporters, proposes axioms (P1–P3, Pg1–Pg4) for a gradual valuation that compensates positive and negative pressure, and sketches a desire-/plan-based selection layer ending in a conflict-free maximal "acceptable set of complete plans" (Def.19). This is the foundational position paper that the subsequent BAF formalisms (Cayrol & Lagasquie-Schiex 2005, Amgoud-Cayrol-Lagasquie-Prade 2008) refine into the now-standard bipolar argumentation framework.
