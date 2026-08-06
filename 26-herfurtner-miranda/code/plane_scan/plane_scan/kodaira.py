from __future__ import annotations


def fiber_from_valuations(v_c4: int, v_c6: int, v_delta: int) -> str:
    """Classify a minimal characteristic-zero Weierstrass fiber by valuations."""
    if v_c4 == 0 and v_c6 == 0 and v_delta >= 1:
        return f"I{v_delta}"
    if v_c4 >= 1 and v_c6 == 1 and v_delta == 2:
        return "II"
    if v_c4 == 1 and v_c6 >= 2 and v_delta == 3:
        return "III"
    if v_c4 >= 2 and v_c6 == 2 and v_delta == 4:
        return "IV"
    if v_c4 >= 2 and v_c6 >= 3 and v_delta == 6:
        return "I0*"
    if v_c4 == 2 and v_c6 == 3 and v_delta >= 7:
        return f"I{v_delta - 6}*"
    if v_c4 >= 3 and v_c6 == 4 and v_delta == 8:
        return "IV*"
    if v_c4 == 3 and v_c6 >= 5 and v_delta == 9:
        return "III*"
    if v_c4 >= 4 and v_c6 == 5 and v_delta == 10:
        return "II*"
    raise ValueError(
        f"unclassified minimal valuation triple {(v_c4, v_c6, v_delta)}"
    )
