"""
Design goals:

- Cache results.
- Prevent the internet from running arbitrary inference jobs.
- Don't worry about, e.g., arbitrary seeds; accept DoS risk.
- Support uvicorn in development, lambda in production.
- Keep it simple.
"""

import logging
import os

from typing import (
    Optional,
    Union,
)

import pydantic

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
)
from pydantic import (
    AnyHttpUrl,
    Field,
)
from mangum import Mangum

from .banana import (
    BananaAPI,
    ModelInputs,
    ModelRunInputs,
)
from .cache import (
    CacheKey,
    DiffusionCache,
)
from .grid_types import (
    GridImageInfo,
    GridPrompt,
    GridRunStatus,
)
from .signing import Signer

logger = logging.getLogger(__name__)

class Settings(pydantic.BaseSettings):
    # how to interact with inference server
    banana_api_url: AnyHttpUrl
    banana_api_key: str = Field(min_length=1)
    banana_model_key: str = Field(min_length=1)
    banana_timeout_seconds: int = 900

    # how the app itself should operate
    diffgrid_signing_key: str
    diffgrid_cache_bucket: str
    diffgrid_auth_header: Optional[str]
    diffgrid_root_path: str = "/api"

    # sentry monitoring
    sentry_dsn: Optional[AnyHttpUrl]

api = FastAPI(title="Diffusion Grid API")
settings = Settings.parse_obj({})
banana = BananaAPI(
    api_url=settings.banana_api_url,
    api_key=settings.banana_api_key,
    model_key=settings.banana_model_key,
    timeout=settings.banana_timeout_seconds,
)
cache = DiffusionCache(bucket=settings.diffgrid_cache_bucket)
signer = Signer(key=settings.diffgrid_signing_key)

@api.get("/prompts", response_model=list[GridPrompt])
def get_prompts():
    unsigned_prompts = [
        "fantasy wizard, portrait, cartoon illustration, colorful",
        "detailed cityscape, isometric, 3d, pixel art, urbanism, vibrant",
        "80s science fiction spacecraft, artistic, detailed, greebling, john berkey, john harris",
        "forest, trees, butterflies, flowers, small animals, watercolor, beautiful",
        "adventure game, myst, riven, interior, intricate, colorful, blue sky",
        "universe, astronomy, astrophotography, high resolution, hubble telescope, detailed",
        "sailboat at sea, stormclouds, detailed, oil on canvas",
        "landscape photo, sunset, mountains, trees, 35mm film, slr, nikon, canon",
    ]

    return [
        GridPrompt(
            text=prompt,
            signature=signer.sign_critical_inputs(prompt=prompt, latents=None),
        )
        for prompt in unsigned_prompts
    ]

@api.post("/diffusions", response_model=Union[GridImageInfo, GridRunStatus])
def run_diffusion(run_inputs: ModelRunInputs, signature: str):
    # reject arbitrary prompts and latents
    expected = signer.sign_critical_inputs(
        prompt=run_inputs.prompt,
        latents=run_inputs.latents,
    )

    if signature != expected:
        raise HTTPException(status_code=400, detail="signature does not match")

    # return from cache if present
    cache_key = cache.key(run_inputs)
    cached = cache.fetch(cache_key)

    if cached is not None:
        return cached

    # cache miss; start a fresh diffusion run
    model_inputs = ModelInputs(cache_key=cache_key, run_inputs=run_inputs)
    (message, call_id) = banana.request_start(model_inputs)

    return GridRunStatus(message=message, call_id=call_id)

@api.get("/diffusions/{call_id}", response_model=Union[GridImageInfo, GridRunStatus])
def get_diffusion(call_id: str):
    # check run status with banana; we may get a "still running" response,
    # may get model outputs, or may time out (and assume we're still running)
    try:
        (message, model_outputs) = banana.request_check(call_id)
    except TimeoutError:
        message = "timeout; probably running"
        model_outputs = None

    if model_outputs is None:
        return GridRunStatus(call_id=call_id, message=message)
    else:
        run_outputs = model_outputs.run_outputs

        image_info = GridImageInfo(
            diffusion=run_outputs,
            signatures={
                v.timestep: signer.sign_critical_inputs(
                    prompt=model_outputs.prompt,
                    latents=v.tensor,
                )
                for v in run_outputs.trajectory
            },
        )

        cache.store(CacheKey(model_outputs.cache_key), image_info)

        return image_info

if settings.diffgrid_root_path != "":
    api_root = FastAPI()

    api_root.mount(settings.diffgrid_root_path, api)
else:
    api_root = api

@api_root.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if request.headers.get("Authorization") != settings.diffgrid_auth_header:
        return Response(
            status_code=401,
            content="authentication failure",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        return await call_next(request)

if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
    logger.setLevel(logging.INFO)

    handle_event = Mangum(api_root, lifespan="off")

if settings.sentry_dsn is not None:
    import sentry_sdk

    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            AwsLambdaIntegration(timeout_warning=True),
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,
    )
