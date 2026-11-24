"""Independent hostile tests of three-choice propagation against ordinary exact cover."""
import itertools
import json
from math import prod
from collections import Counter, defaultdict
from random import Random
import run as local


def oracle(footprints, rows, weights):
    per_row={r:[b for b in footprints if r in b] for r in rows}
    def search(left):
        if not left:
            return 1
        choices=min(([b for b in per_row[r] if b<=left] for r in left), key=len)
        return sum(weights[b]*search(left-b) for b in choices)
    return search(rows)


def components(rows):
    incident=defaultdict(set)
    for i,r in enumerate(rows):
        for v in r:
            incident[v].add(i)
    unseen=set(range(len(rows)))
    while unseen:
        i=next(iter(unseen)); cc={i}; stack=[i]
        while stack:
            for v in rows[stack.pop()]:
                new=incident[v]-cc
                cc.update(new)
                stack.extend(new)
        unseen-=cc
        yield frozenset(cc)


def compressed_decision(footprints, component, weights):
    if not component:
        return True,"empty"
    opts=lambda r: frozenset(i for i,f in enumerate(footprints) if r in f)
    systems={opts(r) for r in component}
    if frozenset() in systems:
        return False,"initial_zero"
    if max(map(len,systems))>3:
        return False,"above_three"
    while True:
        drop=set().union(*(b-a for a in systems for b in systems if a<b))
        if not drop:
            break
        systems={s-drop for s in systems}
        if frozenset() in systems:
            return False,"pruned_zero"
    degrees=set(map(len,systems))
    if 3 in degrees:
        if len(degrees)>1:
            return False,"mixed"
        if len(component)>64:
            return False,"large"
        labels=set().union(*systems)
        assert len(labels)<=12
        count=sum(prod(weights[footprints[i]] for i in t)
                  for k in range(len(labels)+1) for choice in itertools.combinations(labels,k)
                  for t in (set(choice),) if all(len(s&t)==1 for s in systems))
        assert count in (0,3),count
        return count,"tiny"
    adj=defaultdict(set); forced=set()
    for s in systems:
        if len(s)==1:
            forced.update(s)
        else:
            a,b=s
            adj[a].add(b);adj[b].add(a)
    side={}
    total=1
    for v in set(adj)|forced:
        if v in side: continue
        side[v]=1; todo=[v]; family={v}
        while todo:
            u=todo.pop()
            for w in adj[u]:
                if w not in side:
                    side[w]=1-side[u]; todo.append(w); family.add(w)
                elif side[w]==side[u]: return 0,"binary"
        total*=sum(prod(weights[footprints[i]] for i in family if side[i]==a)
                   for a in (0,1) if all(side[i]==a for i in family&forced))
    return total,"binary"


def twisted(base,k,seed,mode):
    rng=Random(seed)
    n=len(base[0])*3
    gauges=[rng.randrange(k) for i in range(n)]
    groups=[]
    for grp in base:
        result=[]
        for row in grp:
            base_shift=rng.randrange(k)
            def offset(i,v):
                if mode=="gauge":
                    return base_shift+gauges[v]
                if mode=="plant":
                    return base_shift+gauges[v]+(rng.randrange(k) if i==2 and rng.randrange(4)==0 else 0)
                if mode=="rare":
                    return base_shift+gauges[v]+(rng.randrange(k) if rng.randrange(40)==0 else 0)
                return base_shift+gauges[v]+rng.randrange(k)
            offsets=[offset(i,v) for i,v in enumerate(row)]
            result.extend(tuple(v+n*((j+a)%k) for v,a in zip(row,offsets)) for j in range(k))
        groups.append(result)
    return groups


def main():
    tests=Counter(); branches=Counter(); answers=Counter(); counts=Counter(); max_three=0
    def compare(groups,name):
        nonlocal max_three
        rows=sum(groups,[])
        grids=local.candidate_grids(rows)
        weights={g:len(v) for g,v in grids.items()}
        footprints=sorted(grids, key=lambda s: tuple(sorted(s)))
        truth=1
        for cc in components(rows):
            fp=[f for f in footprints if f<=cc]
            found,kind=compressed_decision(fp,cc,weights)
            wanted=oracle(fp,cc,weights)
            assert found==wanted,(name,kind,len(cc),len(fp),wanted)
            truth *= wanted
            branches[kind]+=1
            if kind=="tiny":max_three=max(max_three,len(cc))
        tests[name]+=1; answers[str(bool(truth))]+=1; counts[str(truth)]+=1
        return truth

    for seed in range(32):
        for mode in ("gauge","plant","rare","general"):
            k=2 if seed%2==0 else 3
            result=compare(twisted(local.cube(),k,seed,mode),"cubical_"+mode)
            if mode in ("gauge","plant"): assert result
    # Every pair of disjoint permutations of a three- or four-element identity matching.
    # Exhaust the labeled, edge-colored cubic bipartite presentation up to this fixation.
    for n in (3,4):
        ident=tuple(range(n))
        for p,q in itertools.combinations(itertools.permutations(range(n)),2):
            if all(len({i,p[i],q[i]})==3 for i in ident):
                compare(local.cubic_lift([ident,p,q]),"all_cubic_"+str(n))
    # Connected cubical double covers with holonomy (offsets) and many true/false labels.
    for seed in range(50):
        rng=Random(200+seed); n=6+seed%5
        identity=list(range(n))
        def perfect(avoid):
            while True:
                perm=rng.sample(identity,n)
                if all(perm[i] not in avoid[i] for i in identity):
                    return perm
        p=perfect([{i} for i in identity]); q=perfect([{i,p[i]} for i in identity])
        compare(local.cubic_lift([identity,p,q]),"random_cubic_lifts")
    bad=[[3,1,2,0,4,5]]+[[3*(i//3)+(i+j)%3 for i in range(6)] for j in (1,2)]
    assert not compare(local.cubic_lift(bad),"crossed_six_vertex_islands")
    for k in (1,2,5,25):
        compare(local.cyclic(k),"connected_extremal_fixtures")
    compare(local.quotient_cube(),"quotient_cube")
    return {"inputs":sum(tests.values()),"families":dict(tests),"booleans":dict(answers), "numbers_of_distinct_sharp_flats_histogram":dict(counts),
            "connected_components_by_decision_scenario":dict(branches),
            "maximum_full_three_component_rows_on_finite_tests":max_three}

if __name__=="__main__":
    print(json.dumps(main(),indent=2))
