"""Finite checks for the near-extremal affine-flat and local autarky thresholds."""
from collections import Counter, defaultdict, deque
from itertools import combinations
from fractions import Fraction
import json


def graph_bound_checks():
    cases = 0
    equality = []
    for left in range(1, 50):
        for right in range(left, 50):
            size = left + right
            for edges in range(size - 1, min(left * right, 4 * left) + 1):
                cases += 1
                gap = 16 * (size - 1) - 7 * edges
                assert gap >= 0
                if (left, right, edges) != (4, 4, 16):
                    assert 9 * edges <= 20 * (size - 1)
                    assert 2 * size <= 5 * gap
                if size > 14 or edges < 2 * size:
                    assert 7 * edges <= 15 * (size - 1)
                    if 7 * edges == 15 * (size - 1):
                        equality.append((left, right, edges))
    return {'size_edge_cases':cases, 'open_threshold_equality_candidates':equality}


def audit(groups, phases):
    n = len(phases)
    pairs = set()
    for group in groups:
        assert sorted(v for row in group for v in row) == list(range(n))
        for row in group:
            assert len(set(row)) == 3
            edges = set(combinations(sorted(row), 2))
            assert not edges & pairs
            pairs.update(edges)
            assert any(phases[u] == (phases[v][0], phases[v][1] ^ 1)
                       for u, v in combinations(row, 2))
    return len({phase[0] for phase in phases})


def fifteen():
    groups = [[(i, 5 + (i+s)%5, 10 + (i+2*s)%5) for i in range(5)]
              for s in range(4)]
    phases = [(0,0)]*5 + [(0,1)]*5 + [(i+1,0) for i in range(5)]
    dimension = audit(groups, phases)
    neighbors = [set() for _ in phases]
    for group in groups:
        for row in group:
            for x in row:
                neighbors[x].update(y for y in row if y != x)
    common = max(len(set.intersection(*(neighbors[x] for x in shore)))
                 for shore in combinations(range(15),4))
    assert dimension == 6 and common < 4
    return {'points':15,'certified_dimension':dimension,
            'max_common_neighbors_of_any_four_points':common}


def base():
    """Each record is (original color, chosen pair, owner of the third point)."""
    rows = []
    for s in range(4):
        selected = [(8*b+i, 8*b+4+(i ^ (s^b))) for b in range(4)
                    for i in range(4) if not (b == s and i == 0)]
        ports = [8*s,8*s+4]
        targets = [32+(i+3*s)%13 for i in range(13)]
        for x, y in selected:
            z = ports.pop(0) if ports and x//8 != s else targets.pop(0)
            rows.append((s,x,y,z))
    return rows


def atom(point):
    return point//8 if point<32 else 4+point-32


def short_words(stubs, limit):
    """Net signed edge incidence vectors of all cyclically reduced short closed walks."""
    adj = defaultdict(list)
    for e, (u,v) in enumerate(stubs,1):
        assert u != v
        adj[u].append((v,e));adj[v].append((u,-e))
    equations = set()
    def visit(start, u, trace):
        if u == start and len(trace)>=2 and trace[-1] != -trace[0]:
            co = Counter(abs(i) for i in trace if i>0)
            co.subtract(abs(i) for i in trace if i<0)
            form = sorted((i-1,c) for i,c in co.items() if c)
            assert form
            if form[0][1] < 0:
                form = [(i,-c) for i,c in form]
            equations.add(tuple(form))
        if len(trace)<limit:
            for v, e in adj[u]:
                if not trace or trace[-1] != -e:
                    visit(start,v,(*trace,e))
    for u in adj:
        visit(u,u,())
    return sorted(equations)


def cyclic_lift(stubs):
    length = len(stubs)
    equations = short_words(stubs,4)
    for p in (7,11,17,31,67,127,257,521):
        values = []
        for i in range(length):
            forbidden = set()
            for form in equations:
                if form[-1][0] != i: continue
                rest = sum(c * values[j] for j,c in form[:-1])
                forbidden.add((-rest * pow(form[-1][1], -1, p)) % p)
            x = next((a for a in range(p) if a not in forbidden),None)
            if x is None: break
            values.append(x)
        if len(values) == length:
            assert all(sum(c*values[j] for j,c in form) % p for form in equations)
            return p,values,len(equations)
    raise AssertionError('No test cover found')


def quotient_girth(adj, p):
    # Translations act transitively on the copies of each base atom.
    girth = len(adj)+1
    for root in range(17):
        d = {root:0}
        parent = {root:None}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in d:
                    queue.append(v)
                    d[v] = d[u]+1
                    parent[v] = u
                elif v != parent[u]:
                    girth = min(girth, d[u]+d[v]+1)
        assert len(d)==len(adj)
    return girth


