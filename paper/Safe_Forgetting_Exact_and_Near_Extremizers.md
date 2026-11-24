# Which distinctions can a coloring algorithm safely discard?

Research and replication report · November 23, 2026

## Main result

The earlier paper proved the sharp upper bound d ≤ 5V/12 and left recognition of equality open. There is a deterministic polynomial-time algorithm that decides exact attainment, produces an extremal flat if one exists, and counts the distinct extremal flats. Equality is literal, without rounding. This result holds independently of the arithmetic-circuit preprint.

## Search under near-extremal promise

If every satisfiable input is promised a flat within O(log V) dimensions of the maximum, a deterministic polynomial-time algorithm finds a coloring (or correctly rejects). The algorithm repeatedly removes autarkies on at most 14 points. On a promised YES instance at most ⌊240k/7⌋ triples remain; exhaustive search on the residual is then polynomial when k = O(log V).

Under the Exponential Time Hypothesis, any efficiently testable allowance growing asymptotically faster than log V precludes a polynomial-time algorithm for that promise problem.

## Relation to Residual Exclusion

A polynomial-time exclusion on every batch of independent SAT branches remains open. The same actor works on the high-dimension subclass identified above.

## Reproducibility

All new suites (recognition, peeling, stability, gluing, border, etc.) and the prior three-actor and weighted-coloring packages reproduced. See the companion archive for full proofs and code.
