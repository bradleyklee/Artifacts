# ALG-016 — Perturb and record

```text
choose one solved Hamiltonian H
choose one small added polynomial V
set H_test = H + V

write model, V, coordinates and eliminated polynomial to JSON immediately

if the eliminated polynomial uses only even powers of lambda:
    set u=lambda^2 and Q(u)=u*P(sqrt(u))
    reduce using Q, and record this substitution in JSON

for order_cap in 2,4,6,...:
    differentiate the period integrand through order_cap
    reduce every numerator by polynomial division and exact derivatives
    time and save each completed derivative column separately
    form one coefficient column per derivative
    find null relations among the columns
    append matrix size, time, status and order_cap to JSON

    if a relation is found:
        remove trailing zero coefficients
        rebuild the exact derivative Xi
        verify residual = 0
        append operator, Xi, true order and residual to JSON
        stop

if a time or order cap stops the run:
    mark the JSON record blocked and retain every completed test
```

Use plain descriptions in reports: differentiate, reduce polynomials, find a null relation, rebuild the exact derivative. Specialist vocabulary is unnecessary for operating the algorithm.