def core_leaf():
    edges = [(i,4+j) for i in range(4) for j in range(4) if (i,j)!=(0,0)]
    result = Counter()
    for mask in range(1,256):
        a = [(mask>>i)&1 for i in range(8)]
        needed = sum(a[x]!=a[y] for x,y in edges)+a[0]+a[4]
        assert needed >= 2
        result[needed]+=1
    return dict(sorted(result.items()))


def detect_cores(groups):
    """Read only the actual triples. Each candidate chooses 15 distinct rows."""
    rows = [row for group in groups for row in group]
    n = 3*len(groups[0])
    owner = {}
    neighbors = [set() for _ in range(n)]
    for r,row in enumerate(rows):
        for a,b in combinations(row,2):
            owner[(a,b)] = owner[(b,a)] = r
            neighbors[a].add(b);neighbors[b].add(a)
    shores = set()
    for u in range(n):
        for v in {t for w in neighbors[u] for t in neighbors[w] if t>u}:
            common = neighbors[u] & neighbors[v]
            shores.update(combinations(sorted(common),4))
    patterns = set()
    for B in shores:
        counts = Counter(u for v in B for u in neighbors[v] if u not in B)
        for A in combinations(sorted(u for u,k in counts.items() if k>=3),4):
            available = [(a,b) for a in A for b in B if b in neighbors[a]]
            if len(available)<15: continue
            for chosen in combinations(available,15):
                ids = tuple(sorted(owner[x] for x in chosen))
                if len(set(ids))==15:
                    patterns.add((min(A,B), max(A,B), ids))
    ranks = [(set(a+b),set(ids)) for a,b,ids in patterns]
    if (len(set().union(*(v for v,_ in ranks)))!=8*len(ranks)
            or len(set().union(*(q for _,q in ranks)))!=len(rows)
            or len(rows)!=15*len(ranks)):
        return {'patterns':len(patterns),'certified':False}
    word = [0]*n
    for _,B,_ in patterns:
        for v in B: word[v]=1
    assert all(len({word[v] for v in row})==2 for row in rows)
    return {'patterns':len(patterns), 'certified':True,
            'reconstructed_dimension':n-7*len(patterns),
            'verified_rows':len(rows)}


def lifted_control():
    original = base()
    stubs = [(atom(x),atom(z)) for _,x,y,z in original]
    p,shifts,equations = cyclic_lift(stubs)
    adj = [set() for _ in range(17*p)]
    groups = [[] for _ in range(4)]
    phases = [(17*f+atom(v), int(v < 32 and v%8>=4))
              for f in range(p) for v in range(45)]
    for (s,x,y,z),r in zip(original,shifts):
        for f in range(p):
            h = (f+r)%p
            u,v=17*f+atom(x),17*h+atom(z)
            assert v not in adj[u] and u != v
            adj[u].add(v);adj[v].add(u)
            groups[s].append((45*f+x,45*f+y,45*h+z))
    d=audit(groups,phases)
    g=quotient_girth(adj,p)
    assert d==17*p and g>=5
    # Independent stop-set enumeration up to four points. Any minimal nonempty
    # stopping set is connected in the point shadow. Translational symmetry
    # permits anchoring its first point in the base fiber. The closure search
    # below extends only at an actual singleton-touched row.
    allrows=[frozenset(row) for group in groups for row in group]
    touches=defaultdict(list)
    for row in allrows:
        for x in row: touches[x].append(row)
    visited=set()
    def can_stop(S):
        if S in visited: return False
        visited.add(S)
        broken=next((r for x in sorted(S) for r in touches[x] if len(r & S)==1),None)
        if broken is None: return True
        if len(S)==4: return False
        return any(can_stop(S|{x}) for x in sorted(broken-S))
    assert not any(can_stop(frozenset([x])) for x in range(45))
    return {'sheets':p,'base_atoms':17,'base_connectors':60,
            'small_cycle_voltage_constraints':equations,'quotient_girth':g,
            'points':45*p,'rows':60*p,'certified_flat_dimension':d,
            'nonempty_stopping_sets_of_size_at_most_four':0,
            'partial_sets_visited':len(visited),'raw_reader':detect_cores(groups)}


def main():
    return {'component_profiles':graph_bound_checks(),'no_K44_control':fifteen(),
            'nonempty_core_masks_by_required_neighbors':core_leaf(),
            'lifted_obstruction':lifted_control()}

if __name__=='__main__':
    print(json.dumps(main(),indent=2))
