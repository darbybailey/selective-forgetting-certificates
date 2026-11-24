# Selective Forgetting Certificates

Restricted residual-exchange protocols that exclude impossible multi-branch viability patterns, together with a sharp 5V/12 affine-dimension bound on linear four-matching systems.

The **Residual Exclusion Problem** (return one false nonempty pattern on every colorable input of the seven-source compiler) remains open. A deterministic polynomial-time solution would imply P = NP. No such algorithm is exhibited.

## Contents

- `paper/` — working notes (Three Actors and One False Pattern; maximum-complexity push)
- `code/` — residual protocol, generators, and verification
- `results/` — scaling runs (including 34 745-vertex confirmation) and barriers

## Key results

1. **Three-way residual-certificate protocol**  
   On the family A = F ∧ G, B = F ∧ H, C = G ∧ I, constant-round exchange of residual names excludes the pattern “B and C viable and A impossible.” The same protocol abstains on matched controls where the pattern is realized. Scales past 34k vertices.

2. **Sharp 5V/12 bound**  
   On every linear system of four perfect matchings on V points, no affine flat of satisfying colorings has dimension larger than 5V/12. Connected examples attain the bound. Approaching the bound within √V is NP-complete on connected inputs.

3. **Barriers**  
   - Independent residual barrier: residual-name exchange admits zero exclusions when components are private.  
   - Four-branch quantitative barrier: three residual certificates are insufficient for certain four-way dependencies.  
   - Message-size lower bound for pure forced-set exchange.

## Reproduction

See `code/verify.py` and the notes in `paper/`.

## Status

Working paper. Priority for the exact statements is open for independent review. P versus NP remains open.
