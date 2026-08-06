from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

CLASSIFICATION_DIR = Path(__file__).resolve().parents[1]
if str(CLASSIFICATION_DIR) not in sys.path:
    sys.path.insert(0, str(CLASSIFICATION_DIR))

import generate_configurations as gc


class ClassificationReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.derived = gc.derive(progress_enabled=False)

    def test_progress_reporting_is_available_and_flushed(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stderr(stream):
            gc.derive(progress_enabled=True, progress_every=100)
        text = stream.getvalue()
        self.assertIn("[classification] analyzed 100 configurations", text)
        self.assertIn("enumeration complete: 379 configurations", text)
        self.assertIn("four-fibre slice complete: 56 nonconstant-J + 3 constant-J", text)

    def test_default_four_fibre_listing_contains_all_59_cases(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            gc.print_selected_set(*self.derived, selection="four")
        text = stream.getvalue()
        numbered_rows = [line for line in text.splitlines() if line[:3].isdigit()]
        self.assertEqual(len(numbered_rows), 59)
        self.assertIn("001. I9 I1 I1 I1", text)
        self.assertIn("056. I3 III III III", text)
        self.assertIn("001. I0* II II II", text)
        self.assertIn("003. III III III III", text)

    def test_all_derived_sets_can_be_printed(self) -> None:
        expected_headers = {
            "targets": "Nonconstant-J four-fibre targets (56)",
            "allowable": "All allowable configurations (279)",
            "audit": "All Euler-sum-12 configurations (379)",
        }
        for selection, header in expected_headers.items():
            with self.subTest(selection=selection):
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    gc.print_selected_set(*self.derived, selection=selection)
                self.assertIn(header, stream.getvalue())


if __name__ == "__main__":
    unittest.main()
