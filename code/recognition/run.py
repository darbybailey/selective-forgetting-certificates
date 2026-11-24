"""Exact 5V/12-flat recognition via pair grids and footprints. Standard library."""
from collections import defaultdict, Counter
from itertools import combinations, product
from random import Random
from math import prod
import json


def candidate_grids(triples):
    """Each key is a set of sixteen triple indices; store every realization per key."""
    neighbors = defaultdict(set)
    owner = {}
    for i, row in enumerate(triples):
        for a,b in combinations(sorted(row), 2):
            if (a,b) in owner:
                raise ValueError("Two rows share a pair.")
            owner[a,b] = i
            neighbors[a].add(b)
            neighbors[b].add(a)
    grids = {}
    for p in neighbors:
        for ys in combinations(sorted(neighbors[p]), 4):
            common = set.intersection(*(neighbors[y] for y in ys))
            for extra in combinations(sorted(x for x in common if x>p), 3):
                xs = (p,) + extra
                if xs >= ys:
                    continue
                pairs = set(xs) | set(ys)
                index = frozenset(owner[tuple(sorted((x,y)))] for x in xs for y in ys)
                if len(index) == 16 and all(len(pairs.intersection(triples[i]))==2 for i in index):
                    grids.setdefault(index, []).append((xs,ys))
    return grids


def propagated_cover(supports, nrows):
    """Choose blocks, using 0/1/2-variable row reasoning and branching otherwise."""
    containing = [[] for _ in range(nrows)]
    for i, block in enumerate(supports):
        for t in block:
            containing[t].append(i)

    def solve(required, excluded):
        required, excluded = set(required), set(excluded)
        while True:
            added = False
            equations, long = [], []
            for row in containing:
                yes = [i for i in row if i in required]
                free = [i for i in row if i not in required and i not in excluded]
                if len(yes)>1 or (not yes and not free):
                    return None
                if yes and free:
                    excluded.update(free)
                    added=True
                elif not yes and len(free)==1:
                    required.add(free[0])
                    added=True
                elif not yes and len(free)==2:
                    equations.append(free)
                elif not yes:
                    long.append(free)
            if not added:
                break
        adj = defaultdict(set)
        for i,j in equations:
            adj[i].add(j)
            adj[j].add(i)
        side = {}
        for i in adj:
            if i in side:
                continue
            side[i]=0
            stack=[i]
            while stack:
                x=stack.pop()
                for y in adj[x]:
                    if y in side:
                        if side[y]==side[x]:
                            return None
                    else:
                        side[y]=1-side[x]
                        stack.append(y)
        if not long:
            return sorted(required | {i for i in side if side[i]})
        row = min(long, key=len)
        for i in row:
            answer = solve(required | {i},excluded | (set(row)-{i}))
            if answer is not None:
                return answer
        return None

    return solve(set(),set())


def cyclic(k):
    omega = [0,2,3,1]
    return [[(12*b+i,12*b+4+(i^s),12*((b+int(s==1))%k)+8+(i^omega[s]))
             for b in range(k) for i in range(4)] for s in range(4)]


def cube():
    """A row is a lattice point; the three system points are its incident axis lines."""
    groups=[[] for _ in range(4)]
    for x,y,z in product(range(4),repeat=3):
        groups[x^y^z].append((4*y+z,16+4*x+z,32+4*x+y))
    return groups


def quotient_cube():
    """Quotient axis line system by translation (x,y,z) -> (x xor 2,y xor 2,z xor 2)."""
    omega=[0,2,3,1]
    groups=[[] for _ in range(4)]
    names={}
    for x,y,z in product(range(4),repeat=3):
        mate=(x^2,y^2,z^2)
        if (x,y,z)>mate: continue
        points=[]
        for axis,labels in enumerate(((y,z),(x,z),(x,y))):
            key=(axis,min(labels,tuple(v^2 for v in labels)))
            points.append(names.setdefault(key,len(names)))
        groups[x^omega[y]^omega[omega[z]]].append(tuple(points))
    return groups


def crossswap(groups, seed, steps):
    """A local switch of third coordinates keeps row partitions and checks linearity."""
    rng=Random(seed)
    groups=[rows.copy() for rows in groups]
    for _ in range(steps):
        d=rng.randrange(4)
        i,j=rng.sample(range(len(groups[d])),2)
        a,b,c=groups[d][i]
        e,f,g=groups[d][j]
        old=groups[d][i],groups[d][j]
        groups[d][i],groups[d][j]=(a,b,g),(e,f,c)
        pairs=[tuple(sorted(p)) for s in groups for r in s for p in combinations(r,2)]
        if len(pairs)!=len(set(pairs)):
            groups[d][i],groups[d][j]=old
    return groups


