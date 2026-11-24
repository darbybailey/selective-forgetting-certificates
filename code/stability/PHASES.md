# Exact dependence on the allowed size of an autarky

For a fixed positive integer h, consider connected linear triples given as four perfect matchings. Write d(H) for the largest dimension of an affine flat of perfect colorings, restricting to colorable inputs. Among the instances that have no nonempty NAE autarky on at most h points, the maximum possible ratio d(H)/V is attained and equals the following numbers.

| Maximum allowed support h | Maximum ratio without such an autarky |
|---|---:|
| 1 through 7 | 5/12 |
| 8 or 9 | 2/5 |
| 10 or 11 | 7/18 |
| 12 or 13 | 8/21 |
| 14 and above, each h fixed | 17/45 |

**Upper bounds.** A saturated certificate component on s vertices is bipartite 4-regular, with s even, s≥8 and e=2s. When its size is at most h, its opposite-shore coloring is directly an autarky, as proved in PROOF.md. For every unsaturated component, e≤(15/7)(s−1); for s≥8 this follows from e≤2s−1, and for s≤7 it follows from the two-shore product bound. Let r be the least even integer at least 8 and greater than h. If every h-point autarky is forbidden, the remaining components all obey e≤B(s−1), where

    B = max { 15/7, 2r/(r−1) }.

Here the ratio 2s/(s−1) decreases with s. Summing over all components gives d/V≤1−4/(3B). For h=1,…,7 this gives 5/12, the unrestricted sharp bound. For h up to 13, r is successively 10, 12 or 14. For h≥14 the 15/7 term dominates.

**Attainment at h≤13.** Put p=r/2 in {4,5,6,7}. A core contains p vertices A_i and p vertices B_i. In matching s=0,1,2,3 the selected pairs are A_i with B_(i+s) for indices modulo p. Their graph is simple, connected, bipartite and 4-regular. Its proper, nontrivial cuts have positive even size; in particular it is bridgeless. Use p further singleton atoms C_i. In matching s append C_i as the third point of the pair with tail A_i. On the atom graph, take a connected cover of girth greater than max(h,2) by the elementary construction of PROOF.md. Local incidences lift to four actual partitions, and linearity follows from simplicity of the lifted atom graph. Each base copy contributes 3p points, one core parameter, and p singleton parameters. The certified ratio is (p+1)/(3p).

Suppose a nonempty stopping set has at most h points. Because h<2p, any occupied core contains only a proper subset of its points. Its at least two cut edges require two distinct occupied neighboring singleton atoms in the corresponding triples. Each occupied singleton in turn requires four occupied neighbor cores. The occupied atoms contain a cycle and hence exceed h in number, a contradiction. Consequently every autarky has more than h points. Assigning the two shores of any single core oppositely supplies an autarky of exactly 2p points. The upper bounds establish exact flat dimension. For h≥14, the 17/45 construction and the unbounded required support follow from PROOF.md.

**Finite replay.** Run python3 phases.py and compare with PHASE_RESULTS.json. In the four saturated examples, independent searches and explicit overwrites certify minimum support equal to 8, 10, 12 and 14, respectively. The actual finite sizes are 804, 1,905, 2,286 and 2,667 points. In the 3,015-point control, extension search visited 737,235 partial supports and exhausted every candidate of size at most 14, proving the maximum flat dimension of this specific graph is exactly 1,139. Each cyclic lift is connected because the base atom graph is connected, the number of sheets is prime, and at least two parallel base edges have different shifts (all base parallel pairs are forbidden from lifting to 2-cycles). Their nonzero displacement generates the deck translation group. The raw triple-only reader for the 3,015-point control is in run.py.

The enumeration starts at a representative in the base fiber for every physical point type, which suffices by translation symmetry. Whenever a touched row has exactly one currently chosen point, a stopping-set extension must add at least one of its other two points. Branch on both and reject a still-broken state at the support cap. A complete state needs no more rows with exactly one chosen point. The search explores an exhaustive tree for existence at the cap; its visit counts are partial states, not a count of distinct sets. For the cyclic finite controls this direct stopping-set test avoids assuming that their actual quotient girth exceeds the requested support size.

The theorem concerns the support of partial assignments that already satisfy every touched constraint. The unrestricted Boolean task permits other evidence of safe choices.
