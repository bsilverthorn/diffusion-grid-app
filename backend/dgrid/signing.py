import json
import logging

import itsdangerous

from typing import (
    Optional,
    Union,
)

logger = logging.getLogger(__name__)

class Signer:
    def __init__(self, key: str) -> None:
        self._key = key

    def sign_message(self, **message: Union[str, int, None]) -> str:
        signer = itsdangerous.Signer(self._key)
        message_str = json.dumps(message, sort_keys=True)
        signature = signer.get_signature(message_str).decode("ascii")

        logger.debug("signature for %s is %s", message_str, signature)

        return signature

    def sign_critical_inputs(self, prompt: str, latents: Optional[str]) -> str:
        return self.sign_message(prompt=prompt, latents=latents)