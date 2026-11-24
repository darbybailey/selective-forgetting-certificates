"""Verify finite tight examples for each autarky support cap."""
from collections import defaultdict
from itertools import combinations
import json
from run import audit,base,atom,cyclic_lift


def stopping(groups,seeds,limit):
    rows=[tuple(row) for group in groups for row in group]
    hits=defaultdict(list)
    for i,row in enumerate(rows):
        for v in row: hits[v].append(i)
    counts=[0]*len(rows)
    active=set()
    visited=0
    def add(u):
        active.add(u)
        for r in hits[u]: counts[r]+=1
    def drop(u):
        for r in hits[u]: counts[r]-=1
        active.remove(u)
    def extend():
        nonlocal visited
        visited+=1
        broken=next((r for v in sorted(active) for r in hits[v] if counts[r]==1),None)
        if broken is None: return True
        if len(active)==limit: return False
        for v in rows[broken]:
            if v in active: continue
            add(v)
            good=extend()
            drop(v)
            if good:return True
        return False
    for v in seeds:
        add(v)
        found=extend()
        drop(v)
        if found:return True,visited
    return False,visited


def saturated(p):
    records=[(s,i,p+(i+s)%p,2*p+i) for s in range(4) for i in range(p)]
    stubs=[(0,1+(z-2*p)) for s,x,y,z in records]
    sheets,shifts,eqs=cyclic_lift(stubs)
    groups=[[] for _ in range(4)]
    for (s,x,y,z),r in zip(records,shifts):
        for f in range(sheets):
            groups[s].append((3*p*f+x,3*p*f+y,3*p*((f+r)%sheets)+z))
    forms=[((p+1)*f+(0 if x<2*p else x-2*p+1), int(p<=x<2*p))
           for f in range(sheets) for x in range(3*p)]
    assert audit(groups,forms)==(p+1)*sheets
    found,vis=stopping(groups,range(3*p),2*p-1)
    assert not found
    return dict(points=3*p*sheets,rows=4*p*sheets,sheets=sheets,
                certified_dimension=(p+1)*sheets,
                local_autarky_support_minimum=2*p,
                partial_supports_visited=vis)


def unsaturated():
    records=base()
    sheets,shifts,_=cyclic_lift([(atom(x),atom(z)) for s,x,y,z in records])
    groups=[[] for _ in range(4)]
    for (s,x,y,z),r in zip(records,shifts):
        for f in range(sheets):
            groups[s].append((45*f+x,45*f+y,45*((f+r)%sheets)+z))
    found,vis=stopping(groups,range(45),14)
    assert not found
    return dict(points=45*sheets,rows=60*sheets,
                certified_dimension=17*sheets,autarky_support_lower_bound=15,
                partial_supports_visited=vis)


if __name__=='__main__':
    print(json.dumps(dict(saturated=[saturated(p) for p in range(4,8)],
                          unsaturated=unsaturated()),indent=2))
