import logging

from typing import (
    Optional,
    Type,
    TypeVar,
)
from urllib.parse import urljoin

import pydantic
import requests

from pydantic import Field
from pydantic.utils import to_lower_camel

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

class BananaRequest(pydantic.BaseModel):
    api_key: str

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_lower_camel

class BananaStartRequest(BananaRequest):
    model_key: str
    start_only: bool = True
    model_inputs: ModelInputs

class BananaCheckRequest(BananaRequest):
    call_id: str
    long_poll: bool = False

class BananaResponse(pydantic.BaseModel):
    message: str

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_lower_camel

class BananaStartResponse(BananaResponse):
    call_id: str = Field(alias="callID", min_length=1)

class BananaCheckResponse(BananaResponse):
    message: str
    model_outputs: Optional[list[ModelOutputs]] = Field(min_items=1, max_items=1)

BR = TypeVar("BR", bound=BananaResponse)

class BananaAPI:
    def __init__(self, api_url: str, api_key: str, model_key: str, timeout: float):
        self._api_url = api_url
        self._api_key = api_key
        self._model_key = model_key
        self._timeout = timeout

    def request(self, request: BananaRequest, path: str, response_cls: Type[BR]) -> BR:
        logger.debug("making request to %r; request: %r", path, request)

        endpoint = urljoin(self._api_url, path)

        try:
            response = requests.post(
                endpoint,
                json=request.dict(by_alias=True),
                timeout=self._timeout,
            )

            logger.debug(
                "response %s from banana; %s",
                response.status_code,
                response.content,
            )

            response.raise_for_status()
        except requests.Timeout as error:
            logger.error("request timeout error: %s", error)

            raise TimeoutError("banana request timed out") from error
        else:
            parsed = response_cls.parse_obj(response.json())

            # sometimes banana will stuff an error into the response
            # message despite a 200 status; check for that, hackishly
            if "error" in parsed.message:
                raise RuntimeError("banana response looks like an error", parsed)

            return parsed

    def request_start(self, model_inputs: ModelInputs) -> tuple[str, str]:
        request = BananaStartRequest(
            api_key=self._api_key,
            model_key=self._model_key,
            model_inputs=model_inputs,
        )
        response = self.request(request, "/start/v4", BananaStartResponse)

        return (response.message, response.call_id)

    def request_check(self, call_id: str) -> tuple[str, Optional[ModelOutputs]]:
        request = BananaCheckRequest(
            api_key=self._api_key,
            call_id=call_id,
        )
        response = self.request(request, "/check/v4", BananaCheckResponse)

        if response.model_outputs is None:
            model_outputs = None
        else:
            (model_outputs,) = response.model_outputs

        return (response.message, model_outputs)