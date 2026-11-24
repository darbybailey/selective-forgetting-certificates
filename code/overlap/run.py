"""Exhaust the admissible K4,4 tiles and all extremal covers of a fixed fixture."""
from collections import defaultdict
from itertools import product, combinations
from random import Random
from math import prod
import json


def instance(seed):
    """Four true blocks; four common third points reserved for their first rows."""
    rng = Random(seed)
    forbidden = defaultdict(set)
    matchings = []
    for s in range(4):
        fixed, todo = [], []
        for b in range(4):
            for i in range(4):
                a, v = 4*b+i, 16+4*b+(i^s)
                if i == 0:
                    fixed.append((a, v, 32+(b^s)))
                else:
                    todo.append((a, v))
        choices = {}
        for a, v in todo:
            choices[a] = [c for c in range(36,48) if c not in forbidden[a] | forbidden[v]]
            rng.shuffle(choices[a])
        owner = {}
        def assign(a,seen):
            for c in choices[a]:
                if c in seen:
                    continue
                seen.add(c)
                if c not in owner or assign(owner[c],seen):
                    owner[c]=a
                    return True
            return False
        for a, _ in todo:
            if not assign(a,set()):
                return None
        for c, a in owner.items():
            v = dict(todo)[a]
            fixed.append((a,v,c))
            forbidden[a].add(c)
            forbidden[v].add(c)
        matchings.append(sorted(fixed))
    return matchings


def enumerate_tiles(matchings):
    triples = [e for matching in matchings for e in matching]
    point_set = set(sum(triples,()))
    assert len(matchings) == 4 and all(3*len(group)==len(point_set) and set(sum(group,()))==point_set for group in matchings)
    return enumerate_from_rows(triples)


def enumerate_from_rows(triples):
    inc = defaultdict(list)
    pair = {}
    for ri,e in enumerate(triples):
        for v in e:
            inc[v].append(tuple(w for w in e if v!=w))
        for u,v in combinations(e,2):
            assert (min(u,v),max(u,v)) not in pair
            pair[min(u,v),max(u,v)]=ri
    assert all(len(rows)<=4 for rows in inc.values())
    near = {v: set(sum(rows,())) for v, rows in inc.items()}
    footprints = defaultdict(set)
    for v in sorted(near):
        for choices in product(*inc[v]):
            right = frozenset(choices)
            if len(right)!=4:
                continue
            common = set.intersection(*(near[w] for w in right))
            for others in combinations(sorted(common-{v}),3):
                left = frozenset((v,*others))
                rows = frozenset(pair[min(a,b),max(a,b)] for a in left for b in right)
                if len(rows)==16:
                    tile=tuple(sorted((tuple(sorted(left)),tuple(sorted(right)))))
                    footprints[rows].add(tile)
    return footprints


def covers(footprints,m):
    ans=[]
    def go(left,chosen):
        if not left:
            ans.append(tuple(chosen))
            return
        r=min(left)
        for j,fp in enumerate(footprints):
            if r in fp and fp <= left:
                go(left-fp,chosen+(j,))
    go(frozenset(range(m)),())
    return ans


def components(neighbors):
    pool = set(neighbors)
    parts=[]
    while pool:
        root=min(pool)
        seen, stack={root},[root]
        while stack:
            v=stack.pop()
            for w in neighbors[v]-seen:
                stack.append(w)
                seen.add(w)
        parts.append(seen)
        pool.difference_update(seen)
    return parts


