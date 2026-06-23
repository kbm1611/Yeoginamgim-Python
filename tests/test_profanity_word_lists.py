import ast
import importlib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProfanityWordListTest(unittest.TestCase):
    def test_word_lists_are_split_by_normal_and_abnormal_words(self):
        allow_words = importlib.import_module("allow_words")
        block_words = importlib.import_module("block_words")

        self.assertIn("시발점", allow_words.ALLOW_EXACT_WORDS)
        self.assertIn("병아리", allow_words.ALLOW_EXACT_WORDS)
        self.assertEqual({"보지", "섹스"}, block_words.BLOCK_EXACT_WORDS)
        self.assertTrue(allow_words.ALLOW_EXACT_WORDS.isdisjoint(block_words.BLOCK_EXACT_WORDS))

    def test_service_imports_split_word_lists(self):
        service_tree = ast.parse((PROJECT_ROOT / "service.py").read_text(encoding="utf-8"))
        imports = {
            (node.module, alias.name)
            for node in service_tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        self.assertIn(("allow_words", "ALLOW_EXACT_WORDS"), imports)
        self.assertIn(("block_words", "BLOCK_EXACT_WORDS"), imports)


if __name__ == "__main__":
    unittest.main()
