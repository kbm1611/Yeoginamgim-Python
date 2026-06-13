import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from model_storage import ensure_model_available


TEST_TEMP_ROOT = Path(__file__).parent / "test-workspace"


class EnsureModelAvailableTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TEST_TEMP_ROOT / self._testMethodName
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        self.temp_dir.mkdir(parents=True)

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_returns_existing_model_without_s3(self):
        model_dir = self.temp_dir
        for file_name in ("config.json", "tokenizer.json", "model.safetensors"):
            (model_dir / file_name).write_text("ok", encoding="utf-8")

        downloaded = ensure_model_available(model_dir)

        self.assertFalse(downloaded)

    def test_downloads_model_files_from_s3_when_model_is_missing(self):
        model_dir = self.temp_dir / "model"
        s3 = MagicMock()
        s3.download_file.side_effect = self.write_downloaded_file
        s3.get_paginator.return_value.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "models/config.json"},
                    {"Key": "models/tokenizer.json"},
                    {"Key": "models/model.safetensors"},
                    {"Key": "models/nested/extra.json"},
                ]
            }
        ]

        downloaded = ensure_model_available(
            model_dir,
            bucket="bucket",
            prefix="models",
            s3_client=s3,
        )

        self.assertTrue(downloaded)
        s3.download_file.assert_any_call(
            "bucket",
            "models/config.json",
            os.fspath(model_dir / "config.json"),
        )
        s3.download_file.assert_any_call(
            "bucket",
            "models/nested/extra.json",
            os.fspath(model_dir / "nested" / "extra.json"),
        )

    def test_requires_s3_settings_when_model_is_missing(self):
        with self.assertRaisesRegex(RuntimeError, "PROFANITY_MODEL_S3_BUCKET"):
            ensure_model_available(self.temp_dir / "missing-model")

    @patch.dict(
        os.environ,
        {
            "PROFANITY_MODEL_S3_BUCKET": "bucket",
            "PROFANITY_MODEL_S3_PREFIX": "models",
            "AWS_DEFAULT_REGION": "ap-northeast-2",
        },
        clear=True,
    )
    @patch("model_storage._create_s3_client")
    def test_reads_s3_settings_from_environment(self, client_factory):
        s3 = MagicMock()
        client_factory.return_value = s3
        s3.download_file.side_effect = self.write_downloaded_file
        s3.get_paginator.return_value.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "models/config.json"},
                    {"Key": "models/tokenizer.json"},
                    {"Key": "models/model.safetensors"},
                ]
            }
        ]

        ensure_model_available(self.temp_dir / "model")

        client_factory.assert_called_once_with("ap-northeast-2")
        self.assertEqual(s3.download_file.call_count, 3)

    def write_downloaded_file(self, bucket, key, target):
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        Path(target).write_text(f"{bucket}:{key}", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
