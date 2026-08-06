import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]

def test_model_involution():
    p, q = sp.symbols("p q")
    K = p**2 + q**2 + p**3 + q**3
    transformed = sp.expand(
        K.subs({
            p: -p-sp.Rational(2,3),
            q: -q-sp.Rational(2,3),
        })
    )
    assert sp.expand(K+transformed-sp.Rational(8,27)) == 0

def test_laurent_integral():
    data = json.loads((ROOT / "laurent" / "laurent_data.json").read_text())
    assert data["certificate_residual"] == "0"
    assert data["first_coefficients"][:5] == [
        "1", "60", "7380", "1090320", "176978340"
    ]

def test_scalar_certificate():
    data = json.loads(
        (ROOT / "period_certificate" / "certificate_data.json").read_text()
    )
    assert data["verification"]["status"] == "exact residual zero"
