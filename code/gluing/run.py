"""Independent finite audit of interface symmetries and safe SAT pruning."""
from itertools import combinations, product
import json


def echelon(rows):
    result = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in result:
                result[pivot] = row
                break
            row ^= result[pivot]
    return result


def orthogonal(rows, n):
    eqs = echelon(rows)
    result = []
    for free in range(n):
        if free in eqs:
            continue
        vector = 1 << free
        for pivot in sorted(eqs):
            if (eqs[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        result.append(vector)
    return result


def syndrome(word, checks):
    return sum(((word & row).bit_count() % 2) << i for i, row in enumerate(checks))


def expand(mask, scope):
    return sum((1 << v) for j, v in enumerate(scope) if mask >> j & 1)


def passes(clauses, word):
    return all(any(bool(word >> (abs(lit)-1) & 1) == (lit > 0) for lit in row)
               for row in clauses)


def certified_shifts(clauses, n):
    groups = {}
    for row in clauses:
        scope = tuple(sorted({abs(lit) - 1 for lit in row}))
        groups.setdefault(scope, []).append(row)
    full_equations = []
    for scope, rows in groups.items():
        available = set(range(1 << len(scope)))
        local = {v for v in available if passes(rows, expand(v, scope))}
        shifts = {v for v in available if {s ^ v for s in local} == local}
        full_equations.extend(expand(q, scope) for q in orthogonal(shifts, len(scope)))
    return orthogonal(full_equations, n)


def opposite_or_equal(a, b, opposite):
    return [(a, b), (-a, -b)] if opposite else [(-a, b), (a, -b)]


def interface_example(k, closed):
    # Explicit copies leave all k boundary variables present on both pieces.
    f = [row for i in range(k) for row in opposite_or_equal(i+1, k+i+1, False)]
    g = f.copy()
    for i in range(0, k, 2):
        f.extend(opposite_or_equal(i+1, i+2, False))
    for i in range(1, k-1, 2):
        g.extend(opposite_or_equal(i+1, i+2, False))
    if closed:
        g.extend(opposite_or_equal(k, 1, True))
    end = (1 << k)-1
    u = [w & end for w in certified_shifts(f, 2*k)]
    v = [w & end for w in certified_shifts(g, 2*k)]
    checks = orthogonal(u + v, k)
    if closed:
        assert checks == [end]
        g_boundary = 1  # x_1 is one and every other bit is zero.
        assert passes(f, 0) and passes(g, g_boundary | (g_boundary << k))
        assert syndrome(0, checks) != syndrome(g_boundary, checks)
    else:
        assert checks == [] and passes(f + g, 0)
    return dict(k=k, closed=closed, dim_u=len(echelon(u)), dim_v=len(echelon(v)),
                unresolved=len(checks))


def all_spaces(n):
    known = {frozenset([0])}
    for vector in range(1 << n):
        known |= {space | {w ^ vector for w in space} for space in known}
    return sorted(known, key=lambda s: (len(s), sorted(s)))


def cosets(space, n):
    return sorted({frozenset(v ^ w for w in space) for v in range(1 << n)},
                  key=lambda s: sorted(s))


def unions(cells):
    return [frozenset().union(*(s for i,s in enumerate(cells) if bits >> i & 1))
            for bits in range(1 << len(cells))]


def exhaustive_quotients():
    checked_pairs = checked_supports = 0
    for n in (1, 2, 3):
        spaces = all_spaces(n)
        for f in spaces:
            for g in spaces:
                checks = orthogonal(list(f | g), n)
                checked_pairs += 1
                fs = unions(cosets(f, n))
                gs = unions(cosets(g, n))
                f_views = [(s,{syndrome(w,checks) for w in s}) for s in fs]
                g_views = [(s,{syndrome(w,checks) for w in s}) for s in gs]
                for a,av in f_views:
                    for b,bv in g_views:
                        assert bool(a & b) == bool(av & bv)
                        checked_supports += 1
    return {"subspace_pairs":checked_pairs, "distinct_support_pair_cases":checked_supports}


def hard_boundary_sample():
    samples = 0
    for permitted in range(16):
        # Two-bit functions in truth-table CNF, s variable 1, t variable 2.
        logical = [tuple(-(i+3) if val >> i & 1 else i+3 for i in range(2))
                   for val in range(4) if not permitted >> val & 1]
        f = [(-1,2)] + [(-1, *c) for c in logical]
        g = [(1,)]
        u = [w&1 for w in certified_shifts(f,4)]
        v = [w&1 for w in certified_shifts(g,1)]
        assert len(orthogonal(u+v,1)) == 1
        assert passes(f,0) and passes(g,1)
        models = {w for w in range(16) if passes(f,w)}
        assert sum(w%2 == 0 for w in models) == 8
        assert sum(w%2 == 1 for w in models) == permitted.bit_count()
        assert any(passes(g,w) for w in models) == bool(permitted)
        assert not any({w^s for w in models} == models for s in range(1,16,2))
        samples += 1
    return samples


def old_claims():
    full = set()
    for f,g,h,i in product((0,1),repeat=4):
        full.add((f&g) | ((f&h) << 1) | ((g&i) << 2))
    assert full == set(range(8)) - {6}
    for p,q in combinations(range(3),2):
        assert {(a>>p&1,a>>q&1) for a in full - {0}} == set(product((0,1),repeat=2))
    valid_outputs = 0
    for pattern in range(128):
        live = {j for j in range(1,8) if pattern >> (j-1) & 1}
        answer = 0
        for tag in live:
            answer |= tag
        for out in range(1,8):
            if live and out == answer:
                continue
            assert not live or live-{out}
            valid_outputs += 1
    return {"three_branch_allowed_masks":sorted(full),"all_seven_source_live_sets":128,
            "contract_valid_outputs_checked":valid_outputs}


def main():
    return dict(prior_claims=old_claims(), quotient=exhaustive_quotients(),
                wide_interfaces=[interface_example(k,c) for k in [6,12,64] for c in [False,True]],
                hard_one_bit_formulas=hard_boundary_sample())


if __name__ == '__main__':
    print(json.dumps(main(),indent=2,sort_keys=True))
