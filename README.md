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
- [Verification package](code/README.md) — Python implementations, proofs, recorded results, and both prior replay archives

## Reproduce the results

From a fresh clone, use Python 3.10 or later. The verifier uses only the Python standard library and runs offline.

```sh
git clone https://github.com/darbybailey/selective-forgetting-certificates.git
cd selective-forgetting-certificates
python3 code/verify.py
```

The command reruns 12 suites and compares their output with the recorded JSON. Run `python3 code/verify.py --prior` to also replay the 18 three-actor suites and six weighted-coloring suites.

| Recognition case | Points | Extremal dimension | Distinct extremal flats |
|---|---:|---:|---:|
| Connected extremizer (`connected_25`) | 300 | 125 | 1 |
| Cube (`cube`) | 48 | 20 | 3 |

To inspect the regenerated counts for these cases, run `python3 code/recognition/run.py` and look for `sharp_flats_by_weighted_count` in the two named records. Each attains dimension exactly `5V/12`. [Recorded results](code/recognition/RESULTS.json) · [Recognition proof](code/overlap/RECOGNITION.md)

## Status

Working paper. Independent review and priority checking remain open. P versus NP remains open.
