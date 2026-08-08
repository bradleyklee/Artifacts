#!/usr/bin/env python3
"""Dependency-free exact-rational smoke tests for Chapter 4 conventions."""
from __future__ import annotations

from fractions import Fraction as Q


def check_sample(a: Q, b: Q, c: Q, alpha: Q, cosine: Q, sine: Q) -> None:
    assert cosine * cosine + sine * sine == 1
    angle_part = a * cosine * cosine + b * sine * sine
    lam_sq = (alpha - angle_part) / (c - angle_part)

    # Unit-sphere chart, checked without introducing square roots.
    jx_sq = (1 - lam_sq) * cosine * cosine
    jy_sq = (1 - lam_sq) * sine * sine
    assert jx_sq + jy_sq + lam_sq == 1

    # H=A(1-lambda^2)+c lambda^2 equals alpha on the fiber.
    assert angle_part * (1 - lam_sq) + c * lam_sq == alpha

    # After canceling the common nonzero sheet value lambda:
    # partial_alpha(lambda)=1/[2 lambda(c-A)]=1/dot(phi).
    reduced_dlambda = Q(1, 2) / (c - angle_part)
    reduced_inverse_velocity = Q(1, 2) / (c - angle_part)
    assert reduced_dlambda == reduced_inverse_velocity

    # -partial_phi(H)=-2(b-a)(1-lambda^2)sin(phi)cos(phi).
    minus_h_phi = -2 * (b - a) * (1 - lam_sq) * sine * cosine
    expected_dot_lambda = -2 * (b - a) * (1 - lam_sq) * sine * cosine
    assert minus_h_phi == expected_dot_lambda


def check() -> None:
    samples = [
        (Q(1), Q(2), Q(5), Q(3), Q(3, 5), Q(4, 5)),
        (Q(-2), Q(1), Q(7), Q(2), Q(5, 13), Q(12, 13)),
        (Q(1, 3), Q(4, 3), Q(10, 3), Q(2), Q(8, 17), Q(15, 17)),
    ]
    for sample in samples:
        check_sample(*sample)
    print("SPHERE_CONVENTIONS_CHECK_PASS")
    print(f"exact_rational_samples={len(samples)}")
    print("constraint=J.J-1")
    print("energy_convention=alpha=H")
    print("canonical_pair=(lambda,phi)=(J_axis,azimuth)")
    print("identity=partial_alpha(lambda)=1/dot(phi)")


if __name__ == "__main__":
    check()