def small_parity(options, weights):
    variables=set(weights)
    graph={j:set() for j in variables}
    pins=set()
    for cell in options:
        if len(cell)==1:
            pins.update(cell)
        else:
            j,k=cell
            graph[j].add(k)
            graph[k].add(j)
    chosen=set()
    ways=1
    for part in components(graph):
        root=min(part)
        phase={root:0}
        stack=[root]
        while stack:
            v=stack.pop()
            for w in graph[v]:
                if w not in phase:
                    phase[w]=1-phase[v]
                    stack.append(w)
                elif phase[w]==phase[v]:
                    return None,0
        wanted={phase[j] for j in pins & part}
        if len(wanted)>1:
            return None,0
        allowed=wanted or {0,1}
        ways*=sum(prod(weights[j] for j in part if phase[j]==bit) for bit in allowed)
        value=next(iter(wanted),1)
        chosen.update(j for j in part if phase[j]==value)
    return chosen,ways


def solve(groups):
    rows=sum(groups,[])
    return tile_partition(rows,regular=True)


def tile_partition(rows, regular=False):
    if not rows:
        return [],dict(footprints=0,extremal_flats=1,reason="accepted")
    candidates=enumerate_from_rows(rows)
    fps=sorted(candidates,key=lambda fp:tuple(sorted(fp)))
    options=[{j for j,fp in enumerate(fps) if i in fp} for i in range(len(rows))]
    raw_options=[len(o) for o in options]
    result={'rows':len(rows),'footprints':len(fps),'raw_frequency_range':[min(raw_options),max(raw_options)]}
    def reject(reason):
        return None,dict(result,reason=reason)
    if not all(1<=q<=3 for q in raw_options):
        return reject('raw frequency')
    incidences=defaultdict(set)
    for i,row in enumerate(rows):
        for v in row:
            incidences[v].add(i)
    neighbors={i:set.union(*(incidences[v] for v in row))-{i} for i,row in enumerate(rows)}
    removed=set()
    while True:
        doomed=set()
        for i,o in enumerate(options):
            for h in neighbors[i]:
                if options[h] < o:
                    doomed.update(o-options[h])
        if not doomed:
            break
        removed.update(doomed)
        for o in options:
            o.difference_update(doomed)
        if not all(options):
            return reject('empty after propagation')
    result['pruned_footprints']=len(removed)
    chosen=set()
    total=1
    for comp in components(neighbors):
        cells=[options[i] for i in comp]
        live=set.union(*cells)
        weights={j:len(candidates[fps[j]]) for j in live}
        freqs={len(o) for o in cells}
        if max(freqs)<=2:
            pick,ways=small_parity(cells,weights)
        elif freqs=={3} and len(comp)<=64:
            assert len(live)<=12
            variables=sorted(live)
            pick=None
            ways=0
            for mask in range(1<<len(variables)):
                guess={v for k,v in enumerate(variables) if mask>>k&1}
                if all(len(c & guess)==1 for c in cells):
                    if pick is None:
                        pick=guess
                    ways+=prod(weights[j] for j in guess)
        else:
            return reject('mixed frequencies or oversized homogeneous region')
        if pick is None:
            return reject('unsatisfied residual')
        chosen.update(pick)
        total*=ways
    assert all(sum(i in fps[j] for j in chosen)==1 for i in range(len(rows)))
    selected=[[list(side) for side in sorted(candidates[fps[j]])[0]] for j in sorted(chosen)]
    used=set()
    for left,right in selected:
        assert not (used & set(left+right))
        used.update(left+right)
    n=len(incidences)
    dimension=len(selected)+n-len(used)
    if regular:
        assert 12*dimension==5*n
    witness={v:0 for v in incidences}
    for _,right in selected:
        for y in right:
            witness[y]=1
    assert all(len({witness[v] for v in row})==2 for row in rows)
    return selected,dict(result,dimension=dimension,extremal_flats=total,reason='accepted')


def grid():
    groups=[[] for _ in range(4)]
    for i,j,k in product(range(4), repeat=3):
        groups[i^j^k].append((4*i+j,16+4*j+k,32+4*k+i))
    return groups


