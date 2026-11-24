# Safe forgetting at and near extremality

Start with REPORT.md or its PDF equivalent. This package includes complete proofs, Python implementations, recorded JSON, and unchanged copies of the two preceding research archives. Read overlap/RECOGNITION.md for the exact algorithm, and peeling/PROOF.md for the logarithmic promise and conditional converse. All original algorithms take explicit finite input; the tests generate this input deterministically.

Using Python 3.10 or later from the extracted directory, run:

    python3 verify.py --prior

Omit --prior to run the new checks alone. No third-party solver, network access, or numerical approximation is required. The earlier optional full replay runs its compiled-graph cases in temporary directories. References to next_flat and frontier2_near in the proofs refer to the folders in the bundled earlier three-actor ZIP. The exterior Lean project is separate.

| Directory | What the evidence covers |
|---|---|
| overlap | Exact 5V/12 recognition, construction and counting, a decoy footprint and the sharp 64-row bound. |
| grid_check | Independent rectangle checks on a quotient with repeated labels, plus connected mixed cases. |
| recognition | A second grid enumerator, exact-cover oracle, cubic graph examples and 197 adversarial inputs. |
| general_r | All fixed degrees, order classification, and parameterized recognition and counting. |
| xp | Finding an affine flat when the allowed additive deficit is fixed; input exponent depends on that allowance. |
| peeling | Finding a coloring with logarithmic affine deficit, residual bounds, sparse-ETH barrier and seven-source tests. |
| stability | Sharp thresholds on local overwrites, high-girth obstruction and root-input witness reconstruction. |
| gluing | Prior 18-suite replay record, subspace compatibility, boundary profiles and a one-bit hardness control. |
| border | Cross-check of full-polynomial specialization and formal approximation. |
| prior | Unchanged three-actor and weighted-coloring packages with individual proofs and numerical checks. |

The quantified algorithms and their input promises are established by the mathematical arguments. Finite enumerations exercise implementation and sharpness cases. The source priority search is recorded in priority.md. The maximum in the main exact recognition result is literal, without rounding. An algorithm for witnessing colorability near this maximum need not return a near-maximum flat.
