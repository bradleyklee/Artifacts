from __future__ import annotations
import unittest
from lattice_collision.core import (Body, cardinal_velocities, centered_pair_start, enumerate_lattice_starts,
                                    make_container, model_for, run)

class UnifiedRegression(unittest.TestCase):
    def atlas_counts(self, shape: str, L: int, N: int, cap: int):
        model = model_for(shape); box = make_container(model, L); counts = {}
        for _, _, start in enumerate_lattice_starts(model, L, N):
            status = run(model, box, start, cap)["status"]
            counts[status] = counts.get(status, 0) + 1
        return counts

    def test_square_2x2_raw(self):
        # Unreduced raw counterpart of the D4 legacy square control.
        self.assertEqual(self.atlas_counts("square", 2, 2, 100), {"RETURN": 48, "PAIR_CORNER": 40, "WALL_CORNER": 8})

    def test_dodecagon_2x2_transfer(self):
        self.assertEqual(self.atlas_counts("dodecagon", 2, 2, 100), {"RETURN": 64, "PAIR_CORNER": 24, "WALL_CORNER": 8})

    def test_dodecagon_3x3_transfer(self):
        self.assertEqual(self.atlas_counts("dodecagon", 3, 2, 100), {"RETURN": 424, "PAIR_CORNER": 136, "WALL_CORNER": 16})

    def test_24gon_2x2_transfer(self):
        self.assertEqual(self.atlas_counts("24gon", 2, 2, 100), {"RETURN": 72, "CAP": 16, "WALL_CORNER": 8})

    def test_centered_dodecagon_EN_starts_regularly(self):
        model = model_for("dodecagon")
        start, record = centered_pair_start(model, 2, 1, "E", "N")
        out = run(model, make_container(model, 2), start, 100, [record])
        self.assertEqual(out["status"], "CAP")
        self.assertEqual(out["pair_face_word"][:1], [1])

if __name__ == "__main__":
    unittest.main()
