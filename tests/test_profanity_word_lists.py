import ast
import importlib
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ALLOW_EXACT_WORDS = {
    "사발",
    "사발면",
    "물사발",
    "밥사발",
    "국사발",
    "대접사발",
    "사발통문",
    "시발점",
    "시발역",
    "시발지",
    "시발차",
    "씨앗",
    "씨알",
    "씨눈",
    "병식",
    "병아리",
    "병어",
    "병풍",
    "병충해",
    "병정",
    "지라",
    "지리",
    "개나리",
    "개념",
    "개구쟁이",
    "개불",
    "개살구",
    "개암",
    "개망초",
    "개복치",
    "개비",
    "만년",
    "닭살",
    "닭장",
    "망태기",
    "멍울",
    "변기",
    "변소",
    "새끼줄",
    "십오",
    "십육",
    "시바견",
    "자지러지다",
    "자지러짐",
    "젖병",
    "젖니",
    "젖먹이",
    "젖산",
    "젓갈",
    "조개",
    "토막",
    "항문",
    "치질",
    "대장항문",
    "생식기",
    "자궁",
    "고환",
    "음부",
    "정액",
}


class ProfanityWordListTest(unittest.TestCase):
    def test_word_lists_are_split_by_normal_and_abnormal_words(self):
        allow_words = importlib.import_module("allow_words")
        block_words = importlib.import_module("block_words")

        self.assertEqual(EXPECTED_ALLOW_EXACT_WORDS, allow_words.ALLOW_EXACT_WORDS)
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
