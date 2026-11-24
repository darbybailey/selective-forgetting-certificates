# Selective Forgetting Certificates

**Exact recognition of maximum affine flats in linear four-matching systems, and logarithmic search under a near-extremal promise**

Working paper · November 2026

## Abstract

A linear four-matching system on V points consists of four partitions of the points into triples in which any two triples share at most one point. A valid binary coloring assigns both colors to every triple. An affine flat of dimension d is a set of 2^d valid colorings described by d independent binary parameters.

The sharp upper bound d ≤ 5V/12 was established earlier; recognition of equality was left open. This paper gives a deterministic polynomial-time algorithm that decides exact attainment of the bound, constructs an extremal flat when one exists, and counts the distinct extremal flats. Equality is literal, without rounding.

Under the promise that every satisfiable input has a valid affine flat within O(log V) dimensions of the universal bound 5V/12, a second deterministic polynomial-time algorithm recovers a valid coloring. The algorithm repeatedly extracts small autarkies (support at most 14). On a promised YES instance at most ⌊240k/7⌋ triples remain; exhaustive search of the residual is then polynomial for k = O(log V). Under the Exponential Time Hypothesis the same polynomial guarantee cannot hold for every efficiently testable allowance that grows asymptotically faster than log V.

A polynomial-time procedure that excludes one false nonempty viability pattern on every batch of independent SAT branches (the Residual Exclusion Problem) remains open. A solution to that problem would imply P = NP.

## 1. Exact recognition of the 5V/12 bound

Each triple in a satisfying flat has a permanently opposite pair. Selecting one such pair per triple yields a bipartite graph whose connected components bound the dimension of the flat. A component with s points and e selected pairs satisfies e ≤ 16(s-1)/7. Equality holds only for isolated points or K_{4,4} blocks (eight points, 16 triples). Summing over 4V/3 pairs produces the bound 5V/12. At equality the triples are partitioned into footprints of these eight-point blocks, each contributing one phase, together with free bits from isolated points.

Each K_{4,4} block has eight points and covers 16 triples. The three-candidate limit on footprints per triple holds on inputs attaining equality; some negative controls have four candidates for a triple. All candidate footprints can be listed in polynomial time. After elimination, a connected YES component has either at most two choices per row (yielding pinned parity equations) or exactly three choices. In the three-choice case the footprints form 4 × 4 grids and the component has at most 64 rows and 12 distinct footprints, which can be exhausted in constant time. A 64-row cube attains the bound.

Each accepted footprint is weighted by the number of shore choices. Because an extremal flat has a unique opposite pair per triple, the weighted count equals the number of distinct extremal flats.

The algorithm correctly recognizes the 300-point connected extremizer (one flat of dimension 125) and the 48-point cube (three flats of dimension 20). Negative controls are rejected. All checks are reproduced by the verification harness.

## 2. Logarithmic search under a near-extremal promise

The input is promised either to be uncolorable or to possess a satisfying flat of dimension at least 5V/12 - k. Only the triples and the allowance k are supplied.

Any assignment on at most 14 points for which every touched triple already contains two oppositely assigned points is an autarky and may be removed. When overwrites are exhausted, at most ⌊240k/7⌋ triples remain on every promised YES input. Exhaustive search of two candidate opposite pairs per remaining triple, followed by bipartiteness checks and extension through the stored assignments, yields a valid coloring or a negative decision under the promise. The running time is 2^{⌊240k/7⌋} times a polynomial in V, which is polynomial when k = O(log V).

Under the Exponential Time Hypothesis any efficiently testable allowance growing asymptotically faster than log V precludes a polynomial-time algorithm for that promise problem. The reduction embeds sparse 3-SAT into a connected core and pads with extremal blocks until the allowance covers the deficit.

The peeling algorithm recovers full witnesses on the 300-point extremals in 25–26 steps and on near-extremal mixtures with residual size at most 44.

## 3. Residual-certificate protocols and barriers

On the explicit family A = F ∧ G, B = F ∧ H, C = G ∧ I, constant-round exchange of residual names excludes the pattern “B and C viable and A impossible.” The same protocol abstains on matched controls. The protocol scales past 34 000 vertices.

When residuals are independent (private components), residual-name exchange admits zero exclusions. Certain four-way dependencies require four residual certificates; three are insufficient. Pure forced-set exchange without prior component identification requires Ω(s) bits.

These restricted positive results and barriers are complementary to the recognition and search theorems above.

## 4. Open problem

**Residual Exclusion Problem.** Given a colorable instance of the seven-source compiler, output one false nonempty pattern among the seven candidates, or correctly report that none exists. Is there a deterministic polynomial-time algorithm?

A positive answer would imply P = NP via the membership-comparability reduction already established. No such algorithm is exhibited. The actor of Section 2 succeeds on the high-dimension subclass defined by the logarithmic promise.

## 5. Reproducibility

All new suites (recognition, peeling, stability, gluing, border, grid check) and the prior three-actor and weighted-coloring packages reproduced. A separate exact-cover oracle agreed on 197 new inputs, including 105 negatives. The companion archive contains the full proofs, generators, and verification harnesses.

The exact projection onto the Hamiltonian-cycle polynomial is unconditional. Only the arithmetic-circuit lower bound transferred through that projection depends on an external theorem.

## References

Prior three-actor and weighted-coloring packages; the present verification archive.

---

Working paper. Independent human review and bibliographic priority remain open. P versus NP remains open.
