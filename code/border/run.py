"""Exact controls for the formal approximation transfer. Standard library only."""
from collections import Counter
from itertools import permutations, product
from math import factorial
import json


def chart_words():
    # Coordinates 3*r+c. Keep all affine lines except horizontal rows 0 and 1.
    points = tuple((r, c) for r in range(3) for c in range(3))
    lines = [[6, 7, 8]]
    for slope in range(3):
        for b in range(3):
            lines.append([3*r+c for r, c in points if (c-slope*r) % 3 == b])
    phases = [[], []]
    for word in product((0, 1), repeat=9):
        if all(len({word[i] for i in line}) == 2 for line in lines):
            phase = word[0]
            assert word[:6] == (phase,) * 3 + (1-phase,) * 3
            phases[phase].append(word)
    return phases


def actual_local_softening(phases):
    # Use the actual 9-bit assignments. Weights t multiply when bit 6 or 7 is 1.
    local = []
    for words in phases:
        coeff = Counter(w[6] + w[7] for w in words)
        local.append([coeff[j] for j in range(3)])
    assert local == [[1, 4, 1], [1, 4, 1]]
    return local


def is_single_cycle(mask, arcs, n):
    successor = {}
    indegree = [0] * n
    for i, (u, v) in enumerate(arcs):
        if mask & (1 << i):
            if u in successor:
                return False
            successor[u] = v
            indegree[v] += 1
    if len(successor) != n or indegree != [1] * n:
        return False
    reached = set()
    v = 0
    while v not in reached:
        reached.add(v)
        v = successor[v]
    return len(reached) == n


def projected_orientations(n):
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    full = (1 << len(arcs)) - 1
    observed = Counter()
    for mask in range(full + 1):
        for f in (0, 1):
            logical_mask = (full ^ mask) if f else mask
            if is_single_cycle(logical_mask, arcs, n):
                observed[(mask, f)] += 1
    direct = Counter()
    for p in permutations(range(1, n)):
        vertices = (0, *p, 0)
        mask = sum(1 << arcs.index(edge) for edge in zip(vertices, vertices[1:]))
        direct[(mask, 0)] += 1
        direct[(full ^ mask, 1)] += 1
    assert observed == direct
    return observed


def test_laurent_gate_projection(phases, characteristic):
    # Example over the punctured-plane chart. p goes to x+y after hard private
    # pins and putting x or y on one exposed port from each opposite row.
    # First input is a physical mask; the output is (epsilon power,x power,y power).
    def transfer(terms):
        result = Counter()
        for (eps, mask), value in terms.items():
            if mask & ((1 << 6) | (1 << 7)):
                continue
            key = (eps, mask & 1, (mask >> 3) & 1)
            result[key] += value
        if characteristic:
            return {k: v % characteristic for k, v in result.items() if v % characteristic}
        return {k: v for k, v in result.items() if v}

    p = [sum(bit << i for i, bit in enumerate(w)) for phase in phases for w in phase]
    # Preserve Laurent poles at intermediate gates. Epsilon^(-1)(P+epsilon P)
    # minus epsilon^(-1)(P-epsilon^2 R) is exactly P+epsilon R. Distinct
    # physical monomials of R merge or disappear under this same substitution.
    perturbation = {0: 1, 2: 2, 1 << 6: 7, 1: -3}
    first = Counter()
    second = Counter()
    for mask in p:
        first[(-1, mask)] += 1
        first[(0, mask)] += 1
        second[(-1, mask)] += 1
    for mask, value in perturbation.items():
        second[(1, mask)] -= value
    assert any(k[0] < 0 for k in transfer(first))
    assert any(k[0] < 0 for k in transfer(second))
    reduced = first.copy()
    reduced.subtract(second)
    left = transfer(reduced)
    right = Counter(transfer(first))
    right.subtract(transfer(second))
    if characteristic:
        right = {k: v % characteristic for k, v in right.items() if v % characteristic}
    else:
        right = {k: v for k, v in right.items() if v}
    assert left == right
    assert {k: v for k, v in left.items() if k[0] <= 0} == {(0, 1, 0): 1, (0, 0, 1): 1}
    return len(left)


def main():
    phases = chart_words()
    local = actual_local_softening(phases)
    cases = []
    for n in (2, 3, 4):
        observed = projected_orientations(n)
        for f in (0, 1):
            assert sum(value for (mask, phase), value in observed.items() if phase == f) == factorial(n-1)
        cases.append({"m": n, "masks": 1 << (n*(n-1)), "accepted_per_reference_phase": factorial(n-1),
                      "hard_degree": n, "opposite_degree": n*(n-2)})
    fields = (0, 2, 3, 5, 7)
    positive_terms = [test_laurent_gate_projection(phases, p) for p in fields]
    assert sum(local[0]) == 6
    return {"physical_local_assignments_exhausted": 512, "local_private_polynomial_per_phase": local,
            "cycle_and_complement_support": cases,
            "test_characteristics": fields, "terms_after_laurent_pole_cancellation": positive_terms,
            "unpinned_private_factor_at_one_mod_p": {str(p): 6 % p for p in fields if p}}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
