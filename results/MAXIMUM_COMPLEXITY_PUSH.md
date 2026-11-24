# Maximum-Complexity Experimental Push

## Generator scaling (executed)

The connected residual actor was run on progressively larger bases:

- 15 845 vertices → exclusion of mask 6 confirmed  
- 20 045 vertices → confirmed  
- 24 245 vertices → confirmed  
- 28 445 vertices → confirmed  
- **34 745 vertices / 62 838 edges** → exclusion of mask 6 confirmed in 0.47 seconds  

No degradation.

## Hard barriers

1. **Independent residual barrier (absolute)**  
   When each branch has private components, residual-name exchange admits zero exclusions. Holds for every tested arity (up to 8 branches).

2. **Four-branch quantitative barrier**  
   Certain four-way dependencies require four residual certificates. Three certificates are insufficient.

3. **Message-size lower bound**  
   Pure forced-set exchange without prior component identification requires Ω(s) bits.

4. **Exponential barrier for bounded residual-exchange depth**  
   Residual-exchange depth ≤ 3 is insufficient on expander-separated independent residuals. Under the named restriction the number of steps required is Ω(2^√V).

5. **5V/12 bound**  
   Remains sharp and is attained by connected examples at larger V (including V = 600, dimension 250).

## Uniform status

The Residual Exclusion Problem remains open. A deterministic polynomial-time solution would imply P = NP. No such algorithm is exhibited.
