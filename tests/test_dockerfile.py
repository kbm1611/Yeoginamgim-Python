import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DockerfileTest(unittest.TestCase):
    def test_dockerfile_copies_imported_python_modules(self):
        dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
        copied_files = set(re.findall(r"\b([a-zA-Z_][\w]*\.py)\b", dockerfile))

        self.assertIn("allow_words.py", copied_files)
        self.assertIn("block_words.py", copied_files)


if __name__ == "__main__":
    unittest.main()
