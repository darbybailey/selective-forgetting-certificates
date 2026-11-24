"""Check the extremal examples and exact per-component inequalities."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json


def case(r, t):
    n = 3*r*t
    def point(part, b, i):
        return (part*t+b)*r+i
    all_points = set(range(n))
    seen_pairs = set()
    adjacent = [set() for _ in all_points]
    pairs = []
    labels = {}
    for s in range(r):
        used = []
        for b in range(t):
            for i in range(r):
                if r == 4 and t == 1:
                    # GF(4) uses x^2 = x+1. Multiplication by x maps 0,1,2,3 to 0,2,3,1.
                    j = i ^ s
                    k = i ^ (0,2,3,1)[s]
                else:
                    j, k = (i+s)%r, (i+2*s)%r
                shift = (2*s)//r
                row = (point(0,b,i), point(1,b,j), point(2,(b+shift)%t,k))
                if t == 1:
                    labels[i,j] = (s,k)
                used.extend(row)
                pairs.append(row[:2])
                for u,v in combinations(row,2):
                    assert (u,v) not in seen_pairs
                    seen_pairs.add((u,v))
                    adjacent[u].add(v)
                    adjacent[v].add(u)
        assert sorted(used) == sorted(all_points)
    def components(adj):
        unseen=set(all_points)
        sizes=[]
        while unseen:
            root = unseen.pop()
            todo=[root]
            size=1
            while todo:
                u=todo.pop()
                fresh=unseen.intersection(adj[u])
                size+=len(fresh)
                todo.extend(fresh)
                unseen.difference_update(fresh)
            sizes.append(size)
        return sizes
    assert components(adjacent)==[n]
    selected=[set() for _ in all_points]
    for u,v in pairs:
        selected[u].add(v)
        selected[v].add(u)
    sizes=components(selected)
    assert Counter(sizes)=={1:r*t,2*r:t}
    for block in range(t):
        for i in range(r):
            assert selected[point(0,block,i)] == {point(1,block,j) for j in range(r)}
    assert Fraction(r+1,3*r)*n==len(sizes)
    if t == 1:
        assert len(set(labels.values())) == r*r
        for u in range(r):
            for coordinate in (0,1):
                assert len({labels[u,v][coordinate] for v in range(r)}) == r
                assert len({labels[v,u][coordinate] for v in range(r)}) == r
    return {"degree":r,"blocks":t,"vertices":n,"triples":len(pairs),
            "flat_dimension":len(sizes),"connected":True}


def main():
    examined=0
    for r in range(2,51):
        for s in range(2,12*r+1):
            e=min(s*s//4,r*s//2)
            assert (2*r-1)*e<=r*r*(s-1)
            assert (((2*r-1)*e==r*r*(s-1)) == (s==2*r))
            examined+=1
    rows=[case(r,t) for r in (2,3,4,5,6,8,10,13) for t in (2,3,5,7)]
    rows.extend(case(r,1) for r in (3,4,5,7))
    return {"component_checks":examined,"constructions":rows}

if __name__ == "__main__":
    print(json.dumps(main(),indent=2))
