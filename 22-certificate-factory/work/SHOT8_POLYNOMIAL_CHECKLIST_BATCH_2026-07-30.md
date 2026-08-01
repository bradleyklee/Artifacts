# Shot 8 report: polynomial checklist batch

## Outcome

All twelve unfinished primary polynomial cases passed. The batch stopped at
the first observable-power case, A120589, because its numerator seed changes
the remainder dimension.

Newly verified:

- A120594, A120595.
- A120597, A120598, A120599.
- A120601, A120602.
- A120603.
- A120604.
- A120605, A120606.
- A120607.

Together with the earlier seven complete cases, analytic coverage is now
19/23.

## Degree and matrix scaling observed

For denominator degree d:

- G is 2d by 2d.
- The seed-1 remainder matrix is (d-1) by d.
- Its rank is d-1 and nullity is one in every completed primary case.
- The recurrence order and polynomial degree are d-1.
- The certificate numerator degrees are d-2 in n and (d-1)^2 in u.

The largest completed case, A120607:

- denominator degree 10;
- G is 20 by 20;
- X is 9 by 10;
- recurrence order 9;
- certificate numerator degrees 8 in n and 81 in u;
- wall time about 81 seconds;
- peak RSS about 177 MiB;
- compressed payload about 136 KiB.

## Checks

Every completed case passed:

- exact G invertibility;
- exact G/U/V split;
- all pole-lowering assertions;
- last-row vanishing for the seed-1 family;
- expected rank and nullity;
- exact nullvector;
- polynomial certificate numerator;
- cleared telescoping identity zero;
- stored-term recurrence residuals zero;
- recurrence-derived ODE series checks.

Payloads were compressed only after all generation assertions passed.

## Active size

The compressed high-degree payloads keep the project below the 10 MiB active
ceiling. Temporary uncompressed run directories were outside the project.

## Blocker: A120589

A120589 has seed `1+u`. After exact lowering, the top remainder row is nonzero.
Thus the relevant remainder dimension is 2, not 1:

- the old normalized attempt used a 1 by 2 matrix;
- the natural corrected attempt uses a 2 by 3 matrix;
- this predicts three shifted columns and recurrence order 2.

The same issue likely makes A120591 use a 3 by 4 matrix and recurrence order 3.

This is not a matrix failure. It is a choice to generalize the algorithm from
the special seed-1 quotient to the full remainder space and discover the
relation length dynamically.

## Pending checklist

- A120589: blocked at dynamic remainder dimension.
- A120591: pending the same generalization.
- A244627 and A244856: pending numerator-aware direct-x reduction.

## Question

Should the observable-power cases use the full remainder space and add shifted
columns until nullity first becomes positive? This gives the smallest relation
found by the reduction, rather than imposing the parent family’s order.

If yes, the next shot will implement exactly that stopping rule, test A120589
and A120591, and then apply the already validated numerator-aware direct-x
route to A244627 and A244856.
