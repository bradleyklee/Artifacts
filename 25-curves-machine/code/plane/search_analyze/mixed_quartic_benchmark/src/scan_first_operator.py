from __future__ import annotations
import json
import pathlib
import sys

Q2 = pathlib.Path(__file__).resolve().parents[2] / 'q2_order6_engine' / 'src'
sys.path.insert(0, str(Q2))
from scan_cases import scan as scan_by_order

def scan(path, nterms, max_order, degree_cap):
    data = json.loads(pathlib.Path(path).read_text())
    prime = int(data['prime'])
    mins, hits = scan_by_order(path, prime, nterms, max_order, degree_cap)
    first = None
    for order, degree, nullity in hits:
        first = {'order': order, 'degree': degree, 'nullity': nullity}
        break
    return {'first_hit': first, 'first_by_order': mins, 'hits': hits}
