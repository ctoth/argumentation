# Abstract

## Original Text (Verbatim)

Answer-set programming (ASP) has emerged as a declarative programming paradigm where problems are encoded as logic programs, such that the so-called answer sets of theses programs represent the solutions of the encoded problem. The efficiency of the latest ASP solvers reached a state that makes them applicable for problems of practical importance. Consequently, problems from many different areas, including diagnosis, data integration, and graph theory, have been successfully tackled via ASP. In this work, we present such ASP-encodings for problems associated to abstract argumentation frameworks (AFs) and generalisations thereof. Our encodings are formulated as fixed queries, such that the input is the only part depending on the actual AF to process. We illustrate the functioning of this approach, which is underlying a new argumentation system called ASPARTIX in detail and show its adequacy in terms of computational complexity.

Keywords: abstract argumentation frameworks; answer-set programming; implementation

---

## Our Interpretation

This is the foundational ASPARTIX paper: it gives a uniform reduction of seven Dung-AF semantics (and several generalisations) to fixed disjunctive-datalog queries, with the AF supplied as the only varying input database. The key engineering contribution is that the encoding's data complexity matches the natural complexity of each semantics — saturation/disjunction is used precisely where Σ₂ᴾ/Π₂ᴾ hardness demands it (preferred, semi-stable), while tractable cases stay in stratified datalog (grounded). Relevant as the canonical reference for "compute AF extensions via ASP" and as a template for encoding new semantics in the same paradigm.
