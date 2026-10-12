import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import flashcards


class FlashcardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "deck.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_add_and_progress_persist(self):
        flashcards.add_card(self.path, "  Question? ", " Answer. ")
        self.assertEqual(flashcards.progress(self.path), (0, 1))
        flashcards.mark_known(self.path, 1)
        self.assertEqual(flashcards.progress(self.path), (1, 1))
        self.assertTrue(json.loads(self.path.read_text(encoding="utf-8"))[0]["known"])

    def test_invalid_input_and_index(self):
        with self.assertRaises(ValueError):
            flashcards.add_card(self.path, " ", "answer")
        with self.assertRaises(ValueError):
            flashcards.mark_known(self.path, 1)

    def test_cli_add_and_progress(self):
        script = Path(__file__).resolve().parents[1] / "flashcards.py"
        result = subprocess.run([sys.executable, str(script), "--data", str(self.path), "add", "Capital?", "Paris"], capture_output=True, text=True, check=True)
        self.assertIn("Added card", result.stdout)
        result = subprocess.run([sys.executable, str(script), "--data", str(self.path), "progress"], capture_output=True, text=True, check=True)
        self.assertIn("0/1 known", result.stdout)


if __name__ == "__main__":
    unittest.main()
