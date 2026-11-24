"""A bounded-size NAE autarky reader, followed by an exhaustive residual solver."""
from collections import defaultdict
from itertools import combinations, product
import json
from random import Random


def autarky_through(root, rows, incidence, limit):
    """Complement symmetry lets the root have color zero. Return one support."""
    def extend(assignment, touched):
        unresolved = None
        for index in sorted(touched):
            row = rows[index]
            used = {assignment[v] for v in row if v in assignment}
            if len(used) == 2:
                continue
            free = [v for v in row if v not in assignment]
            if not free or len(assignment) == limit:
                return None
            if unresolved is None or len(free) < len(unresolved[0]):
                unresolved = (free, 1 - next(iter(used)))
        if unresolved is None:
            return assignment
        free, value = unresolved
        for v in free:
            answer = extend({**assignment, v:value}, touched | incidence[v])
            if answer is not None:
                return answer
        return None

    return extend({root:0}, set(incidence[root]))


def peel(rows, limit=14):
    residual = sorted(tuple(sorted(t)) for t in rows)
    steps = []
    while residual:
        incidence = defaultdict(set)
        for i,row in enumerate(residual):
            for v in row:
                incidence[v].add(i)
        for root in sorted(incidence):
            overwrite = autarky_through(root, residual, incidence, limit)
            if overwrite is not None:
                break
        else:
            break
        touched = {i for v in overwrite for i in incidence[v]}
        assert touched and all({overwrite[v] for v in residual[i] if v in overwrite} == {0,1}
                               for i in touched)
        steps.append((overwrite,len(touched)))
        residual = [t for i,t in enumerate(residual) if i not in touched]
    return residual, steps


def solve_residual(rows):
    """Pick a permanent opposite pair per triple. XOR consistency prunes early."""
    if not rows:
        return {}
    vertices = sorted({v for row in rows for v in row})
    index = {v:i for i,v in enumerate(vertices)}
    stack = [(0, list(range(len(vertices))), [0]*len(vertices))]
    def find(j, parent, offsets):
        color = 0
        while parent[j] != j:
            color ^= offsets[j]
            j = parent[j]
        return j,color
    while stack:
        i,parent,offsets = stack.pop()
        if i == len(rows):
            return {v:find(index[v],parent,offsets)[1] for v in vertices}
        a,b,c = rows[i]
        ra,va = find(index[a],parent,offsets)
        for neighbor in (b,c):
            rb,vb = find(index[neighbor],parent,offsets)
            if ra == rb:
                if va != vb:
                    stack.append((i+1,parent,offsets))
            else:
                next_parent = parent.copy()
                next_offsets = offsets.copy()
                next_parent[ra] = rb
                next_offsets[ra] = 1 ^ va ^ vb
                stack.append((i+1,next_parent,next_offsets))
    return None


def reader(rows, k, limit=14):
    if limit not in (8,14):
        raise ValueError("The proven residual bounds apply to 8 and 14.")
    remaining, steps = peel(rows, limit)
    numerator,denominator = (240,7) if limit==14 else (80,1)
    if denominator*len(remaining)>numerator*k:
        return "OUTSIDE_YES_PROMISE",remaining,steps
    witness = solve_residual(remaining)
    if witness is None:
        return "UNSAT",remaining,steps
    for part,_ in reversed(steps):
        witness.update(part)
    for v in {v for row in rows for v in row}:
        witness.setdefault(v,0)
    assert all(len({witness[v] for v in row})==2 for row in rows)
    return "WITNESS",remaining,steps


def sharp(t):
    omega = (0,2,3,1)
    return [(12*b+i, 12*b+4+(i^s), 12*((b+(s==1))%t)+8+(i^omega[s]))
            for s in range(4) for b in range(t) for i in range(4)]


def plane():
    return [tuple(3*x+k for x in range(3)) for k in range(3)]+[
        tuple(3*((s*y+k)%3)+y for y in range(3)) for s in range(3) for k in range(3)]


def brute_witness(rows):
    points = sorted({v for row in rows for v in row})
    for bits in product((0,1),repeat=len(points)):
        x = dict(zip(points,bits))
        if all(len({x[v] for v in row})==2 for row in rows):
            return True
    return False


def blind_relabel(rows,n,seed):
    rng=Random(seed); labels=list(range(n)); rng.shuffle(labels)
    result=[tuple(labels[v] for v in row) for row in rows]
    rng.shuffle(result)
    return result


