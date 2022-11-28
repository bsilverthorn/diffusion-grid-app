import boto3
import threading

from typing import (
    NewType,
    Optional,
)
from .banana import ModelRunInputs
from .grid_types import GridImageInfo
from .signing import Signer

CacheKey = NewType("CacheKey", str)

class DiffusionCache:
    VERSION = 0
    KEY_SIGNING_KEY = "key-hashing-not-security-relevant"

    class _Local(threading.local):
        # non-lambda servers may be threaded
        def __init__(self):
            self.s3 = boto3.client("s3")

    def __init__(self, bucket: str):
        self._bucket = bucket
        self._local = self._Local()
        self._key_signer = Signer(key=self.KEY_SIGNING_KEY)

    def fetch(self, key: CacheKey) -> Optional[GridImageInfo]:
        try:
            response = self._local.s3.get_object(
                Bucket=self._bucket,
                Key=key,
            )
        except self._local.s3.exceptions.NoSuchKey:
            return None
        else:
            return GridImageInfo.parse_raw(response["Body"].read())

    def store(self, key: CacheKey, grid_image: GridImageInfo) -> None:
        self._local.s3.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=grid_image.json(),
        )

    def key(self, run_inputs: ModelRunInputs) -> CacheKey:
        inputs_hash = self._key_signer.sign_message(**run_inputs.dict())

        return CacheKey(f"cache_v{self.VERSION}/inputs={inputs_hash}.json")