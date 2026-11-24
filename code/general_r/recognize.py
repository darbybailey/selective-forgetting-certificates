"""Replay the exact-equality recognition algorithm on small general-degree fixtures."""
from collections import defaultdict
from itertools import combinations, product
from math import prod
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"overlap"))
from run import components, small_parity, covers


def footprints(rows, r):
    inc = defaultdict(list)
    pair = {}
    for j, row in enumerate(rows):
        assert len(set(row)) == 3
        for p in row:
            inc[p].append(tuple(x for x in row if x != p))
        for edge in combinations(sorted(row),2):
            if edge in pair:
                raise ValueError("two rows share a pair")
            pair[edge]=j
    assert all(len(neighbors) == r for neighbors in inc.values())
    near={p:{v for edge in rows_at_p for v in edge} for p,rows_at_p in inc.items()}
    found=defaultdict(set)
    for pivot, options in inc.items():
        for right_points in product(*options):
            right=frozenset(right_points)
            if len(right)!=r:
                continue
            common=set.intersection(*(near[q] for q in right))-{pivot}
            for rest in combinations(sorted(common), r-1):
                left=frozenset((pivot,*rest))
                cells=frozenset(pair[tuple(sorted((a,b)))] for a in left for b in right)
                if len(cells)==r*r:
                    found[cells].add(tuple(sorted((tuple(sorted(left)),tuple(sorted(right))))))
    return found


def count(rows, r):
    pool=footprints(rows,r)
    fps=sorted(pool,key=lambda f:tuple(sorted(f)))
    weights={j:len(pool[f]) for j,f in enumerate(fps)}
    allcovers=covers(fps,len(rows))
    reference=sum(prod(weights[j] for j in sol) for sol in allcovers)
    qs=[{j for j,f in enumerate(fps) if cell in f} for cell in range(len(rows))]
    incident=defaultdict(set)
    for i,row in enumerate(rows):
        for v in row:
            incident[v].add(i)
    adj={i:set.union(*(incident[v] for v in row))-{i} for i,row in enumerate(rows)}
    def result(value):
        assert value==reference,(value,reference)
        return {"rows":len(rows),"footprints":len(fps),"flats":value}
    if any(not 1<=len(q)<=3 for q in qs):
        return result(0)
    while True:
        drop=set()
        for i,q in enumerate(qs):
            for j in adj[i]:
                if qs[j]<q:
                    drop.update(q-qs[j])
        if not drop:
            break
        for q in qs:
            q.difference_update(drop)
        if not all(qs):
            return result(0)
    total=1
    for comp in components(adj):
        options=[qs[i] for i in comp]
        live=set.union(*options)
        freq={len(q) for q in options}
        if max(freq)<=2:
            _,s=small_parity(options,{j:weights[j] for j in live})
        elif freq=={3} and len(comp)<=r**3 and len(live)<=3*r:
            labels=sorted(live)
            s=0
            for mask in range(1<<len(labels)):
                marked={j for k,j in enumerate(labels) if mask>>k&1}
                if all(len(marked & q)==1 for q in options):
                    s+=prod(weights[j] for j in marked)
        else:
            s=0
        total*=s
    return result(total)


def cube(r):
    groups=[[] for _ in range(r)]
    for i,j,k in product(range(r),repeat=3):
        groups[(i+j+k)%r].append((i*r+j,r*r+j*r+k,2*r*r+k*r+i))
    return groups


def positive(r):
    t=2 if r==2 else 1
    groups=[[] for _ in range(r)]
    for s,b,i in product(range(r),range(t),range(r)):
        if r==4 and t==1:
            j,k=i^s,i^(0,2,3,1)[s]
        else:
            j,k=(i+s)%r,(i+2*s)%r
        groups[s].append((b*r+i,t*r+b*r+j,2*t*r+((b+2*s//r)%t)*r+k))
    return groups


def rows(groups):
    return [row for group in groups for row in group]


def switched_negative(groups,r):
    unary=groups[0]
    for a,b in combinations(range(len(unary)),2):
        for l,m in product(range(3),repeat=2):
            alt=[list(row) for row in unary]
            alt[a][l],alt[b][m]=alt[b][m],alt[a][l]
            candidate=rows([alt]+groups[1:])
            try:
                value=count(candidate,r)
            except ValueError:
                continue
            if value["flats"]==0:
                return dict(value,swap=[a,b,l,m])
    raise AssertionError("no switched negative")


def main():
    ds=[]
    for r in (2,3,4,5):
        graph=cube(r)
        value=count(rows(graph),r)
        assert value=={"rows":r**3,"footprints":3*r,"flats":3}
        small=positive(r)
        pos=count(rows(small),r)
        assert pos["flats"]>0
        if r>2:
            assert pos["flats"]==3
        maximum=max(max(row) for row in rows(small))+1
        double=rows(small)+[tuple(x+maximum for x in row) for row in rows(small)]
        doubled=count(double,r)
        assert doubled["flats"]==pos["flats"]**2
        if r == 2:
            # Sixteen triples are the stations of a simple cubic bipartite graph of girth >=6.
            # Its 24 edges are shared points; each shore's triples form a matching.
            offsets=(0,1,3)
            left=[tuple(3*i+k for k in range(3)) for i in range(8)]
            right=[tuple(3*((j-delta)%8)+k for k,delta in enumerate(offsets)) for j in range(8)]
            neg=count(left+right,r)
            assert neg["flats"]==0
        else:
            neg=switched_negative(graph,r)
        ds.append({"r":r,"cube":value,"small_positive":pos,"two_copies":doubled,"negative":neg})
    return ds


if __name__=="__main__":
    print(json.dumps(main(),indent=2))
