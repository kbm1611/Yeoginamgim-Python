import os
from pathlib import Path


REQUIRED_MODEL_FILES = ("config.json", "tokenizer.json", "model.safetensors")


def ensure_model_available(
    model_dir,
    bucket=None,
    prefix=None,
    region=None,
    s3_client=None,
):
    model_path = Path(model_dir).expanduser()
    if _has_required_model_files(model_path):
        return False

    bucket = bucket or os.getenv("PROFANITY_MODEL_S3_BUCKET")
    prefix = _normalize_prefix(prefix or os.getenv("PROFANITY_MODEL_S3_PREFIX"))
    region = region or os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")

    if not bucket or not prefix:
        raise RuntimeError(
            "Profanity model files are missing. Set PROFANITY_MODEL_S3_BUCKET "
            "and PROFANITY_MODEL_S3_PREFIX to download them from S3."
        )

    model_path.mkdir(parents=True, exist_ok=True)
    s3_client = s3_client or _create_s3_client(region)
    downloaded = _download_prefix(s3_client, bucket, prefix, model_path)

    if downloaded == 0:
        raise RuntimeError(f"No model files found at s3://{bucket}/{prefix}/")
    if not _has_required_model_files(model_path):
        missing = ", ".join(_missing_required_files(model_path))
        raise RuntimeError(f"Downloaded model is incomplete. Missing: {missing}")

    return True


def _create_s3_client(region):
    import boto3

    kwargs = {}
    if region:
        kwargs["region_name"] = region
    return boto3.client("s3", **kwargs)


def _download_prefix(s3_client, bucket, prefix, destination):
    paginator = s3_client.get_paginator("list_objects_v2")
    downloaded = 0

    for page in paginator.paginate(Bucket=bucket, Prefix=f"{prefix}/"):
        for item in page.get("Contents", []):
            key = item["Key"]
            if key.endswith("/"):
                continue

            relative_key = key[len(prefix) :].lstrip("/")
            if not relative_key:
                continue

            target = destination / relative_key
            target.parent.mkdir(parents=True, exist_ok=True)
            s3_client.download_file(bucket, key, os.fspath(target))
            downloaded += 1

    return downloaded


def _has_required_model_files(model_path):
    return not _missing_required_files(model_path)


def _missing_required_files(model_path):
    return [
        file_name
        for file_name in REQUIRED_MODEL_FILES
        if not (model_path / file_name).is_file()
    ]


def _normalize_prefix(prefix):
    if not prefix:
        return None
    return prefix.strip("/")