def relabel(groups,k):
    rng=Random(k)
    points=sorted({v for row in sum(groups,[]) for v in row})
    perm=points.copy()
    rng.shuffle(perm)
    name=dict(zip(points,perm))
    out=[]
    for g in groups:
        rr=[]
        for e in g:
            block=[name[v] for v in e]
            rng.shuffle(block)
            rr.append(tuple(block))
        rng.shuffle(rr)
        out.append(rr)
    rng.shuffle(out)
    return out


def random_input(n,rng):
    groups=[]
    used_pairs=set()
    for _ in range(4):
        for _ in range(900):
            p=list(range(n))
            rng.shuffle(p)
            group=[tuple(p[i:i+3]) for i in range(0,n,3)]
            pairs={tuple(sorted(t)) for e in group for t in combinations(e,2)}
            if not pairs&used_pairs:
                groups.append(group)
                used_pairs.update(pairs)
                break
        else:
            return None
    return groups


def independent_free_set(groups):
    """Enumerate possible free sets, independently of tile enumeration."""
    rows=sum(groups,[])
    pts={v for row in rows for v in row}
    if (5*len(pts))%12:
        return False
    count=0
    for free in combinations(sorted(pts),len(pts)//3):
        f=set(free)
        if any(len(f.intersection(row))!=1 for row in rows):
            continue
        graph={v:set() for v in pts-f}
        for row in rows:
            x,y=set(row)-f
            graph[x].add(y)
            graph[y].add(x)
        okay=True
        for part in components(graph):
            if len(part)!=8:
                okay=False
                break
            right=graph[min(part)]
            left=part-right
            if len(right)!=4 or any(graph[v]!=right for v in left) or any(graph[v]!=left for v in right):
                okay=False
                break
        if okay:
            count+=1
    return count


def main():
    fixture=instance(0)
    geometry=grid()
    summary={}
    for tag,gs in [('nonextendible_tile',fixture),('three_planes',geometry)]:
        n=sum(len(g) for g in gs)
        tiles=enumerate_tiles(gs)
        fps=sorted(tiles,key=lambda fp:tuple(sorted(fp)))
        solutions=covers(fps,n)
        ns=[sum(r in fp for fp in fps) for r in range(n)]
        counts={str(c):ns.count(c) for c in sorted(set(ns))}
        decoys=[j for j in range(len(fps)) if not any(j in ss for ss in solutions)]
        answer,measure=solve(gs)
        assert answer is not None
        assert sum(prod(len(tiles[fps[j]]) for j in sol) for sol in solutions)==measure["extremal_flats"]
        for i in range(8):
            shift,check=solve(relabel(gs,i))
            assert shift is not None and check["extremal_flats"]==measure["extremal_flats"]
        if tag=='three_planes':
            assert len(fps)==12 and len(solutions)==3 and counts=={'3':64} and not decoys
        else:
            assert len(fps)==5 and len(solutions)==1 and counts=={'1':48,'2':16} and len(decoys)==1
        summary[tag]=dict(measure,exact_covers=len(solutions),nonextendible_footprints=decoys,frequencies=counts,
                          relabeled_checks=8)
    rng=Random(1055)
    tallies=defaultdict(int)
    for s in range(60):
        gs=None
        while gs is None:
            gs=random_input(12,rng)
        reference=independent_free_set(gs)
        _,checked=solve(gs)
        assert checked.get("extremal_flats",0)==reference
        tallies[str(reference)]+=1
    # Also directly check enough positive Latin examples: all three parts have size four.
    for seed in range(10):
        latin=[[(i,4+(i^s),8+(i^[0,2,3,1][s])) for i in range(4)] for s in range(4)]
        gs=relabel(latin,seed)
        assert independent_free_set(gs)==solve(gs)[1]["extremal_flats"]==3
    summary['independent_free_set_oracle']=dict(seed=1055,sampled_linear_12_point_inputs=dict(tallies),
                        relabeled_positive_controls=10)
    return summary


if __name__=='__main__':
    print(json.dumps(main(),indent=2,sort_keys=True))