def verify_instance(groups, seed, independent=False):
    n=len(groups[0])*3
    lab=list(range(n))
    rng=Random(seed)
    rng.shuffle(lab)
    triples=[]
    for group in groups:
        assert sorted(x for row in group for x in row)==list(range(n))
        for row in group:
            perm=[lab[x] for x in row]
            rng.shuffle(perm)
            triples.append(tuple(perm))
    rng.shuffle(triples)
    grids=candidate_grids(triples)
    supports=sorted(grids, key=lambda s: tuple(sorted(s)))
    degrees=[sum(i in s for s in supports) for i in range(len(triples))]
    chosen=propagated_cover(supports,len(triples))
    if chosen is not None:
        assert sorted(i for j in chosen for i in supports[j])==list(range(len(triples)))
        active=set()
        labels={}
        for j in chosen:
            a,b=grids[supports[j]][0]
            assert not active.intersection(set(a)|set(b))
            active.update(a); active.update(b)
            labels.update({x:(j,0) for x in a})
            labels.update({x:(j,1) for x in b})
        for i in range(n):
            if i not in active:
                labels[i]=(i+len(supports),0)
        assert 12*len({key for key,_ in labels.values()})==5*n
        assert all(any(labels[a][0]==labels[b][0] and labels[a][1]!=labels[b][1]
                       for a,b in combinations(row,2)) for row in triples)
    graph=[{j for j,q in enumerate(supports) if j!=i and p.intersection(q)}
           for i,p in enumerate(supports)]
    def has_induced_star(k):
        return any(all(v not in graph[u] for u,v in combinations(leaves,2))
                   for neighbors in graph for leaves in combinations(neighbors,k))
    star4=has_induced_star(4)
    assert not has_induced_star(5)
    count = weighted = None
    if independent or all(d==1 for d in degrees):
        # A direct substitution in the exact-cover constraints, for small lists.
        count=weighted=0
        for selected in combinations(supports,len(triples)//16):
            if all(sum(i in block for block in selected)==1 for i in range(len(triples))):
                count+=1
                weighted+=prod(len(grids[block]) for block in selected)
        assert (count>0)==(chosen is not None)
    return {"points":n,"supports":len(supports),"row_incidence_histogram":dict(sorted(Counter(degrees).items())),
            "sharp_flat":chosen is not None, "distinct_footprint_covers":count, "sharp_flats_by_weighted_count":weighted,
            "contains_induced_claw":has_induced_star(3), "contains_induced_four_leaf_star":star4}


def cubic_lift(perms):
    """Edges of color j are (left i, right perms[j][i]); each gets two points."""
    n = len(perms[0])
    assert len(perms)==3
    for perm in perms:
        assert sorted(perm)==list(range(n))
    assert all(len({p[i] for p in perms})==3 for i in range(n))
    matchings=[[] for _ in range(4)]
    inverse=[[p.index(i) for i in range(n)] for p in perms]
    for z in range(4):
        bits=[z&1,z>>1,(z&1)^(z>>1)]
        for side in (0,1):
            for v in range(n):
                matchings[z].append(tuple(2*(n*color+(inverse[color][v] if side else v))
                                          +(bits[color]^side) for color in range(3)))
    return matchings


def base_squares(perms):
    n=len(perms[0])
    adj=[{n+p[i] for p in perms} for i in range(n)]
    return sorted(frozenset((a,b,c,d)) for a,b in combinations(range(n),2)
                  for c,d in combinations(sorted(adj[a]&adj[b]),2))


def check_lift(perms):
    n=len(perms[0])
    groups=cubic_lift(perms)
    rows=[r for group in groups for r in group]
    candidates=candidate_grids(rows)
    squares=base_squares(perms)
    expected_supports={frozenset(v+2*n*z for v in square for z in range(4)) for square in squares}
    assert set(candidates)==expected_supports
    factor=propagated_cover(squares,2*n)
    solved=verify_instance(groups,92,True)
    assert solved["sharp_flat"]==(factor is not None)
    assert all(len({int(x//(2*n)==1) for x in row})==2 for row in rows)
    return {"base_vertices":2*n,"base_squares":len(squares),"base_square_factor":factor is not None,
            **solved}


def main():
    cases={}
    for k in (1,2,5,25):
        results=[verify_instance(cyclic(k),j,k<=5) for j in (62,821)]
        assert results[0]==results[1] and results[0]["sharp_flat"]
        cases["connected_"+str(k)]=results[0]
    for name,groups in [("cube",cube()),("quotient_cube",quotient_cube()),("cube_after_switches",crossswap(cube(),1024,90))]:
        cases[name]=verify_instance(groups,51,True)
    # A regular colorable control with too few four-by-four grids.
    q=12
    generic=[[(i,q+((i+d)%q),2*q+((i+2*d)%q)) for i in range(q)] for d in range(4)]
    cases["shift_control"]=verify_instance(generic,101,True)
    # The bases have 3 explicitly named perfect matchings. In the negative control,
    # swapping mates of left 0 and 3 connects two K3,3 pieces by two crossing edges.
    bad=[[3,1,2,0,4,5]]+[[3*(i//3)+(i+j)%3 for i in range(6)] for j in (1,2)]
    good=[[(i+j)%4 for i in range(4)] for j in (0,1,2)] # cube graph
    cases["square_lift_positive"]=check_lift(good)
    cases["square_lift_no_cover"]=check_lift(bad)
    assert (cases["square_lift_no_cover"]["sharp_flat"] is False and
            min(cases["square_lift_no_cover"]["row_incidence_histogram"])>0)
    return cases


if __name__=="__main__":
    print(json.dumps(main(),indent=2))
