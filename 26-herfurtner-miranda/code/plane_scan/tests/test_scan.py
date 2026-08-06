from __future__ import annotations

import unittest

from plane_scan.classify import canonical_fibers
from plane_scan import cubic, quartic


class PlaneScanRegressionTests(unittest.TestCase):
    def test_all_cubic_witnesses(self) -> None:
        self.assertEqual(len(cubic.WITNESSES), 3)
        for target, parameters in cubic.WITNESSES.items():
            result = cubic.verify(parameters)
            self.assertEqual(canonical_fibers(result["fibers"]), target)
            self.assertEqual(result["euler_total"], 12)

    def test_all_quartic_witnesses(self) -> None:
        self.assertEqual(len(quartic.WITNESSES), 8)
        for target, parameters in quartic.WITNESSES.items():
            result = quartic.verify(parameters)
            self.assertEqual(canonical_fibers(result["fibers"]), target)
            self.assertEqual(result["euler_total"], 12)

    def test_classes_are_disjoint_on_the_56_slice(self) -> None:
        self.assertTrue(set(cubic.WITNESSES).isdisjoint(quartic.WITNESSES))


if __name__ == "__main__":
    unittest.main()
