import logging

from typing import Optional
from urllib.parse import urljoin

import pydantic
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class ModelRunInputs(pydantic.BaseModel):
    prompt: str
    seed: int
    latents: Optional[str]
    timestep: Optional[int]
    trajectory_at: list[int]

class ModelInputs(pydantic.BaseModel):
    cache_key: str
    run_inputs: ModelRunInputs

class ModelLatentsInfo(pydantic.BaseModel):
    tensor: str
    image: str
    timestep: int

class ModelRunOutputs(pydantic.BaseModel):
    image: str
    trajectory: list[ModelLatentsInfo]

class ModelOutputs(pydantic.BaseModel):
    prompt: str
    cache_key: str
    run_outputs: ModelRunOutputs

class BananaAPI:
    def __init__(self, api_url: str, api_key: str, model_key: str, timeout: float):
        self._api_url = api_url
        self._api_key = api_key
        self._model_key = model_key
        self._timeout = timeout

        # prep requests session with retries
        self._session = requests.Session()

        retries = Retry(
            # hackishly high number of retries because banana doesn't queue
            total=8,
            backoff_factor=2.0,
            # banana uses an assortment of codes to mean "no replicas available"
            status_forcelist=[400, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)

        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

    def request(self, request: dict, path: str) -> dict:
        logger.debug("making request to %r; request: %r", path, request)

        endpoint = urljoin(self._api_url, path)

        try:
            response = self._session.post(
                endpoint,
                json=request,
                timeout=self._timeout,
                headers={
                    "X-Banana-API-Key": self._api_key,
                    "X-Banana-Model-Key": self._model_key,
                },
            )

            logger.debug(
                "response %s from banana; %s",
                response.status_code,
                response.content,
            )

            response.raise_for_status()
        except requests.HTTPError as error:
            logger.error("HTTP error: %s (%s)", error, error.response.content)

            raise
        except requests.Timeout as error:
            logger.error("request timeout error: %s", error)

            raise TimeoutError("banana request timed out") from error
        else:
            return response.json()

    def infer(self, model_inputs: ModelInputs) -> ModelOutputs:
        response = self.request(model_inputs.dict(), "/")

        return ModelOutputs(**response)