def run():
    positive=[]
    for t in (1,2,5,25):
        for seed in (13,101):
            rows=blind_relabel(sharp(t),12*t,seed)
            status,res,steps=reader(rows,0)
            assert status=="WITNESS" and not res
            positive.append(dict(points=12*t,seed=seed,steps=len(steps),
                                 residual=len(res),largest_overwrite=max(len(s) for s,_ in steps)))
    unsat_rows=plane()
    assert len(unsat_rows)==12 and not brute_witness(unsat_rows)
    controls={}
    for k in (0,2):
        status,r,steps=reader(unsat_rows,k)
        assert status==("UNSAT" if k==2 else "OUTSIDE_YES_PROMISE")
        controls[k]=[status,len(r),len(steps)]
    rng=Random(1201)
    for _ in range(96):
        rows=[t for t in combinations(range(7),3) if rng.random()<0.30]
        st,r,steps=reader(rows,100)
        assert (st=="WITNESS")==brute_witness(rows)
    # A connected 33-point tripartite input has a known 12-dimensional flat:
    # one phase for the A/B shores and 11 free C bits. Thus k=2 is valid.
    q=11
    trapped=[(i,q+(i+s)%q,2*q+(i+2*s)%q) for s in range(4) for i in range(q)]
    st,rem,edits=reader(trapped,2)
    assert st=="WITNESS" and len(rem)==44 and not edits
    residual_witness=dict(points=3*q,flat_dimension_at_least=q+1,
                          promised_gap_at_most=2,residual_triples=len(rem),status=st)
    # Deterministic, mixed-core control. Rename a sharp block and the hard core
    # independently, cross the rows that have opposite A/B witnesses, and verify.
    extra=sharp(3)
    first=list(trapped); second=[tuple(3*q+v for v in row) for row in extra]
    a,b,c=first[0]; u,v,w=second[0]
    first[0]=(a,b,w); second[0]=(u,v,c)
    st,rem,edits=reader(blind_relabel(first+second,3*q+36,21),2)
    assert st=="WITNESS" and edits and rem
    mixed_witness=dict(points=3*q+36,flat_dimension_at_least=q+1+15,
                       promised_gap_at_most=2,residual_triples=len(rem),overwrites=len(edits),status=st)
    stopset=0
    # Verify the seed-and-branch reader independently against every partial
    # assignment of at most four variables on these random small systems.
    for _ in range(12):
        rows=[t for t in combinations(range(6),3) if rng.random()<0.45]
        incidence={v:{i for i,row in enumerate(rows) if v in row} for v in range(6)}
        for v in range(6):
            if not incidence[v]:
                continue
            expected=False
            for word in product((-1,0,1),repeat=6):
                if word[v]!=0 or sum(c>=0 for c in word)>4:
                    continue
                if all((not (used:={word[a] for a in row if word[a]>=0})) or len(used)==2 for row in rows):
                    expected=True;break
            assert bool(autarky_through(v,rows,incidence,4))==expected
            stopset+=1
    positives,negatives=[],[]
    dead=[tuple(v+9*b for v in row) for b in range(4) for row in plane()]
    for tag in range(1,8):
        sat,_,_=reader(blind_relabel(sharp(3),36,200+tag),0)
        ruled,_,_=reader(blind_relabel(dead,36,530+tag),0)
        assert sat=="WITNESS" and ruled=="OUTSIDE_YES_PROMISE"
        positives.append(sat=="WITNESS"); negatives.append(ruled=="WITNESS")
    for subset in range(128):
        inferred=0;expected=0
        for index in range(7):
            if subset>>index&1: expected |= index+1
            statuses=positives if subset>>index&1 else negatives
            if statuses[index]: inferred |= index+1
        assert inferred==expected
        exclusion=next(i for i in range(1,8) if i!=inferred)
        if subset.bit_count()==1:
            assert subset!=(1<<(exclusion-1))
    return dict(seven_source_status_patterns=128,separate_36_point_source_readings=14,
                relabelled_connected_extremizers=positive,
                affine_plane_negative=controls,brute_truth_checks=96,
                positive_residual=residual_witness,connected_mixture=mixed_witness,
                exhaustive_partial_assignment_crosschecks=stopset)

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
