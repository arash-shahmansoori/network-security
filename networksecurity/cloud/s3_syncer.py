import os
import subprocess

from networksecurity.logging.logger import logging


class S3Sync:
    def _has_aws_credentials(self) -> bool:
        return bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))

    def _run_sync(self, args: list[str]) -> None:
        try:
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode != 0:
                msg = (
                    f"AWS sync failed (exit {result.returncode}). Suppressing error. Details: "
                    f"{result.stderr.strip()}"
                )
                logging.warning(msg)
        except Exception as e:
            logging.warning(f"AWS sync execution error: {e}")

    def sync_folder_to_s3(self, folder, aws_bucket_url):
        if not self._has_aws_credentials():
            logging.warning("AWS credentials not found. Skipping upload sync.")
            return
        self._run_sync(["aws", "s3", "sync", folder, aws_bucket_url, "--only-show-errors"])

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        if not self._has_aws_credentials():
            logging.warning("AWS credentials not found. Skipping download sync.")
            return
        self._run_sync(["aws", "s3", "sync", aws_bucket_url, folder, "--only-show-errors"])
