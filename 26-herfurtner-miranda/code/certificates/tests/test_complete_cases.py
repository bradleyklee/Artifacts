from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

CERT_DIR = Path(__file__).resolve().parents[1]
CODE_DIR = CERT_DIR.parent
ROOT = CODE_DIR.parent
sys.path.insert(0, str(CERT_DIR))
sys.path.insert(0, str(CODE_DIR))

import verify_complete_cases as complete
import verify_legacy_cases as old_a
import verify_promoted_cases as old_b
import search_curves as search


class CompleteCaseInterfaceTests(unittest.TestCase):
    def test_manifest_has_one_public_status(self) -> None:
        self.assertEqual(complete.COMPLETE_MODELS, (1, 2, 3, 5, 7, 9))
        self.assertEqual(complete.MANIFEST["status"], "complete")
        self.assertEqual(
            {item["status"] for item in complete.MANIFEST["models"]},
            {"complete"},
        )

    def test_old_commands_use_the_same_exact_engine(self) -> None:
        self.assertIs(old_a.main, complete.main)
        self.assertIs(old_b.main, complete.main)
        self.assertEqual(
            set(old_a.MODEL_SUBSET) | set(old_b.MODEL_SUBSET),
            set(complete.COMPLETE_MODELS),
        )
        self.assertTrue(
            set(old_a.MODEL_SUBSET).isdisjoint(old_b.MODEL_SUBSET)
        )

    def test_catalogue_is_complete_exact_and_80_columns(self) -> None:
        rows = search.load_known_catalog()
        self.assertEqual(len(rows), 11)
        self.assertEqual(
            {
                row["model_number"]
                for row in rows
                if row["status"] == "complete"
            },
            set(complete.COMPLETE_MODELS),
        )
        self.assertTrue(all(row["hamiltonian_terms"] for row in rows))
        text = search.catalogue_text(rows, verbose=True)
        self.assertNotIn("HAMILTONIAN", text.splitlines()[2])
        self.assertIn("\n       2H = ", text)
        self.assertTrue(all(len(line) <= 80 for line in text.splitlines()))

    def test_search_json_lists_all_invariant_models(self) -> None:
        data = json.loads(search.OUTPUT_FILE.read_text())
        rows = data["results_by_kodaira_code"]
        models = [
            model
            for row in rows
            for model in row["models"]
        ]
        self.assertEqual(len(rows), 11)
        self.assertEqual(len(models), 52)
        self.assertEqual(
            sum(model["presentation_count"] for model in models),
            244,
        )
        self.assertTrue(all(model["presentations"] for model in models))
        text = search.search_text(rows)
        self.assertIn("Invariant models (52)", text)
        self.assertTrue(all(len(line) <= 80 for line in text.splitlines()))


if __name__ == "__main__":
    unittest.main()
