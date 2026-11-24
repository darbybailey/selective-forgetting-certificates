"""Recognize a fixed additive allowance from a sharp extremal affine dimension."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"overlap"))
from run import components, enumerate_from_rows, tile_partition


def choose_pairs(rows, rank_limit):
    """Search on exceptional rows using memoized signed union-find states."""
    local=sorted({p for row in rows for p in row})
    pos={v:i for i,v in enumerate(local)}
    half=[tuple(pos[v] for v in row) for row in rows]
    pairs=[tuple(combinations(row,2)) for row in half]
    seen=set()

    def visit(i, rank, state):
        if i==len(rows):
            return []
        key=(i,state)
        if key in seen:
            return None
        seen.add(key)
        for a,b in pairs[i]:
            u,x=state[a]
            v,y=state[b]
            if u==v:
                if x^y:
                    tail=visit(i+1,rank,state)
                    if tail is not None:
                        return [(local[a],local[b])]+tail
                continue
            if rank==rank_limit:
                continue
            large,small=max(u,v),min(u,v)
            sign=x^y^1
            joined=tuple((small,t^sign) if lab==large else (lab,t) for lab,t in state)
            tail=visit(i+1,rank+1,joined)
            if tail is not None:
                return [(local[a],local[b])]+tail
        return None
    return visit(0,0,tuple((i,0) for i in range(len(local))))


def solve(groups,k):
    """Return opposite pairs certifying dimension at least ceil(5V/12−k)."""
    k=Fraction(k)
    if k<0:
        return None
    n=3*len(groups[0])
    rows=sum(groups,[])
    target=Fraction(5*n,12)-k
    # If an integer c meets the target, its actual deficit is <=k.
    want= -(-target.numerator//target.denominator)
    if want==Fraction(5*n,12):
        answer,_=tile_partition(rows)
        return None if answer is None else [(a,b) for left,right in answer for a in left for b in right]
    footprints=enumerate_from_rows(rows)
    allrows=set(range(len(rows)))
    can_be_good=set.union(set(),*footprints)
    mandatory=allrows-can_be_good
    optional=sorted(can_be_good)
    maxbad=min(len(rows),int(80*k))
    for b in range(len(rows)%16,maxbad+1,16):
        goodrank=7*((len(rows)-b)//16)
        budget=n-want-goodrank
        if budget<0 or b<len(mandatory):
            continue
        for more in combinations(optional,b-len(mandatory)):
            inds=mandatory.union(more)
            bad_indices=sorted(inds)
            good=[row for i,row in enumerate(rows) if i not in inds]
            tiles,_=tile_partition(good)
            if tiles is None:
                continue
            exceptional=choose_pairs([rows[i] for i in bad_indices],budget)
            if exceptional is None:
                continue
            out=list(exceptional)
            for left,right in tiles:
                out.extend((a,b) for a in left for b in right)
            check_witness(groups,out,want)
            return out
    return None


def check_witness(groups,out,want):
    rows=sum(groups,[])
    idx={frozenset(p):i for i,row in enumerate(rows) for p in combinations(row,2)}
    assert sorted(idx[frozenset(p)] for p in out)==list(range(len(rows)))
    graph={p:set() for row in rows for p in row}
    for a,b in out:
        graph[a].add(b)
        graph[b].add(a)
    parts=components(graph)
    for part in parts:
        start=min(part)
        val,stack={start:0},[start]
        while stack:
            a=stack.pop()
            for b in graph[a]:
                if b not in val:
                    val[b]=1-val[a]
                    stack.append(b)
                else:
                    assert val[b]!=val[a]
    assert len(parts)>=want
    return len(parts)


def linked_pair():
    groups=[[(12*b+i,12*b+4+(i^s),12*((b+int(s==1))%2)+8+(i^[0,2,3,1][s]))
              for b in range(2) for i in range(4)] for s in range(4)]
    a,b,c=groups[0][0]
    x,y,z=groups[0][4]
    groups[0][0]=(x,b,c)
    groups[0][4]=(a,y,z)
    return groups


def main():
    test=linked_pair()
    clean=solve(test,0)
    near=solve(test,1)
    assert clean is None and near is not None
    d=check_witness(test,near,9)
    assert d==9 and solve(test,Fraction(1,2)) is None
    affine_plane=[[(0,1,2),(3,4,5),(6,7,8)]]
    affine_plane+=[[(i,3+(i+k)%3,6+(i+2*k)%3) for i in range(3)] for k in range(3)]
    assert solve(affine_plane,Fraction(3,4)) is None
    # A 16-row intact tile and 32 exceptional rows in another component.
    good=[[(i,4+(i^s),8+(i^[0,2,3,1][s])) for i in range(4)] for s in range(4)]
    mixed=[gg+[(a+12,b+12,c+12) for a,b,c in hh] for gg,hh in zip(good,test)]
    full=solve(good,0)
    assert full is not None
    combined=full+[(a+12,b+12) for a,b in near]
    assert check_witness(mixed,combined,14)==14
    recovered=solve(mixed,1)
    assert recovered is not None and check_witness(mixed,recovered,14)==14
    # With degree below four, an isolated row cannot be a full tile.
    partial, _=tile_partition([good[0][0]])
    assert partial is None
    assert tile_partition([])[0]==[]
    partial_yes=[(i,4+j,8+4*i+j) for i in range(4) for j in range(4)]
    partition,_=tile_partition(partial_yes)
    assert partition is not None and len(partition)==1
    return {'linked_24_points':{'maximum_dimension':d,'k_zero':False,'k_half':False,'k_one':True},
            'nine_point_plane':{'threshold':3,'colorable':False,'k_three_quarters':False},
            'disconnected_36_points':{'certified_product_dimension':14, 'algorithm_found_witness':True},
            'empty_tile_partition':True,'isolated_row_tile_partition':False,'sixteen_degree_one_free_points':True}


if __name__=='__main__':
    print(json.dumps(main(),indent=2,sort_keys=True))
