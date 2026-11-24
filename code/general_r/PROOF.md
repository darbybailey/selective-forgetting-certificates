# Sharp affine dimension for every number of matchings

Let r ≥ 2. A linear 3-uniform hypergraph has three distinct vertices in every edge, and no pair of distinct vertices occurs in two edges. Suppose its N vertices each have degree r. A satisfying coloring uses both bits on every triple. If a nonempty affine subspace F of binary assignments consists of satisfying colorings, then

    dim F ≤ (r+1)N/(3r).

The bound does not require a known resolution into matchings. For each r, infinitely many connected examples attain the bound and have an explicit resolution into r perfect matchings. At r=4 this gives 5N/12.

## Proof and equality

On a valid flat, the two differences of one coordinate of a triple from the other two take values in an affine subset of the binary plane avoiding the origin. Such a subset lies on a line of equation a=1, b=1 or a+b=1. Hence one fixed pair in each triple always differs. Select such a pair in every triple, obtaining a bipartite simple graph with e=rN/3 edges and maximum degree r. Its opposite-pair equations leave a free bit per component, counting isolates, so dim F is at most the number c of components.

A nontrivial component of size s and e_s edges has e_s ≤ min(s²/4,rs/2). The function s²/[4(s−1)] increases for s≥2; the function rs/[2(s−1)] decreases. The expressions coincide at s=2r. Consequently

    e_s ≤ r²(s−1)/(2r−1).

Equality forces s=2r and the component to be a complete K(r,r). Summing gives rN/3 ≤ r²(N−c)/(2r−1), hence the result.

When equality is attained, the selected graph consists of N/(3r) copies of K(r,r) and N/3 isolates. In every triple, the third vertex is an isolate: every nonisolated vertex already uses its r incident triples as an endpoint of selected pairs. The flat equals the full solution space of the selected opposite-pair equations, since its dimension equals their common dimension. Conversely, any such pair selection exhibits an attaining flat.

## Exact order spectrum for connected resolvable examples

For a given r≥2 the possible orders at equality are exactly N=3rt, for positive integer t, except for the two pairs (r,t)=(2,1) and (6,1). This is an existence statement for orders, as distinct from recognizing extremality on a supplied instance.

For t≥2 put b modulo t and i,s modulo r, taking the representative 0≤s<r to define δ(s)=floor(2s/r). The vertices are A(b,i), B(b,i), and C(b,i). Matching s consists of the triples

    (A(b,i), B(b,i+s mod r), C(b+δ(s) mod t,i+2s mod r)).

For fixed s, all three index maps are bijections, so every matching covers all vertices. An A,B pair determines s by subtracting second indices. A B,C pair does so as well. For an A,C pair the second indices determine 2s modulo r. Ambiguity can occur only for even r and two candidates separated by r/2. These two candidates have distinct 0/1 shifts, distinguished by the block indices because t≥2. Thus no pair repeats. The A,B graph is complete bipartite in each block. Each C(b,i) attaches to A,B vertices in the b and b−1 blocks since δ attains both 0 and 1. This makes the hypergraph connected. Assign one free bit to all A in each block, its complement to all B in that block and an independent bit to every C. This flat has dimension (r+1)t at N=3rt.

When t=1, equality forces one K(r,r) plus r isolates. Label its two sides A and B. Associate to each pair (A_i,B_j) its hyperedge's third vertex C and its matching number s. The C labels form a Latin square: at any fixed A_i or B_j a repeated C would violate linearity. The s labels form a second Latin square, because each matching is perfect. Orthogonality follows since each C occurs precisely once in a given matching s. Conversely any pair of orthogonal Latin squares gives such a linear hypergraph, with connectivity through the A,B block. Bose, Shrikhande and Parker proved existence of an orthogonal pair at all orders r>6. Orders 3, 4 and 5 admit the usual finite-field construction. Order 2 fails by inspection and order 6 by the classical 36-officers theorem. [Bose–Shrikhande–Parker, Theorem 10](https://doi.org/10.4153/CJM-1960-016-5) · [Stinson, order-six nonexistence](https://doi.org/10.1016/0097-3165(84)90044-X)

The replay validates the numerical component bound, constructs 36 connected examples at many small and composite r (including r=2,6 at t=2), checks the symbolic pair and dimension certificates, and independently verifies the two Latin squares for t=1 examples. The classification of Latin square orders above uses the cited theorems. No priority claim is made.
