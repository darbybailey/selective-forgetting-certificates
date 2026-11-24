# Selective Forgetting Certificates

Exact recognition of maximum affine flats in linear four-matching systems, and logarithmic search under a near-extremal promise.

## Main results

1. **Exact recognition of the 5V/12 bound**  
   Deterministic polynomial-time algorithm that decides exact attainment, constructs an extremal flat when one exists, and counts the distinct extremal flats. Equality is literal. Verified on the 300-point extremizer (one flat of dimension 125) and the 48-point cube (three flats of dimension 20).

2. **Logarithmic search under a near-extremal promise**  
   If every satisfiable input is promised a flat within O(log V) of the universal bound 5V/12, a deterministic polynomial-time algorithm recovers a valid coloring by extracting small autarkies and searching a residual of size O(k). Under ETH the guarantee cannot extend to every efficiently testable super-logarithmic allowance.

3. **Residual-certificate protocols**  
   Constant-round residual-name exchange excludes the three-way pattern “B and C but not A” on the explicit overlapping family and scales past 34k vertices. Independent residuals admit zero exclusions.

## Open problem

The Residual Exclusion Problem (one false nonempty pattern on every colorable seven-source compiler input) remains open. A polynomial-time solution would imply P = NP.

## Contents

- `paper/SELECTIVE_FORGETTING_CERTIFICATES.md` — full working paper
- `paper/Safe_Forgetting_Exact_and_Near_Extremizers.md` — detailed recognition and search note
- `results/` — scaling runs and recognition summaries
- Companion archive (to be attached) contains the full verification harnesses and proofs

## Status

Working paper. Independent review and priority checking remain open. P versus NP remains open.
