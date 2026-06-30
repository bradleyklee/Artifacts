"""Small exact real fields used by the lattice collision models.

The fields are Q, Q(sqrt(2)), Q(sqrt(3)), and Q(sqrt(2), sqrt(3)).
No float is used in event selection or collision classification.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Iterable

F = Fraction


@dataclass(frozen=True)
class Field:
    name: str
    generators: tuple[int, ...]

    @property
    def basis_masks(self) -> tuple[int, ...]:
        if self.generators == ():
            return (0,)
        if self.generators == (2,):
            return (0, 1)
        if self.generators == (3,):
            return (0, 2)
        if self.generators == (2, 3):
            return (0, 1, 2, 3)
        raise ValueError(f"unsupported field {self.generators}")

    @property
    def dimension(self) -> int:
        return len(self.basis_masks)

    def zero(self) -> "E":
        return E(self, (F(0),) * self.dimension)

    def one(self) -> "E":
        return E(self, (F(1),) + (F(0),) * (self.dimension - 1))

    def q(self, n: int | Fraction = 0, d: int = 1) -> "E":
        return E(self, (F(n, d),) + (F(0),) * (self.dimension - 1))

    def sqrt(self, radicand: int) -> "E":
        target = 1 if radicand == 2 else 2 if radicand == 3 else None
        if target is None or target not in self.basis_masks:
            raise ValueError(f"sqrt({radicand}) is not in {self.name}")
        c = [F(0)] * self.dimension
        c[self.basis_masks.index(target)] = F(1)
        return E(self, tuple(c))


Q = Field("Q", ())
Q2 = Field("Q(sqrt(2))", (2,))
Q3 = Field("Q(sqrt(3))", (3,))
Q23 = Field("Q(sqrt(2),sqrt(3))", (2, 3))


@dataclass(frozen=True)
class E:
    field: Field
    c: tuple[F, ...]

    def __post_init__(self) -> None:
        if len(self.c) != self.field.dimension:
            raise ValueError("wrong coefficient count")

    def _coerce(self, other: object) -> "E":
        if isinstance(other, E):
            if other.field != self.field:
                raise TypeError(f"field mismatch: {self.field.name} vs {other.field.name}")
            return other
        if isinstance(other, (int, Fraction)):
            return self.field.q(other)
        return NotImplemented  # type: ignore[return-value]

    def __add__(self, other: object) -> "E":
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented  # type: ignore[return-value]
        return E(self.field, tuple(a + b for a, b in zip(self.c, o.c)))

    __radd__ = __add__

    def __neg__(self) -> "E":
        return E(self.field, tuple(-a for a in self.c))

    def __sub__(self, other: object) -> "E":
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "E":
        return self._coerce(other) - self

    def __mul__(self, other: object) -> "E":
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented  # type: ignore[return-value]
        masks = self.field.basis_masks
        out = [F(0)] * len(masks)
        index = {m: k for k, m in enumerate(masks)}
        for i, a in enumerate(self.c):
            if not a:
                continue
            mi = masks[i]
            for j, b in enumerate(o.c):
                if not b:
                    continue
                mj = masks[j]
                shared = mi & mj
                factor = 1
                if shared & 1:
                    factor *= 2
                if shared & 2:
                    factor *= 3
                out[index[mi ^ mj]] += a * b * factor
        return E(self.field, tuple(out))

    __rmul__ = __mul__

    def inv(self) -> "E":
        if self.is_zero():
            raise ZeroDivisionError("exact scalar inverse of zero")
        # Solve x*y=1 in the field basis by rational Gaussian elimination.
        n = self.field.dimension
        basis = []
        masks = self.field.basis_masks
        for mask in masks:
            c = [F(0)] * n
            c[masks.index(mask)] = F(1)
            basis.append(E(self.field, tuple(c)))
        cols = [(self * b).c for b in basis]
        mat = [[cols[col][row] for col in range(n)] + [F(1) if row == 0 else F(0)]
               for row in range(n)]
        for col in range(n):
            pivot = next((r for r in range(col, n) if mat[r][col] != 0), None)
            if pivot is None:
                raise ZeroDivisionError("singular multiplication matrix")
            mat[col], mat[pivot] = mat[pivot], mat[col]
            scale = mat[col][col]
            mat[col] = [x / scale for x in mat[col]]
            for row in range(n):
                if row == col:
                    continue
                factor = mat[row][col]
                if factor:
                    mat[row] = [a - factor * b for a, b in zip(mat[row], mat[col])]
        return E(self.field, tuple(mat[r][-1] for r in range(n)))

    def __truediv__(self, other: object) -> "E":
        o = self._coerce(other)
        if o is NotImplemented:
            return NotImplemented  # type: ignore[return-value]
        return self * o.inv()

    def __rtruediv__(self, other: object) -> "E":
        return self._coerce(other) / self

    def is_zero(self) -> bool:
        return all(x == 0 for x in self.c)

    def sign(self) -> int:
        """Certified sign for every supported exact field element."""
        if self.is_zero():
            return 0
        masks = self.field.basis_masks
        if len(masks) == 1:
            return (self.c[0] > 0) - (self.c[0] < 0)
        if len(masks) == 2:
            a, b = self.c
            rad = 2 if masks[1] == 1 else 3
            if b == 0:
                return (a > 0) - (a < 0)
            if a == 0:
                return (b > 0) - (b < 0)
            if (a > 0) == (b > 0):
                return 1 if a > 0 else -1
            cmp = (a * a > rad * b * b) - (a * a < rad * b * b)
            return cmp if a > 0 else -cmp
        return _sign_q23(self.c)

    def __lt__(self, other: object) -> bool:
        return (self - self._coerce(other)).sign() < 0

    def __le__(self, other: object) -> bool:
        return (self - self._coerce(other)).sign() <= 0

    def __gt__(self, other: object) -> bool:
        return (self - self._coerce(other)).sign() > 0

    def __ge__(self, other: object) -> bool:
        return (self - self._coerce(other)).sign() >= 0

    def wire(self) -> dict[str, str]:
        names = {1: ("a",), 2: ("a", "b"), 4: ("a", "b", "c", "d")}[len(self.c)]
        return {k: str(v) for k, v in zip(names, self.c)}

    def key(self) -> str:
        return ";".join(f"{x.numerator}/{x.denominator}" for x in self.c)

    def denominator_max(self) -> int:
        return max(x.denominator for x in self.c)

    def numerator_abs_max(self) -> int:
        return max(abs(x.numerator) for x in self.c)

    def approx(self) -> float:
        vals = {0: 1.0, 1: 2.0 ** 0.5, 2: 3.0 ** 0.5, 3: 6.0 ** 0.5}
        return sum(float(a) * vals[m] for a, m in zip(self.c, self.field.basis_masks))


def _sqrt_bounds(n: int, bits: int) -> tuple[F, F]:
    den = 1 << bits
    lo = F(isqrt(n * den * den), den)
    return lo, lo + F(1, den)


def _sign_q23(c: tuple[F, ...]) -> int:
    # Rational interval refinement.  It terminates for nonzero Q(sqrt2,sqrt3)
    # elements because this field is embedded in R and the bounds converge.
    a, b, cc, d = c
    for bits in range(12, 4097, 4):
        lo2, hi2 = _sqrt_bounds(2, bits)
        lo3, hi3 = _sqrt_bounds(3, bits)
        lo6, hi6 = lo2 * lo3, hi2 * hi3
        lo = hi = a
        for coeff, l, h in ((b, lo2, hi2), (cc, lo3, hi3), (d, lo6, hi6)):
            if coeff >= 0:
                lo += coeff * l
                hi += coeff * h
            else:
                lo += coeff * h
                hi += coeff * l
        if lo > 0:
            return 1
        if hi < 0:
            return -1
    raise ArithmeticError("Q(sqrt2,sqrt3) sign interval did not separate")


def exact_max(values: Iterable[E]) -> tuple[int, int]:
    vals = list(values)
    return (
        max(v.numerator_abs_max() for v in vals),
        max(v.denominator_max() for v in vals),
    )
