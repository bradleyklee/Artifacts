================================================================================
FromKimi — OEIS Submission Package for A120590 (Ternatree Sequence)
================================================================================

Generated: 2026-07-25
Source:    Literal implementation of Harm.On.ica S-O-L's matrix-reduction
           pseudocode for ternary-tree enumeration.

CONTENTS
--------
  q3_algorithm.py   Complete Python/SymPy script implementing every function
                      in the pseudocode: Lower, Normalize3, Cancel3, Apply2,
                      MakeODE, and Q3.  Run with "python3 q3_algorithm.py".

  %I.txt through %A.txt
                      Individual OEIS field files ready for copy-paste into
                      the OEIS internal format.  Each filename corresponds to
                      the standard OEIS tag (%S, %N, %C, %F, %e, %o, %Y, %K, %A).

  KANSHI.txt          A bilingual Chinese-English response poem to the
                      original "Ternatree counting" verses.

ALGORITHM SUMMARY
-----------------
1.  Build 3x3 reduction matrices U and V from the plum-root data.
2.  Apply the backward quotient rule (Lower) to generate column vectors c0, c1, c2.
3.  Take the 2x3 matrix X = [c0 | c1 | c2] and cancel pairs of columns via
    2x2 minors (cross-products) to obtain P0, P1, P2.
4.  Normalize by clearing denominators, taking polynomial GCD, and forcing
    the leading coefficient of P2 positive.
5.  Iterate the recurrence a[k+2] = (-P0(k)*a[k] - P1(k)*a[k+1]) / P2(k)
    starting from a[0]=1, a[1]=1, a[2]=3.
6.  Verify that the truncated series S satisfies both:
       S^3 = 4S - 3 - x          (algebraic)
       (27x^2+162x-13)S'' + (27x+81)S' - 3S = 0   (differential)

VERIFIED TERMS (first 30)
-------------------------
  a[0] = 1
  a[1] = 1
  a[2] = 3
  a[3] = 19
  a[4] = 150
  a[5] = 1326
  a[6] = 12558
  a[7] = 124590
  a[8] = 1278189
  a[9] = 13449205
  a[10] = 144342627
  a[11] = 1573990275
  a[12] = 17389407984
  a[13] = 194228357568
  a[14] = 2189610888840
  a[15] = 24881753664840
  a[16] = 284708154606318
  a[17] = 3277578288381318
  a[18] = 37934510719585350
  a[19] = 441152315040444150
  a[20] = 5152282099512304680
  a[21] = 60406551502736538000
  a[22] = 710696386643487054660
  a[23] = 8388096824571665369220
  a[24] = 99289485169936277117850
  a[25] = 1178418423546361685791818
  a[26] = 14020404767017168928473206
  a[27] = 167188019948314733760056182
  a[28] = 1997841773180952932502806232
  a[29] = 23920144279952150697309393240

CROSS-REFERENCE
---------------
This sequence is OEIS A120590.  It counts rooted planar trees where each
internal node has out-degree 2 (in 3 colors) or out-degree 3.

================================================================================
