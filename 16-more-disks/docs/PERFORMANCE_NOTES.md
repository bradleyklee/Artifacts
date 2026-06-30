# Performance notes

Go is the canonical physics path. It represents every scalar in the fixed
basis `1, sqrt(2), sqrt(3), sqrt(6)` using `math/big.Rat`, with an exact
algebraic sign test rather than numerical approximation. The common-basis
representation makes all four shapes share one engine and one certificate
contract.

Observed single-run low-atlas timings on the assembly host:

```text
square L=2,N=4 (256 starts):       about 1.0 s
ordinary dodecagon L=3,N=2 (576):  about 2.1 s
24-gon L=2,N=2 (96; cap 100):      about 3.8 s
octagon L=2,N=3 (256; cap 256):    about 7.0 s
centered dodecagon all faces cap500: about 9.2 s
```

The exact common-field engine reaches a checked 7,500-event centered-dodecagon
checkpoint. Beyond that, coefficient growth makes generic exact arithmetic
substantially more expensive. A next optimization is a model-specialized
`Q(sqrt(3))` fast path that must first pass the generic-engine and Python
replay parity suite.
