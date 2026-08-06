import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "examples" / "public" / "A303790"

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
    data = json.loads((PUBLIC / "certificates" / "laurent_certificate.json").read_text())
    assert data["certificate_residual"] == "0"
    assert data["first_coefficients"][:5] == [
        "1", "60", "7380", "1090320", "176978340"
    ]

def test_scalar_certificate():
    data = json.loads(
        (PUBLIC / "certificates" / "period_certificate.json").read_text()
    )
    assert data["verification"]["status"] == "exact residual zero"
