# Abstract

## Original Text (Paraphrased)

The paper proposes a way to combine value-based reasoning with ASPIC+ by letting an agent's values filter the propositions and defeasible rules available to that agent. This produces a subjective argumentation theory for each agent, from which grounded extensions are computed and then combined into a collective result. The approach differs from standard value-based argumentation frameworks because values shape argument construction itself rather than only the comparison of completed arguments.

## Our Interpretation

The main contribution is a structural integration of values into structured argumentation: instead of attaching value preferences after argument generation, the system uses them to decide what each agent can premise and infer from. That makes the model closer to agent-specific belief filtering than to classical VAF attack priority, and it gives a clean route to collective reasoning by intersecting per-agent grounded extensions.

