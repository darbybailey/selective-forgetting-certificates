"""Stress-test the equality argument on connected, crossed copies of a fully ambiguous cube."""
from collections import Counter
from itertools import product
import json
from pathlib import Path
import random
import importlib.util

path = Path(__file__).resolve().parents[1] / 'overlap' / 'run.py'
spec = importlib.util.spec_from_file_location('grid_enumeration',path)
grid_enumeration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid_enumeration)


def trial(copies, seed):
    rng = random.Random(seed)
    layers = [[] for _ in range(4)]
    for b in range(copies):
        for i,j,k in product(range(4),repeat=3):
            row = (48*b+4*i+j,48*b+16+4*j+k,48*b+32+4*k+i)
            layers[i^j^k].append(row)
    # All 16 rows at fixed b,j form known feasible footprints, even after moving the third entries.
    for b in range(copies-1):
        z = rng.randrange(4)
        left = 16*b + rng.randrange(16)
        right = 16*(b+1) + rng.randrange(16)
        x,y,w = layers[z][left]
        a,c,d = layers[z][right]
        layers[z][left],layers[z][right] = (x,y,d),(a,c,w)
    for layer in layers:
        assert set(p for t in layer for p in t) == set(range(48*copies))
    rows = sum(layers,[])
    inc = {}
    for index,row in enumerate(rows):
        for p in row:
            inc.setdefault(p,set()).add(index)
    reach={0}
    while (more := set.union(*(inc[p] for i in reach for p in rows[i]))) != reach:
        reach = more
    assert len(reach)==len(rows)
    true = {frozenset(i for i, row in enumerate(rows) if (row[0]//48, row[0]%4)==(b,j))
            for b in range(copies) for j in range(4)}
    alltiles = grid_enumeration.enumerate_tiles(layers)
    assert true.issubset(alltiles)
    opts = [{f for f in alltiles if i in f} for i in range(len(rows))]
    before = sorted(Counter(map(len,opts)).items())
    assert all(1<=len(s)<=3 for s in opts)
    rounds=0
    while True:
        small={frozenset(s) for s in opts if len(s)<3}
        discard=set()
        for s in opts:
            for t in small:
                if t < s: discard |= s-t
        if not discard:
            break
        assert not true.intersection(discard)
        opts=[s - discard for s in opts]
        rounds+=1
    after=sorted(Counter(map(len,opts)).items())
    if any(len(s)==3 for s in opts):
        assert all(len(s)==3 for s in opts) and len(rows)<=64
    if copies==1:
        assert before == [(3,64)] and rounds==0
    if copies>1:
        assert all(len(s)<=2 for s in opts)
    return {"copies":copies,"seed":seed,"rows":len(rows),"old_grids":len(true),
            "raw_options_histogram":before,"pruned_histogram":after,"simultaneous_rounds":rounds}


def quotient_cube():
    # Quotient rows and points by translation (i,j,k) -> (i+1,j+1,k+1) over GF(4).
    # The color i + omega*j + omega^2*k is invariant and remains a permutation along every line.
    omega=(0,2,3,1)
    def point(kind,a,b):
        return (kind, min((a,b),(a^1,b^1)))
    names={}
    layers=[[] for _ in range(4)]
    for i,j,k in product(range(4),repeat=3):
        if (i,j,k)>(i^1,j^1,k^1):
            continue
        pts=[point(0,i,j),point(1,j,k),point(2,k,i)]
        row=tuple(names.setdefault(p,len(names)) for p in pts)
        layers[i^omega[j]^omega[omega[k]]].append(row)
    rows=sum(layers,[])
    assert all(sorted(x for t in group for x in t)==list(range(24)) for group in layers)
    tiles=grid_enumeration.enumerate_tiles(layers)
    ids={block:i for i,block in enumerate(tiles)}
    labels=[{i for block,i in ids.items() if r in block} for r in range(len(rows))]
    assert all(len(s)==3 for s in labels)
    line={p: [r for r,t in enumerate(rows) if p in t] for p in range(24)}
    pairs={}
    for p,neighbors in line.items():
        common=set.intersection(*(labels[r] for r in neighbors))
        shores={ids[s] for s,realizations in tiles.items()
                if any(p in shore for realization in realizations for shore in realization)}
        pairs[p]=common & shores
    assert all(len(a)==2 for a in pairs.values())
    def moves(state,kind):
        row,word=state
        stable={x for j,x in enumerate(word) if j!=kind}
        p,=[p for p in rows[row] if pairs[p]==stable]
        return {(newrow,tuple(next(iter(labels[newrow]-stable)) if k==kind else s
                              for k,s in enumerate(word))) for newrow in line[p]}
    from itertools import permutations
    states=[(i,w) for i in range(len(rows)) for w in permutations(labels[i])]
    for state in states:
        for a,b in product(range(3),repeat=2):
            ab=set.union(*(moves(j,b) for j in moves(state,a)))
            ba=set.union(*(moves(j,a) for j in moves(state,b)))
            assert ab==ba
            if a==b:
                assert ab==moves(state,a)
    return {"points":24,"rows":len(rows),"candidate_footprints":len(tiles),"row_frequency":3,
            "ordered_states_checked":len(states),"two_move_relation_checks":9*len(states)}


if __name__=='__main__':
    print(json.dumps({'crossed_cubes':[trial(t,j) for t in (1,2,4,10) for j in (441,967)],
                      'quotient_cube':quotient_cube()},sort_keys=True,indent=2))
